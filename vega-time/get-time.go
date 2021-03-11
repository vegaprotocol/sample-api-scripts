package main

import (
	"fmt"

	"github.com/vegaprotocol/api-clients/go/generated/code.vegaprotocol.io/vega/proto/api"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
)

func main() {
	conn, err := grpc.Dial("NODE_gRPC_URL", grpc.WithInsecure())
	if err != nil {
		fmt.Println(err)
		return
	}
	defer conn.Close()

	// __get_time:
	// Request the latest timestamp in nanoseconds since epoch from the Vega network
	dataClient := api.NewTradingDataServiceClient(conn)
	request := api.GetVegaTimeRequest{}
	vegaTime, err := dataClient.GetVegaTime(context.Background(), &request)

	// The "timestamp" field contains the resulting data we need.
	fmt.Printf("Vega time: %s", vegaTime.Timestamp)
	// :get_time__
}
