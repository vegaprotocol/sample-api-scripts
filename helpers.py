import random
import requests
import string


def check_response(r: requests.Response) -> None:
    assert (
        r.status_code == 200
    ), f"{r.url} returned HTTP {r.status_code} {r.text}"


def check_var(val: str) -> bool:
    return val is not None and val != "" and "example" not in val


def check_url(url: str) -> bool:
    return check_var(url) and url.startswith("https://")


def random_string(length: int = 20) -> str:
    choices = string.ascii_letters + string.digits
    return "".join(random.choice(choices) for i in range(length))
