import httpx

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


def test_api_url():
    api_url = "https://api.github.com/repos/AquamarineCyan/Onmyoji_Python/releases/latest"
    r = httpx.get(api_url, headers=headers)
    print(f"API URL request latency: {r.elapsed.total_seconds() * 1000:.2f} ms")
    print(f"API URL status_code: {r.status_code}")
    assert r.status_code == 200


def test_mirror_url():
    for url in [
        "https://ghfast.top/",
        "https://gh.222322.xyz/",
        "https://ghproxy.net/",
        "https://gh-proxy.com/",
        "https://gh.pylas.xyz/",
    ]:
        r = httpx.get(url, headers=headers)
        print(f"mirror station: {url} request latency: {r.elapsed.total_seconds() * 1000:.2f} ms")
        print(f"mirror station: {url} status_code: {r.status_code}")
        assert r.status_code == 200
