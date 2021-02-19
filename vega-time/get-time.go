package main

import (
	"fmt"

	"code.vegaprotocol.io/vega/proto/api"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
)

func main() {
	conn, err := grpc.Dial("NODE_gRPC_URL", grpc.WithInsecure())
	if err != nil {
		fmt.Println(err)
		return 1
	}
	defer conn.Close()

	dataClient := api.NewTradingDataServiceClient(conn)
	request := api.GetVegaTimeRequest{}
	vegaTime, err := dataClient.GetVegaTime(context.Background(), &request)

	fmt.Printf("Vega time: %d", vegaTime)
}
