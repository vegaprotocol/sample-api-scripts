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
	// __get_parties:
	// Request a list of parties trading on a Vega network
	request := api.PartiesRequest{}
	parties, err := dataClient.Parties(context.Background(), &request)
	if err != nil {
		panic(err)
	}

	fmt.Printf("Parties: %v\n", parties)
	// :get_parties__

	partyID := parties.Parties[0].Id
	// __get_party_by_id:
	// Request a party by their identifier (this is their public key)
	partyByIDReq := api.PartyByIDRequest{PartyId: partyID}
	partyByIDResp, err := dataClient.PartyByID(context.Background(), &partyByIDReq)
	if err != nil {
		panic(err)
	}

	fmt.Printf("PartyById: %v\n", partyByIDResp.Party)
	// :get_party_by_id__
}
