import React from 'react';
import Navbar from './Navbar';

const MainLayout = ({ children }) => {
    return (
        <div className="h-screen bg-[#F4F7FA] flex flex-col overflow-hidden">
            <Navbar />
            <main className="flex-1 w-full overflow-y-auto custom-scrollbar">
                <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 transition-all duration-300">
                    {children}
                </div>
            </main>

            {/* Chat Floating Button */}
            <div className="fixed bottom-8 right-8 bg-[#215A92] w-14 h-14 rounded-full flex items-center justify-center text-white shadow-2xl cursor-pointer hover:scale-110 transition-transform z-50">
                <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"></path>
                    <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"></path>
                </svg>
            </div>
        </div>
    );
};

export default MainLayout;
