package main

import (
	"bytes"
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/big"
	"net/http"
	"os"
	"strings"
)

type Token struct {
	Token string `json:"token"`
}

type Keys struct {
	Keys []struct {
		Pub     string `json:"pub"`
		Algo    string `json:"algo"`
		Tainted bool   `json:"tainted"`
		Meta    []struct {
			Key   string `json:"key"`
			Value string `json:"value"`
		} `json:"meta"`
	} `json:"keys"`
}

func main() {

	walletName := randSeq(8)
	walletPassphrase := randSeq(12)

	walletServerURL := os.Getenv("WALLETSERVER_URL")
	if !CheckUrl(walletServerURL) {
		panic("Error: Invalid or missing WALLETSERVER_URL environment variable.")
	}

	// Help guide users against including api version suffix on url
	walletServerURL = CheckWalletUrl(walletServerURL)

	fmt.Printf("Creating a new wallet on %s:\n", walletServerURL)
	fmt.Printf("- name:       %s\n", walletName)
	fmt.Printf("- passphrase: %s\n", walletPassphrase)

	// Create a new wallet:
	jsonStr := []byte("{\"wallet\":\"" + walletName + "\",\"passphrase\":\"" + walletPassphrase + "\"}")
	req, err := http.NewRequest("POST", walletServerURL+"/api/v1/wallets", bytes.NewBuffer(jsonStr))

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))
	var token Token
	json.Unmarshal([]byte(body), &token)

	fmt.Println("Token : ", token.Token)

	// The example below uses the credentials we just created
	// and in practice you don't need to log in immediately after
	// creating a new wallet, as the response already contains the
	// token that you need to authenticate with future requests.

	// Log in to an existing wallet
	fmt.Printf("Log in to an existing wallet, wallet on %s:\n", walletServerURL)
	jsonStr = []byte("{\"wallet\":\"" + walletName + "\",\"passphrase\":\"" + walletPassphrase + "\"}")
	req, err = http.NewRequest("POST", walletServerURL+"/api/v1/auth/token", bytes.NewBuffer(jsonStr))

	client = &http.Client{}
	resp, err = client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, _ = ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))
	json.Unmarshal([]byte(body), &token)
	fmt.Println("Token : ", token.Token)

	// Generate a new key pair
	fmt.Printf("Generate key pair on an existing wallet, wallet on %s:\n", walletServerURL)
	jsonStr = []byte("{\"meta\":[{\"key\": \"alias\", \"value\": \"my_key_alias\"}],\"passphrase\":\"" + walletPassphrase + "\"}")
	req, err = http.NewRequest("POST", walletServerURL+"/api/v1/keys", bytes.NewBuffer(jsonStr))
	req.Header.Add("Authorization", "Bearer "+token.Token)

	client = &http.Client{}
	resp, err = client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, _ = ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))

	// Request all key pairs
	fmt.Printf("Request all key pairs from an existing wallet, wallet on %s:\n", walletServerURL)
	req, err = http.NewRequest("GET", walletServerURL+"/api/v1/keys", bytes.NewBuffer(jsonStr))
	req.Header.Add("Authorization", "Bearer "+token.Token)

	client = &http.Client{}
	resp, err = client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, _ = ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))

	var keys Keys
	json.Unmarshal([]byte(body), &keys)
	fmt.Printf("%+v\n", keys)

	pubkey := keys.Keys[0].Pub

	// Request a single key pair
	fmt.Printf("Get a single keypair, wallet on %s:\n", walletServerURL)
	req, err = http.NewRequest("GET", walletServerURL+"/api/v1/keys/"+pubkey, bytes.NewBuffer(jsonStr))
	req.Header.Add("Authorization", "Bearer "+token.Token)

	client = &http.Client{}
	resp, err = client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, _ = ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))

	// Sign a transaction - Note: setting "propagate" to True will also submit the
	// tx to Vega node
	fmt.Printf("Sign a transaction\n")
	data := "data returned from a Vega node 'Prepare<operation>' call"
	sEnc := base64.StdEncoding.EncodeToString([]byte(data))
	jsonStr = []byte("{\"tx\":\"" + string(sEnc) + "\",\"pubkey\":\"" + pubkey + "\", \"propagate\": false}")
	req, err = http.NewRequest("POST", walletServerURL+"/api/v1/messages", bytes.NewBuffer(jsonStr))
	req.Header.Add("Authorization", "Bearer "+token.Token)

	client = &http.Client{}
	resp, err = client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, _ = ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))

	// Log out of a wallet
	fmt.Printf("Log out of a wallet\n")
	req, err = http.NewRequest("DELETE", walletServerURL+"/api/v1/auth/token", nil)
	req.Header.Add("Authorization", "Bearer "+token.Token)

	client = &http.Client{}
	resp, err = client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, _ = ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))

}

var chars = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

func randSeq(n int) string {
	b := make([]rune, n)
	for i := range b {
		v, _ := rand.Int(rand.Reader, big.NewInt(int64(len(chars))))
		b[i] = chars[v.Int64()]
	}
	return string(b)
}

func CheckUrl(url string) bool {
	return url != "" && (strings.HasPrefix(url, "https://") || strings.HasPrefix(url, "http://"))
}

func CheckWalletUrl(url string) string {
	suffix := []string{"/api/v1/", "/api/v1", "/"}
	for _, s := range suffix {
		if strings.HasSuffix(url, s) {
			fmt.Println("There's no need to add ", s, " to WALLETSERVER_URL. Removing it.")
			return url[0 : len(url)-len(s)]
		}
	}
	return url
}
