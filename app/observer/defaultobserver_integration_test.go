package observer

import "testing"

func TestDefaultObserver_GetState(t *testing.T) {
	type args struct {
		url   string
		xpath string
	}
	tests := []struct {
		name         string
		o            *DefaultObserver
		args         args
		wantNewState string
		wantErr      bool
	}{
		{
			name: "positive test",
			o:    &DefaultObserver{},
			args: args{
				url:   "https://github.com/gocolly/colly/tree/master",
				xpath: "//a[@class='color-fg-default']",
			},
			wantNewState: "colly",
			wantErr:      false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotNewState, err := tt.o.GetState(tt.args.url, tt.args.xpath)
			if (err != nil) != tt.wantErr {
				t.Errorf("DefaultObserver.GetState() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if gotNewState != tt.wantNewState {
				t.Errorf("DefaultObserver.GetState() = %v, want %v", gotNewState, tt.wantNewState)
			}
		})
	}
}
