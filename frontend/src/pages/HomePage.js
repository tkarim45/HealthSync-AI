import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import NavBar from "../components/layout/NavBar";
import Footer from "../components/layout/Footer";
import { FaBrain, FaHeartbeat, FaRobot } from "react-icons/fa";

const HomePage = () => {
  // Animation variants
  const heroVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } },
  };

  const cardVariants = {
    hidden: { opacity: 0, scale: 0.9 },
    visible: (i) => ({
      opacity: 1,
      scale: 1,
      transition: { duration: 0.5, delay: i * 0.2, ease: "easeOut" },
    }),
  };

  const testimonialVariants = {
    hidden: { opacity: 0, x: -50 },
    visible: { opacity: 1, x: 0, transition: { duration: 0.6, ease: "easeOut" } },
  };

  return (
    <div className="min-h-screen flex flex-col bg-secondary">
      <NavBar />

      {/* Hero Section */}
      <main className="flex-grow">
        <motion.section className="py-20 px-6 text-center bg-gradient-to-b from-secondary to-bgLight" initial="hidden" animate="visible" variants={heroVariants}>
          <h1 className="text-5xl md:text-6xl font-bold text-text mb-6">
            Welcome to <span className="text-primary">HealthSync AI</span>
          </h1>
          <p className="text-lg md:text-xl text-text max-w-3xl mx-auto mb-8">Your AI-powered companion for smarter healthcare—connecting patients, providers, and insights seamlessly.</p>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="inline-block">
            <Link to="/login" className="bg-primary text-white px-8 py-3 rounded-full font-semibold text-lg hover:bg-accent transition-colors duration-300">
              Get Started
            </Link>
          </motion.div>
        </motion.section>

        {/* Features Section */}
        <section className="py-16 px-6 bg-bgLight">
          <h2 className="text-3xl font-semibold text-text text-center mb-12">Why HealthSync AI?</h2>
          <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
            <motion.div custom={0} initial="hidden" animate="visible" variants={cardVariants} className="bg-secondary p-6 rounded-lg shadow-soft hover:shadow-md transition-shadow duration-300">
              <FaBrain className="text-primary text-4xl mb-4 mx-auto" />
              <h3 className="text-xl font-semibold text-text mb-2">AI-Driven Insights</h3>
              <p className="text-sm text-text">Leverage advanced AI to analyze health data and provide personalized recommendations.</p>
            </motion.div>
            <motion.div custom={1} initial="hidden" animate="visible" variants={cardVariants} className="bg-secondary p-6 rounded-lg shadow-soft hover:shadow-md transition-shadow duration-300">
              <FaHeartbeat className="text-primary text-4xl mb-4 mx-auto" />
              <h3 className="text-xl font-semibold text-text mb-2">Real-Time Monitoring</h3>
              <p className="text-sm text-text">Stay connected with real-time health updates and alerts for proactive care.</p>
            </motion.div>
            <motion.div custom={2} initial="hidden" animate="visible" variants={cardVariants} className="bg-secondary p-6 rounded-lg shadow-soft hover:shadow-md transition-shadow duration-300">
              <FaRobot className="text-primary text-4xl mb-4 mx-auto" />
              <h3 className="text-xl font-semibold text-text mb-2">Seamless Integration</h3>
              <p className="text-sm text-text">Integrate with wearable devices and medical records for a unified health experience.</p>
            </motion.div>
          </div>
        </section>

        {/* Testimonial Section */}
        <section className="py-16 px-6 bg-secondary">
          <h2 className="text-3xl font-semibold text-text text-center mb-12">What Our Users Say</h2>
          <div className="max-w-4xl mx-auto">
            <motion.div initial="hidden" animate="visible" variants={testimonialVariants} className="bg-bgLight p-6 rounded-lg shadow-soft">
              <p className="text-text italic mb-4">"HealthSync AI has transformed how I manage my patients’ care—it’s intuitive and incredibly insightful."</p>
              <p className="text-sm text-primary font-semibold">Dr. Emily Carter, MD</p>
            </motion.div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default HomePage;
