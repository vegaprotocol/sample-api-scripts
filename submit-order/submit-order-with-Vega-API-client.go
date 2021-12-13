package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"

	api "code.vegaprotocol.io/protos/data-node/api/v1"
	proto "code.vegaprotocol.io/protos/vega"
	v1 "code.vegaprotocol.io/protos/vega/commands/v1"
	walletpb "code.vegaprotocol.io/protos/vega/wallet/v1"
	service "code.vegaprotocol.io/vegawallet/service"

	wallethelper "code.vegaprotocol.io/sample/api/scripts/wallet-helper"

	"golang.org/x/net/context"
	"google.golang.org/grpc"
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

	walletserverURL = wallethelper.CheckWalletUrl(walletserverURL)

	walletConfig := wallethelper.WalletConfig{
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

	var token service.TokenResponse
	body, err := wallethelper.LoginWallet(walletConfig)
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
	var keypair service.KeysResponse
	json.Unmarshal([]byte(body), &keypair)

	if len(keypair.Keys) == 0 {
		panic("No keys!")
	}

	pubkey := keypair.Keys[0].Key()
	fmt.Println("pubkey: ", pubkey)

	// __get_market:
	// Get a list of markets
	marketRequest := api.MarketsRequest{}
	markets, err := dataClient.Markets(context.Background(), &marketRequest)
	if err != nil {
		panic(err)
	}
	marketId := markets.Markets[0].Id
	// :get_market__

	// __prepare_order:
	// Vega node: Prepare the SubmitOrder
	orderSubmission := v1.OrderSubmission{
		Size:        1,
		Price:       "100000",
		MarketId:    marketId,
		Side:        proto.Side_SIDE_BUY,
		TimeInForce: proto.Order_TIME_IN_FORCE_GTC,
		Type:        proto.Order_TYPE_LIMIT,
	}

	order := walletpb.SubmitTransactionRequest{
		PubKey:    pubkey,
		Propagate: true,
		Command: &walletpb.SubmitTransactionRequest_OrderSubmission{
			OrderSubmission: &orderSubmission,
		},
	}

	_, err = wallethelper.SendTransaction(walletConfig, token.Token, order)
	if err != nil {
		panic(err)
	}
}
