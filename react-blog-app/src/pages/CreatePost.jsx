import React, { useState } from "react";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import axios from "axios";

import TextInput from "@/components/TextInput";
import TextAreaInput from "@/components/TextAreaInput";
import ImageSelector from "@/components/ImageSelector";

const API_BASE = "http://127.0.0.1:8000";
const LLM_API_BASE = "http://127.0.0.1:8005";

const CreatePost = () => {
  const token = useSelector((state) => state.auth.token);
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [visibility, setVisibility] = useState("public");
  const [tags, setTags] = useState("");
  const [imageMode, setImageMode] = useState("upload");
  const [mainImage, setMainImage] = useState(null);
  const [generatedImage, setGeneratedImage] = useState(null);
  const [prompt, setPrompt] = useState("");

  const [loadingSubmit, setLoadingSubmit] = useState(false);
  const [loadingGenerate, setLoadingGenerate] = useState(false);
  const [error, setError] = useState(null);
  const [touched, setTouched] = useState({ title: false, content: false });

  const uploadImage = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await axios.post(`${API_BASE}/upload/image`, formData, {
      headers: { "Content-Type": "multipart/form-data", Authorization: `Bearer ${token}` },
    });
    return res.data.url;
  };

  const generateImage = async () => {
    if (!prompt.trim()) return;
    setLoadingGenerate(true);
    setError(null);
    try {
      const res = await axios.post(`${LLM_API_BASE}/generate`, { user_input: prompt });
      setGeneratedImage(res.data.image_url);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoadingGenerate(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setTouched({ title: true, content: true });

    if (!token) return setError("You must be logged in to create a blog.");
    if (title.length <= 10 || content.trim().split(/\s+/).length < 100) return;

    setLoadingSubmit(true);
    setError(null);
    try {
      const mainImageUrl =
        imageMode === "upload" && mainImage ? await uploadImage(mainImage) : generatedImage;

      const tagsArray = tags.split(",").map((t) => t.trim()).filter(Boolean);

      await axios.post(
        `${API_BASE}/blogs`,
        {
          title,
          content,
          visibility,
          tags: tagsArray,
          main_image_url: mainImageUrl,
          sub_images: [],
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      alert("Blog created successfully!");
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoadingSubmit(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Create New Blog</h2>
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <TextInput
          label="Title"
          value={title}
          setValue={setTitle}
          touched={touched.title}
          setTouched={(val) => setTouched((t) => ({ ...t, title: val }))}
          minLength={10}
          maxLength={150}
        />
        <TextAreaInput
          label="Content"
          value={content}
          setValue={setContent}
          touched={touched.content}
          setTouched={(val) => setTouched((t) => ({ ...t, content: val }))}
          minWords={100}
          maxWords={3000}
        />

        {/* Visibility */}
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

        {/* Tags */}
        <div>
          <label className="block font-semibold mb-1">Tags (comma separated)</label>
          <input
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="e.g. tech, nature"
            className="w-full border rounded px-3 py-2 border-gray-300"
          />
        </div>

        {/* Image Selector */}
        <ImageSelector
          imageMode={imageMode}
          setImageMode={setImageMode}
          mainImage={mainImage}
          setMainImage={setMainImage}
          prompt={prompt}
          setPrompt={setPrompt}
          generatedImage={generatedImage}
          generateImage={generateImage}
          loading={loadingGenerate} // pass only generate loading
        />

        {error && <div className="text-red-600">{error}</div>}

        {/* Submit Button */}
            <div className="pt-4">
              <button
                type="submit"
                disabled={loadingSubmit}
                className={`w-full py-4 rounded-xl text-white font-semibold text-lg shadow-lg transition-all duration-200 transform ${
                  loadingSubmit
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-gradient-to-r from-gray-600 to-gray-800 hover:from-gray-800 hover:to-gray-600 hover:scale-105 hover:shadow-xl"
                }`}
              >
                {loadingSubmit ? (
                  <div className="flex items-center justify-center">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Creating Your Blog...
                  </div>
                ) : (
                  "Create Blog ✨"
                )}
              </button>
            </div>
      </form>
    </div>
  );
};

export default CreatePost;
