import json
import datetime
import random
import os
import requests
import string
from typing import Any


def check_response(r: requests.Response) -> None:
    """
    Raise a helpful exception if the HTTP response was not 200.
    """
    if r.status_code != 200:
        raise Exception(f"{r.url} returned HTTP {r.status_code} {r.text}")


def check_var(val: str) -> bool:
    """
    Return true if the value is ok.
    """
    if val is None or val == "":
        return False
    if invalid(val):
        return False
    return True


def check_url(url: str) -> bool:
    """
    Return true if the URL is ok.
    """
    if not check_var(url):
        return False
    if not any(url.startswith(prefix) for prefix in ["http://", "https://"]):
        return False
    return True


def get_from_env(var_name: str) -> str:
    """
    Get a value from an environment variable. Used in CI for testing.
    """
    val = os.getenv(var_name, "")
    if val == "":
        print(f"Error: Missing environment variable {var_name}.")
        exit(1)

    return val


def invalid(val: str) -> bool:
    """
    Return true if none of the invalid strings are found in the value.
    """
    bzzt = [">>", "e.g.", "example"]
    return any(x in val for x in bzzt)


def random_string(length: int = 20) -> str:
    """
    Generate a random string, made of letters and digits.
    """
    choices = string.ascii_letters + string.digits
    return "".join(random.choice(choices) for i in range(length))


def fix_wallet_server_url(url: str) -> str:
    """
    Help guide users against including api version suffix in wallet server URL.
    """
    for suffix in ["/api/v1/", "/api/v1", "/api/", "/api", "/"]:
        if not url.endswith(suffix):
            continue
        print(
            f'There\'s no need to add "{suffix}" to the wallet server URL. '
            "Removing it and continuing..."
        )
        url = url[: -len(suffix)]

    return url


def enum_to_str(e: Any, val: int) -> str:
    return e.keys()[e.values().index(val)]


def ts_now():
    return datetime.datetime.now()


def get_nano_ts(dt: datetime.datetime, seconds_delta: int):
    new_dt = dt - datetime.timedelta(seconds=seconds_delta)
    return str(int(new_dt.replace(tzinfo=datetime.timezone.utc).timestamp())*1000000000)


def nano_ts_to_human_date(nanos):
    dt = datetime.datetime.fromtimestamp(nanos / 1e9)
    return '{}{:03.0f}'.format(dt.strftime('%Y-%m-%dT%H:%M:%S.%f'), nanos % 1e3)


def env_market_id() -> str:
    """
    Get env var for a custom MARKET_ID, will not forcibly reload from API
    """
    return env_market_id_from_api(False)


def env_market_id_from_api(reload: bool) -> str:
    """
    Get env var for a custom MARKET_ID, will find one from API if not specified
    """
    market_id = os.getenv("MARKET_ID", "")
    perform_reload = False
    if len(market_id) > 0:
        if reload:
            perform_reload = True
    else:
        perform_reload = True

    if perform_reload:
        # Request a list of markets and select the first one
        data_node_url_rest = get_from_env("DATA_NODE_URL_REST")
        url = f"{data_node_url_rest}/markets"
        response = requests.get(url)
        check_response(response)
        if len(get_nested_response(response, "markets")) == 0:
            print(f"No markets found on {url}")
            print("Please check and try again...")
            exit(1)
        else:
            market_id = get_nested_response(response, "markets")[0]["node"]["id"]
        assert market_id != ""
        print(f"MARKET_ID set: {market_id}")
        os.environ["MARKET_ID"] = market_id

    return market_id


def env_party_id() -> str:
    """
    Get env var for a custom PARTY_ID, will not forcibly reload from API
    """
    return env_party_id_from_api(False)


def env_party_id_from_api(reload: bool) -> str:
    """
    Get env var for a custom PARTY_ID, will find one from API if not specified
    """
    party_id = os.getenv("PARTY_ID", "")
    perform_reload = False
    if len(party_id) > 0:
        if reload:
            perform_reload = True
    else:
        perform_reload = True

    if perform_reload:
        # Request a list of parties and select the first one
        data_node_url_rest = get_from_env("DATA_NODE_URL_REST")
        url = f"{data_node_url_rest}/parties"
        response = requests.get(url)
        check_response(response)
        if len(get_nested_response(response, "parties")) <= 1:
            print(f"No (non network) parties found on {url}")
            print("Please check and try again...")
            exit(1)
        else:
            party_id = get_nested_response(response, "parties")[1]["node"]["id"]
        assert party_id != ""
        print(f"PARTY_ID set: {party_id}")
        os.environ["PARTY_ID"] = party_id

    return party_id


def get_nested_response(response: json, key: str) -> json:
    """
    Get json back from a response string given v2 nesting with edges
    """
    return response.json()[key]["edges"]


def check_nested_response(response: json, key: str) -> bool:
    """
    Check if len > 0 from a response string given v2 nesting with edges
    """
    return len(get_nested_response(response, key)) > 0


def generate_id(n :int) -> str:
    """
    Generate a semi-random identifier string of length n
    """
    return ''.join(random.choices(string.ascii_lowercase + (2 * string.digits), k=n))