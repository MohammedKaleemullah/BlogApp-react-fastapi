import React, { useState } from "react";
import { Bot, Send, X, Loader2 } from "lucide-react";

const LLM_API_BASE = "http://127.0.0.1:8005";

export default function AssistantChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi 👋! I'm your blog assistant. How can I help?" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage = { role: "user", content: input };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    
    const currentInput = input;
    setInput("");

    try {
      const response = await fetch(`${LLM_API_BASE}/query`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({ 
          query: currentInput,
          top_k: 3
        }),
      });

      if (!response.ok) {
        let errorMessage = "API request failed";
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();

      setMessages(prev => [
        ...prev,
        { 
          role: "assistant", 
          content: data.answer,
          processingTime: data.processing_time
        }
      ]);

    } catch (error) {
      console.error("RAG Query Error:", error);
      
      // Show different error messages based on error type
      let errorMessage = "❌ Something went wrong. Please try again.";
      
      if (error.message.includes("Failed to fetch")) {
        errorMessage = "❌ Cannot connect to server. Make sure your FastAPI server is running on port 8005.";
      } else if (error.message.includes("503")) {
        errorMessage = "❌ Services not initialized. Please wait for the server to fully start up.";
      } else if (error.message) {
        errorMessage = `❌ Error: ${error.message}`;
      }
      
      setMessages(prev => [
        ...prev,
        { role: "assistant", content: errorMessage }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 
             px-5 py-3 rounded-2xl shadow-2xl
             bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500
             text-white font-medium flex items-center gap-2
             transition-all duration-300 ease-in-out
             hover:scale-110 hover:shadow-[0_0_25px_rgba(100,108,255,0.6)]
             z-50"
        >
          <span className="absolute inset-0 bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 opacity-40 blur-2xl animate-pulse"></span>

          <Bot size={22} className="relative z-10 animate-bounce" />
          <span className="relative z-10 hidden sm:block">Ask Assistant</span>
        </button>
      )}

      {isOpen && (
        <div className="fixed bottom-6 right-6 w-80 h-96 
                        bg-white/90 backdrop-blur-xl rounded-2xl 
                        shadow-2xl border border-gray-200 
                        flex flex-col text-gray-800 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-3 border-b bg-gradient-to-r from-indigo-500 to-purple-500 text-white">
            <div className="flex items-center gap-2">
              <Bot size={22} className="relative z-10 animate-bounce" />
              <h2 className="font-semibold">RAG Assistant</h2>
              {loading && <Loader2 size={16} className="animate-spin" />}
            </div>
            <button onClick={() => setIsOpen(false)}>
              <X className="text-white hover:text-gray-200" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 bg-gray-50">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`p-2 rounded-lg text-sm max-w-[75%] ${
                  msg.role === "user"
                    ? "ml-auto bg-indigo-100 text-gray-800"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                {msg.content}
                {msg.processingTime && (
                  <div className="text-xs text-gray-500 mt-1">
                    ⏱️ {msg.processingTime}s
                  </div>
                )}
              </div>
            ))}
            
            {/* Loading indicator */}
            {loading && (
              <div className="bg-gray-200 text-gray-800 p-2 rounded-lg text-sm max-w-[75%]">
                <div className="flex items-center gap-2">
                  <Loader2 size={14} className="animate-spin" />
                  <span>Searching through blogs...</span>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="flex items-center gap-2 p-3 border-t bg-white">
            <input
              className="flex-1 border rounded-lg px-3 py-2 text-sm 
                         focus:outline-none focus:ring-2 focus:ring-indigo-500 
                         text-gray-800 disabled:bg-gray-100 disabled:cursor-not-allowed"
              placeholder={loading ? "Processing..." : "Ask me about blogs..."}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !loading && handleSend()}
              disabled={loading}
            />
            <button
              onClick={handleSend}
              className={`p-3 rounded-xl transition ${
                loading
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-indigo-500 hover:bg-indigo-600"
              } text-white`}
              disabled={loading || !input.trim()}
            >
              {loading ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Send size={18} />
              )}
            </button>
          </div>
        </div>
      )}
    </>
  );
}
