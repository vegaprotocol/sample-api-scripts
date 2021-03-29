package main

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"os"
	"code.vegaprotocol.io/go-wallet/wallet"
)

func main() {

	walletName, err := randSeq(8)
	if err != nil {
		panic(err)
	}
	walletPassphrase, err := randSeq(12)
	if err != nil {
		panic(err)
	}

	walletServerURL := os.Getenv("WALLETSERVER_URL")
	if !CheckUrl(walletServerURL) {
		panic("Error: Invalid or missing WALLETSERVER_URL environment variable.")
	}

	// Help guide users against including api version suffix on url
	walletServerURL = CheckWalletUrl(walletServerURL)

	fmt.Printf("Creating a new wallet on %s:\n", walletServerURL)
	fmt.Printf("- name:       %s\n", walletName)
	fmt.Printf("- passphrase: %s\n", walletPassphrase)

	walletConfig := WalletConfig{
		URL:        walletServerURL,
		Name:       walletName,
		Passphrase: walletPassphrase,
	}
	reps, err := CreateWallet(walletConfig)
	if err != nil {
		panic(err)
	}
 
	var token wallet.TokenResponse
	json.Unmarshal([]byte(reps), &token)
	fmt.Println("Token : ", token.Token)

	// The example below uses the credentials we just created
	// and in practice you don't need to log in immediately after
	// creating a new wallet, as the response already contains the
	// token that you need to authenticate with future requests.

	// Log in to an existing wallet
	fmt.Printf("Log in to an existing wallet, wallet on %s:\n", walletConfig.URL)
	loginResp, err := LoginWallet(walletConfig)
	if err != nil {
		panic(err)
	}

	json.Unmarshal([]byte(loginResp), &token)
	fmt.Println("Token : ", token.Token)

	// Generate a new key pair
	fmt.Printf("Generate key pair on an existing wallet, wallet on %s:\n", walletConfig.URL)
	key, err := GenerateKeyPairs(walletConfig, token.Token)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Key pair creation: %v\n", key)

	// Request all key pairs
	fmt.Printf("Request all key pairs from an existing wallet, wallet on %s:\n", walletConfig.URL)

	keysBody, err := GetKeyPairs(walletConfig, token.Token)
	if err != nil {
		panic(err)
	}

	var keys wallet.KeysResponse
	json.Unmarshal([]byte(keysBody), &keys)
	fmt.Printf("%+v\n", keys)

	pubkey := keys.Keys[0].Pub
	// Request a single key pair
	fmt.Printf("Get a single keypair, wallet on %s:\n", walletConfig.URL)

	keyBody, err := GetKeyPair(walletConfig, token.Token, pubkey)
	if err != nil {
		panic(err)
	}

	fmt.Printf("%v\n", keyBody)

	// Sign a transaction - Note: setting "propagate" to True will also submit the
	// tx to Vega node
	fmt.Printf("Sign a transaction\n")
	data := "data returned from a Vega node 'Prepare<operation>' call"
	sEnc := base64.StdEncoding.EncodeToString([]byte(data))
	sign, err := SignTransaction(walletConfig, token.Token, pubkey, string(sEnc))
	if err != nil {
		panic(err)
	}

	fmt.Printf("%v\n", sign)

	// Log out of a wallet
	fmt.Printf("Log out of a wallet\n")
	_, err = LogoutWallet(walletConfig, token.Token)

}
