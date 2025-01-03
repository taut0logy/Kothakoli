'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import { Loader2, Download } from 'lucide-react';

export default function AdminUserViewPage() {
  const { id } = useParams();
  const [user, setUser] = useState(null);
  const [contents, setContents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const [userResponse, contentsResponse] = await Promise.all([
          api.getUser(id),
          api.getUserContents(id)
        ]);
        
        setUser(userResponse);
        setContents(contentsResponse);
      } catch (error) {
        toast.error('Failed to load user data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserData();
  }, [id]);

  const handleDownload = async (contentId) => {
    try {
      const blob = await api.downloadPdf(contentId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `document-${contentId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error('Failed to download PDF');
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-2xl font-bold mb-4">User not found</h1>
          <p className="text-muted-foreground">
            The user you`&apos`re looking for doesn`&apos;`t exist.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <Card className="p-6 mb-8">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <h1 className="text-3xl font-bold mb-2">{user.name}</h1>
              <p className="text-muted-foreground">{user.email}</p>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Role:</span>
                <span className="font-medium">{user.role}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Joined:</span>
                <span className="font-medium">
                  {new Date(user.createdAt).toLocaleDateString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Email Verified:</span>
                <span className="font-medium">
                  {user.isVerified ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Total PDFs:</span>
                <span className="font-medium">{contents.length}</span>
              </div>
            </div>
          </div>
        </Card>

        <h2 className="text-2xl font-semibold mb-4">Generated PDFs</h2>
        <div className="grid gap-4">
          {contents.map((content) => (
            <Card key={content.id} className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">{content.title || 'Untitled'}</h3>
                  <p className="text-sm text-muted-foreground">
                    Created on {new Date(content.createdAt).toLocaleDateString()}
                  </p>
                </div>
                <Button onClick={() => handleDownload(content.id)}>
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>
            </Card>
          ))}
          {contents.length === 0 && (
            <p className="text-center text-muted-foreground">
              No PDFs generated yet.
            </p>
          )}
        </div>
      </div>
    </div>
  );
} 