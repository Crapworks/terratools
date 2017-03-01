#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import json
import argparse

import hcl

from jinja2 import Environment
from jinja2 import FileSystemLoader


def load_variables(filenames):
    """Load terraform variables"""

    variables = {}

    for terrafile in glob.glob('./*.tf'):
        with open(terrafile) as fh:
            data = hcl.load(fh)
            for key, value in data.get('variable', {}).iteritems():
                if 'default' in value:
                    variables.update({key: value['default']})

    for varfile in filenames:
        with open(varfile) as fh:
            data = hcl.load(fh)
            variables.update(data)

    return variables


def render(template, context):
    """Redner Jinja templates"""

    path, filename = os.path.split(template)
    return Environment(
        loader=FileSystemLoader(path or './')
    ).get_template(filename).render(context)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-var-file', dest='vfile', action='append', default=[])
    parser.add_argument('-t', '--test', action='store_true')
    parser.add_argument('-s', '--showvars', action='store_true')
    args = parser.parse_args()

    context = load_variables(args.vfile)
    if args.showvars:
        print(json.dumps(context, indent=2))

    for template in glob.glob('./*.jinja'):
        rendered_filename = '{}.tf'.format(os.path.splitext(template)[0])
        if args.test:
            print(render(template, context))
        else:
            with open(rendered_filename, 'w') as fh:
                fh.write(render(template, context))


if __name__ == '__main__':
    main()
