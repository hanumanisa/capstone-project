import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api/axios';
import { getUserFromToken } from '../utils/auth';
import aiBot from '../assets/AI_BOT.png';
import logoSmi from '../assets/logosmi.png';
import ReactMarkdown from 'react-markdown';

const WELCOME_MSG = { role: 'assistant', content: 'Halo! Saya SMI Assistant 👋 Ada yang bisa saya bantu hari ini?' };

const AiChatPage = () => {
    const navigate = useNavigate();
    const [messages, setMessages] = useState([WELCOME_MSG]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [showHelpModal, setShowHelpModal] = useState(false);
    const [showAdminModal, setShowAdminModal] = useState(false);
    const [waNumber, setWaNumber] = useState('6281234567890');
    const loadingRef = useRef(false);
    const sessionRef = useRef(null);
    
    const chatEndRef = useRef(null);

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        // Role Redirection
        const user = getUserFromToken();
        const adminRoles = ['Super Administrator', 'Administrator'];
        if (user && adminRoles.includes(user.role)) {
            navigate('/ai-admin');
            return;
        }

        const initializeChat = async () => {
            // Fetch WA Number
            try {
                const waRes = await api.get('/api/ai-admin-config/get_wa_number/');
                if (waRes.data?.wa_number) setWaNumber(waRes.data.wa_number);
            } catch (err) {
                console.error('Failed to fetch WA number', err);
            }

            // Always start a fresh session on page load to clear history
            try {
                const newRes = await api.post('/api/ai-sessions/', {});
                const currentSession = newRes.data;
                
                setMessages([WELCOME_MSG]);
                sessionRef.current = currentSession; // always-fresh ref for event handlers

                // Handle auto-question from dashboard — handled INLINE to avoid stale closure
                const autoQuestion = localStorage.getItem('autoQuestion');
                if (autoQuestion) {
                    localStorage.removeItem('autoQuestion');
                    localStorage.removeItem('autoAnswer');
                    const sid = currentSession.session_id;
                    
                    setMessages(prev => [...prev, { role: 'user', content: autoQuestion }]);
                    loadingRef.current = true;
                    setLoading(true);
                    
                    try {
                        const r = await api.post(`/api/ai-sessions/${sid}/chat/`, { message: autoQuestion });
                        setMessages(prev => [...prev, { role: 'assistant', content: r.data.response }]);
                    } catch {
                        setMessages(prev => [...prev, { role: 'assistant', content: 'Maaf, saya sedang mengalami kendala. Silakan coba lagi nanti.' }]);
                    } finally {
                        setLoading(false);
                        loadingRef.current = false;
                    }
                }
            } catch (err) {
                console.error('Failed to initialize chat session', err);
            }
        };

        initializeChat();
    }, []);

    const handleSendMessage = async (text) => {
        const messageText = text || input;
        if (!messageText.trim() || loadingRef.current) return;

        const sid = sessionRef.current?.session_id;
        if (!sid) {
            console.warn('No session ID available, cannot send message');
            return;
        }

        // Add user message
        setMessages(prev => [...prev, { role: 'user', content: messageText }]);
        setInput('');

        loadingRef.current = true;
        setLoading(true);

        try {
            const res = await api.post(`/api/ai-sessions/${sid}/chat/`, { 
                message: messageText,
                history: messages.slice(-4).map(m => ({ role: m.role, content: m.content.substring(0, 200) }))
            });
            setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', content: 'Maaf, saya sedang mengalami kendala koneksi. Silakan coba lagi nanti.' }]);
        } finally {
            setLoading(false);
            loadingRef.current = false;
        }
    };

    const handleWAContinue = () => {
        window.open(`https://wa.me/${waNumber}`, '_blank');
        setShowAdminModal(false);
    };

    return (
        <div className="bg-[#D6EFFF] h-screen flex flex-col font-['Lexend'] overflow-hidden">
            {/* Header */}
            <header className="bg-[#1E5084] h-[60px] flex items-center px-5 relative z-100 shadow-md">
                <img src={logoSmi} alt="SMI Logo" className="h-[35px] absolute left-5" />
                <div className="text-white w-full text-center text-xl font-semibold">Chat With Us!</div>
                <Link to="/dashboard" className="text-white text-2xl absolute right-5 hover:opacity-70 transition-opacity">
                    ✕
                </Link>
            </header>

            {/* Chat Area */}
            <main className="flex-1 relative p-5 flex flex-col overflow-y-auto custom-scrollbar">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center text-[#1E5084]/10 text-6xl font-bold uppercase pointer-events-none z-0">
                    SMI<br />ASSISTANT
                </div>

                <div className="flex flex-col space-y-8 z-10 pb-4">
                    {messages.map((msg, index) => (
                        <div key={index} className={`flex items-start gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            {msg.role === 'assistant' && (
                                <div className="w-[45px] h-[45px] bg-white rounded-full flex justify-center items-center shadow-md shrink-0">
                                    <img src={aiBot} alt="Bot" className="w-7" />
                                </div>
                            )}
                            <div className={`chat-bubble max-w-[75%] px-6 py-4 rounded-2xl text-[15px] shadow-sm word-wrap break-word ${msg.role === 'user' 
                                    ? 'bg-[#1E70B9] text-white rounded-tr-none' 
                                    : 'bg-white text-[#444] rounded-tl-none'
                                }`}>
                                {msg.role === 'assistant' 
                                    ? <ReactMarkdown>{msg.content}</ReactMarkdown>
                                    : msg.content
                                }
                            </div>
                        </div>
                    ))}
                    
                    {loading && (
                        <div className="flex items-start gap-3 justify-start">
                             <div className="w-[45px] h-[45px] bg-white rounded-full flex justify-center items-center shadow-md shrink-0">
                                <img src={aiBot} alt="Bot" className="w-7" />
                            </div>
                            <div className="bg-white text-[#444] px-6 py-4 rounded-2xl rounded-tl-none shadow-sm flex space-x-1">
                                <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce [animation-delay:-.3s]"></div>
                                <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce [animation-delay:-.5s]"></div>
                            </div>
                        </div>
                    )}
                    
                    <div ref={chatEndRef} />
                </div>


            </main>

            {/* Input Bar */}
            <div className="bg-white px-6 py-4 flex items-center gap-4 z-50 shrink-0 shadow-lg">
                <button onClick={() => setShowHelpModal(true)} className="text-[#1E5084] hover:scale-110 transition-transform">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l2.27-2.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                    </svg>
                </button>
                <input 
                    type="text" 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Type something...." 
                    disabled={loading}
                    className="flex-1 border-none outline-none text-[15px] bg-transparent"
                />
                <button 
                    onClick={() => handleSendMessage()}
                    disabled={loading || !input.trim()}
                    className={`transition-all ${input.trim() && !loading ? 'text-[#1E70B9] scale-110' : 'text-gray-300'}`}
                >
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
                </button>
            </div>

            {/* Modals */}
            {(showHelpModal || showAdminModal) && (
                <div 
                    className="fixed inset-0 bg-black/30 z-[2000] flex items-center justify-center p-4 animate-fade-in"
                    onClick={() => { setShowHelpModal(false); setShowAdminModal(false); }}
                >
                    {showHelpModal && (
                        <div 
                            className="bg-white w-[280px] rounded-xl overflow-hidden shadow-2xl fixed bottom-20 left-5 animate-slide-up"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="bg-[#1E5084] p-4 text-white">
                                <h3 className="text-[15px] font-semibold">Need more help?</h3>
                                <p className="text-[11px] opacity-80 mt-1">Select an action below</p>
                            </div>
                            <button 
                                onClick={() => { setShowHelpModal(false); setShowAdminModal(true); }}
                                className="flex items-center gap-4 p-4 hover:bg-gray-50 transition-colors w-full text-left"
                            >
                                <span className="text-2xl">📞</span>
                                <div>
                                    <h4 className="text-sm font-semibold text-gray-800">Go to Admin</h4>
                                    <p className="text-[11px] text-gray-400">Connect with our team</p>
                                </div>
                            </button>
                            <button 
                                onClick={() => setShowHelpModal(false)}
                                className="flex items-center gap-4 p-4 hover:bg-gray-50 transition-colors w-full text-left border-t border-gray-50"
                            >
                                <span className="text-xl">✕</span>
                                <div>
                                    <h4 className="text-sm font-semibold text-gray-800">Close</h4>
                                    <p className="text-[11px] text-gray-400">Back to chat</p>
                                </div>
                            </button>
                        </div>
                    )}

                    {showAdminModal && (
                        <div 
                            className="bg-white w-full max-w-[400px] rounded-2xl overflow-hidden shadow-2xl text-center animate-bounce-in"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="bg-[#1E5084] p-8 text-white">
                                <div className="text-5xl mb-4">📞</div>
                                <h3 className="text-xl font-bold">Go to Admin</h3>
                                <p className="text-sm opacity-80 mt-1">Connect with our team</p>
                            </div>
                            <div className="p-8">
                                <p className="text-sm text-gray-600 mb-8 leading-relaxed">
                                    Would you like to continue this conversation with our admin? You'll be connected directly to the SMI team.
                                </p>
                                <div className="flex gap-4 justify-center">
                                    <button 
                                        onClick={() => setShowAdminModal(false)}
                                        className="px-6 py-2 border border-gray-200 rounded-lg text-gray-500 hover:bg-gray-50 transition-colors"
                                    >
                                        ✕ No
                                    </button>
                                    <button 
                                        onClick={handleWAContinue}
                                        className="px-6 py-2 bg-[#1E5084] text-white rounded-lg hover:bg-[#1E70B9] transition-colors shadow-md"
                                    >
                                        ✓ Yes, Continue
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}

            <style dangerouslySetInnerHTML={{ __html: `
                .custom-scrollbar::-webkit-scrollbar { width: 4px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(30, 80, 132, 0.1); border-radius: 10px; }
                
                @keyframes slide-up {
                    from { transform: translateY(20px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
                .animate-slide-up { animation: slide-up 0.3s ease-out forwards; }
                
                @keyframes fade-in {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                .animate-fade-in { animation: fade-in 0.2s ease-out forwards; }

                @keyframes bounce-in {
                    0% { transform: scale(0.9); opacity: 0; }
                    70% { transform: scale(1.05); }
                    100% { transform: scale(1); opacity: 1; }
                }
                .animate-bounce-in { animation: bounce-in 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
            `}} />
        </div>
    );
};

export default AiChatPage;
