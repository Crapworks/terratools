# TerraState

This is more ore less a working boilerplate for people who want to use [Terraforms](https://www.terraform.io) remote feature with a HTTP backend. The code is small and simple. As it is, it supports multiple environments and saves the state as plain json files on disk. It can be easily extended to work with several backends.

## Quickstart

**Prerequisites**

* some terraform code
* flask installed on the http server

**Clone the repo**

```bash
$ git clone https://github.com/Crapworks/terratools.git
```

**Start the server**

```bash
$ cd terratools/terrastate && ./app.py
```

The server runs per default an port 5000. This can be changed in the ```app.py``` by adding the ```port``` argument the the ```run()``` function. There is also a ready to use wsgi file for deploying the app into apache or nginx.

**Configure terraform remote**
```bash
$ terraform remote config -backend=http -backend-config="address=http://servername:5000/environment"
Remote configuration updated
Remote state configured and pulled.
```

Replace ```servername``` with the hostname of the server where the app is running and ```environment``` with the name of the environment you want to save the state under.

Now you can use the backend!

```bash
$ terraform remote push
State successfully pushed!
```
