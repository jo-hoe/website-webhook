# Website Webhook

[![Test Status](https://github.com/jo-hoe/website-webhook/actions/workflows/test.yml/badge.svg)](https://github.com/jo-hoe/website-webhook/actions?workflow=test)

Scrapes a website, sending a request in case the website is updated.
Still a work in progress.

## Configuration

```yaml
interval: "3m" # interval describing how often the function is run, default is every 3 minutes
url: "https://myurl.com"
commands:
  - kind: "triggerCallbackOnChangedState" # provides name, xpath, kind + old and new value for templating
    name: "changedState"
    xpath: "//a[@class='some class']"
callback:
  url: "https://example.com/callback" # callback url
  method: "POST" # method of the callback, has to be provided as uppercase string
  timeout: 24s # timeout for the callback, default is 24 seconds
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

Intervals only support certain strings

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
