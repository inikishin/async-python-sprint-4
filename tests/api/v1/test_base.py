def test_get_short_url(api_client):
    data = {"url": "url"}
    response = api_client.post("/api/v1", json=data)
    assert response.status_code == 200

    data = response.json()
    short_url = data.get("url")
    assert isinstance(short_url, str)
