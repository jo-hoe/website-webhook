package config

type Config struct {
	WebhookConfig   WebhookConfig     `yaml:"webhookConfig"`
	WebsiteObserver []WebsiteObserver `yaml:"websiteObservers"`
}

type WebhookConfig struct {
	RunOnce  bool   `yaml:"runOnce"`
	Schedule string `yaml:"schedule"`
}

type Callback struct {
	URL     string            `yaml:"url"`
	Method  string            `yaml:"method"`
	Timeout string            `yaml:"timeout"`
	Retries int               `yaml:"retries"`
	Headers map[string]string `yaml:"headers"`
	Body    map[string]string `yaml:"body"`
}

type WebsiteObserver struct {
	URL      string   `yaml:"url"`
	Name     string   `yaml:"name"`
	XPath    string   `yaml:"xpath"`
	Callback Callback `yaml:"callback"`
}
