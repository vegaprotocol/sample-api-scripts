package main

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"time"

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
	tradingClient := api.NewTradingServiceClient(conn)

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

	// Get market
	marketRequest := api.MarketsRequest{}
	markets, err := dataClient.Markets(context.Background(), &marketRequest)
	if err != nil {
		panic(err)
	}
	marketId := markets.Markets[0].Id

	// Get Blockchain time
	// __get_expiry_time:
	// Request the current blockchain time, calculate an expiry time
	request := api.GetVegaTimeRequest{}
	vegaTime, err := dataClient.GetVegaTime(context.Background(), &request)

	expireAt := vegaTime.Timestamp + (120 * 1e9)
	// :get_expiry_time__
	fmt.Printf("Blockchain time: %d\n", vegaTime.Timestamp)
	fmt.Printf("Order expiration time: %d\n", expireAt)

	// Submit order
	// __prepare_submit_order:
	// Prepare a submit order message
	orderSubmission := proto.OrderSubmission{
		Size:        10,
		Price:       1,
		PartyId:     pubkey,
		MarketId:    marketId,
		Side:        proto.Side_SIDE_BUY,
		TimeInForce: proto.Order_TIME_IN_FORCE_GTT,
		Type:        proto.Order_TYPE_LIMIT,
		ExpiresAt:   expireAt,
	}

	order := api.PrepareSubmitOrderRequest{Submission: &orderSubmission}

	fmt.Printf("Request for PrepareSubmitOrder: %v\n", order)
	orderRequest, err := tradingClient.PrepareSubmitOrder(context.Background(), &order)
	// :prepare_submit_order__

	fmt.Printf("%v\n", err)
	fmt.Printf("%v\n", orderRequest)

	// Sign the prepared transaction
	data := orderRequest.Blob
	sEnc := base64.StdEncoding.EncodeToString([]byte(data))
	_, err = SignTransaction(walletConfig, token.Token, pubkey, string(sEnc))
	if err != nil {
		panic(err)
	}

	orderRef := orderRequest.SubmitId

	fmt.Printf("Signed order and sent to Vega\n")

	// Wait for order submission to be included in a block
	fmt.Printf("Waiting for blockchain...\n")
	time.Sleep(4 * time.Second)
	orderByRef := api.OrderByReferenceRequest{Reference: orderRef}
	orderByRefResp, err := dataClient.OrderByReference(context.Background(), &orderByRef)
	if err != nil {
		panic(err)
	}

	orderID := orderByRefResp.Order.Id
	orderStatus := orderByRefResp.Order.Status
	fmt.Printf("Order processed. ID: %s, Status: %d\n", orderID, orderStatus)

	// Amend order
	// __prepare_amend_order:
	// Prepare the amend order message
	price := proto.Price{Value: 2}
	amend := proto.OrderAmendment{
		MarketId:    marketId,
		PartyId:     pubkey,
		OrderId:     orderID,
		Price:       &price,
		TimeInForce: proto.Order_TIME_IN_FORCE_GTC,
	}

	amendObj := api.PrepareAmendOrderRequest{Amendment: &amend}
	amendResp, err := tradingClient.PrepareAmendOrder(context.Background(), &amendObj)
	if err != nil {
		panic(err)
	}
	// :prepare_amend_order__

	// Sign the prepared transaction
	data = amendResp.Blob
	sEnc = base64.StdEncoding.EncodeToString([]byte(data))
	_, err = SignTransaction(walletConfig, token.Token, pubkey, string(sEnc))
	if err != nil {
		panic(err)
	}

	fmt.Printf("Signed order amendment and sent to Vega\n")

	// Wait for amendment to be included in a block
	fmt.Printf("Waiting for blockchain...\n")
	time.Sleep(4 * time.Second)
	orderByRef = api.OrderByReferenceRequest{Reference: orderRef}
	orderByRefResp, err = dataClient.OrderByReference(context.Background(), &orderByRef)
	if err != nil {
		panic(err)
	}

	orderID = orderByRefResp.Order.Id
	orderStatus = orderByRefResp.Order.Status
	orderSize := orderByRefResp.Order.Size
	orderPrice := orderByRefResp.Order.Price
	orderTif := orderByRefResp.Order.TimeInForce

	fmt.Printf("Amended order:\n")
	fmt.Printf("ID: %s, Status: %d, Price(Old): 1,\n", orderID, orderStatus)
	fmt.Printf("Price(New): %d, Size(Old): 100, Size(New): %d\n", orderPrice, orderSize)
	fmt.Printf("TimeInForce(Old): TIME_IN_FORCE_GTT, TimeInForce(New): %d,\n", orderTif)

	// Cancel order
	// __prepare_cancel_order_req1:
	// 1 - Cancel single order for party (pubkey)
	cancel := proto.OrderCancellation{
		OrderId:  orderID,
		MarketId: marketId,
		PartyId:  pubkey,
	}
	// :prepare_cancel_order_req1__

	// __prepare_cancel_order_req2:
	// 2 - Cancel all orders on market for party (pubkey)
	cancel = proto.OrderCancellation{
		MarketId: marketId,
		PartyId:  pubkey,
	}
	// :prepare_cancel_order_req2__

	// __prepare_cancel_order_req3:
	// 3 - Cancel all orders on all markets for party (pubkey)
	cancel = proto.OrderCancellation{
		PartyId: pubkey,
	}
	// :prepare_cancel_order_req3__

	// __prepare_cancel_order:
	// Prepare the cancel order message
	orderCancelReq := api.PrepareCancelOrderRequest{
		Cancellation: &cancel,
	}
	orderCancelResp, err := tradingClient.PrepareCancelOrder(context.Background(), &orderCancelReq)
	if err != nil {
		panic(err)
	}
	// :prepare_cancel_order__
	fmt.Printf("%v\n", err)
	fmt.Printf("%v\n", orderCancelResp)

	// Sign the prepared transaction
	data = orderCancelResp.Blob
	sEnc = base64.StdEncoding.EncodeToString([]byte(data))
	_, err = SignTransaction(walletConfig, token.Token, pubkey, string(sEnc))
	if err != nil {
		panic(err)
	}

	fmt.Printf("Signed order cancellation request and sent to Vega\n")

	// Wait for amendment to be included in a block
	fmt.Printf("Waiting for blockchain...\n")
	time.Sleep(4 * time.Second)
	orderByRef = api.OrderByReferenceRequest{Reference: orderRef}
	orderByRefResp, err = dataClient.OrderByReference(context.Background(), &orderByRef)
	if err != nil {
		panic(err)
	}

	orderID = orderByRefResp.Order.Id
	orderStatus = orderByRefResp.Order.Status

	fmt.Printf("Cancelled order:\n")
	fmt.Printf("ID: %s, Status: %d\n", orderID, orderStatus)
}
