package main

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/vegaprotocol/api-clients/go/generated/code.vegaprotocol.io/vega/proto"
	"github.com/vegaprotocol/api-clients/go/generated/code.vegaprotocol.io/vega/proto/api"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"google.golang.org/protobuf/types/known/wrapperspb"
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
	tradingClient := api.NewTradingServiceClient(conn)

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

	// Get market
	marketRequest := api.MarketsRequest{}
	markets, err := dataClient.Markets(context.Background(), &marketRequest)
	if err != nil {
		panic(err)
	}
	marketId := markets.Markets[0].Id

	// Get Blockchain time
	request := api.GetVegaTimeRequest{}
	vegaTime, err := dataClient.GetVegaTime(context.Background(), &request)

	expireAt := vegaTime.Timestamp + (120 * 1e9)
	fmt.Printf("Blockchain time: %d\n", vegaTime.Timestamp)
	fmt.Printf("Order expiration time: %d\n", expireAt)

	// Submit pegged order
	peggedOrder := proto.PeggedOrder{
		Offset:    -5,
		Reference: proto.PeggedReference_PEGGED_REFERENCE_MID,
	}
	orderSubmission := proto.OrderSubmission{
		Size:        1,
		Price:       100000,
		PartyId:     pubkey,
		MarketId:    marketId,
		Side:        proto.Side_SIDE_BUY,
		TimeInForce: proto.Order_TIME_IN_FORCE_GTT,
		Type:        proto.Order_TYPE_LIMIT,
		ExpiresAt:   expireAt,
		PeggedOrder: &peggedOrder,
	}

	order := api.PrepareSubmitOrderRequest{Submission: &orderSubmission}

	fmt.Printf("Request for PrepareSubmitOrder: %v\n", order)
	orderRequest, err := tradingClient.PrepareSubmitOrder(context.Background(), &order)

	fmt.Printf("%v\n", err)
	fmt.Printf("%v\n", orderRequest)

	// Sign the prepared transaction
	data := orderRequest.Blob
	sEnc := base64.StdEncoding.EncodeToString([]byte(data))
	jsonStr = []byte("{\"tx\":\"" + string(sEnc) + "\",\"pubkey\":\"" + pubkey + "\", \"propagate\": true}")

	req, err = http.NewRequest("POST", walletserverURL+"/api/v1/messages", bytes.NewBuffer(jsonStr))
	req.Header.Add("Authorization", "Bearer "+token.Token)

	client = &http.Client{}
	resp, err = client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, _ = ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))

	orderRef := orderRequest.SubmitId

	fmt.Printf("Signed pegged order and sent to Vega\n")

	// Wait for order submission to be included in a block
	fmt.Printf("Waiting for blockchain...\n")
	time.Sleep(4 * time.Second)
	orderByRef := api.OrderByReferenceRequest{Reference: orderRef}
	orderByRefResp, _ := dataClient.OrderByReference(context.Background(), &orderByRef)

	orderID := orderByRefResp.Order.Id
	orderStatus := orderByRefResp.Order.Status
	fmt.Printf("Pegged order processed. ID: %s, Status: %d\n", orderID, orderStatus)

	// Amend pegged order
	var peggedOffset wrapperspb.Int64Value
	peggedOffset.Value = -100
	amend := proto.OrderAmendment{
		MarketId:        marketId,
		PartyId:         pubkey,
		OrderId:         orderID,
		SizeDelta:       -25,
		TimeInForce:     proto.Order_TIME_IN_FORCE_GTC,
		PeggedReference: proto.PeggedReference_PEGGED_REFERENCE_BEST_BID,
		PeggedOffset:    &peggedOffset,
	}

	amendObj := api.PrepareAmendOrderRequest{Amendment: &amend}
	amendResp, _ := tradingClient.PrepareAmendOrder(context.Background(), &amendObj)

	// Sign the prepared transaction
	data = amendResp.Blob
	sEnc = base64.StdEncoding.EncodeToString([]byte(data))
	jsonStr = []byte("{\"tx\":\"" + string(sEnc) + "\",\"pubkey\":\"" + pubkey + "\", \"propagate\": true}")

	req, err = http.NewRequest("POST", walletserverURL+"/api/v1/messages", bytes.NewBuffer(jsonStr))
	req.Header.Add("Authorization", "Bearer "+token.Token)

	client = &http.Client{}
	resp, err = client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, _ = ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))

	fmt.Printf("Signed pegged order amendment and sent to Vega\n")

	// Wait for amendment to be included in a block
	fmt.Printf("Waiting for blockchain...\n")
	time.Sleep(4 * time.Second)
	orderByRef = api.OrderByReferenceRequest{Reference: orderRef}
	orderByRefResp, _ = dataClient.OrderByReference(context.Background(), &orderByRef)

	orderID = orderByRefResp.Order.Id
	orderStatus = orderByRefResp.Order.Status
	oderSize := orderByRefResp.Order.Size
	orderTif := orderByRefResp.Order.TimeInForce
	peggedOrderRef := orderByRefResp.Order.PeggedOrder

	fmt.Printf("Amended pegged order:\n")
	fmt.Printf("Pegged order processed. ID: %s, Status: %d\n", orderID, orderStatus)
	fmt.Printf("Size(Old): 50, Size(New): %d,\n", oderSize)
	fmt.Printf("TimeInForce(Old): TIME_IN_FORCE_GTT, TimeInForce(New): %d,\n", orderTif)
	fmt.Printf("Pegged at:\n%s\n", peggedOrderRef)
}
