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

export default function Home() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold">Welcome to the Blog App</h1>
    </div>
  );
}
