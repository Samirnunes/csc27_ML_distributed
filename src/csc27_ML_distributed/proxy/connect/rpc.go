package connect

import (
	"log"

	"github.com/kolo/xmlrpc"
)

type Servers struct {
	ServerAddresses, ServerNames []string
	Clients []*xmlrpc.Client
}

func InitRPCConnections() Servers{
	serverAddresses := []string{"http://ml-server-a:80", "http://ml-server-b:80", "http://ml-server-c:80"}
	serverNames := []string{"server_a", "server_b", "server_c"}
	
	clients := make([]*xmlrpc.Client, len(serverAddresses))
	
	for i, address := range serverAddresses {
		client, err := xmlrpc.NewClient(address, nil)
		if err != nil {
			log.Fatalf("Failed to connect to server %s: %v", address, err)
		}
		clients[i] = client
	}
	return Servers{
		ServerAddresses: serverAddresses, 
		ServerNames: serverNames,
		Clients: clients,
	}
}

