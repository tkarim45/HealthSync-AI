import React, { useState } from "react";
import Chatbot from "react-chatbot-kit";
import "react-chatbot-kit/build/main.css"; // Base styles (overridden below)
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";

// Chatbot configuration
const config = {
  botName: "HealthSync Assistant",
  initialMessages: [{ id: 1, message: "Hi! How can I assist you with your health today?", type: "bot" }],
  customStyles: {
    botMessageBox: { backgroundColor: "#2dd4bf" }, // Teal bot messages
    chatButton: { backgroundColor: "#2dd4bf" }, // Teal send button
    userMessageBox: { backgroundColor: "#e5e7eb" }, // Light gray user messages
  },
};

// Message parser for handling user input
const MessageParser = ({ children, actions }) => {
  const parse = async (message) => {
    try {
      const response = await axios.post("http://localhost:8000/chatbot", { query: message });
      actions.handleMessage(response.data.response);
    } catch (error) {
      actions.handleMessage("Sorry, I couldn’t process that. Try again!");
    }
  };
  return <div>{React.cloneElement(children, { parse })}</div>;
};

// Action provider for bot responses
const ActionProvider = ({ createChatBotMessage, setState, children }) => {
  const handleMessage = (message) => {
    const botMessage = createChatBotMessage(message);
    setState((prev) => ({ ...prev, messages: [...prev.messages, botMessage] }));
  };
  return <div>{React.cloneElement(children, { actions: { handleMessage } })}</div>;
};

function ChatbotComponent() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleChatbot = () => {
    setIsOpen(!isOpen);
  };

  // Animation variants
  const chatContainerVariants = {
    hidden: { opacity: 0, y: 50, scale: 0.9 },
    visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.3, ease: "easeOut" } },
    exit: { opacity: 0, y: 50, scale: 0.9, transition: { duration: 0.2 } },
  };

  const buttonVariants = {
    hover: { scale: 1.1, rotate: 5 },
    tap: { scale: 0.95 },
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Floating Chat Button */}
      <motion.button onClick={toggleChatbot} className="w-14 h-14 bg-teal-500 text-white rounded-full flex items-center justify-center shadow-lg" variants={buttonVariants} whileHover="hover" whileTap="tap" initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ duration: 0.4, ease: "easeOut" }}>
        <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16h6m-7 4h8a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </motion.button>

      {/* Chatbot Container */}
      <AnimatePresence>
        {isOpen && (
          <motion.div className="absolute bottom-20 right-0 w-[360px] h-[500px] bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden flex flex-col" variants={chatContainerVariants} initial="hidden" animate="visible" exit="exit">
            {/* Header */}
            <div className="bg-teal-500 text-white p-4 flex justify-between items-center shrink-0">
              <motion.h3 className="text-lg font-semibold tracking-tight" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1, duration: 0.3 }}>
                HealthSync Assistant
              </motion.h3>
              <motion.button onClick={toggleChatbot} className="text-white hover:text-gray-200 focus:outline-none" whileHover={{ scale: 1.2, rotate: 90 }} transition={{ duration: 0.2 }}>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </motion.button>
            </div>

            {/* Chatbot Content */}
            <div className="flex-1 flex flex-col bg-gray-50 overflow-hidden">
              <Chatbot
                config={config}
                messageParser={MessageParser}
                actionProvider={ActionProvider}
                placeholderText="Ask about your health..."
                headerText={null} // Remove default header
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Custom CSS */}
      <style jsx>{`
        .react-chatbot-kit-chat-container {
          width: 100%;
          height: 100%;
          border: none;
          background: transparent;
          border-radius: 0 0 12px 12px;
          display: flex;
          flex-direction: column;
          height: 435px;
        }
        .react-chatbot-kit-chat-inner-container {
          width: 100%;
          height: 100%;
          background: #f9fafb; /* Light gray background */
          border: none;
          border-radius: 0 0 12px 12px;
          display: flex;
          flex-direction: column;
        }
        .react-chatbot-kit-chat-message-container {
          padding: 12px;
          background: transparent;
          flex: 1 1 auto; /* Grow and shrink as needed */
          max-height: calc(100% - 70px); /* Leave space for input container */
          overflow-y: auto; /* Enable vertical scrolling */
          scrollbar-width: thin;
          scrollbar-color: #d1d5db #f9fafb;
        }
        .react-chatbot-kit-chat-bot-message {
          background: #2dd4bf; /* Teal bot messages */
          color: white;
          border-radius: 16px 16px 16px 4px;
          margin: 8px 0;
          padding: 10px 14px;
          max-width: 80%;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          animation: slideInLeft 0.3s ease-out;
        }
        .react-chatbot-kit-user-chat-message {
          background: #e5e7eb; /* Light gray user messages */
          color: #1f2937;
          border-radius: 16px 16px 4px 16px;
          margin: 8px 0;
          padding: 10px 14px;
          max-width: 80%;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          animation: slideInRight 0.3s ease-out;
        }
        .react-chatbot-kit-chat-input-container {
          padding: 12px;
          background: white;
          border-top: 1px solid #e5e7eb;
          flex: 0 0 auto; /* Fixed height, no shrinking */
        }
        .react-chatbot-kit-chat-input-form {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .react-chatbot-kit-chat-input {
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 10px 14px;
          font-size: 14px;
          width: 100%;
          background: white;
          transition: all 0.2s ease;
          /* Reverted margin-bottom */
          margin-bottom: 0; /* Keep it minimal to avoid overflow */
        }
        .react-chatbot-kit-chat-input:focus {
          outline: none;
          border-color: #2dd4bf;
          box-shadow: 0 0 0 3px rgba(45, 212, 191, 0.2);
        }
        .react-chatbot-kit-chat-btn-send {
          background: #2dd4bf;
          border-radius: 8px;
          padding: 8px 12px;
          transition: background 0.2s ease;
          /* Reverted margin-bottom */
          margin-bottom: 0; /* Keep it minimal to avoid overflow */
        }
        .react-chatbot-kit-chat-btn-send:hover {
          background: #26a69a; /* Slightly darker teal */
        }
        @keyframes slideInLeft {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  );
}

export default ChatbotComponent;
