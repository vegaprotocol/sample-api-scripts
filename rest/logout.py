import os
import helpers

wallet_server_url = helpers.get_from_env("WALLET_SERVER_URL")


def perform_logout():
    if os.path.exists("token.temp"):
        print(f"Using API: {wallet_server_url}")
        os.remove("token.temp")
        # Clean up any env vars related to wallet user
        os.unsetenv("WALLET_NAME")
        os.unsetenv("WALLET_PASSPHRASE")
        print("Log out complete (removed token file and environment vars)")
    else:
        print("The token file does not exist, try `python3 login.py`")


if __name__ == "__main__":
    perform_logout()
    exit(0)