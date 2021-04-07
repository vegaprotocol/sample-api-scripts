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

	// __get_markets:
	// Request a list of markets available on the specified Vega Network
	request := api.MarketsRequest{}
	markets, err := dataClient.Markets(context.Background(), &request)
	if err != nil {
		panic(err)
	}

	fmt.Printf("Markets: %s", markets)
	// :get_markets__
	marketId := markets.Markets[0].Id

	// __get_market_data:
	// Request a single market by identifier on a Vega network
	requestMarket := api.MarketByIDRequest{MarketId: marketId}
	MarketObject, err := dataClient.MarketByID(context.Background(), &requestMarket)
	if err != nil {
		panic(err)
	}

	fmt.Printf("MarketData: %s", MarketObject)
	// :get_market_data__
}
