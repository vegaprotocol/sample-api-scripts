# Stream market data

This test script connects to a Vega API node and:

- gets a list of markets
- uses GraphQL to stream market data for the first market found

```bash
virtualenv -p /usr/bin/python3 .venv
source .venv/bin/activate
pip install -r requirements.txt

# cp credentials-template.py template.py
# $EDITOR credentials.py

python3 stream-marketdata.py
```
