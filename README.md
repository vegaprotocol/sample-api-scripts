
# Sample API Scripts

**This repo is not maintained and scripts may be out of date.**

This repo contains Vega code examples in Python. These scripts use the Vega data-node and wallet APIs to interact with a Vega network.

With Vega users can consume APIs on the network using three different options (navigate through to your desired set of scripts):
 
 * **[REST](./rest#readme)**
 * **[GraphQL](./graphql#readme)**
 
The purpose of these samples is to give simple and clear code that can be used to illustrate how to do something via Vega's APIs. 

For example, show me a list of trades on a particular market, stream my latest orders or submit a new liquidity commitment, etc. 

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
    
1. Import the appropriate `vega-config` into your local environment for the network you want to test against (default vega-config is Fairground testnet). 
   ```
   source vega-config
   ```
   You can define, copy or edit your own configurations. Out of the box, the vega-config file is included for ease and defaults to the Fairground testnet with hosted wallet configuration. *Node: Don't forget to source your configs after making any changes.*
   
1. Navigate to the API transport you would like to explore, for example:
   ```
   cd ./rest
   ```
   
1. Follow the sub-folder README.md information on how to run the samples.

1. For most scripts, you will have to run the login script **before** running the script in question. It's also important to note that you should have a desktop or CLI wallet connection open as you run this script, otherwise the connection will be refused. 

 ```
   python3 login.py
   ```
   
# Getting started for Windows

1. Clone this repo onto your local machine so you have access to all the files and can change them as you need.
    ```bash
    git clone git@github.com:vegaprotocol/sample-api-scripts.git
    ```
    This should create you a folder named `sample-api-scripts` that you will use for the rest of this README.
    
1. Import the appropriate `vega-config-win.bat` into your local environment for the network you want to test against (default is Fairground testnet). Simply run this batch script in your terminal:
   ```
   vega-config-win.bat
   ```
   You can define, copy or edit your own configurations. Out of the box, the vega-config-win file is included for ease and defaults to the Fairground testnet with hosted wallet configuration. *Note: Don't forget to rerun this after making any config changes.*

   
1. Navigate to the API transport you would like to explore, for example:
   ```
   cd rest
   ```
   
1. Follow the sub-folder README.md information on how to run the samples.

1. For most scripts, you will have to run the login script **before** running the script in question. It's also important to note that you should have a desktop or CLI wallet connection open as you run this script, otherwise the connection will be refused. 

 ```
   python3 login.py
   ```
   
# Video Walkthrough

This quick [video](https://www.loom.com/share/09407b46492a49afa0ad7ae4d6098559) walks you through how to log in to the sample scripts. 

# Future Improvements

We are constantly trying to improve these sample scripts and keep them up to date with Vega's most recent software releases. Below is a future roadmap for the sample-api-scripts, including what we will add next:

- Add more transaction scripts
- Basic CI support through Github Actions
- Add support for gRPC


# Contributing or raising issues

Please reach out to us on the [Discord chat](https://discord.gg/bkAF3Tu) to enquire further about how to get involved with Vega, alternatively you can check out the [Builders Club](https://vega.xyz/builders-club/).

If you have found an issue or would like to suggest an improvement with our public code samples, please raise an issue in the [Sample-API-Scripts](https://github.com/vegaprotocol/sample-api-scripts/) repository. If you'd like to submit a PR we welcome additional sample code.
