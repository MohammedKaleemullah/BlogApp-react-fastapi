// import { useEffect, useState, useRef, useCallback } from "react";
// import BlogCard from "../components/BlogCard";

// const BATCH_SIZE = 3;

// export default function Home({ blogs }) {
//   const [visibleBlogs, setVisibleBlogs] = useState([]);
//   const observerRef = useRef();

//   useEffect(() => {
//     setVisibleBlogs(blogs.slice(0, BATCH_SIZE));
//   }, [blogs]);

//   const lastBlogRef = useCallback(
//     (node) => {
//       if (observerRef.current) observerRef.current.disconnect();
//       observerRef.current = new IntersectionObserver((entries) => {
//         if (entries[0].isIntersecting) {
//           loadMore();
//         }
//       });
//       if (node) observerRef.current.observe(node);
//     },
//     [visibleBlogs, blogs]
//   );

//   const loadMore = () => {
//     setVisibleBlogs((prev) => {
//       if (prev.length >= blogs.length) {
//           console.log("All blogs loaded");
//           return prev; // No more blogs to load
//       }
//       else{
//         console.log(`Current visible blogs: ${prev.length}, Total blogs: ${blogs.length }`);
//         console.log("Loading more blogs...");
//       }
//       const next = blogs.slice(prev.length, prev.length + BATCH_SIZE);
//       return [...prev, ...next];
//     });
//   };

//   return (
//     <div className="p-4">
//       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-4">
//         {visibleBlogs.map((blog, index) => {
//           const isLast = index === visibleBlogs.length - 1;
//           return (
//             <div key={blog.id} ref={isLast ? lastBlogRef : null}>
//               <BlogCard
//                 id={blog.id}
//                 title={blog.title}
//                 content={blog.content}
//                 author="Kaleemullah"
//               />
//             </div>
//           );
//         })}
//       </div>
//     </div>
//   );
// }
import React, { useEffect, useRef, useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchBlogs } from "../store/slices/blogSlice";
import { Link } from "react-router-dom";

export default function Home() {
  const dispatch = useDispatch();
  const { items, loading, hasMore, offset, limit, error } = useSelector((s) => s.blogs);
  const observer = useRef();

  const lastBlogRef = useCallback(
    (node) => {
      if (loading) return;
      if (observer.current) observer.current.disconnect();
      observer.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && hasMore) {
          dispatch(fetchBlogs({ offset, limit, visibility: "public" }));
        }
      });
      if (node) observer.current.observe(node);
    },
    [loading, hasMore, offset, limit, dispatch]
  );

  // Initial fetch
  useEffect(() => {
    if (items.length === 0) {
      dispatch(fetchBlogs({ offset: 0, limit, visibility: "public" }));
    }
  }, [dispatch, items.length, limit]);

  return (
    <div className="container mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold mb-6">Latest Blogs</h1>

      {items.map((blog, index) => {
        if (index === items.length - 1) {
          return (
            <div
              key={blog.id}
              ref={lastBlogRef}
              className="mb-4 p-4 border rounded shadow-sm"
            >
              <Link to={`/post/${blog.id}`}>
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
            <Link to={`/post/${blog.id}`}>
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
