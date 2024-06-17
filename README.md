# Website Webhook

Watches a website, sending a request in case the website changed.
Still work in progress.

## Configuration

```yaml
webhookConfig:
  runOnce: false # if set to true, the service will run once on startup and exit, default is false
  schedule: "0 */3 * * *" # cronjob schedule, default is every 3 minutes, if set 'runOnce' will be ignored
websiteObservers: # regex to match the body of the mail, if no body is needed do not set this
- url: "test" # name json attribute in the callback 
  name: "test1"
  xpath: ""
  callback:
    url: "https://example.com/callback" # callback url
    method: "POST" # method of the callback, has to be provided as uppercase string
    timeout: 24s # timeout for the callback, default is 24 seconds
    retries: 0 # number of retries for the callback, default is 0
    headers:
    - name: "Content-Type"
      value: "application/json"
    body:
    - name: "test"
      value: "<<website.name>>"
```

## Templating

The body allows for templating with double braces. Allowed variables are:

placesholder | description
----------- | -----------
`<<websiteObservers.name>>` | set value in `websites.name`
`<<websiteObservers.url>>` | set value in `websites.url`
`<<websiteObservers.xpath>>` | set value in `websites.xpath`
`<<value.old>>` | the old value of the xpath
`<<value.new>>` | the new value of the xpath

## Links

- scheduling <https://github.com/go-co-op/gocron/tree/v2>