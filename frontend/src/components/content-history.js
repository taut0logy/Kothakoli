"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import {
  DownloadIcon,
  TrashIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  SpeakerLoudIcon,
} from "@radix-ui/react-icons";
import ReactMarkdown from "react-markdown";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import AudioPlayer from "./audio-player";

export default function ContentHistory({ contents, onDelete = () => {} , admin = false}) {
  const [expandedItems, setExpandedItems] = useState({});
  const [audioBlobs, setAudioBlobs] = useState({});
  const [loadingAudio, setLoadingAudio] = useState({});

  const toggleExpand = (id) => {
    setExpandedItems((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const handleDelete = async (contentId) => {
    try {
      await api.deleteContent(contentId);
      if (onDelete) {
        onDelete(contentId);
      }
    } catch (error) {
      console.error("Error deleting content:", error);
    }
  };

  const handleDownload = async (content, format = "txt") => {
    try {
      let blob;
      let filename;
      let contentType;

      if (content.type === "PDF" || content.type === "BENGALI_STORY") {
        // For PDF type, download the actual PDF file
        const query = content.filename || content.file_id;
        const response = await api.downloadPdf(query);
        blob = new Blob([response], { type: "application/pdf" });
        filename = `${content.title}.pdf`;
        contentType = "application/pdf";
      } else {
        // For other types, handle markdown or text download
        if (format === "md") {
          blob = new Blob([content.content], { type: "text/markdown" });
          filename = `${content.title}.md`;
          contentType = "text/markdown";
        } else {
          blob = new Blob([content.content], { type: "text/plain" });
          filename = `${content.title}.txt`;
          contentType = "text/plain";
        }
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error("Error downloading content:", error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getContentPreview = (content) => {
    // Make sure we have a string to work with
    const text = typeof content === "string" ? content : String(content);
    const lines = text.split("\n").filter((line) => line.trim());
    return lines.slice(0, 3).join("\n");
  };

  const handleTextToSpeech = async (content) => {
    try {
      if (audioBlobs[content.id]) {
        return;
      }

      setLoadingAudio((prev) => ({ ...prev, [content.id]: true }));

      let textToConvert;
      if (content.type === "PDF" || content.type === "BENGALI_STORY") {
        textToConvert = content.content;
      } else {
        textToConvert = expandedItems[content.id]
          ? content.content
          : getContentPreview(content.content);
      }

      if (typeof textToConvert !== "string" || !textToConvert.trim()) {
        throw new Error("No text available for conversion");
      }

      textToConvert = textToConvert.trim();
      if (textToConvert.length > 5000) {
        textToConvert = textToConvert.slice(0, 5000) + "...";
      }

      console.log("textToConvert", textToConvert);
      const audioBlob = await api.textToSpeech(textToConvert);

      setAudioBlobs((prev) => ({
        ...prev,
        [content.id]: audioBlob,
      }));
    } catch (error) {
      console.error("Error converting text to speech:", error);
      // You might want to show an error toast here
    } finally {
      setLoadingAudio((prev) => ({ ...prev, [content.id]: false }));
    }
  };

  return (
    <div className="space-y-6">
      {contents.map((content) => (
        <Card key={content.id}>
          <CardHeader className="flex flex-row items-start justify-between space-y-0 flex-wrap">
            <div className="flex flex-col gap-2">
              <CardTitle>{content.title}</CardTitle>
              <CardDescription>{formatDate(content.createdAt)}</CardDescription>
            </div>
            <div className="flex space-x-2">
              {content.type !== "PDF" && content.type !== "BENGALI_STORY" && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDownload(content, "md")}
                  title="Download as Markdown"
                >
                  .md
                </Button>
              )}
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleDownload(content)}
                title={`Download as ${(content.type === "PDF" || content.type === "BENGALI_STORY") ? "PDF" : "Text"}`}
              >
                <DownloadIcon className="h-4 w-4" />
              </Button>
              {!admin && <Button
                variant="ghost"
                size="icon"
                onClick={() => handleDelete(content.id)}
                className="text-red-600 hover:text-red-800 hover:bg-red-100"
                title="Delete"
              >
                <TrashIcon className="h-4 w-4" />
              </Button>}
            </div>
          </CardHeader>

          <CardContent>
            {/* Metadata */}
            <div className="mb-4 grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">
                  Type:{" "}
                  <span className="font-medium text-foreground">
                    {content.type}
                  </span>
                </p>
                {content.metadata?.model && (
                  <p className="text-muted-foreground">
                    Model:{" "}
                    <span className="font-medium text-foreground">
                      {content.metadata.model}
                    </span>
                  </p>
                )}
              </div>
              <div>
                {content.metadata?.file_type && (
                  <p className="text-muted-foreground">
                    File Type:{" "}
                    <span className="font-medium text-foreground">
                      {content.metadata.file_type}
                    </span>
                  </p>
                )}
                {content.filename && (
                  <p className="text-muted-foreground">
                    Filename:{" "}
                    <span className="font-medium text-foreground">
                      {content.filename}
                    </span>
                  </p>
                )}
              </div>
            </div>

            {/* Content */}
            {content.metadata?.transcription && (
              <div className="prose prose-sm max-w-none dark:prose-invert mb-4">
                <h3>Transcribed Prompt</h3>
                <p>{content.metadata.transcription}</p>
              </div>
            )}
            {content.metadata?.query && (
              <div className="prose prose-sm max-w-none dark:prose-invert mb-4">
                <h3>Query</h3>
                <p>{content.metadata.query}</p>
              </div>
            )}
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <h3>Response</h3>
              {!audioBlobs[content.id] && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleTextToSpeech(content)}
                  disabled={loadingAudio[content.id]}
                  title="Convert to Speech"
                >
                  {loadingAudio[content.id] ? (
                    <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
                  ) : (
                    <SpeakerLoudIcon className="h-4 w-4" />
                  )}
                </Button>
              )}
              {/* Audio Player */}
              {audioBlobs[content.id] && (
                <div className="mb-4">
                  <AudioPlayer audioBlob={audioBlobs[content.id]} />
                </div>
              )}
              {expandedItems[content.id] ? (
                <ReactMarkdown>{content.content}</ReactMarkdown>
              ) : (
                <ReactMarkdown>
                  {getContentPreview(content.content)}
                </ReactMarkdown>
              )}
            </div>
          </CardContent>

          <CardFooter>
            <Button
              variant="ghost"
              className="w-full"
              onClick={() => toggleExpand(content.id)}
            >
              {expandedItems[content.id] ? (
                <>
                  <ChevronUpIcon className="h-4 w-4 mr-2" />
                  Show Less
                </>
              ) : (
                <>
                  <ChevronDownIcon className="h-4 w-4 mr-2" />
                  Show More
                </>
              )}
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}
