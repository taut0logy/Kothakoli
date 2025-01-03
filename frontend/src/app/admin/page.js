'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import { Loader2, Plus } from 'lucide-react';

export default function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const router = useRouter();

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    if (searchQuery.trim()) {
      const filtered = users.filter(user => 
        user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.email.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredUsers(filtered);
    } else {
      setFilteredUsers(users);
    }
  }, [searchQuery, users]);

  const fetchUsers = async () => {
    try {
      const response = await api.getAllUsers();
      setUsers(response);
      setFilteredUsers(response);
    } catch (error) {
      toast.error('Failed to load users');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUserClick = (userId) => {
    router.push(`/admin/users/${userId}`);
  };

  const handleCreateAdmin = () => {
    router.push('/admin/create');
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <Button onClick={handleCreateAdmin}>
            <Plus className="h-4 w-4 mr-2" />
            Create Admin
          </Button>
        </div>

        <div className="mb-8">
          <Input
            placeholder="Search users..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="max-w-md"
          />
        </div>

        <div className="grid gap-4">
          {filteredUsers.map((user) => (
            <Card
              key={user.id}
              className="p-4 cursor-pointer hover:bg-accent"
              onClick={() => handleUserClick(user.id)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">{user.name}</h3>
                  <p className="text-sm text-muted-foreground">{user.email}</p>
                  <div className="flex gap-2 mt-1">
                    <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                      {user.role}
                    </span>
                    <span className="text-xs bg-muted px-2 py-1 rounded">
                      {user._count.contents} PDFs
                    </span>
                  </div>
                </div>
                <div className="text-sm text-muted-foreground">
                  Joined {new Date(user.createdAt).toLocaleDateString()}
                </div>
              </div>
            </Card>
          ))}
          {filteredUsers.length === 0 && (
            <p className="text-center text-muted-foreground">
              No users found matching your search.
            </p>
          )}
        </div>
      </div>
    </div>
  );
} 