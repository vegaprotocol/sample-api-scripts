package main

import (
	"context"
	"fmt"
	"os"

	"code.vegaprotocol.io/vega/proto/api"
	"google.golang.org/grpc"
)

func main() {
	reference := "4617844f-6fab-4cf6-8852-e29dbd96e5f1"
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
	request := api.OrderByReferenceRequest{Reference: reference}
	order, err := dataClient.OrderByReference(context.Background(), &request)
	if err != nil {
		panic(err)
	}

	fmt.Printf("OrderByReference: %s", order)
}
