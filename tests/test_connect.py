import httpx
import pytest

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

MIRROR_URLS = [
    "https://ghproxy.gpnu.org/",
    "https://gh.222322.xyz/",
    "https://ghproxy.net/",
    "https://gh-proxy.com/",
    "https://gh.pylas.xyz/",
]


def test_api_url():
    api_url = "https://api.github.com/repos/AquamarineCyan/Onmyoji_Python/releases/latest"
    try:
        r = httpx.get(api_url, headers=headers, timeout=10)
    except httpx.RequestError as e:
        pytest.fail(f"API request failed: {e}")

    latency = r.elapsed.total_seconds() * 1000
    print(f"API URL request latency: {latency:.2f} ms, status_code: {r.status_code}")
    assert r.status_code == 200, f"Expected status code 200, got {r.status_code}"


@pytest.mark.parametrize("url", MIRROR_URLS)
def test_mirror_url(url):
    try:
        r = httpx.get(url, headers=headers, timeout=10)
    except httpx.RequestError as e:
        pytest.fail(f"Mirror site {url} request failed: {e}")

    latency = r.elapsed.total_seconds() * 1000
    print(f"Mirror site {url} latency: {latency:.2f} ms, status_code: {r.status_code}")
    assert r.status_code == 200, f"Mirror site {url} expected status code 200, got {r.status_code}"
