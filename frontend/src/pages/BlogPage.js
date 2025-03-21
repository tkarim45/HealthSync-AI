import { motion } from "framer-motion";
import NavBar from "../components/layout/NavBar";
import Footer from "../components/layout/Footer";
import { FaSearch, FaTag } from "react-icons/fa";

const BlogPage = () => {
  // Animation variants
  const heroVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } },
  };

  const postVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i) => ({
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, delay: i * 0.2, ease: "easeOut" },
    }),
  };

  const sidebarVariants = {
    hidden: { opacity: 0, x: 50 },
    visible: { opacity: 1, x: 0, transition: { duration: 0.6, ease: "easeOut" } },
  };

  // Dummy blog posts
  const blogPosts = [
    {
      title: "AI in Healthcare: Revolutionizing Patient Care",
      excerpt: "Discover how artificial intelligence is enhancing diagnostics, personalizing treatments, and improving patient outcomes in modern medicine.",
      date: "March 15, 2025",
    },
    {
      title: "The Future of Wearable Health Tech with AI",
      excerpt: "Explore how HealthSync AI integrates with wearable devices to provide real-time health insights and proactive care solutions.",
      date: "March 10, 2025",
    },
    {
      title: "Ethical Considerations in AI-Driven Medicine",
      excerpt: "A deep dive into the ethical challenges and responsibilities of deploying AI in healthcare settings.",
      date: "March 5, 2025",
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-secondary">
      <NavBar />

      {/* Hero Section */}
      <main className="flex-grow">
        <motion.section className="py-20 px-6 text-center bg-gradient-to-b from-secondary to-bgLight" initial="hidden" animate="visible" variants={heroVariants}>
          <h1 className="text-5xl md:text-6xl font-bold text-text mb-6">
            <span className="text-primary">HealthSync AI</span> Blog
          </h1>
          <p className="text-lg md:text-xl text-text max-w-3xl mx-auto">Stay informed with the latest insights, updates, and innovations in AI-driven healthcare.</p>
        </motion.section>

        {/* Blog Posts & Sidebar */}
        <section className="py-16 px-6 bg-bgLight">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row gap-8">
            {/* Blog Posts */}
            <div className="md:w-2/3">
              {blogPosts.map((post, index) => (
                <motion.article key={index} custom={index} initial="hidden" animate="visible" variants={postVariants} className="bg-bgLight p-6 rounded-lg shadow-soft hover:shadow-md transition-shadow duration-300 mb-8">
                  <h2 className="text-xl font-semibold text-text mb-2">{post.title}</h2>
                  <p className="text-sm text-gray-500 mb-4">{post.date}</p>
                  <p className="text-text mb-4">{post.excerpt}</p>
                  <motion.a href="#" className="text-primary hover:text-accent transition-colors duration-300 font-semibold" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    Read More
                  </motion.a>
                </motion.article>
              ))}
            </div>

            {/* Sidebar */}
            <motion.aside className="md:w-1/3" initial="hidden" animate="visible" variants={sidebarVariants}>
              {/* Search Bar */}
              <div className="bg-secondary p-6 rounded-lg shadow-soft mb-8">
                <h3 className="text-lg font-semibold text-text mb-4">Search Posts</h3>
                <div className="relative">
                  <input type="text" placeholder="Search..." className="w-full p-3 pl-10 rounded-full border border-gray-300 focus:outline-none focus:border-primary text-text" />
                  <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                </div>
              </div>

              {/* Categories */}
              <div className="bg-secondary p-6 rounded-lg shadow-soft">
                <h3 className="text-lg font-semibold text-text mb-4">Categories</h3>
                <ul className="space-y-2">
                  <li>
                    <a href="#" className="text-text hover:text-accent transition-colors duration-300 flex items-center space-x-2">
                      <FaTag className="text-primary" />
                      <span>AI Technology</span>
                    </a>
                  </li>
                  <li>
                    <a href="#" className="text-text hover:text-accent transition-colors duration-300 flex items-center space-x-2">
                      <FaTag className="text-primary" />
                      <span>Healthcare Innovation</span>
                    </a>
                  </li>
                  <li>
                    <a href="#" className="text-text hover:text-accent transition-colors duration-300 flex items-center space-x-2">
                      <FaTag className="text-primary" />
                      <span>Wearable Tech</span>
                    </a>
                  </li>
                  <li>
                    <a href="#" className="text-text hover:text-accent transition-colors duration-300 flex items-center space-x-2">
                      <FaTag className="text-primary" />
                      <span>Ethics in AI</span>
                    </a>
                  </li>
                </ul>
              </div>
            </motion.aside>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default BlogPage;
