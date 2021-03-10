package main

import (
	"context"
	"fmt"
	"io"
	"os"

	"github.com/vegaprotocol/api-clients/go/generated/code.vegaprotocol.io/vega/proto"
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

	// Request the identifier for a market

	request := api.MarketsRequest{}
	markets, err := dataClient.Markets(context.Background(), &request)
	if err != nil {
		panic(err)
	}
	marketID := markets.Markets[0].Id
	fmt.Printf("Found market: %s \n", marketID)

	fmt.Println("Connecting to stream...")

	eventType := proto.BusEventType_BUS_EVENT_TYPE_MARKET_TICK
	event, err := dataClient.ObserveEventBus(context.Background())

	done := make(chan bool)
	go func() {
		for {
			resp, err := event.Recv()

			if err == io.EOF {
				// read done.
				close(done)
				return
			}
			if err != nil {
				panic(err)
			}
			fmt.Printf("Resp received: %s\n", &resp.Events)
		}
	}()

	observerEvent := api.ObserveEventBusRequest{Type: []proto.BusEventType{eventType}, MarketId: marketID}
	event.Send(&observerEvent)
	event.CloseSend()

	<-done //we will wait until all response is received
	fmt.Printf("finished")

}
