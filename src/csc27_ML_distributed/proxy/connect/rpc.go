package connect

import (
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/kolo/xmlrpc"
)

type Servers struct {
	ServerAddresses, ServerNames []string
	Clients                      []*xmlrpc.Client
}

func newClientWithCustomTransport(address string) (*xmlrpc.Client, error) {
	transport := &http.Transport{
		TLSHandshakeTimeout:    300 * time.Second,
		IdleConnTimeout:        300 * time.Second,
		MaxIdleConns:           10,
		MaxIdleConnsPerHost:    10,
		MaxResponseHeaderBytes: 100000,
		WriteBufferSize:        100000,
		ReadBufferSize:         100000,
	}

	return xmlrpc.NewClient(address, transport)
}

func InitRPCConnections() Servers {
	ML_SERVERS_NUMBER := 4

	serverNames := make([]string, ML_SERVERS_NUMBER)
	serverAddresses := make([]string, ML_SERVERS_NUMBER)

	for i := 1; i <= ML_SERVERS_NUMBER; i++ {
		serverNames[i-1] = "ml-server-" + strconv.Itoa(i)
		serverAddresses[i-1] = "http://" + serverNames[i-1] + ":80"
	}

	clients := make([]*xmlrpc.Client, len(serverAddresses))

	for i, address := range serverAddresses {
		client, err := newClientWithCustomTransport(address)
		if err != nil {
			log.Fatalf("Failed to connect to server %s: %v", address, err)
		}
		clients[i] = client
	}
	return Servers{
		ServerAddresses: serverAddresses,
		ServerNames:     serverNames,
		Clients:         clients,
	}
}
