import React, { useState } from "react";
import { Bot, Send, X } from "lucide-react";

export default function AssistantChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi 👋! I’m your blog assistant. How can I help?" },
  ]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    const newMessage = { role: "user", content: input };
    setMessages([...messages, newMessage]);

    // Mock AI response (later connect to FastAPI RAG backend)
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `🤖 You asked: "${input}"` },
      ]);
    }, 500);

    setInput("");
  };

  return (
    <>
      {/* Floating Assistant Button */}
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
            
          {/* Glow effect */}
          <span className="absolute inset-0 bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 opacity-40 blur-2xl animate-pulse"></span>

          <Bot size={22} className="relative z-10 animate-bounce" />
          <span className="relative z-10 hidden sm:block">Ask Assistant</span>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-80 h-96 
                        bg-white/90 backdrop-blur-xl rounded-2xl 
                        shadow-2xl border border-gray-200 
                        flex flex-col text-gray-800 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-3 border-b bg-gradient-to-r from-indigo-500 to-purple-500 text-white">
            <div className="flex items-center gap-2">
              <Bot size={22} className="relative z-10 animate-bounce" />
              <h2 className="font-semibold">Assistant</h2>
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
              </div>
            ))}
          </div>

          {/* Input */}
          <div className="flex items-center gap-2 p-3 border-t bg-white">
            <input
              className="flex-1 border rounded-lg px-3 py-2 text-sm 
                         focus:outline-none focus:ring-2 focus:ring-indigo-500 
                         text-gray-800"
              placeholder="Ask me about blogs..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
            />
            <button
              onClick={handleSend}
              className="p-3 bg-indigo-500 text-white rounded-xl 
                         hover:bg-indigo-600 transition"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
