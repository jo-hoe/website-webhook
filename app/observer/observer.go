package observer

type Observer interface {
	GetState(url string, xpath string) (newState string)
}
