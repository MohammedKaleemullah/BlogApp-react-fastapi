def test_get_users(client):

    response = client.get("/users/")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
