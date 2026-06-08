import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import logoSmi from '../assets/logosmi.png';
import aiBot from '../assets/AI_BOT.png'; 
import api from '../api/axios';
import { getUserFromToken } from '../utils/auth';

const AiDashboard = () => {
    const navigate = useNavigate();
    const [faqs, setFaqs] = useState([]);

    useEffect(() => {
        // Role Redirection
        const user = getUserFromToken();
        const adminRoles = ['Super Administrator', 'Administrator'];
        if (user && adminRoles.includes(user.role)) {
            navigate('/ai-admin');
            return;
        }
    }, []);

    return (
        <div className="min-h-screen bg-linear-to-b from-[#5389BA] to-[#B8D3E9] flex flex-col items-center justify-center p-6 relative overflow-hidden font-sans">
            {/* Logo Section */}
            <div className="absolute top-6 left-6">
                <img src={logoSmi} alt="SMI Logo" className="w-24 h-auto drop-shadow-lg" />
            </div>

            {/* Close Button */}
            <Link 
                to="/dashboard" 
                className="absolute top-6 right-8 text-white text-3xl font-bold hover:scale-110 hover:opacity-75 transition-all duration-200 z-50"
                title="Back to Dashboard"
            >
                ✕
            </Link>

            <div className="max-w-3xl w-full flex flex-col items-center text-center">
                {/* AI Bot Image */}
                <div className="w-64 h-64 mb-6">
                    <img 
                        src={aiBot} 
                        alt="SMI AI Assistant" 
                        className="w-full h-full object-contain drop-shadow-2xl"
                    />
                </div>

                <h1 className="text-white text-2xl font-semibold mb-2 drop-shadow-md">
                    Hi, welcome to SMI Assistant!
                </h1>
                <p className="text-white/90 text-lg font-light mb-12 drop-shadow-sm">
                    Feel free to ask anything you'd like to know 😊
                </p>

                {/* Start Chat Button */}
                <button
                    onClick={() => navigate('/ai-start')}
                    className="w-full bg-[#1E70B9] text-white py-5 px-10 rounded-xl text-xl font-semibold shadow-[0_8px_25px_rgba(0,0,0,0.2)] hover:bg-[#165a96] hover:shadow-[0_10px_30px_rgba(0,0,0,0.3)] transition-all duration-300 active:transform active:translate-y-1"
                >
                    Chat SMI Assistant
                </button>
            </div>

            <style dangerouslySetInnerHTML={{ __html: `
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
                
                .custom-scrollbar::-webkit-scrollbar {
                    width: 4px;
                }
                .custom-scrollbar::-webkit-scrollbar-track {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: rgba(255, 255, 255, 0.4);
                    border-radius: 10px;
                }
            `}} />
        </div>
    );
};

export default AiDashboard;
