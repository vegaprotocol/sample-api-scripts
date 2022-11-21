
# Sample API Scripts

This repo contains Vega code examples in Python. These scripts use the Vega data-node and wallet APIs to interact with a Vega network.

With Vega users can consume APIs on the network using three different options (navigate through to your desired set of scripts):
 
 * **[REST](./rest)**
 * **[GraphQL](./graphql)**
 * gRPC - *coming soon!*
 
The purpose of these samples is to give simple and clear code that can be used to illustrate how to do something via Vega's APIs. 

For example; show me a list of trades on a particular market, stream my latest orders or submit a new liquidity commitment, etc. 

If these scripts do not provide what you're looking for there are even more tutorials, code and further examples on how to integrate with Vega (including API reference docs) at **https://docs.vega.xyz**

## Gitpod

This repo has been designed to be quick for a user to get started with. If you do not want to clone the code locally, you can use [Gitpod](https://gitpod.io/) to get started with zero configuration in your browser.

[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/vegaprotocol/sample-api-scripts)

Click on the "Gitpod ready-to-code" button above to load a browser based linux development environment and start experimenting straight away.

## Getting started for Unix based systems (Gitpod, Mac OS & Linux)

1. Load up a Gitpod environment (above) OR Clone this repo onto your local machine so you have access to all the files and can change them as you need.
    ```bash
    git clone https://github.com/vegaprotocol/sample-api-scripts.git
    ```
    This should create you a folder named `sample-api-scripts` that you will use for the rest of this README. 
    *Note: When running on Gitpod this is already done for you.*
    
1. Import the appropriate `vega-config` into your local environment for the network you want to test against (default is Fairground testnet). 
   ```
   source vega-config
   ```
   Pre-defined configs are available for testnet (vega-config *hosted wallet*), stagnet1 (vega-config-stagnet1 *local wallet*) and stagnet3 (vega-config-stagnet3 *local wallet*). You can define, copy or edit your own configurations. Out of the box, the vega-config file is included for ease and defaults to the Fairground testnet with hosted wallet configuration. *Node: Don't forget to source your configs after making any changes.*
   
1. Navigate to the API transport you would like to explore, for example:
   ```
   cd ./rest
   ```
   
1. Follow the sub-folder README.md information on how to run the samples.
   
# Getting started for Windows

1. Clone this repo onto your local machine so you have access to all the files and can change them as you need.
    ```bash
    git clone git@github.com:vegaprotocol/sample-api-scripts.git
    ```
    This should create you a folder named `sample-api-scripts` that you will use for the rest of this README.
    
1. Import the appropriate `vega-config-win` into your local environment for the network you want to test against (default is Fairground testnet). 
   ```
   source vega-config-win
   ```
   You can define, copy or edit your own configurations. Out of the box, the vega-config-win file is included for ease and defaults to the Fairground testnet with hosted wallet configuration. *Node: Don't forget to source your configs after making any changes.*
   
1. Run the setup batch script on your command prompt/terminal to import the vega-config into your local environment: 
   ```
   setenv.bat
   ```
   
1. Navigate to the API transport you would like to explore, for example:
   ```
   cd ./rest
   ```
   
1. Follow the sub-folder README.md information on how to run the samples.


# Troubleshooting

Python/terminal: If you get `No module named 'helpers'...`, you should enter `source credentials` and check with `echo "$PYTHONPATH"` than it shows `"."`.

# Contributing or raising issues

Please reach out to us on the [Discord chat](https://discord.gg/bkAF3Tu) to enquire further about how to get involved with Vega.

If you have found an issue or would like to suggest an improvement with our public code samples, please raise an issue in the [Sample-API-Scripts](https://github.com/vegaprotocol/sample-api-scripts/) repository. If you'd like to submit a PR we welcome additional sample code.
