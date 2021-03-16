package main

import (
	"bytes"
	"crypto/rand"
	"fmt"
	"io/ioutil"
	"math/big"
	"net/http"
	"strings"
	"code.vegaprotocol.io/go-wallet/wallet"
	"encoding/json"
)

type WalletConfig struct {
	URL        string `json:"URL"`
	Passphrase string `json:"passphrase"`
	Name       string `json:"Name"`
}

var chars = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

func randSeq(n int) (string, error) {
	b := make([]rune, n)
	for i := range b {
		v, err := rand.Int(rand.Reader, big.NewInt(int64(len(chars))))
		if err != nil {
			return "", err
		}
		b[i] = chars[v.Int64()]
	}
	return string(b), nil
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
	// __create_wallet:
	// Create a new wallet:
	creationReq :=  &wallet.CreateLoginWalletRequest{Wallet: config.Name, Passphrase: config.Passphrase}
	payload, err := json.Marshal(creationReq)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequest(http.MethodPost, config.URL+"/api/v1/wallets", bytes.NewBuffer(payload))

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	fmt.Println("response Body:", string(body))
	// :create_wallet__

	return body, nil
}

func LoginWallet(config WalletConfig) ([]byte, error) {
	// __login_wallet:
	// Log in to an existing wallet
	creationReq :=  &wallet.CreateLoginWalletRequest{Wallet: config.Name, Passphrase: config.Passphrase}
	payload, err := json.Marshal(creationReq)
	if err != nil {
		return nil, err
	}
	req, err := http.NewRequest(http.MethodPost, config.URL+"/api/v1/auth/token", bytes.NewBuffer(payload))

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	fmt.Println("response Body:", string(body))
	// :login_wallet__

	return body, nil
}

func GenerateKeyPairs(config WalletConfig, token string) ([]byte, error) {
	// __generate_keypair:
	// Generate a new key pair
	meta := &wallet.Meta{Key: "alias", Value: "my_key_alias"}
	metaArray := []wallet.Meta{*meta}
	creationReq :=  &wallet.PassphraseMetaRequest{Meta: metaArray, Passphrase: config.Passphrase}
	payload, err := json.Marshal(creationReq)
	if err != nil {
		return nil, err
	}
	req, err := http.NewRequest(http.MethodPost, config.URL+"/api/v1/keys", bytes.NewBuffer(payload))
	req.Header.Add("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	fmt.Println("response Body:", string(body))

	// :generate_keypair__
	return body, nil
}

func GetKeyPairs(config WalletConfig, token string) ([]byte, error) {
	// __get_keys:
	// Request all key pairs
	req, err := http.NewRequest(http.MethodGet, config.URL+"/api/v1/keys", bytes.NewBuffer(nil))
	req.Header.Add("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	fmt.Println("response Body:", string(body))
	// :get_keys__

	return body, nil
}

func GetKeyPair(config WalletConfig, token string, pubkey string) ([]byte, error) {
	// __get_key:
	// Request a single key pair
	req, err := http.NewRequest(http.MethodGet, config.URL+"/api/v1/keys/"+pubkey, bytes.NewBuffer(nil))
	req.Header.Add("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	fmt.Println("response Body:", string(body))
	// :get_key__

	return body, nil
}

func SignTransaction(config WalletConfig, token string, pubkey string, message string) ([]byte, error) {
	// __sign_tx:
	// Sign a transaction - Note: setting "propagate" to True will also submit the
	// tx to Vega node
	txSignRequest := &wallet.SignTxRequest{Tx: message, PubKey: pubkey, Propagate: false}
	payload, err := json.Marshal(txSignRequest)
	if err != nil {
		return nil, err
	}
	req, err := http.NewRequest(http.MethodPost, config.URL+"/api/v1/messages", bytes.NewBuffer(payload))
	req.Header.Add("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	fmt.Println("response Body:", string(body))
	// :sign_tx__

	return body, nil
}

func LogoutWallet(config WalletConfig, token string) ([]byte, error) {
	// __logout_wallet:
	// Log out of a wallet
	req, err := http.NewRequest(http.MethodDelete, config.URL+"/api/v1/auth/token", nil)
	req.Header.Add("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	//:logout_wallet__

	return body, nil
}
