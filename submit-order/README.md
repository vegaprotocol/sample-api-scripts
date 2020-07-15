# Submit Order

| Language | Talks to                        | App/Library |
| :------- | :------------------------------ | :---------- |
| bash     | wallet (REST), Vega node (REST) | curl        |
| python3  | wallet (REST), Vega node (REST) | requests    |

These test scripts connect to a Vega Wallet server and a Vega API node, and:

1. Wallet server: creates a new wallet, or logs in to an existing one
1. Wallet server: creates a keypair, if one has not already been created
1. Vega node: calls `PrepareSubmitOrder` (send the order details, receive a
   `PreparedOrder`)
1. Wallet server: calls `SignTx` (send the `PreparedOrder` and a public key
   associated with the logged-in wallet, receive a `SignedBundle`)
1. Vega node: calls `SubmitTransaction` (send the `SignedBundle`)

## Running


### bash

```bash
# cp credentials-template.sh credentials.sh
# $EDITOR credentials.sh

./submit-order.sh
```

### python (requests)

```bash
virtualenv -p /usr/bin/python3 .venv
source .venv/bin/activate
pip install -r requirements.txt

# cp credentials-template.py credentials.py
# $EDITOR credentials.py

python3 submit-order.py
```

### python (Vega-API-client)

```bash
virtualenv -p /usr/bin/python3 .venv
source .venv/bin/activate
pip install -r requirements-Vega-API-client.txt

# cp credentials-template.py credentials.py
# $EDITOR credentials.py

python3 submit-order-with-Vega-API-client.py
```
