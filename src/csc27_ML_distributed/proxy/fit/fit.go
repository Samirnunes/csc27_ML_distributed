package fit

import (
	"log"
	"proxy/connect"
	"sync"

	"github.com/kolo/xmlrpc"
)

func fit(client *xmlrpc.Client, wg *sync.WaitGroup) {
	var reply string
	client.Call("fit", nil, &reply)
	wg.Done()
}


func Fit(){
	var wg sync.WaitGroup
	servers := connect.InitRPCConnections()

	log.Println("Fitting server's models...")
	for _, client := range servers.Clients {
		defer client.Close()
		wg.Add(1)
		go fit(client, &wg)
	}
	wg.Wait()
}
