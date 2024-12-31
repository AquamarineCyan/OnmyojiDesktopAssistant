import httpx

repo_url = "https://github.com/AquamarineCyan/Onmyoji_Python"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


def test_api_url():
    api_url = "https://api.github.com/repos/AquamarineCyan/Onmyoji_Python/releases/latest"
    r = httpx.get(api_url, headers=headers)
    print(f"API URL request latency: {r.elapsed.total_seconds() * 1000} ms")
    assert r.status_code == 200


def test_mirror_url():
    mirror_station = "https://ghgo.xyz/"
    r = httpx.get(mirror_station, headers=headers)
    print(f"mirror station request latency: {r.elapsed.total_seconds() * 1000} ms")
    assert r.status_code == 200
