import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { signup } from "../store/slices/authSlice";

export default function Signup({ switchToLogin }) {
  const dispatch = useDispatch();
  const { loading, error } = useSelector((s) => s.auth);

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [localError, setLocalError] = useState(null);

  const handleChange = (e) =>
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const validate = () => {
    if (!form.username || !form.email || !form.password || !form.confirmPassword) {
      return "All fields are required.";
    }
    if (form.password !== form.confirmPassword) {
      return "Passwords do not match.";
    }
    if (!/\S+@\S+\.\S+/.test(form.email)) {
      return "Invalid email format.";
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError(null);

    const validationError = validate();
    if (validationError) {
      setLocalError(validationError);
      return;
    }

    try {
      await dispatch(
        signup({
          username: form.username,
          email: form.email,
          password: form.password,
        })
      ).unwrap();

      alert("Signup successful! Please login.");
      switchToLogin();
      setForm({ username: "", email: "", password: "", confirmPassword: "" });
    } catch (err) {
      setLocalError(err?.detail || err.message || "Signup failed.");
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow">
      <h2 className="text-2xl font-semibold mb-4">Sign Up</h2>

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
          <label className="block text-sm font-medium mb-1">Email</label>
          <input
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded"
            placeholder="your email"
            autoComplete="email"
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
            autoComplete="new-password"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Confirm Password</label>
          <input
            name="confirmPassword"
            type="password"
            value={form.confirmPassword}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded"
            placeholder="confirm password"
            autoComplete="new-password"
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
            {loading ? "Signing up..." : "Sign Up"}
          </button>
        </div>
      </form>

      <div className="mt-4 text-center">
        Already have an account?
        <button
          onClick={() => {
            setLocalError(null);
            switchToLogin();
          }}
          className="text-indigo-600 underline"
          type="button"
        >
          Login
        </button>
      </div>
    </div>
  );
}
