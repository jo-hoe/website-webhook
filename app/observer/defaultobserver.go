package observer

import (
	"net/http"

	"github.com/antchfx/htmlquery"
	"golang.org/x/net/html"
)

type DefaultObserver struct{}

func (o *DefaultObserver) GetState(url string, xpath string) (newState string, err error) {
	response, err := http.Get(url)
	if err != nil {
		return
	}
	defer response.Body.Close()

	var doc *html.Node
	doc, err = htmlquery.Parse(response.Body)
	if err != nil {
		return
	}
	node := htmlquery.FindOne(doc, xpath)
	if node == nil {
		return
	}
	newState = htmlquery.InnerText(node)

	return newState, nil
}
