[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - Stream events

These scripts talk to a Vega node and will stream events from the event bus for a node.  
Please see the documentation on Vega for further information.

## Shell + curl/graphqurl

Stream using shell scripts and `curl` and [graphqurl](https://github.com/hasura/graphqurl) only [GraphQL API]:

```bash
bash stream-events/stream-events.sh
```

## Python + Vega-API-client

Stream events using python3 and the [Vega-API-client](https://pypi.org/project/Vega-API-client/) library [gRPC API]:

```bash
python3 stream-events/stream-events-with-Vega-API-client.py
```

---

**[Home](../README.md)**
 
