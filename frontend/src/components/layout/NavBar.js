import { useState } from "react";
import { NavLink } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../../context/AuthContext";
import { FaHome, FaInfoCircle, FaBlog, FaSignInAlt, FaSignOutAlt, FaDollarSign, FaHeartbeat, FaUser } from "react-icons/fa";

const NavBar = () => {
  const { user, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const menuVariants = {
    hidden: { opacity: 0, y: -20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.3, ease: "easeInOut" } },
    exit: { opacity: 0, y: -20, transition: { duration: 0.2 } },
  };

  const dropdownVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: { opacity: 1, scale: 1, transition: { duration: 0.2 } },
    exit: { opacity: 0, scale: 0.95, transition: { duration: 0.15 } },
  };

  // Determine dashboard path based on user role
  const dashboardPath = user ? `/dashboard/${user.role}` : "/dashboard/user";

  return (
    <nav className="bg-gradient-to-r from-secondary to-bgLight p-4 shadow-soft sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        {/* Logo */}
        <NavLink to="/" className="text-primary text-2xl font-bold tracking-tight flex items-center space-x-2">
          <FaHeartbeat className="text-primary" />
          <motion.span initial={{ scale: 0.9 }} animate={{ scale: 1 }} transition={{ duration: 0.5, ease: "easeOut" }}>
            HealthSync AI
          </motion.span>
        </NavLink>

        {/* Hamburger Menu */}
        <button className="md:hidden text-text hover:text-accent focus:outline-none" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} aria-label="Toggle menu">
          <motion.svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" animate={{ rotate: isMobileMenuOpen ? 90 : 0 }} transition={{ duration: 0.3 }}>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={isMobileMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
          </motion.svg>
        </button>

        {/* Desktop Navigation */}
        <ul className="hidden md:flex space-x-8 items-center">
          <li>
            <NavLink to="/" className={({ isActive }) => `${isActive ? "text-accent" : "text-text"} hover:text-accent transition-colors duration-300 flex items-center space-x-2`}>
              <FaHome />
              <motion.span whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
                Home
              </motion.span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/about" className={({ isActive }) => `${isActive ? "text-accent" : "text-text"} hover:text-accent transition-colors duration-300 flex items-center space-x-2`}>
              <FaInfoCircle />
              <motion.span whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
                About Us
              </motion.span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/blog" className={({ isActive }) => `${isActive ? "text-accent" : "text-text"} hover:text-accent transition-colors duration-300 flex items-center space-x-2`}>
              <FaBlog />
              <motion.span whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
                Blog
              </motion.span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/pricing" className={({ isActive }) => `${isActive ? "text-accent" : "text-text"} hover:text-accent transition-colors duration-300 flex items-center space-x-2`}>
              <FaDollarSign />
              <motion.span whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
                Pricing
              </motion.span>
            </NavLink>
          </li>
          {user && (
            <li>
              <NavLink to={dashboardPath} className={({ isActive }) => `${isActive ? "text-accent" : "text-text"} hover:text-accent transition-colors duration-300 flex items-center space-x-2`}>
                <FaUser />
                <motion.span whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
                  Dashboard
                </motion.span>
              </NavLink>
            </li>
          )}
          {user ? (
            <li className="relative">
              <motion.button className="text-text hover:text-accent transition-colors duration-300 flex items-center space-x-2" onClick={() => setIsDropdownOpen(!isDropdownOpen)} whileHover={{ scale: 1.1 }}>
                <FaUser />
                <span>Account</span>
                <motion.svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" animate={{ rotate: isDropdownOpen ? 180 : 0 }} transition={{ duration: 0.3 }}>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                </motion.svg>
              </motion.button>

              <AnimatePresence>
                {isDropdownOpen && (
                  <motion.ul className="absolute right-0 mt-2 w-40 bg-bgLight rounded-lg shadow-soft py-2 text-text" initial="hidden" animate="visible" exit="exit" variants={dropdownVariants}>
                    <li>
                      <button
                        onClick={() => {
                          logout();
                          setIsDropdownOpen(false);
                        }}
                        className="block w-full text-left px-4 py-2 hover:bg-secondary hover:text-accent transition-colors flex items-center space-x-2"
                      >
                        <FaSignOutAlt />
                        <span>Logout</span>
                      </button>
                    </li>
                  </motion.ul>
                )}
              </AnimatePresence>
            </li>
          ) : (
            <li>
              <NavLink to="/login" className={({ isActive }) => `${isActive ? "text-accent" : "text-text"} hover:text-accent transition-colors duration-300 flex items-center space-x-2`}>
                <FaSignInAlt />
                <motion.span whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }}>
                  Login
                </motion.span>
              </NavLink>
            </li>
          )}
        </ul>
      </div>

      {/* Mobile Navigation */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div className="md:hidden bg-bgLight text-text mt-4 rounded-lg shadow-soft" initial="hidden" animate="visible" exit="exit" variants={menuVariants}>
            <ul className="flex flex-col space-y-4 p-4">
              <li>
                <NavLink to="/" className={({ isActive }) => `${isActive ? "text-accent" : "text-text"} hover:text-accent transition-colors duration-300 flex items-center space-x-2`} onClick={() => setIsMobileMenuOpen(false)}>
                  <FaHome />
                  <span>Home</span>
                </NavLink>
              </li>
              <li>
                <NavLink to="/about" className={({ isActive }) => `${isActive ? "text-accent" : "text-text"} hover:text-accent transition-colors duration-300 flex items-center space-x-2`} onClick={() => setIsMobileMenuOpen(false)}>
                  <FaInfoCircle />
                  <span>About Us</span>
                </NavLink>
              </li>
              <li>
                <NavLink to="/blog" className={({ isActive }) => `${isActive ? "text-accent" : "text-text"} hover:text-accent transition-colors duration-300 flex items-center space-x-2`} onClick={() => setIsMobileMenuOpen(false)}>
                  <FaBlog />
                  <span>Blog</span>
                </NavLink>
              </li>
              <li>
                <NavLink to="/pricing" className={({ isActive }) => `${isActive ? "text-accent" : "text-text"} hover:text-accent transition-colors duration-300 flex items-center space-x-2`} onClick={() => setIsMobileMenuOpen(false)}>
                  <FaDollarSign />
                  <span>Pricing</span>
                </NavLink>
              </li>
              {user && (
                <li>
                  <NavLink to={dashboardPath} className={({ isActive }) => `${isActive ? "text-accent" : "text-text"} hover:text-accent transition-colors duration-300 flex items-center space-x-2`} onClick={() => setIsMobileMenuOpen(false)}>
                    <FaUser />
                    <span>Dashboard</span>
                  </NavLink>
                </li>
              )}
              {user ? (
                <li>
                  <button
                    onClick={() => {
                      logout();
                      setIsMobileMenuOpen(false);
                    }}
                    className="text-text hover:text-accent transition-colors duration-300 flex items-center space-x-2"
                  >
                    <FaSignOutAlt />
                    <span>Logout</span>
                  </button>
                </li>
              ) : (
                <li>
                  <NavLink to="/login" className={({ isActive }) => `${isActive ? "text-accent" : "text-text"} hover:text-accent transition-colors duration-300 flex items-center space-x-2`} onClick={() => setIsMobileMenuOpen(false)}>
                    <FaSignInAlt />
                    <span>Login</span>
                  </NavLink>
                </li>
              )}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default NavBar;
