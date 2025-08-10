import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { login } from "../store/slices/authSlice";
import { useNavigate } from "react-router-dom";

export default function Login({ switchToSignup }) {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error } = useSelector((s) => s.auth);

  const [form, setForm] = useState({ username: "", password: "" });
  const [localError, setLocalError] = useState(null);

  const handleChange = (e) =>
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError(null);
    if (!form.username || !form.password) return;

    try {
      await dispatch(login(form)).unwrap();
      navigate("/", { replace: true });
    } catch (err) {
      setLocalError(err?.detail || err.message || "Login failed.");
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow">
      <h2 className="text-2xl font-semibold mb-4">Login</h2>

      {(localError || error) && (
        <div className="mb-4 text-sm text-red-700 bg-red-100 p-2 rounded">
          {localError || (typeof error === "string" ? error : error?.detail || error?.message)}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <div>
          <label className="block text-sm font-medium mb-1">Username</label>
          <input
            name="username"
            value={form.username}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded"
            placeholder="your username"
            autoComplete="username"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Password</label>
          <input
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded"
            placeholder="password"
            autoComplete="current-password"
            required
          />
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className={`px-4 py-2 rounded text-white ${
              loading ? "bg-gray-400" : "bg-indigo-600 hover:bg-indigo-700"
            }`}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </div>
      </form>

      <div className="mt-4 text-center">
        Don't have an account?
        <button
          onClick={() => {
            setLocalError(null);
            switchToSignup();
          }}
          className="text-indigo-600 underline bg-white"
          type="button"
        >
        Sign Up
        </button>
      </div>
    </div>
  );
}
