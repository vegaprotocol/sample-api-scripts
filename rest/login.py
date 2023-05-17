import json
import requests

url = "http://localhost:1789/api/v2/requests"
connect_payload = {
    "id": "1",
    "jsonrpc": "2.0",
    "method": "client.connect_wallet"
}
connect_headers = {
    'Content-Type': 'application/json-rpc',
    'Accept': 'application/json-rpc',
    'Origin': 'application/json-rpc'
}

try:
    connectionResponse = requests.post(url, headers=connect_headers, json=connect_payload)
    connectionResponse.raise_for_status()  # Raise an exception for unsuccessful responses
except requests.exceptions.RequestException as e:
    print("Error connecting to the API - Make sure you have a wallet connection open and have imported the right vega-config:", str(e))
    exit(1)

authorize_payload = {
    "id": "1",
    "jsonrpc": "2.0",
    "method": "client.list_keys"
}
authorize_headers = {
    'Content-Type': 'application/json-rpc',
    'Accept': 'application/json-rpc',
    'Origin': 'application/json-rpc',
    "Authorization": connectionResponse.headers["Authorization"]
}

try:
    authorizationResponse = requests.post(url, headers=authorize_headers, json=authorize_payload)
    authorizationResponse.raise_for_status()
except requests.exceptions.RequestException as e:
    print("Error authorizing request:", str(e))
    exit(1)

try:
    token = connectionResponse.headers["Authorization"]
    authContent = json.loads(authorizationResponse.content)
    pubkey = authContent['result']['keys'][0]['publicKey']
except (KeyError, IndexError, json.JSONDecodeError) as e:
    print("Error parsing authorization response:", str(e))
    exit(1)

# Rest of your code...
