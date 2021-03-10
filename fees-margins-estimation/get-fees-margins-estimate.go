package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strings"

	"github.com/vegaprotocol/api-clients/go/generated/code.vegaprotocol.io/vega/proto"
	"github.com/vegaprotocol/api-clients/go/generated/code.vegaprotocol.io/vega/proto/api"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
)

type Req struct {
	Wallet     string `json:"wallet"`
	Passphrase string `json:"passphrase"`
}

type Token struct {
	Token string `json:"token"`
}

type Keypair struct {
	Keys []struct {
		Pub     string      `json:"pub"`
		Algo    string      `json:"algo"`
		Tainted bool        `json:"tainted"`
		Meta    interface{} `json:"meta"`
	} `json:"keys"`
}

func checkWalletURL(url string) string {
	suffixs := []string{"/api/v1/", "/api/v1", "/"}
	for _, suffix := range suffixs {
		if strings.HasSuffix(url, suffix) {
			fmt.Printf("There's no need to add %s to WALLETSERVER_URL.", suffix)
			fmt.Printf("Removing it.")
			url = string(url[:len(url)-len(suffix)])
		}
	}
	return url
}

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
	walletPassword := os.Getenv("WALLET_PASSPHRASE")
	if len(walletPassword) == 0 {
		panic("WALLET_PASSPHRASE is null or empty")
	}

	walletserverURL = checkWalletURL(walletserverURL)

	conn, err := grpc.Dial(nodeURLGrpc, grpc.WithInsecure())
	if err != nil {
		panic(err)
	}
	defer conn.Close()

	dataClient := api.NewTradingDataServiceClient(conn)

	// Create new wallet
	createNewWallet := false
	var url string
	if createNewWallet {
		url = walletserverURL + "/api/v1/wallets"
	} else {
		url = walletserverURL + "/api/v1/auth/token"
	}

	// Make request to create new wallet or log in to existing wallet
	jsonStr := []byte("{\"wallet\":\"" + walletName + "\",\"passphrase\":\"" + walletPassword + "\"}")
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonStr))

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	fmt.Println(url, " returns response Status:", resp.Status)
	fmt.Println("response Headers:", resp.Header)

	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))
	var token Token
	json.Unmarshal([]byte(body), &token)

	fmt.Println(token.Token)

	// List existing keypairs
	url = walletserverURL + "/api/v1/keys"
	req, err = http.NewRequest("GET", url, nil)
	req.Header.Set("Authorization", "Bearer "+token.Token)

	client = &http.Client{}
	resp, err = client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, _ = ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))
	var keypair Keypair
	json.Unmarshal([]byte(body), &keypair)

	if len(keypair.Keys) == 0 {
		panic("No keys!")
	}

	pubkey := keypair.Keys[0].Pub
	fmt.Println("pubkey: ", pubkey)

	// Find market
	// Request a list of markets available on the specified Vega Network
	request := api.MarketsRequest{}
	markets, err := dataClient.Markets(context.Background(), &request)
	if err != nil {
		panic(err)
	}

	marketID := markets.Markets[0].Id
	fmt.Printf("Market id: %s\n", marketID)

	// Fee estimation
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
	estimation, _ := dataClient.EstimateFee(context.Background(), &estimationRequest)
	fmt.Printf("Estimation: %v\n", estimation)

	// Margin estimation
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
	margin, _ := dataClient.EstimateMargin(context.Background(), &marginRequest)
	fmt.Printf("Margin estimation: %v\n", margin)
}
