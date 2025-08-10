import React, { useState } from "react";
import Login from "../components/Login";
import Signup from "../components/Signup";

export default function LoginPage() {
  const [mode, setMode] = useState("login");

  return (
    <>
      {mode === "login" ? (
        <Login switchToSignup={() => setMode("signup")} />
      ) : (
        <Signup switchToLogin={() => setMode("login")} />
      )}
    </>
  );
}
