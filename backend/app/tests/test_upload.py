def test_image_upload(client):
    file_path = r"D:\OneDrive - 1CloudHub\Desktop\full-blog-app\backend\app\assets\pikachu.jpg"  # Add a small image file here or create dynamically
    with open(file_path, "rb") as f:
        response = client.post("/upload/image", files={"file": ("test_image.png", f, "image/png")})
    assert response.status_code == 200
    assert "url" in response.json()
