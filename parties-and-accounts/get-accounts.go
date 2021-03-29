package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strings"

	"github.com/vegaprotocol/api-clients/go/generated/code.vegaprotocol.io/vega/proto/api"
	"code.vegaprotocol.io/go-wallet/wallet"
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
	creationReq :=  &wallet.CreateLoginWalletRequest{Wallet: walletName, Passphrase: walletPassword}
	payload, err := json.Marshal(creationReq)
	if err != nil {
		panic(err)
	}
	req, err := http.NewRequest(http.MethodPost, url, bytes.NewBuffer(payload))

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	fmt.Println(url, " returns response Status:", resp.Status)
	fmt.Println("response Headers:", resp.Header)

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}
	fmt.Println("response Body:", string(body))
	var token wallet.TokenResponse
	json.Unmarshal([]byte(body), &token)

	fmt.Println(token.Token)

	// List existing keypairs
	url = walletserverURL + "/api/v1/keys"
	req, err = http.NewRequest(http.MethodGet, url, nil)
	req.Header.Set("Authorization", "Bearer "+token.Token)

	client = &http.Client{}
	resp, err = client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, err = ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}
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
	marketID := markets.Markets[0].Id

	// __get_accounts_by_market:
	// Request a list of accounts for a market on a Vega network
	accountsReq := api.MarketAccountsRequest{MarketId: marketID}
	acconutsResp, err := dataClient.MarketAccounts(context.Background(), &accountsReq)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Market accounts: %v\n", acconutsResp)
	// :get_accounts_by_market__

	// __get_accounts_by_party:
	// Request a list of accounts for a party (pubkey) on a Vega network
	partyReq := api.PartyAccountsRequest{PartyId: pubkey}
	partyResp, err := dataClient.PartyAccounts(context.Background(), &partyReq)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Party accounts: %v\n", partyResp)
	// :get_accounts_by_party__

	// __get_positions_by_party:
	// Request a list of positions for a party (pubkey) on a Vega network
	partyPosReq := api.PositionsByPartyRequest{PartyId: pubkey}
	partyPosResp, err := dataClient.PositionsByParty(context.Background(), &partyPosReq)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Party positions: %v\n", partyPosResp)
	// :get_positions_by_party__
}
