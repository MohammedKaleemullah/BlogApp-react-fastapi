import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";
import axios from "axios";
import { ToastModal } from "@/components/ToastModal"; // ✅ Import toast

const API_BASE = "http://127.0.0.1:8000";
const LLM_API_BASE = "http://127.0.0.1:8005";

export default function BlogDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const token = useSelector((state) => state.auth.token);
  
  const [blog, setBlog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleting, setDeleting] = useState(false);

  // Toast state
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState("success");
  const [isConfirmation, setIsConfirmation] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);

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

  const showConfirmationToast = () => {
    if (!token) {
      setToastMessage("You must be logged in to delete a blog.");
      setToastType("error");
      setShowToast(true);
      return;
    }

    setToastMessage("Are you sure you want to delete this blog? This action cannot be undone.");
    setToastType("warning");
    setIsConfirmation(true);
    setShowToast(true);
  };

  const executeDelete = async () => {
    setDeleting(true);
    try {
      await axios.delete(`${API_BASE}/blogs/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      try {
        await axios.delete(`${LLM_API_BASE}/delete-blog/${id}`);
        console.log("✅ Blog removed from RAG index");
      } catch (ragError) {
        console.warn("⚠️ RAG index deletion failed:", ragError.message);
      }

      // Show success toast
      setToastMessage("Blog deleted successfully! 🗑️");
      setToastType("success");
      setIsConfirmation(false);
      setShowToast(true);

      // Navigate after showing toast
      setTimeout(() => navigate("/"), 2000);
    } catch (err) {
      console.error("Delete error:", err);
      let errorMessage = "Failed to delete blog.";
      
      if (err.response?.status === 401) {
        errorMessage = "You are not authorized to delete this blog. Please log in.";
      } else if (err.response?.status === 403) {
        errorMessage = "You don't have permission to delete this blog.";
      }

      setToastMessage(errorMessage);
      setToastType("error");
      setIsConfirmation(false);
      setShowToast(true);
    } finally {
      setDeleting(false);
    }
  };

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

      <div className="flex flex-wrap gap-3">
        <Link
          to="/"
          className="inline-block px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded transition-colors"
        >
          ← Back to Blogs
        </Link>

        {token && (
          <button
            onClick={showConfirmationToast}
            disabled={deleting}
            className={`px-4 py-2 rounded transition-colors ${
              deleting
                ? "bg-gray-400 cursor-not-allowed text-gray-600"
                : "bg-red-600 hover:bg-red-700 text-white"
            }`}
          >
            {deleting ? (
              <div className="flex items-center">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Deleting...
              </div>
            ) : (
              "🗑️ Delete Blog"
            )}
          </button>
        )}
      </div>

      {showToast && (
        <ToastModal
          message={toastMessage}
          type={toastType}
          isConfirmation={isConfirmation}
          onConfirm={executeDelete}
          onCancel={() => {
            setShowToast(false);
            setIsConfirmation(false);
          }}
          onClose={() => {
            setShowToast(false);
            setIsConfirmation(false);
          }}
        />
      )}
    </div>
  );
}
