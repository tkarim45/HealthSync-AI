import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import NavBar from "../components/layout/NavBar"; // Adjust path if needed
import { FaHeart, FaCheckCircle, FaTimesCircle } from "react-icons/fa"; // Icons for footer and features

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

const PricingPage = () => {
  const cardVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
    hover: { scale: 1.05, transition: { duration: 0.3 } },
  };

  const pricingPlans = [
    {
      name: "Free",
      price: "$0",
      period: "month",
      description: "Perfect for trying out HealthSync AI.",
      features: [
        { text: "Basic Health Insights", available: true },
        { text: "Chatbot Access (Limited)", available: true },
        { text: "Community Support", available: true },
        { text: "Advanced Analytics", available: false },
        { text: "Priority Support", available: false },
      ],
      buttonText: "Get Started",
      buttonLink: "/signup",
      highlighted: false,
    },
    {
      name: "Pro",
      price: "$9.99",
      period: "month",
      description: "Ideal for individuals seeking deeper health insights.",
      features: [
        { text: "Advanced Health Insights", available: true },
        { text: "Unlimited Chatbot Access", available: true },
        { text: "Email Support", available: true },
        { text: "Basic Analytics", available: true },
        { text: "Custom Integrations", available: false },
      ],
      buttonText: "Sign Up Now",
      buttonLink: "/signup",
      highlighted: true,
    },
    {
      name: "Premium",
      price: "$19.99",
      period: "month",
      description: "For power users and professionals.",
      features: [
        { text: "Comprehensive Health Insights", available: true },
        { text: "Unlimited Chatbot Access", available: true },
        { text: "Priority Phone & Email Support", available: true },
        { text: "Advanced Analytics", available: true },
        { text: "Custom Integrations", available: true },
      ],
      buttonText: "Get Premium",
      buttonLink: "/signup",
      highlighted: false,
    },
  ];

  return (
    <div className="flex flex-col min-h-screen bg-gray-100">
      {/* Navbar */}
      <NavBar />

      {/* Pricing Section */}
      <section className="flex-1 py-16 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <motion.h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4" initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            Choose Your <span className="text-teal-500">HealthSync AI</span> Plan
          </motion.h1>
          <motion.p className="text-lg text-gray-600 mb-12" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.6, delay: 0.2 }}>
            Flexible pricing to suit your health journey—start free or go premium.
          </motion.p>

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <motion.div key={plan.name} className={`bg-white rounded-xl shadow-lg p-6 flex flex-col ${plan.highlighted ? "border-2 border-teal-500 scale-105" : "border border-gray-200"}`} variants={cardVariants} initial="hidden" animate="visible" whileHover="hover" transition={{ delay: index * 0.1 }}>
                <h2 className="text-2xl font-semibold text-gray-800 mb-2">{plan.name}</h2>
                <div className="flex items-baseline mb-4">
                  <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                  <span className="text-gray-600 ml-1">/{plan.period}</span>
                </div>
                <p className="text-gray-600 mb-6">{plan.description}</p>
                <ul className="flex-1 space-y-3 mb-6">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-center">
                      {feature.available ? <FaCheckCircle className="text-teal-500 mr-2" /> : <FaTimesCircle className="text-gray-400 mr-2" />}
                      <span className={feature.available ? "text-gray-700" : "text-gray-500"}>{feature.text}</span>
                    </li>
                  ))}
                </ul>
                <Link to={plan.buttonLink}>
                  <motion.button className={`w-full py-3 rounded-lg font-semibold text-white ${plan.highlighted ? "bg-teal-500 hover:bg-teal-600" : "bg-gray-600 hover:bg-gray-700"}`} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    {plan.buttonText}
                  </motion.button>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default PricingPage;
