import json
import requests
from login import token

url = "http://localhost:1789/api/v2/requests"
connect_payload = "{\n        \"id\": \"1\",\n        \"jsonrpc\": \"2.0\",\n        \"method\": \"client.disconnect_wallet\"\n    }"
connect_headers = {
  'Content-Type': 'application/json-rpc',
  'Accept': 'application/json-rpc', 
  'Origin': 'application/json-rpc', 
  'Authorization': token
}
connectionResponse = requests.request("POST", url, headers=connect_headers, data=connect_payload)
print(connectionResponse.text)