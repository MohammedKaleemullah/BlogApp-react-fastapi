// import React, { useState } from "react";
// import { Dialog, DialogTrigger } from "@/components/ui/dialog";
// import { Button } from "@/components/ui/button";
// import BlogModal from "./BlogModal";
// import logo from "../assets/Logo.webp";


// export default function Navbar({ onBlogAdded }) {
//   const [open, setOpen] = useState(false);

//   return (
//     <div className="flex justify-between items-center p-4 border-b bg-gray-300 text-gray-800">
//       <div className="flex items-center">
//           <img src={logo} className="h-12 w-12 mr-2" alt="Logo" />
//           <div className="text-xl font-bold">React Blog</div>
//         </div>

//       <Dialog open={open} onOpenChange={setOpen}>
//         <DialogTrigger asChild>
//           <Button>+ Add Blog</Button>
//         </DialogTrigger>

//         <BlogModal
//           onBlogAdded={onBlogAdded}
//           onClose={() => setOpen(false)}
//         />
//       </Dialog>
//     </div>
//   );
// }

import React from 'react'
import { Link } from 'react-router-dom'
import { useSelector } from 'react-redux'

export default function Navbar(){
  const token = useSelector(state => state.auth.token)

  return (
    <nav className="bg-white shadow">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-600 rounded flex items-center justify-center text-white font-bold">B</div>
          <Link to="/" className="text-lg font-semibold">BlogApp</Link>
        </div>

        <div className="flex-1 mx-4">
          <input
            disabled={!token}
            placeholder={token ? "Search by tags or title..." : "Login to enable search"}
            className="w-full max-w-xl px-3 py-2 border rounded disabled:opacity-60"
          />
        </div>

        <div className="flex items-center gap-3">
          <button title="Language" className="p-2 rounded hover:bg-gray-100">🌐</button>
          {token ? (
            <>
              <Link to="/create" className="px-3 py-2 bg-indigo-600 text-white rounded">Create</Link>
              <Link to="/profile" className="px-3 py-2 border rounded">Profile</Link>
            </>
          ) : (
            <Link to="/login" className="px-3 py-2 bg-indigo-600 text-white rounded">Login / Get started</Link>
          )}
        </div>
      </div>
    </nav>
  )
}
