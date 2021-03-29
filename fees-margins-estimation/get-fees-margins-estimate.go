package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"

	"github.com/vegaprotocol/api-clients/go/generated/code.vegaprotocol.io/vega/proto"
	"github.com/vegaprotocol/api-clients/go/generated/code.vegaprotocol.io/vega/proto/api"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"code.vegaprotocol.io/go-wallet/wallet"
)

func main() {
	nodeURLGrpc := os.Getenv("NODE_URL_GRPC")
	if len(nodeURLGrpc) == 0 {
		panic("NODE_URL_GRPC is null or empty")
	}
	walletserverURL := os.Getenv("WALLETSERVER_URL")
	if len(walletserverURL) == 0 {
		panic("WALLETSERVER_URL is null or empty")
	}
	walletName := os.Getenv("WALLET_NAME")
	if len(walletName) == 0 {
		panic("WALLET_NAME is null or empty")
	}
	walletPassphrase := os.Getenv("WALLET_PASSPHRASE")
	if len(walletPassphrase) == 0 {
		panic("WALLET_PASSPHRASE is null or empty")
	}

	walletserverURL = CheckWalletUrl(walletserverURL)

	walletConfig := WalletConfig{
		URL:        walletserverURL,
		Name:       walletName,
		Passphrase: walletPassphrase,
	}

	conn, err := grpc.Dial(nodeURLGrpc, grpc.WithInsecure())
	if err != nil {
		panic(err)
	}
	defer conn.Close()

	dataClient := api.NewTradingDataServiceClient(conn)

	var token wallet.TokenResponse
	body, err := LoginWallet(walletConfig)
	if err != nil {
		panic(err)
	}
	json.Unmarshal([]byte(body), &token)

	fmt.Println(token.Token)

	// List existing keypairs
	url := walletserverURL + "/api/v1/keys"
	req, err := http.NewRequest(http.MethodGet, url, nil)
	req.Header.Set("Authorization", "Bearer "+token.Token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, err = ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}
	fmt.Println("response Body:", string(body))
	var keypair wallet.KeysResponse
	json.Unmarshal([]byte(body), &keypair)

	if len(keypair.Keys) == 0 {
		panic("No keys!")
	}

	pubkey := keypair.Keys[0].Pub
	fmt.Println("pubkey: ", pubkey)

	// Find market
	// __get_market:
	// Request a list of markets available on the specified Vega Network
	request := api.MarketsRequest{}
	markets, err := dataClient.Markets(context.Background(), &request)
	if err != nil {
		panic(err)
	}
	// :get_market__

	marketID := markets.Markets[0].Id
	fmt.Printf("Market id: %s\n", marketID)

	// Fee estimation
	// __get_fees_estimate:
	// Request to estimate trading fees on a Vega network
	order := proto.Order{
		MarketId:    marketID,
		PartyId:     pubkey,
		Price:       100000,
		Size:        100,
		Side:        proto.Side_SIDE_BUY,
		TimeInForce: proto.Order_TIME_IN_FORCE_GTC,
		Type:        proto.Order_TYPE_LIMIT,
	}
	estimationRequest := api.EstimateFeeRequest{Order: &order}
	estimation, err := dataClient.EstimateFee(context.Background(), &estimationRequest)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Estimation: %v\n", estimation)
	// :get_fees_estimate__

	// Margin estimation
	// __get_margins_estimate:
	// Request to estimate trading margin on a Vega network
	order = proto.Order{
		MarketId:    marketID,
		PartyId:     pubkey,
		Price:       600000,
		Size:        100,
		Side:        proto.Side_SIDE_BUY,
		TimeInForce: proto.Order_TIME_IN_FORCE_GTC,
		Type:        proto.Order_TYPE_LIMIT,
	}
	marginRequest := api.EstimateMarginRequest{Order: &order}
	margin, err := dataClient.EstimateMargin(context.Background(), &marginRequest)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Margin estimation: %v\n", margin)
	// :get_margins_estimate__
}
