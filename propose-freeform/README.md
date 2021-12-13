[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts - Propose Markets

These scripts talk to a Vega node as well as a Vega wallet to propose a freeform proposal:

- Login to existing wallet
- Select key-pair
- Find an existing asset with a specific name
- Get current time on Vega blockchain
- Prepare and submit a freeform proposal
- Wait for proposal to be accepted and processed
- Vote on the proposal
- Wait for voting to be enacted

Please see the documentation on Vega for further information.

## Python + requests

Interact with wallet and node API operations using python3 and the [requests](https://pypi.org/project/requests/) library [REST API]:

```bash
python3 propose-markets/propose-vote-enact-freeform.py
```

---

**[Home](../README.md)**
 
