[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - Stream market data

This Python script talks to a Vega node and:

- (REST) gets a list of markets using [requests](https://pypi.org/project/requests/) library
- (GraphQL) streams market data for the first market found

```bash
python3 stream-marketdata/stream-marketdata.py
```

## Shell + graphqurl
[![Graphql - Stream-MarketData](https://img.shields.io/badge/Graphql-Stream--MarketData-2ea44f?logo=GraphQL)](https://graphqlbin.com/v2/L0vEHk)

Stream using shell scripts and [graphqurl](https://github.com/hasura/graphqurl) only [GraphQL API]:

```bash
bash stream-marketdata/stream-marketdata-gql.sh
```

---

**[Home](../README.md)**
