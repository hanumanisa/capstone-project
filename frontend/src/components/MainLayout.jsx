import React, { useState, useEffect } from 'react';
import Navbar from './Navbar';
import { useNavigate } from 'react-router-dom';
import { getUserFromToken } from '../utils/auth';
import { notify } from '../utils/swal';

const MainLayout = ({ children }) => {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);

    useEffect(() => {
        const userData = getUserFromToken();
        if (userData) {
            setUser(userData);
        }
    }, []);

    const adminRoles = ['Super Administrator', 'Administrator'];
    const userRoles = ['Head of Division', 'Team Leader', 'Employee', 'Dean'];

    const handleChatClick = () => {
        if (!user) {
            notify.alert('Akses Terbatas', 'Silakan login terlebih dahulu untuk mengakses AI Assistant.');
            return;
        }
        
        if (adminRoles.includes(user.role)) {
            navigate('/ai-admin');
        } else if (userRoles.includes(user.role)) {
            navigate('/ai-dashboard');
        } else {
            notify.alert('Akses Terbatas', 'AI Assistant saat ini hanya tersedia untuk karyawan dan pimpinan.');
        }
    };

    return (
        <div className="h-screen bg-[#F4F7FA] flex flex-col overflow-hidden">
            <Navbar />
            <main className="flex-1 w-full overflow-y-auto custom-scrollbar">
                <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 transition-all duration-300">
                    {children}
                </div>
            </main>

            {/* Chat Floating Button */}
            <div 
                onClick={handleChatClick}
                className="fixed bottom-8 right-8 bg-[#215A92] w-14 h-14 rounded-full flex items-center justify-center text-white shadow-2xl cursor-pointer hover:scale-110 transition-transform z-50 group"
            >
                <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"></path>
                    <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"></path>
                </svg>
                {/* Tooltip */}
                <div className="absolute right-16 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                    SMI Assistant
                </div>
            </div>
        </div>
    );
};

export default MainLayout;
