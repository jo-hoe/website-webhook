# Website Webhook

[![Test Status](https://github.com/jo-hoe/website-webhook/actions/workflows/test.yml/badge.svg)](https://github.com/jo-hoe/website-webhook/actions?workflow=test)

Scrapes a website, sending a request in case the website is updated.
Provides a helm chart for K8s deployments.

## Configuration

```yaml
interval: "3m" # interval* between command execution, default is every 3 minutes
url: "https://myurl.com"
commands:
  - kind: "triggerCallbackOnChangedState" # provides name, xpath, kind + old and new value for templating
    name: "changedState"
    xpath: "//a[@class='some class']/text()"
callback:
  url: "https://example.com/callback" # callback url
  method: "POST" # method of the callback, has to be provided as uppercase string
  timeout: 24s # timeout* for the callback, default is 24 seconds
  retries: 0 # number of retries for the callback, default is 0
  headers:
  - name: "Content-Type"
    value: "application/json"
  body:
  - name: "event"
    value: "some static string"
  - name: "description"
    value: "The value on page <<url>> changed from '<<commands.changedState.old>>' to '<<commands.changedState.new>>'"
```

`intervals` and `timeout` only support certain string formats. See below

|string|interval|
|---|---|
|s|seconds|
|m|minutes|
|h|hours|
|d|days|

## Templating

The the values of `callback.body` and `callback.headers` allow for templating with double braces. Values can be address as follows:

| placesholder | command kind | description |
| ----------- | ----------- | ----------- |
| `<<url>>` | all kinds | set value in `url` |
| `<<commands.{command_name}.name>>` | all kinds | set value in `name` of the command |
| `<<commands.{command_name}.xpath>>` | `triggerCallbackOnChangedState` | set to the xpath of the command |
| `<<commands.{command_name}.old>>` | `triggerCallbackOnChangedState` | the old value of the xpath |
| `<<commands.{command_name}.new>>` | `triggerCallbackOnChangedState` | the new value of the xpath |

## Prerequisites to run locally

The project is using `make`. `make` is typically installed by default on Linux and Mac.
`make` is not strictly required, but it helps and documents commonly used commands.

If you run on Windows, you can directly install it from [gnuwin32](https://gnuwin32.sourceforge.net/packages/make.htm) or via `winget`

```PowerShell
winget install GnuWin32.Make
```

Futhermore you will need Docker and Python.
Run `make init` to install all dependencies in a virtual python environment.

### How to Use

You can check all `make` commands by running

```bash
make help
```

## How To Run Locally

For local development and testing, put a [`config.yaml`](#configuration) in folder `dev`.
To run the service locally, you can use `docker-compose` or just run it via make:

```bash
make start
```

### K3D

[Install K3D](https://k3d.io/#install-script) to run the service in a local kubernetes cluster.
Ensure your [turned on Kubernetes in Docker Desktop](https://docs.docker.com/desktop/kubernetes/#install-and-turn-on-kubernetes).
Run the following command to start the service in a local kubernetes cluster.

```bash
make start-k3d
```

and stop it with

```bash
make stop-k3d
```

### Test

You can use `make` to start the tests.
Just run

```bash
make test
```
