import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";
import { Highlight, themes } from "prism-react-renderer";
import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { SpeakerLoudIcon } from "@radix-ui/react-icons";
import AudioPlayer from "@/components/audio-player";


const CodeBlock = ({ language, code }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-md overflow-hidden my-2 bg-muted">
      <div className="bg-muted/80 px-4 py-2 flex items-center justify-between border-gray-600 dark:border-gray-400 border-2 rounded-md">
        <span className="text-xs font-mono text-muted-foreground">
          {language || "plain text"}
        </span>
        <button
          onClick={handleCopy}
          className="hover:bg-muted rounded p-1 transition-colors"
          title="Copy code"
        >
          {copied ? (
            <Check className="h-4 w-4 text-green-500" />
          ) : (
            <Copy className="h-4 w-4 text-muted-foreground" />
          )}
        </button>
      </div>
      <Highlight
        theme={themes.vsDark}
        code={code}
        language={language || "plaintext"}
      >
        {({ className, style, tokens, getLineProps, getTokenProps }) => (
          <pre className={cn(className, "p-4 overflow-x-auto")} style={style}>
            {tokens.map((line, i) => (
              <div key={i} {...getLineProps({ line })}>
                {line.map((token, key) => (
                  <span key={key} {...getTokenProps({ token })} />
                ))}
              </div>
            ))}
          </pre>
        )}
      </Highlight>
    </div>
  );
};

const MarkdownComponents = {
  code: ({ inline, className, children, ...props }) => {
    const match = /language-(\w+)/.exec(className || "");
    const language = match ? match[1] : "";
    return !inline ? (
      <CodeBlock
        language={language}
        code={String(children).replace(/\n$/, "")}
      />
    ) : (
      <code
        className={cn(
          "relative rounded bg-muted px-4 py-[0.2rem] font-mono text-sm",
          className
        )}
        {...props}
      >
        {children}
      </code>
    );
  },
  p: ({ children }) => {
    // Check if children contains a block-level element
    const hasBlockElement = React.Children.toArray(children).some(
      (child) =>
        React.isValidElement(child) &&
        ["div", "pre", "ul", "ol", "blockquote"].includes(child.type)
    );

    // If it contains a block element, render without p wrapper
    return hasBlockElement ? (
      <>{children}</>
    ) : (
      <p className="mb-2 last:mb-0 leading-7">{children}</p>
    );
  },
  ul: ({ children, ...props }) => (
    <ul className="mb-2 list-disc pl-4 space-y-1" {...props}>
      {children}
    </ul>
  ),
  ol: ({ children, ...props }) => (
    <ol className="mb-2 list-decimal pl-4 space-y-1" {...props}>
      {children}
    </ol>
  ),
  li: ({ children }) => {
    // Check if children contains a block-level element
    const hasBlockElement = React.Children.toArray(children).some(
      (child) =>
        React.isValidElement(child) &&
        ["div", "pre", "ul", "ol", "p", "blockquote"].includes(child.type)
    );

    // If it contains a block element, render without additional p wrapper
    return (
      <li className="leading-7">
        {hasBlockElement ? children : <p className="mb-0">{children}</p>}
      </li>
    );
  },
  blockquote: ({ children }) => (
    <blockquote className="mt-2 border-l-2 border-primary/50 pl-4 italic text-muted-foreground">
      {children}
    </blockquote>
  ),
  h1: ({ children }) => (
    <h1 className="mb-2 text-2xl font-bold tracking-tight">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="mb-2 text-xl font-semibold tracking-tight">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="mb-2 text-lg font-semibold tracking-tight">{children}</h3>
  ),
  a: ({ children, href }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-primary underline hover:text-primary/80 transition-colors"
    >
      {children}
    </a>
  ),
  table: ({ children }) => (
    <div className="my-2 w-full overflow-x-auto">
      <table className="w-full border-collapse border border-border text-sm">
        {children}
      </table>
    </div>
  ),
  th: ({ children }) => (
    <th className="border border-border bg-muted px-4 py-2 text-left font-semibold">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="border border-border px-4 py-2">{children}</td>
  ),
  hr: () => <hr className="my-4 border-border" />,
  img: ({ src, alt }) => (
    <img src={src} alt={alt} className="rounded-lg max-w-full h-auto my-2" />
  ),
};

export function ChatMessage({ message, transcription = null, isBot }) {
  const [audioBlob, setAudioBlob] = useState(null);
  const [loadingAudio, setLoadingAudio] = useState(false);

  const handleTextToSpeech = async () => {
    try {
      if (!!audioBlob) {
        return;
      }
      setLoadingAudio(true);

      let textToConvert = message.trim();
      if (textToConvert.length > 10000) {
        textToConvert = textToConvert.slice(0, 10000) + "...";
      }

      const blob = await api.textToSpeech(textToConvert);
      setAudioBlob(blob);

    } catch (error) {
      console.log(error);
      toast.error("Error converting text to speech");
    } finally {
      setLoadingAudio(false);
    }
  };

  return (
    <div
      className={cn(
        "flex w-full items-start gap-4 rounded-lg p-4",
        isBot ? "bg-muted" : "bg-primary/10"
      )}
    >
      <span className="font-semibold min-w-[50px]">
        {isBot ? "🤖 AI" : "👤 You"}:
      </span>
      <div className="flex-1 space-y-2 overflow-hidden prose prose-sm dark:prose-invert max-w-none">
        {isBot && audioBlob && (
          <AudioPlayer audioBlob={audioBlob} />
        )}
        {isBot && !audioBlob && (
          <Button
            variant="ghost"
            size="icon"
            onClick={handleTextToSpeech}
            disabled={loadingAudio}
            title="Convert to Speech"
          >
            {loadingAudio ? (
              <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
            ) : (
              <SpeakerLoudIcon className="h-4 w-4" />
            )}
          </Button>
        )}
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={MarkdownComponents}
        >
          {message}
        </ReactMarkdown>
        {transcription && (
          <div className="prose prose-sm max-w-none dark:prose-invert text-muted-foreground">
            <p>
              <span className="font-bold">Transcribed prompt: </span>
              {transcription}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
