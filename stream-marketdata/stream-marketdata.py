import json
import requests
import websocket

from credentials import NODE_URL
assert NODE_URL.startswith("https://")


def check(r: requests.Response):
    assert r.status_code == 200, "HTTP {} {}".format(r.status_code, r.text)


def on_message(ws, message):
    print(message.strip())


def on_error(ws, error):
    print(str(error).strip())


def on_close(ws):
    print("### closed ###")


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


if __name__ == "__main__":
    ### Get a Market ID ###
    url = "{base}/markets".format(base=NODE_URL)
    response = requests.get(url)
    check(response)
    marketID = response.json()["markets"][0]["id"]
    print(f"Got a market ID: {marketID}")

    # Optional: enable websocket trace debugging
    # websocket.enableTrace(True)

    ### Create and run a websocket client
    wssURL = "{}/query".format(NODE_URL.replace("https://", "wss://"))
    ws = websocket.WebSocketApp(
        wssURL,
        on_close=on_close,
        on_error=on_error,
        on_open=generate_on_open_function(marketID),
        on_message=on_message,
    )
    ws.run_forever()
