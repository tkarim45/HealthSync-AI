import { motion } from "framer-motion";
import NavBar from "../components/layout/NavBar";
import Footer from "../components/layout/Footer";
import { FaUserMd, FaCode, FaFlask } from "react-icons/fa";

const AboutPage = () => {
  // Animation variants
  const heroVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } },
  };

  const sectionVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i) => ({
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, delay: i * 0.2, ease: "easeOut" },
    }),
  };

  const cardVariants = {
    hidden: { opacity: 0, scale: 0.9 },
    visible: (i) => ({
      opacity: 1,
      scale: 1,
      transition: { duration: 0.5, delay: i * 0.2, ease: "easeOut" },
    }),
  };

  return (
    <div className="min-h-screen flex flex-col bg-secondary">
      <NavBar />

      {/* Hero Section */}
      <main className="flex-grow">
        <motion.section className="py-20 px-6 text-center bg-gradient-to-b from-secondary to-bgLight" initial="hidden" animate="visible" variants={heroVariants}>
          <h1 className="text-5xl md:text-6xl font-bold text-text mb-6">
            About <span className="text-primary">HealthSync AI</span>
          </h1>
          <p className="text-lg md:text-xl text-text max-w-3xl mx-auto">We’re a team dedicated to revolutionizing healthcare through artificial intelligence, making it more accessible, efficient, and patient-centered.</p>
        </motion.section>

        {/* Our Story Section */}
        <section className="py-16 px-6 bg-bgLight">
          <h2 className="text-3xl font-semibold text-text text-center mb-12">Our Story</h2>
          <div className="max-w-4xl mx-auto text-text">
            <motion.p custom={0} initial="hidden" animate="visible" variants={sectionVariants} className="text-base mb-6">
              HealthSync AI was born in 2023 from a shared vision among healthcare professionals and tech innovators. We saw a gap in how technology could bridge the divide between patients and providers, and we set out to fix it.
            </motion.p>
            <motion.p custom={1} initial="hidden" animate="visible" variants={sectionVariants} className="text-base mb-6">
              Starting with a small prototype, we developed an AI system to analyze patient data and provide actionable insights. Today, HealthSync AI integrates with wearables, medical records, and clinical systems to empower healthcare decisions.
            </motion.p>
            <motion.p custom={2} initial="hidden" animate="visible" variants={sectionVariants} className="text-base">
              Our journey continues as we collaborate with hospitals, clinics, and patients worldwide to refine and expand our platform, driven by a passion for better health outcomes.
            </motion.p>
          </div>
        </section>

        {/* Team Section */}
        <section className="py-16 px-6 bg-secondary">
          <h2 className="text-3xl font-semibold text-text text-center mb-12">Meet Our Team</h2>
          <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
            <motion.div custom={0} initial="hidden" animate="visible" variants={cardVariants} className="bg-bgLight p-6 rounded-lg shadow-soft hover:shadow-md transition-shadow duration-300 text-center">
              <FaUserMd className="text-primary text-4xl mb-4 mx-auto" />
              <h3 className="text-xl font-semibold text-text mb-2">Dr. Sarah Lin</h3>
              <p className="text-sm text-text mb-2">Chief Medical Officer</p>
              <p className="text-sm text-text">A practicing physician with 15 years of experience, Sarah guides our clinical strategy.</p>
            </motion.div>
            <motion.div custom={1} initial="hidden" animate="visible" variants={cardVariants} className="bg-bgLight p-6 rounded-lg shadow-soft hover:shadow-md transition-shadow duration-300 text-center">
              <FaCode className="text-primary text-4xl mb-4 mx-auto" />
              <h3 className="text-xl font-semibold text-text mb-2">James Patel</h3>
              <p className="text-sm text-text mb-2">Lead Developer</p>
              <p className="text-sm text-text">James architects our AI systems, blending code with healthcare innovation.</p>
            </motion.div>
            <motion.div custom={2} initial="hidden" animate="visible" variants={cardVariants} className="bg-bgLight p-6 rounded-lg shadow-soft hover:shadow-md transition-shadow duration-300 text-center">
              <FaFlask className="text-primary text-4xl mb-4 mx-auto" />
              <h3 className="text-xl font-semibold text-text mb-2">Dr. Maria Gomez</h3>
              <p className="text-sm text-text mb-2">AI Research Lead</p>
              <p className="text-sm text-text">Maria’s expertise in machine learning drives our cutting-edge health algorithms.</p>
            </motion.div>
          </div>
        </section>

        {/* Mission & Vision Section */}
        <section className="py-16 px-6 bg-bgLight">
          <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
            <motion.div custom={0} initial="hidden" animate="visible" variants={sectionVariants} className="p-6">
              <h3 className="text-2xl font-semibold text-primary mb-4">Our Mission</h3>
              <p className="text-base text-text">To harness AI to deliver precise, accessible, and compassionate healthcare solutions, improving lives globally.</p>
            </motion.div>
            <motion.div custom={1} initial="hidden" animate="visible" variants={sectionVariants} className="p-6">
              <h3 className="text-2xl font-semibold text-primary mb-4">Our Vision</h3>
              <p className="text-base text-text">A world where technology and healthcare unite seamlessly, empowering every individual with personalized care.</p>
            </motion.div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default AboutPage;
