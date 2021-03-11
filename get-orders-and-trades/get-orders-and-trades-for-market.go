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

	// Request a list of markets available on the specified Vega Network
	request := api.MarketsRequest{}
	markets, err := dataClient.Markets(context.Background(), &request)
	if err != nil {
		panic(err)
	}

	fmt.Printf("Markets: %s", markets)
	marketID := markets.Markets[0].Id

	// Request a list of orders by market on a Vega network
	ordersByMarketReq := api.OrdersByMarketRequest{MarketId: marketID}
	ordersByMarketResp, _ := dataClient.OrdersByMarket(context.Background(), &ordersByMarketReq)
	fmt.Printf("OrdersByMarket: %v\n", ordersByMarketResp)

	//Request a list of trades by market on a Vega network
	tradesByMarketReq := api.TradesByMarketRequest{MarketId: marketID}
	tradesByMarketResp, _ := dataClient.TradesByMarket(context.Background(), &tradesByMarketReq)
	fmt.Printf("TradesByMarket: %v\n", tradesByMarketResp)

}
