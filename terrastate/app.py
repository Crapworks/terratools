#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import json
import errno

from os.path import dirname
from os.path import join

from flask import Flask
from flask import request
from flask import jsonify
from flask.views import MethodView

from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException


class TerraformState(dict):
    """Representation of a Terraform statefile"""

    def __init__(self, config):
        dict.__init__(self)
        self.env = None
        self.config = config
        self.statepath = self._mkstatedir(config['statepath'])
        self.update({
            'version': 1,
            'serial': 0,
            'modules': [{
                'path': ['root'],
                'outputs': {},
                'resources': {}
            }]
        })

    def _mkstatedir(self, statepath):
        try:
            os.makedirs(statepath, mode=0o744)
        except OSError as err:
            if err.errno == errno.EEXIST and os.path.isdir(statepath):
                pass
            else:
                raise
        return statepath

    def _getstatefilename(self, env):
        return os.path.join(self.statepath, '%s-tfstate.json' % (env, ))

    def _getlockfilename(self, env):
        return os.path.join(self.statepath, '%s-tfstate.lock' % (env, ))

    def load(self):
        if not os.path.isfile(self._getstatefilename(self.env)):
            return
        with open(self._getstatefilename(self.env)) as fh:
            self.update(json.load(fh))

    def save(self):
        with open(self._getstatefilename(self.env), 'w+') as fh:
            json.dump(self, fh, indent=2)

    def destroy(self):
        if os.path.isfile(self._getstatefilename(self.env)):
            os.unlink(self._getstatefilename(self.env))

    def lock(self):
        if os.path.isfile(self._getlockfilename(self.env)):
            raise Exception('Already locked')
        with open(self._getlockfilename(self.env), 'w') as fh:
            fh.write('locked')

    def unlock(self):
        if os.path.isfile(self._getlockfilename(self.env)):
            os.unlink(self._getlockfilename(self.env))
        else:
            raise Exception('Not locked')


class Config(dict):
    """A simple json config file loader

    :param str filename: path to the json file
    """
    def __init__(self, filename):
        dict.__init__(self)
        self.update(json.load(open(filename)))


class StateView(MethodView):
    """Terraform State MethodView"""

    def __init__(self, *args, **kwargs):
        MethodView.__init__(self, *args, **kwargs)
        self.config = Config(join(dirname(__file__), 'config.json'))
        self.state = TerraformState(self.config)

    def get(self, env):
        self.state.env = env
        self.state.load()
        return jsonify(self.state)

    def post(self, env):
        self.state.env = env
        self.state.update(request.get_json())
        self.state.save()
        return jsonify(self.state)

    def delete(self, env):
        self.state.env = env
        self.state.update(request.get_json())
        self.state.destroy()
        return jsonify(self.state)

    def lock(self, env):
        self.state.env = env
        self.state.lock()
        self.state.load()
        return jsonify(self.state)

    def unlock(self, env):
        self.state.env = env
        self.state.unlock()
        self.state.load()
        return jsonify(self.state)


class TerraStateApi(Flask):
    def __init__(self, name):
        Flask.__init__(self, name)

        dhc_view = StateView.as_view('status')
        self.add_url_rule('/', defaults={'env': None}, view_func=dhc_view)
        self.add_url_rule('/<env>', view_func=dhc_view, methods=['GET', 'POST', 'DELETE', 'LOCK', 'UNLOCK'])

        # add custom error handler
        for code in default_exceptions.iterkeys():
            self.register_error_handler(code, self.make_json_error)

    def make_json_error(self, ex):
        if isinstance(ex, HTTPException):
            code = ex.code
            message = ex.description
        else:
            code = 500
            message = str(ex)

        response = jsonify(code=code, message=message)
        response.status_code = code

        return response


app = TerraStateApi(__name__)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
