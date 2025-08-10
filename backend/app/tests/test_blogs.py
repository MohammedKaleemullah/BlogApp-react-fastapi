def test_blog_crud(client):
    # Login first
    login_data = {
        "username": "testuser",
        "password": "Test@1234"
    }
    login_resp = client.post("/auth/login", json=login_data)
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create blog
    blog_data = {
        "title": "Test Blog",
        "content": "<b>Hello World</b>",
        "visibility": "public",
        "tags": ["test", "blog"],
        "main_image_url": None,
        "sub_images": []
    }
    response = client.post("/blogs/", json=blog_data, headers=headers)
    assert response.status_code == 200
    blog = response.json()
    assert blog["title"] == "Test Blog"
    blog_id = blog["id"]

    # Get blog by ID
    response = client.get(f"/blogs/{blog_id}")
    assert response.status_code == 200
    assert response.json()["id"] == blog_id

    # Update blog
    update_data = {
        "title": "Updated Blog Title"
    }
    response = client.put(f"/blogs/{blog_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Blog Title"

    # Soft delete blog
    response = client.delete(f"/blogs/{blog_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Blog soft deleted successfully"

    # Confirm deleted blog is not returned in list
    response = client.get("/blogs/")
    assert all(b["id"] != blog_id for b in response.json())
