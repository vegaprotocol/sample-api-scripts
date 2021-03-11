package main

import (
	"bytes"
	"crypto/rand"
	"fmt"
	"io/ioutil"
	"math/big"
	"net/http"
	"strings"
)

type WalletConfig struct {
	URL        string `json:"URL"`
	Passphrase string `json:"passphrase"`
	Name       string `json:"Name"`
}

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

func CreateWallet(config WalletConfig) ([]byte, error) {
	// Create a new wallet:
	jsonStr := []byte("{\"wallet\":\"" + config.Name + "\",\"passphrase\":\"" + config.Passphrase + "\"}")
	req, err := http.NewRequest("POST", config.URL+"/api/v1/wallets", bytes.NewBuffer(jsonStr))

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))

	return body, nil
}

func LoginWallet(config WalletConfig) ([]byte, error) {
	jsonStr := []byte("{\"wallet\":\"" + config.Name + "\",\"passphrase\":\"" + config.Passphrase + "\"}")
	req, err := http.NewRequest("POST", config.URL+"/api/v1/auth/token", bytes.NewBuffer(jsonStr))

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))

	return body, nil
}

func GenerateKeyPairs(config WalletConfig, token string) ([]byte, error) {
	jsonStr := []byte("{\"meta\":[{\"key\": \"alias\", \"value\": \"my_key_alias\"}],\"passphrase\":\"" + config.Passphrase + "\"}")
	req, err := http.NewRequest("POST", config.URL+"/api/v1/keys", bytes.NewBuffer(jsonStr))
	req.Header.Add("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))
	return body, nil
}

func GetKeyPairs(config WalletConfig, token string) ([]byte, error) {
	req, err := http.NewRequest("GET", config.URL+"/api/v1/keys", bytes.NewBuffer(nil))
	req.Header.Add("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))

	return body, nil
}

func GetKeyPair(config WalletConfig, token string, pubkey string) ([]byte, error) {
	req, err := http.NewRequest("GET", config.URL+"/api/v1/keys/"+pubkey, bytes.NewBuffer(nil))
	req.Header.Add("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))

	return body, nil
}

func SignTransaction(config WalletConfig, token string, pubkey string, message string) ([]byte, error) {
	jsonStr := []byte("{\"tx\":\"" + message + "\",\"pubkey\":\"" + pubkey + "\", \"propagate\": false}")
	req, err := http.NewRequest("POST", config.URL+"/api/v1/messages", bytes.NewBuffer(jsonStr))
	req.Header.Add("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Println("response Body:", string(body))
	return body, nil
}

func LogoutWallet(config WalletConfig, token string) ([]byte, error) {
	req, err := http.NewRequest("DELETE", config.URL+"/api/v1/auth/token", nil)
	req.Header.Add("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)

	return body, nil
}
