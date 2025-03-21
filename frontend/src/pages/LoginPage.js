import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import NavBar from "../components/layout/NavBar"; // Adjust path if needed
import { FaHeart } from "react-icons/fa"; // For footer icon

// Footer Component
const Footer = () => {
  const footerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
  };

  return (
    <motion.footer className="bg-gray-50 py-6 border-t border-gray-200" initial="hidden" animate="visible" variants={footerVariants}>
      <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center text-gray-600">
        <p className="text-sm">© {new Date().getFullYear()} HealthSync AI. All rights reserved.</p>
        <div className="flex items-center space-x-2 mt-2 md:mt-0">
          <span className="text-sm">Made with</span>
          <motion.span className="text-teal-500" animate={{ scale: [1, 1.2, 1] }} transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}>
            <FaHeart />
          </motion.span>
          <span className="text-sm">by the HealthSync Team</span>
        </div>
      </div>
    </motion.footer>
  );
};

const LoginPage = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login, loading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await login({ username, password });
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    }
  };

  const formVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } },
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-100">
      {/* Navbar */}
      <NavBar />

      {/* Login Form */}
      <div className="flex-1 flex items-center justify-center py-12">
        <motion.div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full" initial="hidden" animate="visible" variants={formVariants}>
          <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">
            Login to <span className="text-teal-500">HealthSync AI</span>
          </h1>
          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-semibold mb-2" htmlFor="username">
                Username
              </label>
              <input type="text" id="username" value={username} onChange={(e) => setUsername(e.target.value)} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., johndoe" required disabled={loading} />
            </div>
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-semibold mb-2" htmlFor="password">
                Password
              </label>
              <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="••••••••" required disabled={loading} />
            </div>
            {error && (
              <motion.p className="text-red-500 text-sm mb-4 text-center" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                {error}
              </motion.p>
            )}
            <motion.button type="submit" className="w-full p-3 bg-teal-500 text-white rounded-lg font-semibold hover:bg-teal-600 disabled:bg-gray-400" whileHover={!loading ? { scale: 1.05 } : {}} whileTap={!loading ? { scale: 0.95 } : {}} disabled={loading}>
              {loading ? "Logging in..." : "Login"}
            </motion.button>
          </form>
          <p className="text-gray-700 text-sm text-center mt-4">
            Don’t have an account?{" "}
            <Link to="/signup" className="text-teal-500 hover:text-teal-700">
              Sign Up
            </Link>
          </p>
        </motion.div>
      </div>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default LoginPage;
