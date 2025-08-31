import React from "react";

const ImageSelector = ({
  imageMode,
  setImageMode,
  mainImage,
  setMainImage,
  prompt,
  setPrompt,
  generatedImage,
  generateImage,
  loading,
}) => {
  return (
    <div>
      <label className="block font-semibold mb-2">Main Image</label>

      {/* Toggle buttons */}
      <div className="flex gap-4 mb-2">
        <button
          type="button"
          onClick={() => setImageMode("upload")}
          className={`px-4 py-2 rounded font-semibold transition ${
            imageMode === "upload"
              ? "bg-gray-800 text-white shadow-md"
              : "bg-gray-200 text-gray-800 hover:bg-gray-300"
          }`}
        >
          Upload
        </button>
        <button
          type="button"
          onClick={() => setImageMode("generate")}
          className={`px-4 py-2 rounded font-semibold transition ${
            imageMode === "generate"
              ? "bg-gray-800 text-white shadow-md"
              : "bg-gray-200 text-gray-800 hover:bg-gray-300"
          }`}
        >
          Generate with AI
        </button>
      </div>

      {/* Upload Mode */}
      {imageMode === "upload" && (
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setMainImage(e.target.files[0])}
          className="border rounded px-3 py-2 w-full"
        />
      )}

      {/* Generate Mode */}
      {imageMode === "generate" && (
        <div className="space-y-2">
          <input
            type="text"
            placeholder="Describe the image..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full border rounded px-3 py-2 border-gray-300"
          />
          <button
            type="button"
            onClick={generateImage}
            disabled={loading || !prompt.trim()}
            className={`px-4 py-2 rounded font-semibold text-white transition ${
              loading
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-gray-800 hover:bg-gray-900"
            }`}
          >
            {loading ? "Generating..." : "Generate"}
          </button>

          {generatedImage && (
            <div className="mt-2">
              <div className="mb-1 font-semibold">Image has been generated successfully!!</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ImageSelector;
