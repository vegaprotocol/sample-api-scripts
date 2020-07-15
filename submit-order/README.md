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
