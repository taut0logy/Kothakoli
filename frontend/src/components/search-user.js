"use client";

import { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Toggle } from "@/components/ui/toggle";
import { api } from "@/lib/api";
import { useDebounce } from "@/hooks/use-debounce";
import { Loader2, Users, FileText, Download } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import { useUser } from "@/hooks/use-user";
import { Button } from "@/components/ui/button";

export default function SearchUser() {
  const { user } = useUser();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [searchType, setSearchType] = useState("users"); // 'users' or 'pdfs'
  const debouncedQuery = useDebounce(query, 300);
  const searchRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowResults(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (debouncedQuery.trim()) {
      performSearch();
    } else {
      setResults([]);
    }
  }, [debouncedQuery, searchType]);

  const performSearch = async () => {
    if (!debouncedQuery.trim()) return;

    setLoading(true);
    try {
      const response =
        searchType === "users"
          ? await api.searchUsers(debouncedQuery, 1, 5)
          : await api.searchPdfs(debouncedQuery, 1, 5);

      setResults(response.items || []);
      setShowResults(true);
    } catch (error) {
      toast.error(`Failed to search ${searchType}`);
    } finally {
      setLoading(false);
    }
  };

  const handlePdfDownload = async (content) => {
    try {
      const response = await api.downloadPdf(content.filename);
      const blob = new Blob([response], { type: "application/pdf" });
      const filename = content.filename || `${content.title}.pdf`;
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error("Error downloading PDF:", error);
      toast.error("Failed to download PDF");
    }
  };

  return (
    <div className="w-full space-y-2">
      <div className="flex items-center gap-2">
        <div className="relative flex-1" ref={searchRef}>
          <Input
            type="text"
            placeholder={`Search ${searchType}...`}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setShowResults(true)}
            className="w-full"
          />
          {loading && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
            </div>
          )}

          {showResults && (results.length > 0 || loading) && (
            <div className="absolute z-50 w-full mt-1 bg-background border rounded-md shadow-lg max-h-[300px] overflow-y-auto">
              {results.map((item) =>
                searchType === "users" ? (
                  <Link
                    key={item._id || item.id}
                    href={
                      user.role === "admin"
                        ? `/admin/users/${item._id || item.id}`
                        : `/users/${item._id || item.id}`
                    }
                    onClick={() => setShowResults(false)}
                    className="block px-4 py-2 hover:bg-accent transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{item.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {item.email}
                        </p>
                      </div>
                    </div>
                  </Link>
                ) : (
                  <div
                    key={item._id || item.id}
                    className="px-4 py-2 hover:bg-accent transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="font-medium">{item.title}</p>
                        <p className="text-sm text-muted-foreground">
                          Created by {item.user?.name || "Unknown"}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(item.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handlePdfDownload(item)}
                        className="ml-2"
                        title="Download PDF"
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                )
              )}
              {loading && results.length === 0 && (
                <div className="px-4 py-2 text-center text-muted-foreground">
                  Searching...
                </div>
              )}
              {!loading && results.length === 0 && query.trim() && (
                <div className="px-4 py-2 text-center text-muted-foreground">
                  No {searchType} found
                </div>
              )}
            </div>
          )}
        </div>
        <Toggle
          pressed={searchType === "pdfs"}
          onPressedChange={(pressed) => {
            setSearchType(pressed ? "pdfs" : "users");
            setResults([]);
            setQuery("");
          }}
          className="gap-2"
        >
          {searchType === "users" ? (
            <Users className="h-4 w-4" />
          ) : (
            <FileText className="h-4 w-4" />
          )}
          {searchType === "users" ? "Users" : "PDFs"}
        </Toggle>
      </div>
    </div>
  );
}
