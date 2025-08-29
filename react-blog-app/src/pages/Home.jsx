import React, { useEffect, useRef, useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchBlogs } from "@/store/slices/blogSlice";
import { Link } from "react-router-dom";

export default function Home({ searchQuery }) {
  const dispatch = useDispatch();
  const { items, loading, hasMore, offset, limit, error } = useSelector((s) => s.blogs);
  const observer = useRef();
  const [initialLoaded, setInitialLoaded] = React.useState(false);

  const lastBlogRef = useCallback(
    (node) => {
      if (loading) return;
      if (observer.current) observer.current.disconnect();

      observer.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && hasMore && !loading) {
          dispatch(fetchBlogs({ offset, limit, visibility: "public" }));
        }
      });

      if (node) observer.current.observe(node);
    },
    [loading, hasMore, offset, limit, dispatch]
  );

  useEffect(() => {
    if (!initialLoaded) {
      dispatch(fetchBlogs({ offset: 0, limit, visibility: "public" }));
      setInitialLoaded(true);
    }
  }, [dispatch, limit, offset, initialLoaded]);

  const filteredBlogs = items.filter(
    (blog) =>
      // blog.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      // blog.content.toLowerCase().includes(searchQuery.toLowerCase())
      blog.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase())) ||
      blog.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="container mx-auto px-4 py-6">
      <h2 className="text-2xl font-bold mb-6">Latest Blogs</h2>

      {filteredBlogs.map((blog, index) => {
        if (index === filteredBlogs.length - 1) {
          return (
            <div
              key={blog.id}
              ref={lastBlogRef}
              className="mb-4 p-4 border rounded shadow-sm"
            >
              <Link to={`/blogs/${blog.id}`}>
                <h2 className="text-lg font-semibold">{blog.title}</h2>
              </Link>
              <p className="text-sm text-gray-600">
                {blog.summary || blog.content?.slice(0, 100) + "..."}
              </p>
            </div>
          );
        }
        return (
          <div key={blog.id} className="mb-4 p-4 border rounded shadow-sm">
            <Link to={`/blogs/${blog.id}`}>
              <h2 className="text-lg font-semibold">{blog.title}</h2>
            </Link>
            <p className="text-sm text-gray-600">
              {blog.summary || blog.content?.slice(0, 100) + "..."}
            </p>
          </div>
        );
      })}

      {loading && <div className="text-center py-4">Loading...</div>}
      {error && <div className="text-red-500 py-4 text-center">{error}</div>}
      {!hasMore && !loading && (
        <div className="text-center text-gray-500 py-4">No more blogs</div>
      )}
    </div>
  );
}
