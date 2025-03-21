import React, { useState } from "react";
import { useAuth } from "../context/AuthContext"; // Adjust path if needed
import { motion } from "framer-motion";
import NavBar from "../components/layout/NavBar"; // Adjust path if needed
import { FaHeart } from "react-icons/fa";

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

const ProfilePage = () => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState({
    username: user?.username || "",
    email: user?.email || "",
  });
  const [error, setError] = useState("");

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfile((prev) => ({ ...prev, [name]: value }));
  };

  const handleSaveProfile = () => {
    // Mock save logic (replace with API call later)
    if (!profile.username || !profile.email) {
      setError("All fields are required.");
      return;
    }
    setError("");
    setIsEditing(false);
    console.log("Profile updated:", profile);
    // TODO: Add API call to update user profile in backend
  };

  const contentVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-100">
      {/* Navbar */}
      <NavBar />

      {/* Profile Content */}
      <main className="flex-1 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.h1 className="text-3xl font-bold text-gray-800 mb-6" initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            Your Profile, <span className="text-teal-500">{user?.username || "User"}</span>
          </motion.h1>

          <motion.div className="bg-white rounded-xl shadow-lg p-6 max-w-md mx-auto" variants={contentVariants} initial="hidden" animate="visible">
            {isEditing ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-700 text-sm font-semibold mb-2" htmlFor="username">
                    Username
                  </label>
                  <input type="text" id="username" name="username" value={profile.username} onChange={handleProfileChange} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="Your username" />
                </div>
                <div>
                  <label className="block text-gray-700 text-sm font-semibold mb-2" htmlFor="email">
                    Email
                  </label>
                  <input type="email" id="email" name="email" value={profile.email} onChange={handleProfileChange} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="Your email" />
                </div>
                {error && <p className="text-red-500 text-sm">{error}</p>}
                <div className="flex space-x-4">
                  <motion.button className="px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600" onClick={handleSaveProfile} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    Save
                  </motion.button>
                  <motion.button className="px-4 py-2 bg-gray-400 text-white rounded-lg hover:bg-gray-500" onClick={() => setIsEditing(false)} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    Cancel
                  </motion.button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-gray-600">
                  <strong>Username:</strong> {profile.username}
                </p>
                <p className="text-gray-600">
                  <strong>Email:</strong> {profile.email}
                </p>
                <motion.button className="px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600" onClick={() => setIsEditing(true)} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  Edit Profile
                </motion.button>
              </div>
            )}
          </motion.div>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default ProfilePage;
