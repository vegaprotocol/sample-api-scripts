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

	// __get_trades_for_order:
	// Request a list of trades for a specific order on a Vega network
	orderID := "V0000929211-0046318720"
	tradesByOrderReq := api.TradesByOrderRequest{OrderId: orderID}
	tradesByOrderResp, err := dataClient.TradesByOrder(context.Background(), &tradesByOrderReq)
	if err != nil {
		panic(err)
	}
	fmt.Printf("TradesByOrder: %v\n", tradesByOrderResp)
	// :get_trades_for_order__

}
