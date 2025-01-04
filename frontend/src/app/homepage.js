'use client'

import { useUser } from '@/hooks/use-user';
import { Loader2 } from 'lucide-react';
import AdminDashBoard from './admin-dashboard';
import UserDashboard from './user-dashboard';

export default function Homepage() {
    const { user, isLoading, isError } = useUser();

    if (isLoading) return <div className="flex justify-center items-center h-screen"><Loader2 className="animate-spin h-10 w-10 text-gray-500" /></div>;
    if (isError) return <div>Error</div>;

    if (user?.role === 'ADMIN') {
        return <AdminDashBoard/>
    }

    return <UserDashboard/>
}
