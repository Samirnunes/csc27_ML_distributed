package fit

import (
	"log"
	"proxy/connect"
	"sync"

	"github.com/kolo/xmlrpc"
)

func fit(client *xmlrpc.Client, wg *sync.WaitGroup) {
    defer wg.Done() // Ensure the WaitGroup is decremented

    var reply string
    if err := client.Call("fit", nil, &reply); err != nil {
        log.Println("error during fitting:", err)
        return
    }
}

func Fit() {
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
