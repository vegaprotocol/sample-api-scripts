package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strings"

	"code.vegaprotocol.io/vega/proto"
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

	// List open proposals
	orderSubmission := api.OptionalProposalState{
		Value: proto.Proposal_STATE_FAILED,
	}

	proposalsRequest := api.GetProposalsRequest{SelectInState: &orderSubmission}
	proposalsRequest = api.GetProposalsRequest{}
	proposalResponse, err := dataClient.GetProposals(context.Background(), &proposalsRequest)
	fmt.Printf("Proposals: %+v\n", proposalResponse)

	if len(proposalResponse.Data) == 0 {
		fmt.Println("No open proposal, exit!")
		return
	}

	proposalID := proposalResponse.Data[0].Proposal.Id

	// Get proposal by ID
	proposalByIDRequest := api.GetProposalByIDRequest{ProposalId: proposalID}
	proposalByIDResponse, err := dataClient.GetProposalByID(context.Background(), &proposalByIDRequest)

	fmt.Printf("ProposalById: %+v\n", proposalByIDResponse)

	// Party proposals
	proposalsByPartyIDRequest := api.GetProposalsByPartyRequest{PartyId: pubkey}
	proposalsByPartyIDResponse, err := dataClient.GetProposalsByParty(context.Background(), &proposalsByPartyIDRequest)

	fmt.Printf("ProposalByPartyId: %+v\n", proposalsByPartyIDResponse)

}
