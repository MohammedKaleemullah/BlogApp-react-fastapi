import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { logout } from "../store/slices/authSlice";

export default function Navbar({ onSearch }) {
  const token = useSelector((s) => s.auth.token);
  const dispatch = useDispatch();
  const [searchQuery, setSearchQuery] = useState("");

  const handleLogout = () => {
    dispatch(logout());
  };

  const handleChange = (e) => {
    setSearchQuery(e.target.value);
    if (onSearch) onSearch(e.target.value);
  };

  return (
    <nav className="bg-gray-50 border-b border-gray-200">
      
      <div className="container mx-auto px-4 py-3 flex flex-col md:flex-row items-center md:justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gray-700 rounded flex items-center justify-center text-white font-semibold text-lg">
            KB
          </div>
          <Link to="/" className="text-lg font-semibold text-gray-800 hover:text-gray-900">
            KaleemBlogs
          </Link>
        </div>

        <div className="flex-1 mx-4">
          <input
            disabled={!token}
            value={searchQuery}
            onChange={handleChange}
            placeholder={token ? "Search by tags or title..." : "Login to enable search"}
            className="w-full max-w-xl px-3 py-2 border border-gray-300 rounded text-gray-700 placeholder-gray-400 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-1 focus:ring-gray-400 focus:border-gray-400"
          />
        </div>

        <div className="flex items-center gap-3">
          {token ? (
            <>
              <Link
                to="/create"
                className="px-3 py-2 bg-gray-800 text-white rounded hover:bg-gray-900 transition"
              >
                Create
              </Link>
              <Link
                to="/profile"
                className="px-3 py-2 bg-gray-800 text-white rounded hover:bg-gray-900 transition"
              >
                Profile
              </Link>
              <button
                onClick={handleLogout}
                className="px-3 py-2 bg-gray-800 text-white rounded hover:bg-gray-900 transition"
              >
                Logout
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="px-3 py-2 bg-gray-800 text-white rounded hover:bg-gray-900 transition"
            >
              Login / Get started
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
