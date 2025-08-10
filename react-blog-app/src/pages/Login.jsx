// // import { LoginForm } from "../components/LoginForm";

// export default function Login() {
//   return (
//     <div className="flex min-h-screen items-center justify-center">
//       {/* <LoginForm /> */}
//     </div>
//   );
// }



import React, { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { login } from "../store/slices/authSlice";
import { useNavigate, useLocation } from "react-router-dom";

export default function Login() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { token, loading, error } = useSelector((s) => s.auth);

  const [form, setForm] = useState({ username: "", password: "" });

  // redirect if already logged in
  useEffect(() => {
    if (token) {
      const from = location.state?.from?.pathname || "/";
      navigate(from, { replace: true });
    }
  }, [token, navigate, location]);

  const handleChange = (e) =>
    setForm((p) => ({ ...p, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.username || !form.password) return;
    try {
      // unwrap will throw on rejection so you can catch here (optional)
      await dispatch(login({ username: form.username, password: form.password })).unwrap();
      // navigate is handled by useEffect, but we can also redirect explicitly
      navigate("/", { replace: true });
    } catch (err) {
      // error stored in slice — nothing extra needed here
      console.error("Login failed:", err);
    }
  };

  const errorMsg =
    error?.detail || (typeof error === "string" ? error : error?.message) || null;

  return (
    <div className="max-w-md mx-auto mt-12 bg-white p-6 rounded-lg shadow">
      <h1 className="text-2xl font-semibold mb-4">Login</h1>

      {errorMsg && (
        <div className="mb-4 text-sm text-red-700 bg-red-100 p-2 rounded">{errorMsg}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Username</label>
          <input
            name="username"
            value={form.username}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded"
            placeholder="your username"
            autoComplete="username"
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
          />
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading || !form.username || !form.password}
            className={`px-4 py-2 rounded text-white ${
              loading || !form.username || !form.password ? "bg-gray-400" : "bg-indigo-600 hover:bg-indigo-700"
            }`}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </div>
      </form>
    </div>
  );
}

