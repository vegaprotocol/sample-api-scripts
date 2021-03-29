package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"

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

	// __get_orders_for_party:
	// Request a list of orders by party (pubKey)
	ordersByPartyReq := api.OrdersByPartyRequest{PartyId: pubkey}
	ordersByPartyResp, err := dataClient.OrdersByParty(context.Background(), &ordersByPartyReq)
	if err != nil {
		panic(err)
	}
	fmt.Printf("OrdersByParty: %v\n", ordersByPartyResp)
	// :get_orders_for_party__

	// __get_trades_for_party:
	//Request a list of trades by market on a Vega network
	tradesByPartyReq := api.TradesByPartyRequest{PartyId: pubkey}
	tradesByPartyResp, err := dataClient.TradesByParty(context.Background(), &tradesByPartyReq)
	if err != nil {
		panic(err)
	}
	fmt.Printf("TradesByParty: %v\n", tradesByPartyResp)
	// :get_trades_for_party__
}
