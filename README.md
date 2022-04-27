[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

# Sample API scripts

This repo contains sample scripts in various languages. These scripts use the
Vega core and wallet APIs to interact with Vega core nodes and wallet servers.

# Gitpod

Get started with the sample API scripts with zero configuration. Click on the
"Gitpod ready-to-code" button above.

# Getting started for Unix based systems (Mac OS & Linux)
1. Clone this repo onto your local machine so you have access to all the files and can change them as you need.
    ```bash
    git clone https://github.com/vegaprotocol/sample-api-scripts.git
    ```
    This should create you a folder named `sample-api-scripts` that you will use for the rest of this README.
1. Copy or rename the `credentials-template` file as `credentials`.  
    *Note: When running on Gitpod this is already done for you.*
    ```bash
    cp credentials-template credentials
    ```
1. Edit the `credentials` file. (`nano` and `vim` are installed, or use the built-in Gitpod text editor.)
    ```bash
    nano credentials
    (press Ctrl-O, Enter, Ctrl-X to save and exit)
    ```
1. The URL values will already be set up correctly for testnet including using the testnet hosted wallet. You will need to update your wallet credentials, near the top of the file. If you are going to use the scripts on mainnet, the URL details can be found in your wallet connections file of your local wallet server or in the Vega Wallet desktop app. If you are uncomfortable placing your wallet password into the credentials file, you can directly set the value using the export command:
    ```bash
    export WALLET_PASSPHRASE="<your password>"
    ```

1. Import the credentials into your local environment: `source credentials`

# Getting started for Windows

1. Clone this repo onto your local machine so you have access to all the files and can change them as you need.
    ```bash
    git clone git@github.com:vegaprotocol/sample-api-scripts.git
    ```
    This should create you a folder named `sample-api-scripts` that you will use for the rest of this README.
1. Copy or rename the `credentials-win-template` file as `credentials-win`.  
    ```bash
    copy credentials-win-template credentials-win
    ```
1. Edit the `credentials-win` file.
    ```bash
    notepad credentials-win
    ```
1. The URL values will already be set up correctly for testnet including using the testnet hosted wallet. You will need to update your wallet credentials, near the top of the file. If you are going to use the scripts on mainnet, the URL details can be found in your wallet connections file of your local wallet server or in the Vega Wallet desktop app. If you are uncomfortable placing your wallet password into the credentials file, you can directly set the value using the export command:
    ```bash
    set WALLET_PASSPHRASE="<your password>"
    ```
1. Run the setup batch script to import the credentials into your local environment: `setup.bat`


# Prerequisites 

The following tools or applications are required for these scripts to work. Here are the commands to check they are installed on your system:

1. python3
   ```bash
   python3 --version
   ```
1. pip3
    ```bash
    pip3 --version
    ```
    To make sure we have all the correct libraries you can use pip with the requirements.txt to install them all
    ```bash
    pip3 install -r requirements.txt
    ```
1. gq (https://github.com/hasura/graphqurl)
    ```bash
    gq --version
    ```
    

To make sure you have all the tools required and have setup your environment correctly, it is best to try out the most basic `vega-time` script.

```bash
python3 vega-time/get-time.py
```

If this correctly gets the time then you have everything you need to use the other scripts. If the script fails to run, check out the trouble shooting guide at the bottom of this page.


And you're good to go. Now choose a sample program to run from the following (see the link in the **Folder** column to learn how to run each sample script):

# Sample scripts

| Script description            | Languages |   API transport                      | Folder & README |
| :----------------- | :------- | :------------------------------ | :---------- |
| Get Asset | python3 | Vega node [GraphQL, REST, gRPC]  | / [get-assets](get-assets) |
| Orders by reference | bash, python3 | Vega node [GraphQL, REST, gRPC]  | / [get-by-reference](get-by-reference) |
| List market details and market data | bash, python3 | Vega node [GraphQL, REST, gRPC]  | / [get-markets-and-market-data](get-markets-and-market-data) |
| List Vega network parameters | bash, python3  | Vega node [GraphQL, REST, gRPC]  | / [get-network-parameters](get-network-parameters) |
| List orders and trades | bash, python3 | Vega node [GraphQL, REST, gRPC]  | / [get-orders-and-trades](get-orders-and-trades) |
| Vega statistics | bash, python3 | Vega node [GraphQL, REST, gRPC]  | / [get-statistics](get-statistics) |
| List parties and accounts | bash, python3 | Vega node [REST, gRPC]  | / [parties-and-accounts](parties-and-accounts) |
| Stream market data | python3 | Vega node [GraphQL] | / [stream-marketdata](stream-marketdata) |
| Stream orders and trades | python3  | Vega node [GraphQL] | / [stream-orders-and-trades](stream-orders-and-trades) |
| Interact with Vega wallet API | bash, python3 | Vega wallet [REST] | / [wallet](wallet) |
| Submit, amend and cancel orders | bash, python3 | Vega wallet [REST], Vega node [REST, gRPC] | / [submit-amend-cancel-orders](submit-amend-cancel-orders) |
| Submit and amend pegged orders | bash, python3 | Vega wallet [REST], Vega node [REST, gRPC] | / [submit-amend-pegged-order](submit-amend-pegged-order) |
| Vega/blockchain time  | bash, python3 | Vega node [GraphQL, REST, gRPC] | / [vega-time](vega-time) |
| Streaming events | bash, python3 | Vega node [GraphQL, REST, gRPC] | / [stream-events](stream-events) |
| Fees and margins estimation | bash, python3 | Vega node [REST, gRPC] | / [fees-margins-estimation](fees-margins-estimation) |
| Propose, vote and enact new markets | python3 | Vega node [REST] | / [propose-markets](propose-markets) |
| Propose, vote and enact network parameters update | python3 | Vega node [REST] | / [propose-netparams](propose-netparams) |
| Propose, vote and enact new freeform proposal | python3 | Vega node [REST] | / [propose-freeform](propose-freeform) |
| List proposals | bash, python3 | Vega node [GraphQL, gRPC] | / [propose-votes](propose-votes) |
| Submit create liquidity provision | bash, python3 | Data node [GraphQL, gRPC] | / [submit-create-liquidity-provision](submit-create-liquidity-provision) |
| Submit amend liquidity provision | bash, python3 | Data node [GraphQL, gRPC] | / [submit-amend-liquidity-provision](submit-amend-liquidity-provision) |
| Submit cancel liquidity provision | bash, python3 | Data node [GraphQL, gRPC] | / [submit-cancel-liquidity-provision](submit-cancel-liquidity-provision) |

# Troubleshooting

Python/terminal: If you get `No module named 'helpers'...`, you should enter `source credentials` and check with `echo "$PYTHONPATH"` than it shows `"."`.

# Contributing or raising issues

Please reach out to us on the [community forums](https://community.vega.xyz/c/testnet/) or [Discord chat](https://discord.gg/bkAF3Tu) to enquire further about how to get involved with Vega.

If you have found an issue or would like to suggest an improvement with our public code samples, please raise an issue in the [Sample-API-Scripts](https://github.com/vegaprotocol/sample-api-scripts/) repository. If you'd like to submit a PR we welcome additional sample code.
