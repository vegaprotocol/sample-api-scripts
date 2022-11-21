#!/usr/bin/python3

###############################################################################
#                          S T R E A M   T R A D E S                          #
###############################################################################

#  How to stream trade information from a Data Node using Websockets:
#  ----------------------------------------------------------------------
#  Pagination is not supported, but the initial snapshot may contain
#  multiple pages. Date Range is not supported, this is a realtime stream.
#  ----------------------------------------------------------------------
#  The list can be filtered by various parameters, including:
#   partyId:    Vega party id (public key)
#   marketId:   Vega market id
#     > Include none, one or both to refine the stream of data from Vega
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import websocket
import threading
import json
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

# Load Vega market id
market_id = helpers.env_market_id()
assert market_id != ""

# Connect to the data node with a WSS based endpoint, this is not a HTTPS:// url
#  Hint: to include/filter data from a party add the param `partyId`
#  e.g. ?marketIds=xxx&partyId=yyy
url = f"{data_node_url_rest}/stream/trades?market_id={market_id}".replace("https://", "wss://")
res = []
event = threading.Event()

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

# __stream_trades_by_market:
# Request a stream of live trades and updates for a market id on a Vega network

def on_message(wsa, line):
    # Vega data-node v2 returns the json line by line so we need to wait
    # for a full structure before we can parse to valid JSON in python
    if line == "{":
        del res[:]
        res.append(line)
    elif line == "}":
        res.append(line)
        obj = json.loads(''.join(res))
        if "trades" in obj["result"]:
            # Result contains each trade update (may be multiple)
            total_in_update = len(obj["result"]["trades"])
            print(f"Trade data found [{total_in_update}]:")
            print(obj["result"]["trades"])
    else:
        res.append(line)


def on_error(wsa, error):
    print(error)


def on_close(wsa, close_status_code, close_msg):
    print(f"Trades stream closed: {url}")


def on_open(wsa):
    print(f"Trades stream open: {url}")


def timeout():
    while not event.wait(timeout=30):
        ws.close()
        exit(1)


thread = threading.Thread(target=timeout)
thread.start()

ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_close=on_close)
ws.on_open = on_open
ws.run_forever()
# :stream_trades_by_market__
