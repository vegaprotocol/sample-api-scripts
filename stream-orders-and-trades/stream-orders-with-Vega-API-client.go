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

	// __stream_orders:
	// Subscribe to the Orders stream for the marketID specified
	// Optional: Market identifier - filter by market
	//            Party identifier - filter by party
	// By default, all orders on all markets for all parties will be returned on the stream.
	eventType := proto.BusEventType_BUS_EVENT_TYPE_ORDER
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
			fmt.Printf("Resp received: %v\n", &resp.Events)
		}
	}()

	observerEvent := api.ObserveEventBusRequest{Type: []proto.BusEventType{eventType}, MarketId: marketID}
	event.Send(&observerEvent)
	event.CloseSend()

	<-done //we will wait until all response is received
	// :stream_orders__
	fmt.Printf("finished")

}
