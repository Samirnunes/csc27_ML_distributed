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
		if err := client.Call("fit", nil, &reply); err != nil {
			log.Fatalf("Error during fitting: %v", err)
		}
	}
} 