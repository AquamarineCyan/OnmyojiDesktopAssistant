import pytest

import httpx
import json


def api_url_func() -> httpx.Response:

    api_url = "https://api.github.com/repos/AquamarineCyan/Onmyoji_Python/releases/latest"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70"
    }
    r = httpx.get(api_url, headers=headers)
    return r


def ghproxy_http_func(r: httpx.Response):
    data_dict = json.loads(r.text)
    browser_download_url = data_dict["assets"][0]["browser_download_url"]
    browser_download_url_ghproxy: str = f"https://ghproxy.com/{browser_download_url}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70"
    }
    with httpx.stream("GET", browser_download_url_ghproxy, headers=headers) as r:
        return r.status_code


def test_connect():
    r = api_url_func()
    assert r.status_code == 200
    # assert ghproxy_http_func(r) == 200
