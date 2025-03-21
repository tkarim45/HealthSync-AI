import { motion } from "framer-motion";
import { FaTwitter, FaFacebookF, FaLinkedinIn, FaEnvelope, FaPhone, FaHome, FaInfoCircle, FaBlog } from "react-icons/fa";

const Footer = () => {
  const sectionVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i) => ({
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, delay: i * 0.2, ease: "easeOut" },
    }),
  };

  return (
    <footer className="bg-gradient-to-r from-secondary to-bgLight text-text py-12">
      <div className="max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* Company Info */}
        <motion.div custom={0} initial="hidden" animate="visible" variants={sectionVariants}>
          <h3 className="text-primary text-xl font-bold tracking-tight mb-4">HealthSync AI</h3>
          <p className="text-sm leading-relaxed">Pioneering AI-driven healthcare solutions to empower patients and professionals alike.</p>
          <p className="text-sm mt-2">© 2025 HealthSync AI. All rights reserved.</p>
        </motion.div>

        {/* Quick Links */}
        <motion.div custom={1} initial="hidden" animate="visible" variants={sectionVariants}>
          <h3 className="text-primary text-lg font-semibold mb-4">Quick Links</h3>
          <ul className="space-y-2">
            <li>
              <a href="/" className="text-text hover:text-accent transition-colors duration-300 text-sm flex items-center space-x-2">
                <FaHome />
                <span>Home</span>
              </a>
            </li>
            <li>
              <a href="/about" className="text-text hover:text-accent transition-colors duration-300 text-sm flex items-center space-x-2">
                <FaInfoCircle />
                <span>About Us</span>
              </a>
            </li>
            <li>
              <a href="/blog" className="text-text hover:text-accent transition-colors duration-300 text-sm flex items-center space-x-2">
                <FaBlog />
                <span>Blog</span>
              </a>
            </li>
            <li>
              <a href="/privacy" className="text-text hover:text-accent transition-colors duration-300 text-sm flex items-center space-x-2">
                <span>Privacy Policy</span>
              </a>
            </li>
          </ul>
        </motion.div>

        {/* Contact Info */}
        <motion.div custom={2} initial="hidden" animate="visible" variants={sectionVariants}>
          <h3 className="text-primary text-lg font-semibold mb-4">Contact Us</h3>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center space-x-2">
              <FaEnvelope className="text-accent" />
              <span>support@healthsync.ai</span>
            </li>
            <li className="flex items-center space-x-2">
              <FaPhone className="text-accent" />
              <span>+1 (800) 555-1234</span>
            </li>
            <li>
              <span>123 AI Health Lane, Tech City, TC 45678</span>
            </li>
          </ul>
        </motion.div>

        {/* Social Media */}
        <motion.div custom={3} initial="hidden" animate="visible" variants={sectionVariants}>
          <h3 className="text-primary text-lg font-semibold mb-4">Follow Us</h3>
          <div className="flex space-x-4">
            <motion.a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="text-text hover:text-accent transition-colors duration-300" whileHover={{ scale: 1.2, rotate: 5 }} transition={{ duration: 0.2 }}>
              <FaTwitter size={20} />
            </motion.a>
            <motion.a href="https://facebook.com" target="_blank" rel="noopener noreferrer" className="text-text hover:text-accent transition-colors duration-300" whileHover={{ scale: 1.2, rotate: 5 }} transition={{ duration: 0.2 }}>
              <FaFacebookF size={20} />
            </motion.a>
            <motion.a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="text-text hover:text-accent transition-colors duration-300" whileHover={{ scale: 1.2, rotate: 5 }} transition={{ duration: 0.2 }}>
              <FaLinkedinIn size={20} />
            </motion.a>
          </div>
        </motion.div>
      </div>

      {/* Bottom Bar */}
      <motion.div className="mt-8 border-t border-gray-300 pt-4 text-center text-sm" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5, delay: 0.8 }}>
        <p>
          Designed with <span className="text-accent">♥</span> by the HealthSync Team
        </p>
      </motion.div>
    </footer>
  );
};

export default Footer;
