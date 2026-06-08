import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api/axios';
import { getUserFromToken } from '../utils/auth';
import aiBot from '../assets/AI_BOT.png';
import logoSmi from '../assets/logosmi.png';
import ReactMarkdown from 'react-markdown';

const WELCOME_MSG = { role: 'assistant', content: 'Halo! Saya SMI Assistant 👋 Ada yang bisa saya bantu hari ini?' };

// Normalize phone number to international format for wa.me
// Handles: '088xxx' → '6288xxx', '+6288xxx' → '6288xxx', '6288xxx' → '6288xxx'
const normalizeWaNumber = (number) => {
    if (!number) return '';
    let n = String(number).replace(/\D/g, ''); // remove non-digits
    if (n.startsWith('0')) {
        n = '62' + n.slice(1);
    } else if (n.startsWith('+')) {
        n = n.slice(1);
    }
    return n;
};

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
                        const token = localStorage.getItem('access_token');
                        const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                        const res = await fetch(`${baseURL}/api/ai-sessions/${sid}/chat/?stream=true`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                            body: JSON.stringify({ message: autoQuestion, history: [] })
                        });
                        
                        if (!res.ok) throw new Error('API Error');
                        
                        setLoading(false);
                        setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
                        
                        const reader = res.body.getReader();
                        const decoder = new TextDecoder("utf-8");
                        let done = false;

                        while (!done) {
                            const { value, done: readerDone } = await reader.read();
                            done = readerDone;
                            if (value) {
                                const chunkStr = decoder.decode(value, { stream: true });
                                const lines = chunkStr.split('\n');
                                for (const line of lines) {
                                    if (line.trim()) {
                                        try {
                                            const parsed = JSON.parse(line);
                                            if (parsed.chunk) {
                                                setMessages(prev => {
                                                    const newMsgs = [...prev];
                                                    const lastIdx = newMsgs.length - 1;
                                                    newMsgs[lastIdx] = {
                                                        ...newMsgs[lastIdx],
                                                        content: newMsgs[lastIdx].content + parsed.chunk
                                                    };
                                                    return newMsgs;
                                                });
                                            } else if (parsed.error) {
                                                setMessages(prev => {
                                                    const newMsgs = [...prev];
                                                    const lastIdx = newMsgs.length - 1;
                                                    newMsgs[lastIdx] = {
                                                        ...newMsgs[lastIdx],
                                                        content: parsed.error
                                                    };
                                                    return newMsgs;
                                                });
                                            }
                                        } catch(e) {}
                                    }
                                }
                            }
                        }
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
            const token = localStorage.getItem('access_token');
            const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const res = await fetch(`${baseURL}/api/ai-sessions/${sid}/chat/?stream=true`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ 
                    message: messageText,
                    history: messages.slice(-4).map(m => ({ role: m.role, content: m.content.substring(0, 200) }))
                })
            });

            if (!res.ok) throw new Error('API Error');

            setLoading(false);
            setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
            
            const reader = res.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let done = false;

            while (!done) {
                const { value, done: readerDone } = await reader.read();
                done = readerDone;
                if (value) {
                    const chunkStr = decoder.decode(value, { stream: true });
                    const lines = chunkStr.split('\n');
                    for (const line of lines) {
                        if (line.trim()) {
                            try {
                                const parsed = JSON.parse(line);
                                if (parsed.chunk) {
                                    setMessages(prev => {
                                        const newMsgs = [...prev];
                                        const lastIdx = newMsgs.length - 1;
                                        newMsgs[lastIdx] = {
                                            ...newMsgs[lastIdx],
                                            content: newMsgs[lastIdx].content + parsed.chunk
                                        };
                                        return newMsgs;
                                    });
                                } else if (parsed.error) {
                                    setMessages(prev => {
                                        const newMsgs = [...prev];
                                        const lastIdx = newMsgs.length - 1;
                                        newMsgs[lastIdx] = {
                                            ...newMsgs[lastIdx],
                                            content: parsed.error
                                        };
                                        return newMsgs;
                                    });
                                }
                            } catch(e) {}
                        }
                    }
                }
            }
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', content: 'Maaf, saya sedang mengalami kendala koneksi. Silakan coba lagi nanti.' }]);
        } finally {
            setLoading(false);
            loadingRef.current = false;
        }
    };

    const handleWAContinue = () => {
        const normalizedNumber = normalizeWaNumber(waNumber);
        window.open(`https://wa.me/${normalizedNumber}`, '_blank');
        setShowAdminModal(false);
    };

    return (
        <div className="bg-[#D6EFFF] h-screen flex flex-col font-sans overflow-hidden">
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
                <button onClick={() => setShowHelpModal(true)} className="text-[#25D366] hover:scale-110 transition-transform">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
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
                                <span className="bg-[#25D366] text-white p-2 rounded-lg">
                                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                                    </svg>
                                </span>
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
                                <div className="text-5xl mb-4 text-[#25D366] flex justify-center">
                                    <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
                                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                                    </svg>
                                </div>
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
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
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
