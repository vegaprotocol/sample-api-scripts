# REST API samples in Python 

The files here represent how to call various aspects of the Vega data-node REST APIs and Wallet APIs programmatically using Python.

**REFERENCE APIs:** Reference API documentation for the REST APIs can be found at: https://docs.vega.xyz/


## Prerequisites 

*Ensure you have set up `vega-config` on your environment as explained in the main [Getting Started](../) guides.*

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
   
    To make sure you have all the tools required and have setup your environment correctly, it is best to try out the most basic `vega-time` script.
    
    ```bash
    python3 get-vega-time.py
    ```

1. Import the appropriate vega-config into your local environment for the network you want to test against (default vega-config is Fairground testnet).

    ```bash
    source vega-config
    ```

1. wallet

    If this correctly gets the Vega blockchain time then next we need to authenticate with the Vega wallet API so that the scripts can sign transactions.
    
    ```bash
    python3 login.py
    ```

    Run the login script, enter your wallet username and passphrase to authenticate and store a token for use in scripts such as submit-amend-cancel-order.py

    To logout or remove the token, simply run the logout script or delete `token.temp` 
    
    ```bash
    python3 logout.py
    ```
 
## How to run a script

All the source files are named logically so that the caller can read the file tree and understand the actions performed within. 
Hint: If you do not require all of the actions within a script, simply comment them out.

If the prerequisites are installed and set up correctly you can run a simple query or 'read' action script as follows:
    
```bash
python3 get-statistics.py
```

To run a 'write' action, sending a command into Vega, make sure you are authenticated first and have edited the file to your requirements:

```bash
python3 submit-amend-cancel-order.py
```

Finally to run a streaming action (the code is set to exit after 30 seconds):

```bash
python3 stream-market-data.py
```

