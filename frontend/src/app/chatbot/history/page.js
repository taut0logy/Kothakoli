'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatMessage } from "@/components/chat-message";
import { api } from '@/lib/api';
import { toast } from 'sonner';
import { Database } from "lucide-react";

export default function ChatHistory() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      const response = await api.getCachedConversations();
      if (response.status === "success") {
        setConversations(response.conversations);
      }
    } catch (error) {
      console.error('Error fetching conversations:', error);
      toast.error('Failed to load conversations');
    } finally {
      setLoading(false);
    }
  };

  const handleCache = async (conversationId) => {
    try {
      const response = await api.cacheConversation(conversationId);
      if (response.status === "success") {
        toast.success(response.message || 'Conversation cached for training');
        await fetchConversations();
      }
    } catch (error) {
      console.error('Error caching conversation:', error);
      toast.error(error.message || 'Failed to cache conversation');
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container max-w-4xl mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Conversation History</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[70vh]">
            <div className="space-y-8">
              {conversations.map((conversation) => (
                <div key={conversation.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold">
                      {conversation.display_name}
                    </h3>
                    <Button
                      onClick={() => handleCache(conversation.id)}
                      variant="outline"
                      size="sm"
                    >
                      <Database className="h-4 w-4 mr-2" />
                      Cache for Training
                    </Button>
                  </div>
                  <div className="space-y-4">
                    {conversation.messages.map((message, index) => (
                      <ChatMessage
                        key={index}
                        message={message.content}
                        isBot={message.role === 'bot'}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}