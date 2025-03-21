/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#14B8A6", // Teal for medical vibe
        secondary: "#F9FAFB", // Soft white background
        accent: "#5EEAD4", // Light teal for hover/active
        text: "#374151", // Dark gray text
        error: "#EF4444", // Red for errors
        bgLight: "#FFFFFF", // Pure white for contrast
      },
      fontFamily: { inter: ["Inter", "Arial", "sans-serif"] },
      boxShadow: {
        soft: "0 4px 6px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.1)",
      },
    },
  },
  plugins: [],
};
