# Submit Order

| Language | Talks to      | App/Library |
| :------- | :------------ | :---------- |
| python3  | wallet (REST) | [Vega-API-client](https://pypi.org/project/Vega-API-client/) |

These test scripts contains sample code for interacting with a Vega Wallet
server.

## Running

```bash
virtualenv -p /usr/bin/python3 .venv
source .venv/bin/activate
pip install -r requirements.txt

# cp credentials-template.py credentials.py
# $EDITOR credentials.py

python3 wallet.py
```
