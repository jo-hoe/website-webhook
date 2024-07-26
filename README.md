# Website Webhook

Scrapes a website, sending a request in case the website is updated.
Still a work in progress.

## Configuration

```yaml
webhookConfig:
  interval: "3m" # interval describing how often the function is run, default is every 3 minutes, if set 'runOnce' will be ignored
websiteObserver:
  url: "https://myurl.com"
  commands:
    - kind: "triggerCallbackOnChangedState"
      parameters:
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
      value: "The value on page <<websiteObserver.url>> changed from '<<command.oldState>>' to '<<command.changedState>>'"
```

## Templating

The body allows for templating with double braces. Allowed variables are:

placesholder | description
----------- | -----------
`<<websiteObserver.url>>` | set value in `websiteObserver.url`
`<<value.old>>` | the old value of the xpath
`<<value.new>>` | the new value of the xpath
