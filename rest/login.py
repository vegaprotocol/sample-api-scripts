
import json
import requests

url = "http://localhost:1789/api/v2/requests"
connect_payload = "{\n        \"id\": \"1\",\n        \"jsonrpc\": \"2.0\",\n        \"method\": \"client.connect_wallet\"\n    }"
connect_headers = {
  'Content-Type': 'application/json-rpc',
  'Accept': 'application/json-rpc', 
  'Origin': 'application/json-rpc'
}
connectionResponse = requests.request("POST", url, headers=connect_headers, data=connect_payload)

authorize_payload = "{\n        \"id\": \"1\",\n        \"jsonrpc\": \"2.0\",\n        \"method\": \"client.list_keys\"\n    }"
authorize_headers = {
  'Content-Type': 'application/json-rpc',
  'Accept': 'application/json-rpc',
  'Origin': 'application/json-rpc',
  "Authorization": connectionResponse.headers["Authorization"]
}

authorizationResponse = requests.request("POST", url, headers=authorize_headers, data=authorize_payload)

token = connectionResponse.headers["Authorization"]
authConent = json.loads(authorizationResponse.content)
pubkey = authConent['result']['keys'][0]['publicKey']
