package main

import (
	"context"
	"fmt"
	"os"

	"github.com/vegaprotocol/api-clients/go/generated/code.vegaprotocol.io/vega/proto/api"
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

	// __get_order_by_ref:
	// Request an order by reference on a Vega network
	// Note: This is an example and order reference will be provided in the response
	// from a prepareSubmitOrder request in the field named `submitID` or similar.
	reference := "4617844f-6fab-4cf6-8852-e29dbd96e5f1"

	dataClient := api.NewTradingDataServiceClient(conn)
	request := api.OrderByReferenceRequest{Reference: reference}
	order, err := dataClient.OrderByReference(context.Background(), &request)
	if err != nil {
		panic(err)
	}

	fmt.Printf("OrderByReference: %s", order)
	// :get_order_by_ref__
}
