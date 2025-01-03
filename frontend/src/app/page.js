'use client'

import { useState, useRef } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ChatMessage } from "@/components/chat-message"
import { FileUpload } from "@/components/file-upload"
import { api } from "@/lib/api"
import { Mic, MicOff, Loader2, ChevronDown } from "lucide-react"
import { toast } from "sonner"

export default function Home() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const mediaRecorder = useRef(null)
  const audioChunks = useRef([])
  const [showScrollButton, setShowScrollButton] = useState(false)
  const chatContainerRef = useRef(null)

  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target
    const isNotAtBottom = scrollHeight - scrollTop - clientHeight > 100
    setShowScrollButton(isNotAtBottom)
  }

  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const newMessage = { text: inputMessage, isBot: false }
    setMessages(prev => [...prev, newMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await api.sendMessage(inputMessage)
      if (response.success) {
        setMessages(prev => [...prev, { text: response.data.text, isBot: true }])
      }
    } catch (error) {
      toast.error("Failed to send message", {
        description: error.message
      })
      // Remove the failed message
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setIsLoading(false)
    }
  }

  const startRecording = async () => {
    try {
      // Check for browser support
      if (!MediaRecorder.isTypeSupported('audio/webm;codecs=opus') && 
          !MediaRecorder.isTypeSupported('audio/webm')) {
        throw new Error("Your browser doesn't support the required audio formats. Please use a modern browser.")
      }

      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true
        }
      })
      
      // Use the first supported MIME type
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
        ? 'audio/webm;codecs=opus'
        : 'audio/webm'
      
      mediaRecorder.current = new MediaRecorder(stream, {
        mimeType,
        audioBitsPerSecond: 16000
      })
      
      audioChunks.current = []

      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data)
        }
      }

      mediaRecorder.current.onstop = async () => {
        try {
          // Create blob from chunks
          const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' })
          
          setIsLoading(true)
          const response = await api.sendVoice(audioBlob)
          
          if (response) {
            setMessages(prev => [
              ...prev,
              { text: "Voice message sent", isBot: false, transcription: response.transcription },
              { text: response.text, isBot: true }
            ])
          }
        } catch (error) {
          console.error('Voice processing error:', error)
          toast.error("Failed to process voice", {
            description: error.message
          })
        } finally {
          setIsLoading(false)
        }
      }

      mediaRecorder.current.start(1000) // Collect data every second
      setIsRecording(true)
      toast.success("Recording started", {
        description: "Speak clearly into your microphone"
      })
    } catch (error) {
      console.error('Recording error:', error)
      toast.error("Microphone Access Failed", {
        description: error.message || "Please check your microphone permissions and try again."
      })
    }
  }

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop()
      setIsRecording(false)
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop())
      toast.info("Recording stopped", {
        description: "Processing your audio..."
      })
    }
  }

  const handleFileUpload = async (file) => {
    try {
      toast.loading("Processing file...", { id: "fileUploadLoading" });
      const response = await api.uploadFile(file);
      
      if (response.success) {
        setMessages(prev => [
          ...prev,
          { text: `File processed: ${file.name}`, isBot: false },
          { text: response.data.text, isBot: true }
        ]);
        toast.success("File processed successfully", { id: "fileUploadSuccess" });
      } else if (response.error) {
        toast.error("Failed to process file", {
          id: "fileUploadError",
          description: response.error || "An unexpected error occurred"
        });
      }
    } catch (error) {
      toast.error("Failed to process file", {
        id: "fileUploadError",
        description: error.message || "An unexpected error occurred"
      });
      // Reset any upload state or progress
      setMessages(prev => [
        ...prev,
        { text: `Error processing file: ${file.name}`, isBot: false }
      ]);
    }
  }

  const handleGenerateStory = async (prompt) => {
    if (!prompt.trim()) return

    setIsLoading(true)
    try {
      const result = await api.generateStory(prompt)
      
      if (result.success) {
        setInputMessage('')
        toast.success("Story generated successfully", {
          description: "Click the download button to get your PDF",
          action: {
            label: "Download",
            onClick: async () => {
              try {
                const blob = await api.downloadPdf(result.data.file_id)
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = result.data.title + '.pdf'
                document.body.appendChild(a)
                a.click()
                document.body.removeChild(a)
                URL.revokeObjectURL(url)
              } catch (error) {
                toast.error("Failed to download PDF", {
                  description: error.message
                })
              }
            }
          }
        })
      }
    } catch (error) {
      toast.error("Failed to generate story", {
        description: error.message
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-4 pt-6">
      <div className="max-w-4xl mx-auto">
        <Tabs defaultValue="chat" className="w-full">
          <div className="sticky top-14 z-40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 pb-2">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="chat">Chat</TabsTrigger>
              <TabsTrigger value="voice">Voice</TabsTrigger>
              <TabsTrigger value="pdf">PDF Generation</TabsTrigger>
              <TabsTrigger value="files">Files</TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="chat">
            <Card className="border-t-0">
              <CardHeader>
                <CardTitle>Chat</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col space-y-4">
                  <div 
                    ref={chatContainerRef}
                    onScroll={handleScroll}
                    className="flex-1 min-h-[400px] bg-secondary/20 rounded-lg p-4 space-y-4 overflow-y-auto"
                  >
                    {messages.map((msg, index) => (
                      <ChatMessage
                        key={index}
                        message={msg.text}
                        transcription={msg.transcription}
                        isBot={msg.isBot}
                      />
                    ))}
                    {isLoading && (
                      <div className="flex justify-center">
                        <Loader2 className="h-6 w-6 animate-spin" />
                      </div>
                    )}
                  </div>
                  {showScrollButton && (
                    <button
                      onClick={scrollToBottom}
                      className="fixed bottom-24 right-8 bg-primary text-primary-foreground p-2 rounded-full shadow-lg hover:bg-primary/90 transition-colors"
                    >
                      <ChevronDown className="h-5 w-5" />
                    </button>
                  )}
                  <div className="sticky bottom-0 bg-background pt-2">
                    <div className="flex space-x-2">
                      <Input
                        placeholder="Type your message..."
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                        className="flex-1"
                        disabled={isLoading}
                      />
                      <Button
                        onClick={handleSendMessage}
                        disabled={isLoading || !inputMessage.trim()}
                      >
                        {isLoading ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          "Send"
                        )}
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="voice">
            <Card className="border-t-0">
              <CardHeader>
                <CardTitle>Voice Chat</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col space-y-4">
                  <div 
                    ref={chatContainerRef}
                    onScroll={handleScroll}
                    className="flex-1 min-h-[400px] bg-secondary/20 rounded-lg p-4 space-y-4 overflow-y-auto"
                  >
                    {messages.map((msg, index) => (
                      <ChatMessage
                        key={index}
                        message={msg.text}
                        transcription={msg.transcription}
                        isBot={msg.isBot}
                      />
                    ))}
                    {isLoading && (
                      <div className="flex justify-center">
                        <Loader2 className="h-6 w-6 animate-spin" />
                      </div>
                    )}
                  </div>
                  {showScrollButton && (
                    <button
                      onClick={scrollToBottom}
                      className="fixed bottom-24 right-8 bg-primary text-primary-foreground p-2 rounded-full shadow-lg hover:bg-primary/90 transition-colors"
                    >
                      <ChevronDown className="h-5 w-5" />
                    </button>
                  )}
                  <div className="sticky bottom-0 bg-background pt-2">
                    <div className="flex justify-center space-x-4">
                      <Button
                        variant={isRecording ? "destructive" : "outline"}
                        onClick={isRecording ? stopRecording : startRecording}
                        disabled={isLoading}
                      >
                        {isRecording ? (
                          <>
                            <MicOff className="h-4 w-4 mr-2" />
                            Stop Recording
                          </>
                        ) : (
                          <>
                            <Mic className="h-4 w-4 mr-2" />
                            Start Recording
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="files">
            <Card className="border-t-0">
              <CardHeader>
                <CardTitle>File Upload</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col space-y-4">
                  <div 
                    ref={chatContainerRef}
                    onScroll={handleScroll}
                    className="flex-1 min-h-[400px] bg-secondary/20 rounded-lg p-4 space-y-4 overflow-y-auto"
                  >
                    {messages.map((msg, index) => (
                      <ChatMessage
                        key={index}
                        message={msg.text}
                        isBot={msg.isBot}
                      />
                    ))}
                    {isLoading && (
                      <div className="flex justify-center">
                        <Loader2 className="h-6 w-6 animate-spin" />
                      </div>
                    )}
                  </div>
                  {showScrollButton && (
                    <button
                      onClick={scrollToBottom}
                      className="fixed bottom-24 right-8 bg-primary text-primary-foreground p-2 rounded-full shadow-lg hover:bg-primary/90 transition-colors"
                    >
                      <ChevronDown className="h-5 w-5" />
                    </button>
                  )}
                  <div className="sticky bottom-0 bg-background pt-2">
                    <FileUpload onUpload={handleFileUpload} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="pdf">
            <Card className="border-t-0">
              <CardHeader>
                <CardTitle>Story Generation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col space-y-4">
                  <div className="sticky bottom-0 bg-background pt-2">
                    <Input
                      placeholder="Enter your story prompt..."
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      disabled={isLoading}
                    />
                    <Button
                      className="w-full mt-2"
                      onClick={() => handleGenerateStory(inputMessage)}
                      disabled={isLoading || !inputMessage.trim()}
                    >
                      {isLoading ? (
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      ) : null}
                      Generate Story
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
} 