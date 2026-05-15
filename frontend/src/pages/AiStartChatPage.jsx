import React, { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { getUserFromToken } from '../utils/auth';
import aiBotImg from '../assets/AI_BOT.png';
import logoImg from '../assets/logosmi.png';

const AiStartChatPage = () => {
    const navigate = useNavigate();

    useEffect(() => {
        // Role Redirection
        const user = getUserFromToken();
        const allowedRoles = ['Super Administrator', 'Administrator'];
        if (user && allowedRoles.includes(user.role)) {
            navigate('/ai-admin');
            return;
        }
    }, [navigate]);

    return (
        <div className="bg-[#D6EFFF] h-screen flex flex-col font-['Lexend']">
            {/* Header Biru Gelap */}
            <header className="bg-[#1E5084] h-[60px] flex items-center px-5 relative shrink-0 shadow-md">
                <img src={logoImg} alt="SMI Logo" className="h-[40px] absolute left-5" />
                <div className="text-white w-full text-center text-xl font-semibold">Chat With Us!</div>
                <Link to="/dashboard" className="text-white text-2xl font-bold absolute right-5 hover:opacity-70 transition-opacity">
                    ✕
                </Link>
            </header>

            {/* Area Konten Utama */}
            <main className="flex-1 flex justify-center items-center p-4">
                <div className="bg-white w-full max-w-[400px] p-10 rounded-[15px] shadow-2xl text-center flex flex-col items-center">
                    <img src={aiBotImg} alt="AI Icon" className="w-20 mb-5" />
                    <h2 className="text-lg text-[#444] mb-2 font-semibold">Hello, nice to meet you!</h2>
                    <p className="text-sm text-[#777] leading-relaxed mb-8">
                        Welcome to SMI Assistant. We're ready to help you find information about SMI services and products quickly and easily.
                    </p>
                    
                    <button 
                        onClick={() => navigate('/ai-chat')}
                        className="bg-[#2D79BE] hover:bg-[#1E5A91] text-white w-full py-3 rounded-lg text-lg transition-colors shadow-lg"
                    >
                        Start Chat
                    </button>
                </div>
            </main>
            
            <style dangerouslySetInnerHTML={{ __html: `
                @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;600&display=swap');
            `}} />
        </div>
    );
};

export default AiStartChatPage;
