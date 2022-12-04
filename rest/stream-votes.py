#!/usr/bin/python3

###############################################################################
#                          S T R E A M   V O T E S                            #
###############################################################################

#  How to stream vote information from a Data Node using Websockets:
#  ----------------------------------------------------------------------
#  Pagination and Date Range are not supported, this is a realtime stream.
#  ----------------------------------------------------------------------
#  The stream can be filtered by various parameters, including:
#   partyId:      Vega party id (public key)
#   proposalId:   Optional proposal id
#     > Include one or both to refine the stream of data from Vega
#  ----------------------------------------------------------------------
#  For full details see the REST Reference API docs at https://docs.vega.xyz

import websocket
import threading
import json
import helpers

# Load Vega node API v2 URL, this is set using 'source vega-config'
# located in the root folder of the sample-api-scripts repository
data_node_url_rest = helpers.get_from_env("DATA_NODE_URL_REST")

# Load Vega party id
party_id = helpers.env_party_id()
assert party_id != ""

# Connect to the data node with a WSS based endpoint, this is not a HTTPS:// url
#  Hint: to include/filter data from a proposal id add the param `proposalId`
#  e.g. ?partyId=xxx&proposalId=yyy
url = f"{data_node_url_rest}/stream/votes?partyId={party_id}".replace("https://", "wss://")
res = []
event = threading.Event()

# __stream_votes_by_party:
# Request a stream of votes for a party id on a Vega network

def on_message(wsa, line):
    # Vega data-node v2 returns the json line by line so we need to wait
    # for a full structure before we can parse to valid JSON in python
    if line == "{":
        del res[:]
        res.append(line)
    elif line == "}":
        res.append(line)
        obj = json.loads(''.join(res))
        if "vote" in obj["result"]:
            # Result contains reward data for party
            print(f"Vote data found:")
            print(obj["result"]["vote"])
    else:
        res.append(line)


def on_error(wsa, error):
    print(error)


def on_close(wsa, close_status_code, close_msg):
    print(f"Votes stream closed: {url}")


def on_open(wsa):
    print(f"Votes stream open: {url}")


def timeout():
    while not event.wait(timeout=30):
        ws.close()
        exit(1)


thread = threading.Thread(target=timeout)
thread.start()

ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_close=on_close)
ws.on_open = on_open
ws.run_forever()
# :stream_votes_by_party__
