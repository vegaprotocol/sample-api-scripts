# Stream market data

| Language | Talks to                  | App/Library |
| :------- | :------------------------ | :---------- |
| python3  | Vega node (REST, GraphQL) | REST: [requests](https://pypi.org/project/requests/); GraphQL: [websocket-client](https://pypi.org/project/websocket_client/) |

This test script connects to a Vega API node and:

- (REST) gets a list of markets
- (GraphQL) streams market data for the first market found

## Running

```bash
virtualenv -p /usr/bin/python3 .venv
source .venv/bin/activate
pip install -r requirements.txt

# cp credentials-template.py credentials.py
# $EDITOR credentials.py

python3 stream-marketdata.py
```
