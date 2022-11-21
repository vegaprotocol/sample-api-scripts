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

If this correctly gets the Vega blockchain time then you have everything you need to use the other scripts. If the script fails to run, check out the trouble shooting guide at the bottom of this page.

