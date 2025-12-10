"use client";

import { useState, useEffect, useRef } from "react";
import {
  Send,
  Loader2,
  Undo2,
  Sparkles,
  Sun,
  Palette,
  Image as ImageIcon,
  Layers,
  Move,
} from "lucide-react";
import {
  chatApi,
  ChatSession,
  ChatMessage,
  RefinementSuggestion,
} from "@/lib/api";

interface ChatInterfaceProps {
  mockupId: string;
  initialImageUrl: string;
  onImageUpdate?: (imageUrl: string) => void;
}

const CATEGORY_ICONS: Record<string, typeof Sun> = {
  lighting: Sun,
  color: Palette,
  background: ImageIcon,
  surface: Layers,
  style: Sparkles,
  add_element: Sparkles,
  position: Move,
};

export default function ChatInterface({
  mockupId,
  initialImageUrl,
  onImageUpdate,
}: ChatInterfaceProps) {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [suggestions, setSuggestions] = useState<RefinementSuggestion[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize session
  useEffect(() => {
    async function init() {
      try {
        const [sessionRes, suggestionsRes] = await Promise.all([
          chatApi.createSession(mockupId),
          chatApi.getSuggestions(),
        ]);
        setSession(sessionRes);
        setSuggestions(suggestionsRes.suggestions);
      } catch (err) {
        console.error("Failed to initialize chat:", err);
      } finally {
        setIsInitializing(false);
      }
    }
    init();
  }, [mockupId]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [session?.messages]);

  // Notify parent of image updates
  useEffect(() => {
    if (session?.current_image_url && onImageUpdate) {
      onImageUpdate(session.current_image_url);
    }
  }, [session?.current_image_url, onImageUpdate]);

  const handleSend = async (message: string) => {
    if (!session || !message.trim() || isLoading) return;

    setInputValue("");
    setIsLoading(true);

    // Optimistically add user message
    const tempUserMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: message,
      image_url: null,
      refinement_type: null,
      created_at: new Date().toISOString(),
    };

    setSession((prev) =>
      prev
        ? { ...prev, messages: [...prev.messages, tempUserMessage] }
        : prev
    );

    try {
      const response = await chatApi.sendMessage(session.id, message);

      // Update session with real response
      setSession((prev) => {
        if (!prev) return prev;
        // Remove temp message and add real ones
        const messages = prev.messages.filter((m) => !m.id.startsWith("temp-"));
        return {
          ...prev,
          messages: [...messages, tempUserMessage, response],
          current_image_url: response.image_url || prev.current_image_url,
        };
      });
    } catch (err) {
      console.error("Failed to send message:", err);
      // Remove optimistic message on error
      setSession((prev) =>
        prev
          ? {
              ...prev,
              messages: prev.messages.filter((m) => !m.id.startsWith("temp-")),
            }
          : prev
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleUndo = async () => {
    if (!session || isLoading) return;

    setIsLoading(true);
    try {
      const response = await chatApi.undo(session.id);
      setSession((prev) =>
        prev
          ? {
              ...prev,
              messages: [...prev.messages, response],
              current_image_url: response.image_url || prev.current_image_url,
            }
          : prev
      );
    } catch (err) {
      console.error("Undo failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: RefinementSuggestion) => {
    handleSend(suggestion.prompt);
  };

  if (isInitializing) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    );
  }

  if (!session) {
    return (
      <div className="text-center text-gray-500 py-8">
        Failed to start chat session
      </div>
    );
  }

  // Group suggestions by category
  const suggestionsByCategory = suggestions.reduce((acc, s) => {
    if (!acc[s.category]) acc[s.category] = [];
    acc[s.category].push(s);
    return acc;
  }, {} as Record<string, RefinementSuggestion[]>);

  return (
    <div className="flex flex-col h-full bg-white rounded-xl border overflow-hidden">
      {/* Current Image */}
      <div className="p-4 border-b bg-gray-50">
        <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden flex items-center justify-center">
          <img
            src={session.current_image_url}
            alt="Current mockup"
            className="max-w-full max-h-full object-contain"
          />
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[200px] max-h-[300px]">
        {session.messages
          .filter((m) => m.role !== "system")
          .map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
        {isLoading && (
          <div className="flex items-center gap-2 text-gray-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">Processing your request...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Suggestions */}
      <div className="p-3 border-t bg-gray-50">
        <p className="text-xs text-gray-500 mb-2">Quick refinements:</p>
        <div className="flex flex-wrap gap-2">
          {Object.entries(suggestionsByCategory)
            .slice(0, 3)
            .map(([category, items]) => {
              const Icon = CATEGORY_ICONS[category] || Sparkles;
              return items.slice(0, 2).map((suggestion) => (
                <button
                  key={suggestion.label}
                  onClick={() => handleSuggestionClick(suggestion)}
                  disabled={isLoading}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-white border rounded-full text-sm hover:bg-gray-100 disabled:opacity-50 transition"
                >
                  <Icon className="w-3.5 h-3.5" />
                  {suggestion.label}
                </button>
              ));
            })}
        </div>
      </div>

      {/* Input Area */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <button
            onClick={handleUndo}
            disabled={isLoading || session.messages.length < 3}
            className="p-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 transition"
            title="Undo last change"
          >
            <Undo2 className="w-5 h-5" />
          </button>
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend(inputValue);
                }
              }}
              placeholder="Describe how to refine your mockup..."
              disabled={isLoading}
              className="w-full px-4 py-2 border rounded-lg pr-12 focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-50"
            />
            <button
              onClick={() => handleSend(inputValue)}
              disabled={!inputValue.trim() || isLoading}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 bg-primary text-white rounded-lg disabled:opacity-50 hover:opacity-90 transition"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser ? "bg-primary text-white" : "bg-gray-100 text-gray-900"
        }`}
      >
        {!isUser && (
          <div className="flex items-center gap-1 text-xs text-gray-500 mb-1">
            <Sparkles className="w-3 h-3" />
            AI Assistant
          </div>
        )}
        <p className="text-sm">{message.content}</p>
      </div>
    </div>
  );
}
