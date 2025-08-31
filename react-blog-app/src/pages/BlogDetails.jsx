import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export default function BlogDetails() {
  const { id } = useParams();
  const [blog, setBlog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const getFullUrl = (url) => {
    if (!url) return "";
    if (url.startsWith("http://") || url.startsWith("https://")) return url;
    return `${API_BASE}${url}`;
  };

  useEffect(() => {
    async function fetchBlog() {
      try {
        const res = await axios.get(`${API_BASE}/blogs/${id}`);
        setBlog(res.data);
      } catch (err) {
        setError(err.response?.data || "Failed to load blog");
      } finally {
        setLoading(false);
      }
    }
    fetchBlog();
  }, [id]);

  if (loading) return <div className="p-6">Loading...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;
  if (!blog) return <div className="p-6">Blog not found</div>;

  return (
    <div className="container mx-auto px-4 py-6">
      <h2 className="text-4xl font-bold mb-4">{blog.title}</h2>

      <div className="flex flex-wrap items-center text-sm text-gray-500 mb-4 gap-4">
        <span>Author ID: {blog.user_id}</span>
        <span>
          Visibility:{" "}
          <span
            className={`ml-1 font-medium ${
              blog.visibility === "public" ? "text-green-600" : "text-yellow-600"
            }`}
          >
            {blog.visibility}
          </span>
        </span>
        <span>Created: {new Date(blog.created_at).toLocaleString()}</span>
      </div>

      {blog.is_deleted && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded mb-4">
          ⚠ This blog has been marked as deleted.
        </div>
      )}
      
      <div className="mb-6">
        {blog.main_image_url && blog.main_image_url !== "string" && (
          <img
            src={getFullUrl(blog.main_image_url)}
            alt={blog.title}
            className="float-left w-full md:w-1/3 md:max-w-sm max-h-96 object-cover rounded shadow mr-0 md:mr-6 mb-4"
          />
        )}
        
        <div className="prose max-w-none text-gray-800 whitespace-pre-line text-justify">
          {blog.content}
        </div>
        
        {/* Clear float */}
        <div className="clear-both"></div>
      </div>

      {blog.tags && blog.tags.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Tags</h3>
          <div className="flex flex-wrap gap-2">
            {blog.tags.map((tag, idx) => (
              <span
                key={idx}
                className="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>
      )}

      <div>
        <Link
          to="/"
          className="inline-block px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded"
        >
          ← Back to Blogs
        </Link>
      </div>
    </div>
  );
}
