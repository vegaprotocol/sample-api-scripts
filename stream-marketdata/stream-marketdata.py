#!/usr/bin/python3

# This example script is adapted from:
# https://github.com/websocket-client/websocket-client#long-lived-connection
# in accordance with the licence:
# https://github.com/websocket-client/websocket-client/blob/master/LICENSE
# Copyright 2018 Hiroki Ohtani.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

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
    # Get a Market ID
    url = "{base}/markets".format(base=NODE_URL)
    response = requests.get(url)
    check(response)
    marketID = response.json()["markets"][0]["id"]
    print(f"Got a market ID: {marketID}")

    # Optional: enable websocket trace debugging
    # websocket.enableTrace(True)

    # Create and run a websocket client
    wssURL = "{}/query".format(NODE_URL.replace("https://", "wss://"))
    ws = websocket.WebSocketApp(
        wssURL,
        on_close=on_close,
        on_error=on_error,
        on_open=generate_on_open_function(marketID),
        on_message=on_message,
    )
    ws.run_forever()
