'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2 } from "lucide-react"
import { api } from "@/lib/api"
import { toast } from "sonner"
import { BengaliOutput } from "@/components/bengali-output"

export default function BanglishConverter() {
  const [inputText, setInputText] = useState('')
  const [bengaliText, setBengaliText] = useState('')
  const [title, setTitle] = useState('')
  const [caption, setCaption] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isGeneratingTitleCaption, setIsGeneratingTitleCaption] = useState(false)
  const [isPublic, setIsPublic] = useState(true)

  const handleConvert = async () => {
    if (!inputText.trim()) return

    setIsLoading(true)
    try {
      const convertResponse = await api.convertToBengali(inputText)
      setBengaliText(convertResponse.bengali_text)
      setTitle('')
      setCaption('')
      toast.success("Text converted successfully")
    } catch (error) {
      toast.error("Conversion failed", {
        description: error.message
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerateTitleCaption = async () => {
    if (!bengaliText) return

    setIsGeneratingTitleCaption(true)
    try {
      const response = await api.generateTitleCaption(bengaliText)
      setTitle(response.title)
      setCaption(response.caption)
      toast.success("Title and caption generated")
    } catch (error) {
      toast.error("Failed to generate title and caption", {
        description: error.message
      })
    } finally {
      setIsGeneratingTitleCaption(false)
    }
  }

  const handleClear = () => {
    setInputText('')
    setBengaliText('')
    setTitle('')
    setCaption('')
  }

  return (
    <div className="container mx-auto p-4 pt-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Input Card */}
        <Card>
          <CardHeader>
            <CardTitle>Banglish Text</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col space-y-4">
              <Textarea
                placeholder="Type your Banglish text here..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                className="min-h-[300px] font-mono"
              />
              <div className="flex space-x-2">
                <Button
                  onClick={handleConvert}
                  disabled={isLoading || !inputText.trim()}
                  className="flex-1"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Converting...
                    </>
                  ) : (
                    "Convert to Bengali"
                  )}
                </Button>
                <Button
                  variant="outline"
                  onClick={handleClear}
                  disabled={isLoading || (!inputText && !bengaliText)}
                >
                  Clear
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Output Card */}
        <BengaliOutput
          bengaliText={bengaliText}
          title={title}
          caption={caption}
          isLoading={isLoading}
          onGenerateTitleCaption={handleGenerateTitleCaption}
          isGeneratingTitleCaption={isGeneratingTitleCaption}
          isPublic={isPublic}
          onTogglePublic={(value) => setIsPublic(value)}
        />
      </div>
    </div>
  )
} 