// import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// import { useState, useEffect } from "react";
// import Home from "./pages/Home";
// import BlogDetail from "./pages/BlogDetail";
// import Navbar from "./components/Navbar";

// function App() {
//   const [blogs, setBlogs] = useState([]);

//   useEffect(() => {
//     const storedBlogs = JSON.parse(localStorage.getItem("blogs") || "[]");
//     setBlogs(storedBlogs);
//   }, []);

//   const handleBlogAdded = (newBlog) => {
//     setBlogs((prev) => {
//       const updated = [newBlog, ...prev];
//       localStorage.setItem("blogs", JSON.stringify(updated));
//       return updated;
//     });
//   };

//   return (
//     <Router>
//       <div className="min-h-screen flex flex-col">
//         <Navbar onBlogAdded={handleBlogAdded} />
//         <div className="container mx-auto px-4 py-6 flex-grow">
//           <Routes>
//             <Route path="/" element={<Home blogs={blogs} />} />
//             <Route path="/post/:id" element={<BlogDetail blogs={blogs} />} />
//           </Routes>
//         </div>
//       </div>
//     </Router>
//   );
// }

// export default App;


// import React from 'react'
// import { Routes, Route } from 'react-router-dom'
// import Home from './pages/Home'
// import Login from './pages/Login'
// import CreatePost from './pages/CreatePost'
// import PostDetail from './pages/PostDetail'
// import Profile from './pages/Profile'
// import Navbar from './components/Navbar'


// import LoginPage from "./pages/Login"
// import HomePage from "./pages/Home"

// import ProtectedRoute from "./components/ProtectedRoute";

import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Login from './pages/Login'
import CreatePost from './pages/CreatePost'
import PostDetail from './pages/PostDetail'
import Profile from './pages/Profile'
import Navbar from './components/Navbar'
import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="container mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/create" element={<CreatePost />} />
          <Route path="/post/:id" element={<PostDetail />} />
          <Route path="/profile" element={<Profile />} />

          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/post/:id" element={<PostDetail />} />
          <Route path="/create" element={
            <ProtectedRoute>
              <CreatePost />
            </ProtectedRoute>
          } />
          <Route path="/profile" element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } />
        </Routes>
      </main>
    </div>
  )
}
