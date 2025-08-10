import React, { useState } from "react";
import axios from "axios";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

const API_BASE ="http://127.0.0.1:8000";

const CreatePost = () => {
  const token = useSelector((state) => state.auth.token);
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [visibility, setVisibility] = useState("public");
  const [tags, setTags] = useState("");
  const [mainImage, setMainImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [touched, setTouched] = useState({
    title: false,
    content: false,
  });

  const countWords = (str) => {
    return str.trim().split(/\s+/).filter(Boolean).length;
  };

  const titleValid = title.length > 10;
  const contentWordCount = countWords(content);
  const contentValid = contentWordCount >= 100 && contentWordCount <= 3000;

  const uploadImage = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await axios.post(`${API_BASE}/upload/image`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ${token}`,
      },
    });
    return res.data.url;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setTouched({ title: true, content: true });
    if (!titleValid || !contentValid) return;
    if (!token) {
      setError("You must be logged in to create a blog.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let mainImageUrl = null;
      if (mainImage) {
        mainImageUrl = await uploadImage(mainImage);
      }

      const tagsArray = tags.split(",").map((t) => t.trim()).filter(Boolean);

      const payload = {
        title,
        content,
        visibility,
        tags: tagsArray,
        main_image_url: mainImageUrl,
        sub_images: [],
      };

      await axios.post(`${API_BASE}/blogs`, payload, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      alert("Blog created successfully!");
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Create New Blog</h2>
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <div>
          <label className="block font-semibold mb-1">Title</label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onBlur={() => setTouched((t) => ({ ...t, title: true }))}
            className={`w-full border rounded px-3 py-2 ${
              touched.title && !titleValid ? "border-red-500" : "border-gray-300"
            }`}
          />
          {touched.title && !titleValid && (
            <p className="text-red-600 text-sm mt-1">
              Title must be more than 10 characters.
            </p>
          )}
        </div>

        <div>
          <label className="block font-semibold mb-1">Content</label>
          <textarea
            required
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onBlur={() => setTouched((t) => ({ ...t, content: true }))}
            rows={8}
            className={`w-full border rounded px-3 py-2 ${
              touched.content && !contentValid ? "border-red-500" : "border-gray-300"
            }`}
          />
          <p className="text-sm text-gray-600 mt-1">
            Word count: {contentWordCount} (min 100, max 3000)
          </p>
          {touched.content && !contentValid && (
            <p className="text-red-600 text-sm mt-1">
              Content must be between 100 and 3000 words.
            </p>
          )}
        </div>

        <div>
          <label className="block font-semibold mb-1">Visibility</label>
          <select
            value={visibility}
            onChange={(e) => setVisibility(e.target.value)}
            className="w-full border rounded px-3 py-2 border-gray-300"
          >
            <option value="public">Public</option>
            <option value="private">Private</option>
            <option value="draft">Draft</option>
            <option value="anonymous">Anonymous</option>
          </select>
        </div>

        <div>
          <label className="block font-semibold mb-1">Tags (comma separated)</label>
          <input
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="e.g. tech, nature, happiness"
            className="w-full border rounded px-3 py-2 border-gray-300"
          />
        </div>

        <div>
          <label className="block font-semibold mb-1">Main Image</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setMainImage(e.target.files[0])}
          />
        </div>

        {error && <div className="text-red-600">{error}</div>}

        <button
          type="submit"
          disabled={loading || !titleValid || !contentValid}
          className={`px-4 py-2 rounded text-white ${
            loading || !titleValid || !contentValid ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          {loading ? "Creating..." : "Create Blog"}
        </button>
      </form>
    </div>
  );
};

export default CreatePost;
