package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

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

type PendingProposal struct {
	Blob            string `json:"blob"`
	PendingProposal struct {
		ID        string `json:"id"`
		Reference string `json:"reference"`
		PartyID   string `json:"partyId"`
		State     string `json:"state"`
		Timestamp string `json:"timestamp"`
		Terms     struct {
			ClosingTimestamp    string `json:"closingTimestamp"`
			EnactmentTimestamp  string `json:"enactmentTimestamp"`
			ValidationTimestamp string `json:"validationTimestamp"`
			NewMarket           struct {
				Changes struct {
					Instrument struct {
						Name   string `json:"name"`
						Code   string `json:"code"`
						Future struct {
							Maturity        time.Time `json:"maturity"`
							SettlementAsset string    `json:"settlementAsset"`
							QuoteName       string    `json:"quoteName"`
						} `json:"future"`
					} `json:"instrument"`
					DecimalPlaces             string        `json:"decimalPlaces"`
					Metadata                  []interface{} `json:"metadata"`
					PriceMonitoringParameters struct {
						Triggers []struct {
							Horizon          string  `json:"horizon"`
							Probability      float64 `json:"probability"`
							AuctionExtension string  `json:"auctionExtension"`
						} `json:"triggers"`
					} `json:"priceMonitoringParameters"`
					LogNormal struct {
						RiskAversionParameter float64 `json:"riskAversionParameter"`
						Tau                   float64 `json:"tau"`
						Params                struct {
							Mu    int     `json:"mu"`
							R     float64 `json:"r"`
							Sigma float64 `json:"sigma"`
						} `json:"params"`
					} `json:"logNormal"`
					Continuous struct {
						TickSize string `json:"tickSize"`
					} `json:"continuous"`
				} `json:"changes"`
				LiquidityCommitment interface{} `json:"liquidityCommitment"`
			} `json:"newMarket"`
		} `json:"terms"`
		Reason string `json:"reason"`
	} `json:"pendingProposal"`
}

type VoteResponse struct {
	Blob string `json:"blob"`
	Vote struct {
		PartyID    string `json:"partyId"`
		Value      string `json:"value"`
		ProposalID string `json:"proposalId"`
		Timestamp  string `json:"timestamp"`
	} `json:"vote"`
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
	nodeURLRest := "https://lb.testnet.vega.xyz"

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

	// Find Assets
	// Request a list of assets available on a Vega network
	request := api.AssetsRequest{}
	assets, err := dataClient.Assets(context.Background(), &request)
	if err != nil {
		panic(err)
	}

	// Find asset with name DAI
	assetFound := false
	var assetID string
	assetID = ""
	for _, asset := range assets.Assets {
		fmt.Printf("Assets: %s \n", asset.Name)
		fmt.Printf("Assets: %s \n", asset.Symbol)
		if asset.Symbol == "tDAI" {
			fmt.Println("Found an asset with name tDAI:")
			assetFound = true
		}
		if asset.Symbol == "tVOTE" {
			fmt.Println("Found an asset with name tDAI:")
			assetID = asset.Id
		}
	}

	if !assetFound {
		panic("tDAI asset not found on specified Vega network, please propose and create the tDAI asset")
	}

	// Governance token check
	partyReq := api.PartyAccountsRequest{PartyId: pubkey}
	partyResp, _ := dataClient.PartyAccounts(context.Background(), &partyReq)
	fmt.Printf("Party accounts: %v\n", partyResp)

	var votingBalance uint64
	votingBalance = 0

	fmt.Printf("Looking for assetID %s\n", assetID)
	for _, account := range partyResp.Accounts {
		if account.Asset == assetID {
			fmt.Println("Found governance asset account")
			votingBalance = account.Balance
			break
		}
	}

	if votingBalance == 0 {
		panic("Please deposit tVOTE asset to public key " + pubkey + " and try again")
	}

	// Get Blockchain time
	timeRequest := api.GetVegaTimeRequest{}
	vegaTime, err := dataClient.GetVegaTime(context.Background(), &timeRequest)

	blockchainTime := vegaTime.Timestamp
	blockchainTimeSeconds := vegaTime.Timestamp / 1e9
	fmt.Printf("Blockchain time: %d  (%d seconds past epoch)\n", blockchainTime, blockchainTimeSeconds)

	// Propose Market
	// STEP 1 - Propose a BTC/DAI futures market
	//Further documentation on creating markets: https://docs.testnet.vega.xyz/docs/api-howtos/create-market/

	// Prepare a market proposal for a new market
	validationTimestamp := blockchainTimeSeconds + 1
	closingTimestamp := blockchainTimeSeconds + 3601
	enactmentTimestamp := blockchainTimeSeconds + 3701
	market := `{
		"partyId": "` + pubkey + `",
		"proposal": {
			"validationTimestamp": ` + strconv.FormatInt(validationTimestamp, 10) + `,
			"closingTimestamp": ` + strconv.FormatInt(closingTimestamp, 10) + `,
			"enactmentTimestamp": ` + strconv.FormatInt(enactmentTimestamp, 10) + `,
			"newMarket": {
				"changes": {
					"continuous": {"tickSize": "0.01"},
					"decimalPlaces": "5",
					"instrument": {
						"code": "CRYPTO:BTCDAI/JUL21",
						"future": {
							"settlementAsset": "` + assetID + `",
							"quoteName": "DAI",
							"maturity": "2021-06-30T23:59:59Z"
						},
						"name": "BTCDAI/JUL21"
					},
					"logNormal": {
						"params": {"mu": 0, "r": 0.016, "sigma": 0.05},
						"riskAversionParameter": 0.01,
						"tau": 1.90128526884173e-06
					},
					"metadata": [],
					"priceMonitoringParameters": {
					   "triggers": [{
						 "auctionExtension": "300",
						 "horizon": "43200",
						 "probability": 0.9999999
					   }],
					   "updateFrequency": "120"
					}
				}
			}
		}
	}`

	marketBytes := []byte(market)
	proposalURL := nodeURLRest + "/governance/prepare/proposal"
	reqProposal, err := http.NewRequest("POST", proposalURL, bytes.NewBuffer(marketBytes))

	clientProposal := &http.Client{}
	resp, err = clientProposal.Do(reqProposal)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	fmt.Println(proposalURL, " returns response Status:", resp.Status)
	fmt.Println("response Headers:", resp.Header)

	respBody, _ := ioutil.ReadAll(resp.Body)

	var pendingProposal PendingProposal
	json.Unmarshal([]byte(respBody), &pendingProposal)

	// Sign the prepared proposal transaction
	// Note: Setting propagate to true will also submit to a Vega node
	proposalRef := pendingProposal.PendingProposal.Reference
	jsonStr = []byte("{\"tx\":\"" + pendingProposal.Blob + "\",\"pubkey\":\"" + pubkey + "\", \"propagate\": true}")

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

	fmt.Printf("Signed proposal and sent to Vega\n")

	// Wait for proposal to be included in a block and to be accepted by Vega network
	fmt.Printf("Waiting for blockchain...")
	proposalID := ""
	done := false

	proposalReq := api.GetProposalByReferenceRequest{Reference: proposalRef}

	for {
		if done {
			break
		}
		time.Sleep(1 * time.Second)
		fmt.Printf(".")
		proposalResp, _ := dataClient.GetProposalByReference(context.Background(), &proposalReq)

		if proposalResp != nil {
			if proposalResp.Data.Proposal.Reference == proposalRef {
				proposalID = proposalResp.Data.Proposal.Id
				fmt.Println("Your proposal has been accepted by the network")
				done = true
				break
			}
		}
	}

	// STEP 2 - Let's vote on the market proposal

	// IMPORTANT: When voting for a proposal on the Vega Testnet, typically a single
	// YES vote from the proposer will not be enough to vote the market into existence.
	// This is because of the network minimum threshold for voting on proposals, this
	// threshold for market proposals this is currently a 66% majority vote either YES or NO.
	// A proposer should enlist the help/YES votes from other community members, ideally on the
	// Community forums (https://community.vega.xyz/c/testnet) or Discord (https://vega.xyz/discord)

	// Further documentation on proposal voting and review here: https://docs.testnet.vega.xyz/docs/api-howtos/proposals/
	vote := `{
		"vote": {
			"partyId": "` + pubkey + `",
			"value": "VALUE_NO",          
			"proposalId": "` + proposalID + `"
		}
	}`

	fmt.Println(vote)

	voteBytes := []byte(vote)
	voteURL := nodeURLRest + "/governance/prepare/vote"
	reqVote, err := http.NewRequest("POST", voteURL, bytes.NewBuffer(voteBytes))

	clientVote := &http.Client{}
	resp, err = clientVote.Do(reqVote)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	fmt.Println(voteURL, " returns response Status:", resp.Status)
	respBody, _ = ioutil.ReadAll(resp.Body)

	// Sign the prepared vote transaction
	// Note: Setting propagate to true will also submit to a Vega node
	var voteResponse VoteResponse
	json.Unmarshal([]byte(respBody), &voteResponse)

	// Sign the prepared proposal transaction
	// Note: Setting propagate to true will also submit to a Vega node
	jsonStr = []byte("{\"tx\":\"" + voteResponse.Blob + "\",\"pubkey\":\"" + pubkey + "\", \"propagate\": true}")

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

	fmt.Println("Signed vote on proposal and sent to Vega")

	fmt.Printf("Waiting for vote on proposal to succeed or fail...")
	done = false

	proposalByIDReq := api.GetProposalByIDRequest{ProposalId: proposalID}

	for {
		if done {
			break
		}
		time.Sleep(1 * time.Second)
		proposalByIDResp, _ := dataClient.GetProposalByID(context.Background(), &proposalByIDReq)

		if proposalByIDResp != nil {
			if proposalByIDResp.Data.Proposal.Reference == proposalRef {
				if proposalByIDResp.Data.Proposal.State == proto.Proposal_STATE_OPEN {
					continue
				}
				if proposalByIDResp.Data.Proposal.State == proto.Proposal_STATE_ENACTED {
					done = true
					break
				}
				if proposalByIDResp.Data.Proposal.State != proto.Proposal_STATE_PASSED {
					fmt.Println("proposal vote has succeeded, waiting for enactment")
					continue
				}

				fmt.Printf("%v", proposalByIDResp.Data.Proposal)
				return
			}
		}
	}

	// STEP 3 - Wait for market to be enacted

	// IMPORTANT: When voting for a proposal on the Vega Testnet, typically a single
	// YES vote from the proposer will not be enough to vote the market into existence.
	// As described above in STEP 2, a market will need community voting support to be
	// passed and then enacted.
	fmt.Println("Waiting for proposal to be enacted or failed...")
	done = false

	marketRequest := api.MarketsRequest{}
	for {
		if done {
			break
		}

		time.Sleep(1 * time.Second)

		markets, err := dataClient.Markets(context.Background(), &marketRequest)
		if err != nil {
			panic(err)
		}

		for _, market := range markets.Markets {
			if market.Id == proposalID {
				fmt.Printf("%v\n", market)
				done = true
				break
			}
		}

	}
}
