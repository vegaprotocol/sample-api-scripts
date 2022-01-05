#!/usr/bin/python3

"""
Script language: Python3

Talks to:
- Vega node (REST, GraphQL)

Apps/Libraries:
- REST: requests (https://pypi.org/project/requests/)
- GraphQL: websocket-client (https://pypi.org/project/websocket_client/)
"""

import json
import os
import requests
import websocket

import helpers


def on_message(ws, message: str):
    print(message.strip())


def on_error(ws, error):
    print(str(error).strip())


def on_close(ws, close_status_code, close_msg):
    print(f"### closed {close_status_code}: {close_msg} ###")


def generate_on_open_function(marketID: str):
    # Generate an on_open function which knows marketID
    def on_open(ws):
        msg = json.dumps({"type": "connection_init", "payload": {}})
        ws.send(msg)
        query = """subscription marketDataSub($marketId: String!)
        {
            marketData(marketId: $marketId) {
                bestBidPrice
            }
        }"""
        msg = json.dumps(
            {
                "id": "1",
                "type": "start",
                "payload": {
                    "variables": {"marketId": marketID},
                    "extensions": {},
                    "operationName": "marketDataSub",
                    "query": query,
                },
            }
        )
        ws.send(msg)

    return on_open


node_url_rest = os.getenv("NODE_URL_REST")
if not helpers.check_url(node_url_rest):
    print("Error: Invalid NODE_URL_REST.")
    exit(1)

# Get a Market ID
response = requests.get(f"{node_url_rest}/markets")
helpers.check_response(response)
marketID = response.json()["markets"][0]["id"]
print(f"Got a market ID: {marketID}")

# Optional: enable websocket trace debugging
# websocket.enableTrace(True)

# Create and run a websocket client
node_url_wss = "{}/query".format(node_url_rest.replace("https://", "wss://"))
ws = websocket.WebSocketApp(
    node_url_wss,
    on_close=on_close,
    on_error=on_error,
    on_open=generate_on_open_function(marketID),
    on_message=on_message,
)
ws.run_forever()
