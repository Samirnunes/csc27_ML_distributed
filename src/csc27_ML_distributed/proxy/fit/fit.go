package fit

import (
	"log"
	"proxy/connect"
)


func Fit(){
	servers := connect.InitRPCConnections()

	log.Println("Fitting server's models...")
	for _, client := range servers.Clients {
		defer client.Close()
		var reply string
		go client.Call("fit", nil, &reply)
	}
} 