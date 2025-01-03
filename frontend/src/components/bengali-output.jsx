"use client"

import { useState } from "react"
import { Skeleton } from "@/components/ui/skeleton"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Loader2, FileDown, Wand2 } from "lucide-react"
import { api } from "@/lib/api"
import { toast } from "sonner"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

const BENGALI_FONTS = [
  { id: "Kalpurush", name: "Kalpurush" },
  { id: "Mitra", name: "Mitra" },
  { id: "Nikosh", name: "Nikosh" },
  { id: "Muktinarrow", name: "Muktinarrow" }
]

export function BengaliOutput({ 
  bengaliText, 
  title, 
  caption, 
  isLoading,
  onGenerateTitleCaption,
  isGeneratingTitleCaption,
  isPublic = true,
  onTogglePublic
}) {
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false)
  const [selectedFont, setSelectedFont] = useState("Kalpurush")

  const handleGeneratePDF = async () => {
    if (!bengaliText || !title) return

    setIsGeneratingPDF(true)
    try {
      const result = await api.generateCustomPDF({
        content: bengaliText,
        title: title,
        caption: caption,
        isPublic: isPublic,
        fontName: selectedFont
      })

      if (result.success) {
        toast.success("PDF generated successfully", {
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
      toast.error("Failed to generate PDF", {
        description: error.message
      })
    } finally {
      setIsGeneratingPDF(false)
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </CardHeader>
        <Separator className="mb-4" />
        <CardContent>
          <Skeleton className="h-[200px] w-full" />
        </CardContent>
      </Card>
    )
  }

  if (!bengaliText) {
    return (
      <Card className="border-dashed">
        <CardContent className="flex items-center justify-center min-h-[300px]">
          <p className="text-muted-foreground">
            Converted text will appear here
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        {title ? (
          <>
            <CardTitle className="text-xl font-semibold tracking-tight text-primary">
              {title}
            </CardTitle>
            {caption && (
              <CardDescription>
                <Badge variant="secondary" className="font-normal">
                  {caption}
                </Badge>
              </CardDescription>
            )}
          </>
        ) : bengaliText && (
          <Button
            variant="outline"
            onClick={onGenerateTitleCaption}
            disabled={isGeneratingTitleCaption}
          >
            {isGeneratingTitleCaption ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Wand2 className="h-4 w-4 mr-2" />
                Generate Title & Caption
              </>
            )}
          </Button>
        )}
      </CardHeader>
      <Separator />
      <CardContent className="pt-6">
        <ScrollArea className="h-[350px] w-full rounded-md">
          <div className="pr-4">
            <div className="font-bengali text-lg leading-relaxed">
              {bengaliText}
            </div>
          </div>
        </ScrollArea>
      </CardContent>
      {bengaliText && title && (
        <CardFooter className="flex flex-col space-y-4">
          <div className="flex justify-between w-full">
            <div className="flex items-center space-x-2">
              <Switch
                id="public"
                checked={isPublic}
                onCheckedChange={onTogglePublic}
              />
              <Label htmlFor="public">Make Public</Label>
            </div>
            <div className="flex items-center space-x-2">
              <Label htmlFor="font">Font:</Label>
              <Select value={selectedFont} onValueChange={setSelectedFont}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Select font" />
                </SelectTrigger>
                <SelectContent>
                  {BENGALI_FONTS.map(font => (
                    <SelectItem key={font.id} value={font.id}>
                      {font.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="flex justify-end w-full">
            <Button
              onClick={handleGeneratePDF}
              disabled={isGeneratingPDF}
            >
              {isGeneratingPDF ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <FileDown className="h-4 w-4 mr-2" />
              )}
              Generate PDF
            </Button>
          </div>
        </CardFooter>
      )}
    </Card>
  )
} 