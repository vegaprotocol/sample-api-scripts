#!/usr/bin/python3

###############################################################################
#                         S T R E A M   C A N D L E S                         #
###############################################################################

#  How to stream candle information from a Data Node using Websockets:
#  ----------------------------------------------------------------------
#  Pagination and Date Range are not supported, this is a realtime stream.
#  ----------------------------------------------------------------------
#  The stream requires the following parameter:
#   candleId:   Candle id (see below on how to retrieve this)
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import websocket
import threading
import json
import requests
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

# Load Vega market id
market_id = helpers.env_market_id()
assert market_id != ""

# Hint: In order to get candles of a suitable bucket size e.g. 5 minutes and
# market id e.g. 13b081fe5bc8fd256b0a374dc04d94b904118312dd0d942e891a5f57ce0c556c
# you should use the list candle intervals API to get back a candle id:

# __get_candle_intervals:
# Request a list of candle intervals available for a market and select a candle id
url = f"{data_node_url_rest}/candle/intervals?marketId={market_id}"
response = requests.get(url)
helpers.check_response(response)
print("Candle intervals for market:\n{}".format(
    json.dumps(response.json(), indent=2, sort_keys=True)))
# :get_candle_intervals__

# Find the first candle id in the list e.g. trades_candle_5_minutes_<market_id> etc
candle_id = response.json()["intervalToCandleId"][0]["candleId"]
assert candle_id != ""
print(f"Candle found: {candle_id}")

# Connect to the data node with a WSS based endpoint, this is not a HTTPS:// url
#  Hint: to include/filter data from a party add the param `partyId`
#  e.g. ?marketIds=xxx&partyId=yyy
url = f"{data_node_url_rest}/stream/candle/data?candleId={candle_id}".replace("https://", "wss://")
res = []
event = threading.Event()

# __stream_candles_by_market:
# Request a stream of candle updates for a market id and time bucket (e.g. candle id) on a Vega network

def on_message(wsa, line):
    # Vega data-node v2 returns the json line by line so we need to wait
    # for a full structure before we can parse to valid JSON in python
    if line == "{":
        del res[:]
        res.append(line)
    elif line == "}":
        res.append(line)
        obj = json.loads(''.join(res))
        if "candle" in obj["result"]:
            # When a new candle update arrives print the changes
            print(f"Candle data found:")
            print(obj["result"]["candle"])
    else:
        res.append(line)


def on_error(wsa, error):
    print(error)


def on_close(wsa, close_status_code, close_msg):
    print(f"Candle stream closed: {url}")


def on_open(wsa):
    print(f"Candle stream open: {url}")


def timeout():
    while not event.wait(timeout=30):
        ws.close()
        exit(1)


thread = threading.Thread(target=timeout)
thread.start()

ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_close=on_close)
ws.on_open = on_open
ws.run_forever()
# :stream_candles_by_market__
