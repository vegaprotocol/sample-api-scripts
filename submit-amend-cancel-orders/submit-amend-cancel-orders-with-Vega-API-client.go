package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"time"

	api "code.vegaprotocol.io/protos/data-node/api/v1"
	proto "code.vegaprotocol.io/protos/vega"
	v1 "code.vegaprotocol.io/protos/vega/commands/v1"
	walletpb "code.vegaprotocol.io/protos/vega/wallet/v1"
	wallethelper "code.vegaprotocol.io/sample/api/scripts/wallet-helper"
	service "code.vegaprotocol.io/vegawallet/service"
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
	// tradingClient := core.NewCoreServiceClient(conn)

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
	keypair := struct {
		Keys []struct {
			Pubkey string `json:"pub"`
		} `json:"Keys"`
	}{}

	json.Unmarshal(body, &keypair)

	if len(keypair.Keys) == 0 {
		panic("No keys!")
	}

	fmt.Println(keypair.Keys)
	pubkey := keypair.Keys[0].Pubkey
	fmt.Println("pubkey: ", pubkey)

	// Get market
	// marketRequest := api.MarketsRequest{}
	// markets, err := dataClient.Markets(context.Background(), &marketRequest)
	if err != nil {
		panic(err)
	}
	// marketId := markets.Markets[5].Id
	marketId := "blah"
	// fmt.Printf("Market: %+v\n", markets.Markets[5])

	// Get Blockchain time
	// __get_expiry_time:
	// Request the current blockchain time, calculate an expiry time
	request := api.GetVegaTimeRequest{}
	vegaTime, _ := dataClient.GetVegaTime(context.Background(), &request)

	expireAt := vegaTime.Timestamp + (120 * 1e9)
	// :get_expiry_time__
	fmt.Printf("Blockchain time: %d\n", vegaTime.Timestamp)
	fmt.Printf("Order expiration time: %d\n", expireAt)

	// Submit order
	// __prepare_submit_order:
	// Prepare a submit order message

	orderSubmission := v1.OrderSubmission{
		Size:        10,
		Price:       "1",
		MarketId:    marketId,
		Side:        proto.Side_SIDE_BUY,
		TimeInForce: proto.Order_TIME_IN_FORCE_GTT,
		Type:        proto.Order_TYPE_LIMIT,
		ExpiresAt:   expireAt,
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
		fmt.Println(err)
		return
	}

	orderRef := "" // orderRequest.SubmitId

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
	price := proto.Price{Value: "2"}
	amend := v1.OrderAmendment{
		MarketId:    marketId,
		OrderId:     orderID,
		Price:       &price,
		TimeInForce: proto.Order_TIME_IN_FORCE_GTC,
	}

	order = walletpb.SubmitTransactionRequest{
		PubKey:    pubkey,
		Propagate: true,
		Command: &walletpb.SubmitTransactionRequest_OrderAmendment{
			OrderAmendment: &amend,
		},
	}

	// :prepare_amend_order__

	// Sign the prepared transaction

	_, err = wallethelper.SendTransaction(walletConfig, token.Token, order)
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
	// 1 - Cancel single order for this party (pubkey)
	cancel := v1.OrderCancellation{
		OrderId:  orderID,
		MarketId: marketId,
	}
	// :prepare_cancel_order_req1__

	// __prepare_cancel_order_req2:
	// 2 - Cancel all orders on market for this party (pubkey)
	cancel = v1.OrderCancellation{
		MarketId: marketId,
	}
	// :prepare_cancel_order_req2__

	// __prepare_cancel_order_req3:
	// 3 - Cancel all orders on all markets for this party (pubkey)
	cancel = v1.OrderCancellation{}
	// :prepare_cancel_order_req3__

	// __prepare_cancel_order:
	// Prepare the cancel order message
	order = walletpb.SubmitTransactionRequest{
		PubKey:    pubkey,
		Propagate: true,
		Command: &walletpb.SubmitTransactionRequest_OrderCancellation{
			OrderCancellation: &cancel,
		},
	}

	_, err = wallethelper.SendTransaction(walletConfig, token.Token, order)
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
