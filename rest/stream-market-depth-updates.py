#!/usr/bin/python3

###############################################################################
#            S T R E A M   M A R K E T   D E P T H   U P D A T E S            #
###############################################################################

#  IMPORTANT: This streaming endpoint returns only the changes to market depth
#  /order book on each update, if you're looking for a stream of the full order
#  book, see the script `stream-market-depth.py`

#  How to stream market depth information from a Data Node using Websockets:
#  ----------------------------------------------------------------------
#  Pagination and Date Range are not supported, this is a realtime stream.
#  ----------------------------------------------------------------------
#  The stream requires the following parameter/filter:
#   marketIds:   Vega market id (a repeated param) for one or more markets
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
#  Hint: to include data from multiple markets repeat the param `marketIds`
#  e.g. marketIds=xxx&marketIds=yyy&marketIds=zzz
url = f"{data_node_url_rest}/stream/markets/depth/updates?marketIds={market_id}"\
    .replace("https://", "wss://")
res = []
event = threading.Event()

print(url)

# __stream_market_depth_updates_by_markets:
# Request a stream of live market depth update data for one or more market ids on a Vega network

def on_message(wsa, line):
    # Vega data-node v2 returns the json line by line so we need to wait
    # for a full structure before we can parse to valid JSON in python
    if line == "{":
        del res[:]
        res.append(line)
    elif line == "}":
        res.append(line)
        obj = json.loads(''.join(res))
        if "update" in obj["result"]:
            # Result contains each market-depth update (may be multiple)
            found_market = obj["result"]["update"][0]["marketId"]
            print(f"Market depth data found for {found_market}:")
            print(obj["result"]["update"][0])
    else:
        res.append(line)


def on_error(wsa, error):
    print(error)


def on_close(wsa, close_status_code, close_msg):
    print(f"Market-depth stream closed: {url}")


def on_open(wsa):
    print(f"Market-depth stream open: {url}")


def timeout():
    while not event.wait(timeout=30):
        ws.close()
        exit(1)


thread = threading.Thread(target=timeout)
thread.start()

ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_close=on_close)
ws.on_open = on_open
ws.run_forever()
# :stream_market_depth_updates_by_markets__
