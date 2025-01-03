'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, History } from "lucide-react";
import { api } from '../../lib/api';
import { useDebounce } from '@/hooks/use-debounce';
import { ChatMessage } from "@/components/chat-message";
import Link from 'next/link';

export default function ChatBot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  // Use the debounce hook for input value
  const debouncedInput = useDebounce(input, 500);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch suggestions whenever debounced input changes
  useEffect(() => {
    const fetchSuggestions = async () => {
      try {
        if (!debouncedInput.trim()) {
          setSuggestions([]);
          return;
        }
        
        const response = await api.checkBanglishSpelling(debouncedInput);
        console.log('Spell check response:', response);
        
        if (response.status === "success" && Array.isArray(response.suggestions)) {
          const validSuggestions = response.suggestions
            .filter(Boolean)
            .filter((suggestion, index, self) => self.indexOf(suggestion) === index);
          
          setSuggestions(validSuggestions);
        } else {
          setSuggestions([]);
        }
      } catch (error) {
        console.error('Error fetching suggestions:', error);
        setSuggestions([]);
      }
    };

    fetchSuggestions();
  }, [debouncedInput]);

  // Handle input change
  const handleInputChange = (e) => {
    const value = e.target.value;
    setInput(value);
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
    setSuggestions([]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);
    setSuggestions([]); // Clear suggestions when sending

    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await api.sendChatbotMessage(userMessage);
      
      if (response.response) {
        // Add bot response to chat
        setMessages(prev => [...prev, { role: 'bot', content: response.response }]);

        // Show Banglish correction if available
        if (response.banglish_correction) {
          setMessages(prev => [...prev, {
            role: 'system',
            content: `Suggested correction: ${response.banglish_correction}`
          }]);
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Sorry, an error occurred. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Click outside handler
  useEffect(() => {
    function handleClickOutside(event) {
      if (inputRef.current && !inputRef.current.contains(event.target)) {
        setSuggestions([]);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="container max-w-4xl mx-auto p-4">
      <Card className="h-[80vh]">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Banglish Chatbot</CardTitle>
          <Link href="/chatbot/history">
            <Button variant="outline" size="sm">
              <History className="h-4 w-4 mr-2" />
              View History
            </Button>
          </Link>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Messages Container */}
          <ScrollArea className="h-[60vh] pr-4">
            <div className="space-y-4">
              {messages.map((message, index) => (
                <ChatMessage
                  key={index}
                  message={message.content}
                  isBot={message.role === 'bot'}
                />
              ))}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* Input Form with Suggestions */}
          <div ref={inputRef} className="relative flex-1">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <Input
                value={input}
                onChange={handleInputChange}
                placeholder="Type your message..."
                disabled={isLoading}
                className="w-full"
              />
              <Button 
                type="submit" 
                disabled={isLoading}
                size="icon"
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>

            {/* Suggestions Panel */}
            {suggestions.length > 0 && (
              <div className="absolute bottom-full left-0 w-full bg-popover rounded-md shadow-lg mb-1 p-2 space-y-1 z-50">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    className="w-full text-left px-3 py-1.5 rounded hover:bg-accent hover:text-accent-foreground text-sm transition-colors"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
