#!/usr/bin/python3

###############################################################################
#                   S T R E A M   M A R G I N   L E V E L S                   #
###############################################################################

#  How to stream margin levels information from a Data Node using Websockets:
#  ----------------------------------------------------------------------
#  Pagination and Date Range are not supported, this is a realtime stream.
#  ----------------------------------------------------------------------
#  The stream has two required parameters, as follows:
#   partyId:    Vega party id (public key)
#   marketId:   Vega market id
#     > Both are required to stream margin level data
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import websocket
import threading
import json
import helpers

# Vega wallet interaction helper, see login.py for detail
from login import pubkey

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

# Load Vega market id
market_id = helpers.env_market_id()
assert market_id != ""

# Connect to the data node with a WSS based endpoint, this is not a HTTPS:// url
#  e.g. ?marketId=xxx&partyId=yyy
url = f"{data_node_url_rest}/stream/margin/levels?partyId={pubkey}&marketId={market_id}"\
    .replace("https://", "wss://")
res = []
event = threading.Event()

# __stream_margin_levels:
# Request a stream of margin level updates for a party and market id on a Vega network

def on_message(wsa, line):
    # Vega data-node v2 returns the json line by line so we need to wait
    # for a full structure before we can parse to valid JSON in python
    if line == "{":
        del res[:]
        res.append(line)
    elif line == "}":
        res.append(line)
        obj = json.loads(''.join(res))
        if "marginLevels" in obj["result"]:
            # Result contains margin level update for party on a market
            print(f"Margin level data found:")
            print(obj["result"]["marginLevels"])
    else:
        res.append(line)


def on_error(wsa, error):
    print(error)


def on_close(wsa, close_status_code, close_msg):
    print(f"Margin levels stream closed: {url}")


def on_open(wsa):
    print(f"Margin levels stream open: {url}")


def timeout():
    while not event.wait(timeout=30):
        ws.close()
        exit(1)


thread = threading.Thread(target=timeout)
thread.start()

ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_close=on_close)
ws.on_open = on_open
ws.run_forever()
# :stream_margin_levels__
