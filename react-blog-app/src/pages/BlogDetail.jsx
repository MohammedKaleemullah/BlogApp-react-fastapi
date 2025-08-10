import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";

function BlogDetail() {
  const { id } = useParams();
  const [blog, setBlog] = useState(null);

  useEffect(() => {
    const storedBlogs = JSON.parse(localStorage.getItem("blogs") || "[]");
    const found = storedBlogs.find((b) => b.id === id);
    setBlog(found);
  }, [id]);

  if (!blog) return <p className="text-center">Blog not found.</p>;

  return (
    <div className="max-w-3xl mx-auto bg-white p-6 rounded shadow">
      <h1 className="text-2xl font-bold mb-4">{blog.title}</h1>
      <p className="text-gray-700 whitespace-pre-wrap whitespace-pre-wrap break-words">{blog.content}</p>
      <p className="text-sm text-muted-foreground mt-4 text-right">
        Posted on: {new Date(blog.createdAt).toLocaleString()}
      </p>
    </div>
  );
}

export default BlogDetail;