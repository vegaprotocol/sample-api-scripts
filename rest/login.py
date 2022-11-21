import requests
import os.path
import json
import sys
import helpers

ci_args = "--ci"
wallet_server_url = helpers.get_from_env("WALLET_SERVER_URL")


def load_token():
    if ci_args in sys.argv:
        return perform_login()
        # login will call exit with appropriate code
    if not os.path.isfile("token.temp"):
        print('Error: No token file found: try running "python3 login.py"')
        exit(1)
    with open("token.temp", "r") as token_file:
        return json.load(token_file)["token"]


def get_pubkey(token):
    auth_headers = {"Authorization": "Bearer " + token}
    response = requests.get(wallet_server_url + "/api/v1/keys",
                            headers=auth_headers)
    if response.status_code != 200:
        print("Error listing keys: " + response.text)
        exit(1)
    keys = response.json()["keys"]
    if len(keys) < 1:
        print("Error: No keys found, use Vega Console" +
              " or Vega Wallet CLI to create one")
        exit(1)
    return keys[0]["pub"], auth_headers


def perform_login():
    import getpass
    print(f"Using API: {wallet_server_url}")
    wallet_name = os.getenv("WALLET_NAME")
    wallet_passphrase = os.getenv("WALLET_PASSPHRASE")
    valid_user = helpers.check_var(wallet_name)
    valid_pass = helpers.check_var(wallet_passphrase)
    if ci_args in sys.argv and not valid_user:
        print("Error: Missing environment variable WALLET_NAME")
        exit(1)
    if ci_args in sys.argv and not valid_pass:
        print("Error: Missing environment variable WALLET_PASSPHRASE")
        exit(1)
    if not valid_user or not valid_pass:
        wallet_name = input("Enter Vega wallet username: ")
        wallet_passphrase = getpass.getpass("Vega wallet passphrase: ")
    req = {"wallet": wallet_name, "passphrase": wallet_passphrase}
    response = requests.post(wallet_server_url
                             + "/api/v1/auth/token", json=req)
    if response.status_code != 200:
        print("Error logging in: " + response.text)
        exit(1)
    if ci_args not in sys.argv:
        with open("token.temp", "w") as token_file:
            json.dump(response.json(), token_file)
        print('Token saved to "token.temp", done.')
    return response.json()["token"]


if __name__ == "__main__":
    perform_login()
    exit(0)


token = load_token()
pubkey, auth_headers = get_pubkey(token)
