import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import * as XLSX from 'xlsx';
import { 
    BarChart3, 
    AlertTriangle, 
    FileSpreadsheet, 
    Settings, 
    MessageCircle, 
    ShieldCheck, 
    Database, 
    Send, 
    RefreshCw, 
    Info, 
    Save 
} from 'lucide-react';
import api from '../api/axios';
import { getUserFromToken } from '../utils/auth';
import { notify } from '../utils/swal';

const AiAdminPage = () => {
    const navigate = useNavigate();
    const [stats, setStats] = useState({ total_chats: 0, wa_redirects: 0, unanswered: 0, out_of_scope: 0 });
    const [unansweredLogs, setUnansweredLogs] = useState([]);
    const [waNumber, setWaNumber] = useState('6281234567890');
    const [publishStatus, setPublishStatus] = useState('');
    const [waSaveStatus, setWaSaveStatus] = useState('');
    const [exportStatus, setExportStatus] = useState('');
    const [exportDates, setExportDates] = useState({ from: '', to: '' });
    const [adminSession, setAdminSession] = useState(null);
    const [chatMessages, setChatMessages] = useState([
        { role: 'ai', content: 'Selamat datang, Admin. Semua akses database terbuka. Gunakan bahasa natural untuk melakukan audit atau rekap data.' }
    ]);
    const [adminInput, setAdminInput] = useState('');
    const [adminLoading, setAdminLoading] = useState(false);

    useEffect(() => {
        // Role Protection
        const user = getUserFromToken();
        const allowedRoles = ['Super Administrator', 'Administrator'];
        if (!user || !allowedRoles.includes(user.role)) {
            notify.error('Akses Terbatas', 'Halaman ini hanya dapat diakses oleh Administrator dan Dean.');
            navigate('/dashboard');
            return;
        }

        fetchData();
        
        let mounted = true;
        const initAdminSession = async () => {
            try {
                const res = await api.post('/api/ai-sessions/', {});
                if (mounted) {
                    console.log('Admin session created:', res.data);
                    setAdminSession(res.data);
                }
            } catch (err) {
                console.error('Failed to create admin session', err);
                // Retry sekali lagi setelah 2 detik
                setTimeout(async () => {
                    if (!mounted) return;
                    try {
                        const res2 = await api.post('/api/ai-sessions/', {});
                        if (mounted) setAdminSession(res2.data);
                    } catch (err2) {
                        console.error('Retry session failed', err2);
                    }
                }, 2000);
            }
        };
        initAdminSession();
        
        return () => { mounted = false; };
    }, []);

    const fetchData = async () => {
        // Fetch each independently so one failure doesn't block the others
        try {
            const statsRes = await api.get('/api/ai-logs/stats/');
            setStats(statsRes.data);
        } catch (err) {
            console.error('Failed to fetch stats', err.response?.status, err.message);
        }



        try {
            const unansweredRes = await api.get('/api/ai-logs/unanswered_logs/');
            setUnansweredLogs(Array.isArray(unansweredRes.data) ? unansweredRes.data : []);
        } catch (err) {
            console.error('Failed to fetch unanswered logs', err.response?.status, err.message);
        }

        try {
            const waRes = await api.get('/api/ai-admin-config/get_wa_number/');
            if (waRes.data?.wa_number) setWaNumber(waRes.data.wa_number);
        } catch (err) {
            console.error('Failed to fetch WA number', err.response?.status, err.message);
        }
    };



    const saveWaConfig = async () => {
        try {
            await api.post('/api/ai-admin-config/set_wa_number/', { wa_number: waNumber });
            setWaSaveStatus(`✅ Nomor WA disimpan: +${waNumber}`);
            notify.success('Nomor WhatsApp berhasil disimpan.');
            setTimeout(() => setWaSaveStatus(''), 3000);
        } catch (err) {
            const errMsg = err.response?.data?.error || err.response?.data?.detail || err.message;
            console.error("Save WA Error:", err.response?.data || err.message);
            notify.error('Gagal menyimpan nomor WA: ' + errMsg);
        }
    };

    const exportToExcel = () => {
        let filtered = [...unansweredLogs];
        if (exportDates.from) filtered = filtered.filter(d => d.date >= exportDates.from);
        if (exportDates.to) filtered = filtered.filter(d => d.date <= exportDates.to);

        if (filtered.length === 0) {
            notify.alert('Kosong', 'Tidak ada data untuk rentang tanggal yang dipilih.');
            return;
        }

        const byYear = {};
        filtered.forEach(item => {
            const year = item.date.substring(0, 4);
            if (!byYear[year]) byYear[year] = [];
            byYear[year].push(item);
        });

        const wb = XLSX.utils.book_new();
        Object.keys(byYear).sort().forEach(year => {
            const rows = byYear[year].map((item, idx) => ({
                'No': idx + 1,
                'NIK': item.nik,
                'Nama': item.name,
                'Divisi': item.division,
                'Pertanyaan': item.message,
                'Tanggal': item.date,
            }));
            const ws = XLSX.utils.json_to_sheet(rows);
            XLSX.utils.book_append_sheet(wb, ws, `Unanswered ${year}`);
        });

        XLSX.writeFile(wb, `Unanswered_Log_${new Date().toISOString().split('T')[0]}.xlsx`);
        setExportStatus(`✅ ${filtered.length} data exported!`);
        setTimeout(() => setExportStatus(''), 4000);
    };


    const sendAdminMessage = async () => {
        if (!adminInput.trim() || !adminSession || adminLoading) return;
        const text = adminInput;
        setChatMessages(prev => [...prev, { role: 'user', content: text }]);
        setAdminInput('');
        setAdminLoading(true);

        console.log('Sending to session:', adminSession?.session_id);
        try {
            const res = await api.post(`/api/ai-sessions/${adminSession.session_id}/chat/`, {
                message: text,
                history: chatMessages.slice(-4).map(m => ({ role: m.role === 'ai' ? 'assistant' : 'user', content: m.content }))
            });
            console.log('Response status:', res.status);
            console.log('Response data:', res.data);
            const aiText = res.data.response || 'Tidak ada respons.';
            setChatMessages(prev => [...prev, { role: 'ai', content: aiText }]);
        } catch (err) {
            console.error('Chat error status:', err.response?.status);
            console.error('Chat error data:', err.response?.data);
            console.error('Chat error message:', err.message);
            setChatMessages(prev => [...prev, { role: 'ai', content: 'Maaf, terjadi kendala koneksi ke sistem AI.' }]);
        } finally {
            setAdminLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-[#D6EFFF] font-sans overflow-hidden text-[#1E293B]">
            <header className="bg-[#1E5084] h-15 flex items-center px-5 justify-between shadow-lg shrink-0">
                <div className="flex items-center space-x-4">
                    <Link to="/dashboard" className="text-white hover:opacity-80 transition-all">
                         <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7 7-7" /></svg>
                    </Link>
                    <div className="flex items-center gap-2 text-white text-sm font-semibold tracking-wide">
                        Integrated L&D System
                    </div>
                </div>
                <div className="bg-[#E74C3C] text-white px-3 py-1 rounded-full text-[10px] font-bold tracking-widest uppercase">System Administrator</div>
            </header>

            <main className="flex-1 p-4 grid grid-cols-1 lg:grid-cols-[340px_1fr] gap-4 overflow-hidden">
                {/* Left Column */}
                <div className="flex flex-col gap-4 overflow-y-auto pr-1 custom-scrollbar">
                    {/* Stats Card */}
                    <section className="bg-white rounded-2xl p-4 shadow-sm border border-[#D0E8F8]">
                        <h3 className="text-[#1E5084] text-xs font-bold flex items-center gap-2 mb-3 pb-2 border-b-2 border-[#D6EFFF]">
                            <BarChart3 className="w-4 h-4 text-[#2174C3]" /> Quick Stats
                        </h3>
                        <div className="grid grid-cols-2 gap-2">
                            <div className="bg-[#F8FBFF] p-3 rounded-xl border border-[#D0E8F8] text-center">
                                <span className="block text-xl font-bold text-[#1E70B9]">{stats.total_chats}</span>
                                <span className="text-[9px] text-gray-400 uppercase">Total Chats</span>
                            </div>
                            <div className="bg-[#F8FBFF] p-3 rounded-xl border border-[#D0E8F8] text-center">
                                <span className="block text-xl font-bold text-[#E74C3C]">{stats.unanswered}</span>
                                <span className="text-[9px] text-gray-400 uppercase">Unanswered</span>
                            </div>
                        </div>
                    </section>



                    {/* Unanswered Log */}
                    <section className="bg-white rounded-2xl p-4 shadow-sm border border-[#D0E8F8]">
                        <div className="flex justify-between items-center mb-3">
                            <h3 className="text-[#1E5084] text-xs font-bold flex items-center gap-2">
                                <AlertTriangle className="w-4 h-4 text-[#E74C3C]" /> Unanswered Log
                            </h3>
                            <div className="flex items-center gap-2">
                                <span className="text-[9px] text-gray-400 italic">Update</span>
                                <button 
                                    onClick={fetchData} 
                                    className="text-[#1E70B9] hover:rotate-180 transition-all duration-500 p-1 hover:bg-blue-50 rounded-full"
                                    title="Refresh Data"
                                >
                                    <RefreshCw className="w-3.5 h-3.5" />
                                </button>
                            </div>
                        </div>
                        <div className="space-y-2 mb-4">
                            {unansweredLogs.slice(0, 5).map(log => (
                                <div key={log.id} className="bg-red-50/50 border-red-500 rounded-r-xl p-2 border border-[#FDE0DC] border-l-4">
                                    <div className="flex justify-between items-center text-[10px] mb-1">
                                        <span className="font-bold text-[#1E5084]">{log.name && log.name !== 'N/A' ? log.name : 'User'}</span>
                                        <span className="text-gray-400">{log.date}</span>
                                    </div>
                                    <p className="text-[11px] text-gray-600 truncate italic">"{log.message}"</p>
                                    <div className="text-[9px] text-gray-400 mt-1">{log.division && log.division !== 'N/A' ? log.division : ''}</div>
                                </div>
                            ))}
                        </div>

                        {/* Export Box */}
                        <div className="bg-[#F0FAF4] border border-[#B7E4CB] rounded-xl p-3">
                            <div className="text-[#1D6F42] text-[11px] font-bold flex items-center gap-2 mb-3">
                                <FileSpreadsheet className="w-4 h-4" /> Export to Excel
                            </div>
                            <div className="grid grid-cols-2 gap-2 mb-3">
                                <div className="space-y-1">
                                    <label className="text-[9px] font-bold text-gray-400 uppercase">From</label>
                                    <input type="date" value={exportDates.from} onChange={(e) => setExportDates({...exportDates, from: e.target.value})} className="w-full bg-white border border-[#B7E4CB] rounded-lg p-1 text-[10px]" />
                                </div>
                                <div className="space-y-1">
                                    <label className="text-[9px] font-bold text-gray-400 uppercase">To</label>
                                    <input type="date" value={exportDates.to} onChange={(e) => setExportDates({...exportDates, to: e.target.value})} className="w-full bg-white border border-[#B7E4CB] rounded-lg p-1 text-[10px]" />
                                </div>
                            </div>
                            <button onClick={exportToExcel} className="w-full bg-[#1D6F42] text-white text-[11px] font-bold py-2.5 rounded-lg hover:bg-[#155230] transition-all shadow-sm tracking-wide">Export</button>
                            {exportStatus && <p className="text-center text-[#1D6F42] text-[10px] mt-2 font-medium">{exportStatus}</p>}
                        </div>
                    </section>

                    {/* AI Settings */}
                    <section className="bg-white rounded-2xl p-4 shadow-sm border border-[#D0E8F8]">
                        <h3 className="text-[#1E5084] text-xs font-bold mb-3 flex items-center gap-2">
                            <Settings className="w-4 h-4 text-gray-400" /> AI Settings
                        </h3>
                        <div className="bg-[#F0FDF4] border-l-4 border-[#25D366] rounded-r-lg p-2.5 text-[10px] text-gray-600 mb-3 leading-relaxed flex gap-2">
                            <Info className="w-4 h-4 text-[#25D366] shrink-0" />
                            <span>Set the WhatsApp number for the <strong>"Contact Admin"</strong> button in user view.</span>
                        </div>
                        <div className="flex items-center gap-2 mb-3">
                            <div className="bg-[#25D366] text-white w-9 h-9 flex items-center justify-center rounded-lg shadow-sm shrink-0">
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                                </svg>
                            </div>
                            <input 
                                type="tel" 
                                value={waNumber}
                                onChange={(e) => setWaNumber(e.target.value.replace(/\D/g, ''))}
                                className="flex-1 bg-white border border-[#D0E8F8] rounded-lg p-2 text-xs outline-none focus:border-[#25D366] transition-all font-semibold"
                            />
                        </div>
                        <p className="text-[9px] text-gray-400 mb-4 px-1">🔗 Link: <a href={`https://wa.me/${waNumber}`} target="_blank" className="text-[#075e54] font-bold">wa.me/{waNumber}</a></p>
                        <button onClick={saveWaConfig} className="w-full bg-[#075e54] text-white text-xs font-bold py-3 rounded-xl hover:bg-[#054d44] transition-all tracking-wide">
                            Save Number
                        </button>
                        {waSaveStatus && <p className="text-center text-[#075e54] text-[10px] mt-2 font-medium">{waSaveStatus}</p>}
                    </section>
                </div>

                {/* Right Column - Chat Panel */}
                <div className="bg-white rounded-2xl shadow-lg border border-[#D0E8F8] flex flex-col overflow-hidden">
                    <div className="bg-[#1E5084] p-4 text-white flex justify-between items-center">
                        <div className="flex items-center gap-3">
                            <ShieldCheck className="w-5 h-5 opacity-80" />
                            <div>
                                <div className="text-sm font-bold">Admin Query Console</div>
                                <div className="text-[10px] opacity-70">Natural language database analytics</div>
                            </div>
                        </div>
                        <Database className="w-5 h-5 opacity-40" />
                    </div>

                    <div className="flex-1 p-5 overflow-y-auto space-y-4 custom-scrollbar">
                        {chatMessages.map((msg, idx) => (
                            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div 
                                    className={`max-w-[85%] px-4 py-3 rounded-2xl text-[13px] leading-relaxed shadow-xs ${
                                        msg.role === 'user' 
                                        ? 'bg-[#1E5084] text-white rounded-tr-none' 
                                        : 'bg-gray-50 text-gray-700 border border-gray-100 rounded-tl-none'
                                    }`}
                                >
                                    {msg.content.split('\n').map((line, i) => (
                                        <span key={i}>{line}{i < msg.content.split('\n').length - 1 && <br />}</span>
                                    ))}
                                </div>
                            </div>
                        ))}
                        
                        {adminLoading && (
                            <div className="flex justify-start">
                                <div className="bg-gray-50 border border-gray-100 px-4 py-3 rounded-2xl rounded-tl-none shadow-xs flex items-center gap-1.5">
                                    <div className="w-2 h-2 bg-[#1E5084] rounded-full animate-bounce"></div>
                                    <div className="w-2 h-2 bg-[#1E5084] rounded-full animate-bounce [animation-delay:-.3s]"></div>
                                    <div className="w-2 h-2 bg-[#1E5084] rounded-full animate-bounce [animation-delay:-.5s]"></div>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="p-4 bg-white border-t border-[#D6EFFF] flex gap-2">
                        <input 
                            type="text" 
                            value={adminInput}
                            onChange={(e) => setAdminInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && sendAdminMessage()}
                            placeholder="Ketik perintah analisis data..." 
                            className="flex-1 bg-gray-50 border border-[#D0E8F8] rounded-xl px-4 py-3 text-xs outline-none focus:border-[#1E70B9] focus:bg-white transition-all"
                        />
                        <button 
                            onClick={sendAdminMessage} 
                            disabled={!adminSession || adminLoading}
                            className={`px-6 rounded-xl transition-all text-white shadow-sm flex items-center justify-center gap-2 ${
                                !adminSession || adminLoading 
                                ? 'bg-gray-300 cursor-not-allowed' 
                                : 'bg-[#1E70B9] hover:bg-[#1E5084]'
                            }`}
                            title={!adminSession ? 'Menghubungkan ke AI...' : 'Kirim pesan'}
                        >
                            {adminLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                        </button>
                    </div>
                </div>
            </main>

            <style dangerouslySetInnerHTML={{ __html: `
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
                .custom-scrollbar::-webkit-scrollbar { width: 4px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #D0E8F8; border-radius: 10px; }
            `}} />
        </div>
    );
};

export default AiAdminPage;