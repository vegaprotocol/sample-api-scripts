#!/usr/bin/python3

###############################################################################
#                      S T R E A M   G O V E R N A N C E                      #
###############################################################################

#  How to stream governance information from a Data Node using Websockets:
#  ----------------------------------------------------------------------
#  Pagination is not supported, but the initial snapshot may contain
#  multiple pages. Date Range is not supported, this is a realtime stream.
#  ----------------------------------------------------------------------
#  The stream can be filtered the following parameter:
#   partyId:    Vega party id (public key)
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import websocket
import threading
import json
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

# Connect to the data node with a WSS based endpoint, this is not a HTTPS:// url
url = f"{data_node_url_rest}/stream/governance".replace("https://", "wss://")
res = []
event = threading.Event()

# __stream_governance:
# Request a stream of governance data on a Vega network

def on_message(wsa, line):
    # Vega data-node v2 returns the json line by line so we need to wait
    # for a full structure before we can parse to valid JSON in python
    if line == "{":
        del res[:]
        res.append(line)
    elif line == "}":
        res.append(line)
        obj = json.loads(''.join(res))
        if "governance" in obj["result"]:
            print(f"Governance data found:")
            print(obj["result"]["governance"])
    else:
        res.append(line)

    print(line)

def on_error(wsa, error):
    print(error)


def on_close(wsa, close_status_code, close_msg):
    print(f"Governance stream closed: {url}")


def on_open(wsa):
    print(f"Governance stream open: {url}")


def timeout():
    while not event.wait(timeout=30):
        ws.close()
        exit(1)


thread = threading.Thread(target=timeout)
thread.start()

ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_close=on_close)
ws.on_open = on_open
ws.run_forever()
# :stream_governance__
