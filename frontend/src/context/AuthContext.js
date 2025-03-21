import { createContext, useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(JSON.parse(localStorage.getItem("user")) || null);
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    localStorage.setItem("user", JSON.stringify(user));
    localStorage.setItem("token", token);
  }, [user, token]);

  const login = async ({ username, password }) => {
    setLoading(true);
    try {
      console.log("Fetching login from: http://localhost:8000/api/auth/login");
      const response = await fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const text = await response.text();
      console.log("Login response status:", response.status);
      console.log("Login raw response:", text);
      const data = JSON.parse(text);
      if (!response.ok) throw new Error(data.detail || "Login failed");
      setUser(data.user);
      setToken(data.token);
    } catch (err) {
      console.error("Login error:", err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const signup = async ({ username, email, password }) => {
    setLoading(true);
    try {
      console.log("Fetching signup from: http://localhost:8000/api/auth/signup");
      const response = await fetch("http://localhost:8000/api/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });
      const text = await response.text();
      console.log("Signup response status:", response.status);
      console.log("Signup raw response:", text);
      const data = JSON.parse(text);
      if (!response.ok) throw new Error(data.detail || "Signup failed");
      setUser(data.user);
      setToken(data.token);
    } catch (err) {
      console.error("Signup error:", err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    navigate("/");
  };

  return <AuthContext.Provider value={{ user, token, login, signup, logout, loading }}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
