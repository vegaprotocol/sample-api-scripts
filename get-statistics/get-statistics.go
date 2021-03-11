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

	dataClient := api.NewTradingDataServiceClient(conn)
	// __get_statistics:
	// Request the statistics for a node on Vega
	request := api.StatisticsRequest{}
	statistics, err := dataClient.Statistics(context.Background(), &request)
	if err != nil {
		panic(err)
	}

	fmt.Printf("Network statistics: %s", statistics)
	// :get_statistics__
}
