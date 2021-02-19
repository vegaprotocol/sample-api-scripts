package main

import (
	"context"
	"fmt"
	"os"

	"code.vegaprotocol.io/vega/proto/api"
	"google.golang.org/grpc"
)

func main() {
	nodeURLGrpc := os.Getenv("NODE_URL_GRPC")
	if len(nodeURLGrpc) == 0 {
		panic("NODE_URL_GRPC is null or empty")
	}

	conn, err := grpc.Dial(nodeURLGrpc, grpc.WithInsecure())
	if err != nil {
		panic(err)
	}
	defer conn.Close()

	dataClient := api.NewTradingDataServiceClient(conn)
	request := api.PartiesRequest{}
	parties, err := dataClient.Parties(context.Background(), &request)
	if err != nil {
		panic(err)
	}

	fmt.Printf("Parties: %s", parties)
}
