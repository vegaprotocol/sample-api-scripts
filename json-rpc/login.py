

import requests
import walletClient

def get_chain_id():
   {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "client.get_chain_id",
    "params": []
}

def connect_wallet():
{
    "id": 1,
    "jsonrpc": "2.0",
    "method": "client.connect_wallet",
    "params": {
        "hostname": "vega.xyz"
    }
}

def verify_permissions():
    print(" client.get_permissions")


# 1. Get a live session token.
# Jump direction to step 2 if you are using a long-living token.
connectionRequest = {
    "method": "POST",
    "path": "/api/v2/requests",
    "body": {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "client.connect_wallet"
    }
}

connectionResponse = walletClient.send(connectionRequest)

# 2. Set the connection token in the `Authorization` header.
listKeysRequest = {
    "method": "POST",
    "path": "/api/v2/requests",
    "body": {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "client.list_keys"
    },
    "headers": {
        "Authorization": connectionResponse.Header("Authorization")
    }
}

listKeysResponse = walletClient.send(listKeysRequest)




url = "http://localhost:1789/api/v2/requests"

payload = ""
headers = {
  'Content-Type': 'application/json-rpc',
  'Accept': 'application/json-rpc'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

