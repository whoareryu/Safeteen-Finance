"use client";

import { useState } from "react";
import { Send, Sparkles } from "lucide-react";

export default function ChatInput() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    setIsLoading(true);
    setResponse("");

    // Simulated response - in production, connect to an actual LLM API
    setTimeout(() => {
      setResponse(
        `Thank you for your question about "${message}". I'm Whoareryu's AI assistant. Currently studying at IBM x RedHat AI Academy, I'm learning to build powerful AI agents. Connect with me to learn more about my projects and AI journey!`
      );
      setIsLoading(false);
    }, 1500);
  };

  const suggestions = [
    "What AI projects have you built?",
    "Tell me about your AI Academy experience",
    "What technologies do you work with?",
  ];

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="relative">
        <div className="absolute -inset-1 bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-500 rounded-2xl blur opacity-30" />
        <div className="relative bg-card border border-border rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-primary" />
            <span className="text-sm font-medium text-muted-foreground">
              Ask me anything
            </span>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your question here..."
                rows={3}
                className="w-full px-4 py-3 bg-input border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all resize-none"
              />
            </div>

            <div className="flex flex-wrap gap-2 mb-4">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => setMessage(suggestion)}
                  className="px-3 py-1.5 text-xs font-medium bg-secondary text-secondary-foreground rounded-full hover:bg-secondary/80 transition-colors border border-border"
                >
                  {suggestion}
                </button>
              ))}
            </div>

            <button
              type="submit"
              disabled={isLoading || !message.trim()}
              className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-500 text-white font-medium rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Thinking...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Send Message
                </>
              )}
            </button>
          </form>

          {response && (
            <div className="mt-6 p-4 bg-secondary/50 border border-border rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-6 h-6 rounded-full bg-gradient-to-r from-purple-500 to-cyan-500 flex items-center justify-center">
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
                <span className="text-sm font-medium text-primary">
                  Whoareryu AI
                </span>
              </div>
              <p className="text-foreground/90 text-sm leading-relaxed">
                {response}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
