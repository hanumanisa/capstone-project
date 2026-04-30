import React, { useState, useEffect, useMemo } from 'react';
import { Navigate } from 'react-router-dom';
import MainLayout from '../components/MainLayout';
import { getUserFromToken } from '../utils/auth';
import api from '../api/axios';
import './TrainingEvaluationPage.css';

export default function TrainingEvaluationEmployeePage() {
    const user = getUserFromToken();
    const canAccess = user?.role === 'Head of Division' || user?.role === 'Team Leader' || user?.role === 'Employee';

    const [allCards, setAllCards] = useState([]);
    const [selectedCard, setSelectedCard] = useState(null);
    const [showL1Modal, setShowL1Modal] = useState(false);
    const [showL2Modal, setShowL2Modal] = useState(false);
    const [showSubmitSuccess, setShowSubmitSuccess] = useState(false);
    const [alertModal, setAlertModal] = useState({ show: false, message: '', title: '' });

    // Answers format: l1Answers[question_id] = rating(number) | text(string)
    const [l1Answers, setL1Answers] = useState({});
    const [l2Answers, setL2Answers] = useState({});

    const [selectedMainTemplate, setSelectedMainTemplate] = useState('All_Templates');
    const [searchQuery, setSearchQuery] = useState('');
    const [activeYear, setActiveYear] = useState('2026');
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 20;

    useEffect(() => {
        loadEvaluations();
    }, []);

    const loadEvaluations = async () => {
        try {
            const res = await api.get('/api/evaluation-forms/my_evaluations/');
            const mapped = (res.data || []).map(item => {
                // Backend already provides 'type' (L1 or L2) and 'title' (cleaned form_name)
                const isL2 = item.type === 'L2';
                return {
                    ...item,
                    // 'title' is already provided by backend, fallback in case
                    title: item.title || (item.form_name || '').replace('[L1] ', '').replace('[L2] ', ''),
                    type: isL2 ? 'L2' : 'L1',
                    year: item.year ? String(item.year) : (item.created_at ? new Date(item.created_at).getFullYear().toString() : '2026'),
                    questions: (item.questions || []).map(q => ({
                        id: q.id || q.question_id,
                        q: q.q || q.question_text,
                        type: q.type || q.question_type || 'Rating Scale',
                        opts: q.opts || q.options || [],
                        score: q.score || 0
                    }))
                };
            });
            setAllCards(mapped);
        } catch (err) {
            console.error("Failed to load evaluations:", err);
        }
    };

    useEffect(() => {
        setCurrentPage(1);
    }, [searchQuery, selectedMainTemplate, activeYear]);

    const filteredCards = useMemo(() => {
        return allCards.filter(c => {
            const matchYear = c.year === parseInt(activeYear) || c.year === activeYear || !c.year;
            const matchType = selectedMainTemplate === 'All_Templates' ? true
                : (selectedMainTemplate === 'L1_Templates' ? c.type === 'L1' : c.type === 'L2');
            const matchSearch = searchQuery.trim() === '' ? true : (c.title && c.title.toLowerCase().includes(searchQuery.toLowerCase()));

            return matchYear && matchType && matchSearch;
        });
    }, [allCards, selectedMainTemplate, searchQuery, activeYear]);

    const totalPages = Math.max(1, Math.ceil(filteredCards.length / itemsPerPage));
    const paginatedCards = filteredCards.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

    const isPastDeadline = (card) => {
        if (!card.deadline) return false;
        return new Date() > new Date(card.deadline);
    };

    const isLocked = (card) => {
        return !card.is_submitted && isPastDeadline(card);
    };

    const openCardDetail = (card) => {
        if (isLocked(card)) {
            setAlertModal({
                show: true,
                title: 'Akses Ditolak',
                message: 'Tidak bisa di akses karena sudah melebihi batas waktu pengisian.'
            });
            return;
        }

        setSelectedCard(card);
        if (card.type === 'L1') {
            const ObjectAns = {};
            (card.questions || []).forEach(q => {
                const qType = (q.type || '').trim().toLowerCase();
                ObjectAns[q.id] = (qType === 'rating' || qType === 'rating scale') ? null : '';
            });
            setL1Answers(ObjectAns);
            setShowL1Modal(true);
        } else {
            const ObjectAns = {};
            (card.questions || []).forEach(q => {
                ObjectAns[q.id] = null;
            });
            setL2Answers(ObjectAns);
            setShowL2Modal(true);
        }
    };

    const setRating = (qId, val) => {
        setL1Answers(prev => ({
            ...prev,
            [qId]: prev[qId] === val ? null : val
        }));
    };

    const ratingClass = (qId, val) => {
        return l1Answers[qId] === val ? `rating-btn sel-${val}` : 'rating-btn';
    };

    const selectL2Answer = (qId, optId) => {
        setL2Answers(prev => ({
            ...prev,
            [qId]: optId
        }));
    };

    const l2OptionClass = (qId, optId) => {
        return l2Answers[qId] === optId ? 'mc-option selected' : 'mc-option';
    };

    const l2Progress = useMemo(() => {
        if (!selectedCard) return 0;
        const total = (selectedCard.questions || []).length;
        if (total === 0) return 0;
        const answered = Object.values(l2Answers).filter(v => v !== null).length;
        return answered / total;
    }, [selectedCard, l2Answers]);

    const l2MaxScore = useMemo(() => {
        if (!selectedCard) return 100;
        return (selectedCard.questions || []).reduce((s, q) => s + (q.score || 0), 0) || 100;
    }, [selectedCard]);

    const submitResponse = async (type) => {
        if (!selectedCard) return;

        let payloadAnswers = [];
        if (type === 'L1') {
            selectedCard.questions.forEach(q => {
                const qType = (q.type || '').trim().toLowerCase();
                if ((qType === 'rating' || qType === 'rating scale') && l1Answers[q.id]) {
                    payloadAnswers.push({ question_id: q.id, rating: l1Answers[q.id] });
                } else if ((qType === 'comment' || qType === 'text') && l1Answers[q.id]?.trim()) {
                    payloadAnswers.push({ question_id: q.id, text: l1Answers[q.id] });
                }
            });
        } else {
            selectedCard.questions.forEach(q => {
                if (l2Answers[q.id]) {
                    payloadAnswers.push({ question_id: q.id, option_id: l2Answers[q.id] });
                }
            });
        }

        try {
            await api.post(`/api/evaluation-forms/${selectedCard.id}/submit_answers/`, {
                answers: payloadAnswers
            });
            setShowL1Modal(false);
            setShowL2Modal(false);
            setShowSubmitSuccess(true);
            setTimeout(() => setShowSubmitSuccess(false), 3000);
            loadEvaluations();
        } catch (err) {
            setAlertModal({
                show: true,
                title: 'Gagal',
                message: 'Gagal mengirim jawaban. Silakan coba lagi atau hubungi administrator.'
            });
            console.error(err);
        }
    };

    const scoreColor = (score, type = 'L2') => {
        if (type === 'L2') {
            if (score >= 80) return '#10B981';
            if (score >= 60) return '#F59E0B';
            return '#EF4444';
        }
        // L1 scale (1-4)
        if (score >= 3.5) return '#10B981';
        if (score >= 2.5) return '#F59E0B';
        return '#EF4444';
    };

    const scoreLabel = (score) => {
        if (score >= 80) return 'Very Good';
        if (score >= 60) return 'Fair';
        return 'Needs Improvement';
    };

    if (!canAccess) {
        return <Navigate to="/dashboard" replace />;
    }

    return (
        <MainLayout>
            <div className="relative pb-24 max-w-[1400px] mx-auto">
                {/* Submit success toast */}
                {showSubmitSuccess && (
                    <div className="fixed top-20 right-6 bg-green-500 text-white px-6 py-3 rounded-xl shadow-xl z-[300] flex items-center gap-2 animate-fade-in-down">
                        <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
                        <span className="font-semibold">Answer submitted successfully!</span>
                    </div>
                )}

                {/* Toolbar */}
                <div className="bg-white p-3 rounded-xl shadow-sm border border-gray-100 flex flex-col sm:flex-row justify-between items-center gap-3 mb-10">
                    <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-1/2">
                        <div className="relative w-full sm:w-2/3">
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={e => setSearchQuery(e.target.value)}
                                placeholder="Search evaluation..."
                                className="w-full pl-4 pr-10 py-2 rounded-lg border-none bg-gray-100 focus:bg-white focus:ring-1 focus:ring-[#2174C3] transition-all text-gray-600 placeholder-gray-400 text-sm"
                            />
                            <span className="absolute right-3 top-2.5 text-gray-400 pointer-events-none">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                </svg>
                            </span>
                        </div>
                        <div className="relative w-full sm:w-1/3">
                            <select
                                value={selectedMainTemplate}
                                onChange={e => setSelectedMainTemplate(e.target.value)}
                                className="w-full border border-gray-200 rounded-lg px-4 py-2 text-sm text-gray-700 bg-white focus:outline-none focus:ring-1 focus:ring-[#2174C3] focus:border-transparent appearance-none bg-no-repeat bg-right-4"
                                style={{
                                    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M19 9l-7 7-7-7'/%3e%3c/svg%3e")`,
                                    backgroundSize: '20px 20px',
                                    backgroundPosition: 'right 12px center'
                                }}
                            >
                                <option value="All_Templates">All Templates</option>
                                <option value="L1_Templates">L1 Templates</option>
                                <option value="L2_Templates">L2 Templates</option>
                            </select>
                        </div>
                    </div>
                    <div className="flex items-center gap-6">
                        <div className="font-bold flex space-x-4 text-sm">
                            <button onClick={() => setActiveYear('2026')} className={activeYear === '2026' ? 'text-[#2174C3] cursor-pointer' : 'text-gray-300 cursor-pointer hover:text-gray-500 transition-colors'}>2026</button>
                            <button onClick={() => setActiveYear('2025')} className={activeYear === '2025' ? 'text-[#2174C3] cursor-pointer' : 'text-gray-300 cursor-pointer hover:text-gray-500 transition-colors'}>2025</button>
                        </div>
                    </div>
                </div>

                <h1 className="text-4xl font-bold text-gray-800 tracking-tight mb-2">Training Evaluation</h1>
                <p className="text-sm text-gray-400 mb-8">Click on a card to fill out the evaluation. Completed cards will display the results.</p>

                {/* Cards Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 mb-10">
                    {paginatedCards.length === 0 ? (
                        <div className="col-span-5 py-16 flex flex-col items-center text-gray-400">
                            <svg className="w-12 h-12 mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            <p className="text-sm font-medium">No evaluations found</p>
                        </div>
                    ) : (
                        paginatedCards.map((card, i) => (
                            <div key={i} onClick={() => openCardDetail(card)} className={`bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all border cursor-pointer relative ${card.is_submitted ? 'border-green-200' : 'border-gray-100'} ${isLocked(card) ? 'opacity-70 grayscale-[0.2]' : ''}`}>

                                <div className={`aspect-video relative overflow-hidden ${card.type === 'L2' ? 'bg-gradient-to-br from-[#a8d5b5] via-[#c4e6cf] to-[#b2d9c0]' : 'bg-gradient-to-br from-[#aac8e4] via-[#c8dff0] to-[#b8d0e8]'}`}>
                                    <span className="bubble b1"></span><span className="bubble b2"></span>
                                    <span className="bubble b3"></span><span className="bubble b4"></span><span className="bubble b5"></span>

                                    <div className="absolute top-2 right-2">
                                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${card.type === 'L2' ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'}`}>
                                            {card.type}
                                        </span>
                                    </div>

                                    {card.is_submitted && (
                                        <div className="absolute inset-0 bg-black/10 flex items-center justify-center">
                                            <div className="w-10 h-10 rounded-full bg-green-500 shadow-lg flex items-center justify-center">
                                                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
                                            </div>
                                        </div>
                                    )}

                                    {isLocked(card) && (
                                        <div className="absolute inset-0 bg-black/40 flex items-center justify-center backdrop-blur-[1px]">
                                            <div className="bg-red-500 text-white text-[10px] font-bold px-3 py-1 rounded-full shadow-lg flex items-center gap-1">
                                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
                                                Locked
                                            </div>
                                        </div>
                                    )}
                                </div>

                                <div className="p-4">
                                    <h3 className="text-xs font-bold text-gray-800 leading-tight mb-2">{card.title}</h3>

                                    {card.is_submitted ? (
                                        <div className="flex items-center justify-between">
                                            <span className="completed-badge">
                                                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>
                                                Done
                                            </span>
                                            {card.score !== null && (
                                                <span className="text-xs font-bold" style={{ color: scoreColor(card.score, card.type) }}>
                                                    {card.score}{card.type === 'L2' ? ' pts' : ' avg'}
                                                </span>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="flex justify-between items-center">
                                            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-tighter">
                                                {isLocked(card) ? 'Deadline Passed' : (card.hasQuestions ? 'Not filled yet' : 'Not available')}
                                            </span>
                                            {card.hasQuestions && !isLocked(card) && (
                                                <span className="text-[10px] font-semibold text-[#2174C3] bg-blue-50 px-2 py-0.5 rounded-full">Fill Now</span>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Pagination */}
                {filteredCards.length > 0 && (
                    <div className="flex justify-between items-center mt-8">
                        <span className="text-sm text-gray-400">
                            Showing <span className="font-semibold text-gray-600">{Math.min((currentPage - 1) * itemsPerPage + 1, filteredCards.length)}</span>–<span className="font-semibold text-gray-600">{Math.min(currentPage * itemsPerPage, filteredCards.length)}</span> of <span className="font-semibold text-gray-600">{filteredCards.length}</span> evaluations
                        </span>
                        <div className="flex items-center space-x-1">
                            <button onClick={() => setCurrentPage(Math.max(1, currentPage - 1))} disabled={currentPage === 1} className={`px-4 py-2 rounded-md font-medium text-sm transition-all ${currentPage === 1 ? 'bg-[#E2E8F0] text-gray-400 cursor-not-allowed' : 'bg-[#E2E8F0] text-gray-600 hover:bg-gray-300'}`}>Previous</button>
                            {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => (
                                <button key={p} onClick={() => setCurrentPage(p)} className={`px-4 py-2 rounded-md font-medium text-sm transition-all ${p === currentPage ? 'bg-[#2174C3] text-white' : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'}`}>{p}</button>
                            ))}
                            <button onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))} disabled={currentPage === totalPages} className={`px-4 py-2 rounded-md font-medium text-sm transition-all ${currentPage === totalPages ? 'bg-white border border-gray-200 text-gray-400 cursor-not-allowed' : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'}`}>Next</button>
                        </div>
                    </div>
                )}
            </div>

            {/* L1 MODAL */}
            {showL1Modal && selectedCard && (
                <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[92vh] overflow-hidden flex flex-col animate-in zoom-in duration-300">
                        <div className="h-1.5 bg-gradient-to-r from-[#aac8e4] via-[#c8dff0] to-[#b8d0e8] flex-shrink-0"></div>
                        <div className="px-8 pt-6 pb-7 overflow-y-auto flex-1">
                            <div className="flex items-start justify-between mb-1">
                                <h2 className="text-xl font-bold text-gray-800 leading-tight">{selectedCard.title}</h2>
                                <span className="ml-3 mt-0.5 shrink-0 text-[11px] font-bold px-2.5 py-1 bg-blue-100 text-blue-700 rounded-full">L1</span>
                            </div>
                            <hr className="my-4 border-gray-200" />

                            {selectedCard.is_submitted ? (
                                <div className="done-banner bg-gradient-to-br from-slate-50 to-gray-50 border border-gray-200">
                                    <p className="text-sm font-semibold text-gray-500 mb-5">Your Average Evaluation Score</p>
                                    <div className="flex justify-center mb-6">
                                        <div className="score-ring">
                                            <svg viewBox="0 0 120 120" width="120" height="120">
                                                <circle className="track" cx="60" cy="60" r="50" />
                                                <circle className="fill" cx="60" cy="60" r="50"
                                                    stroke={scoreColor(selectedCard.score || 0, 'L1')}
                                                    strokeDasharray={2 * Math.PI * 50}
                                                    strokeDashoffset={2 * Math.PI * 50 * (1 - (selectedCard.score || 0) / 4)}
                                                />
                                            </svg>
                                            <div className="score-num">
                                                <span className="text-3xl font-bold" style={{ color: scoreColor(selectedCard.score || 0, 'L1') }}>{Number(selectedCard.score || 0).toFixed(1)}</span>
                                                <span className="text-xs text-gray-400 font-medium">/ 4.0</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-bold mb-3" style={{ background: scoreColor(selectedCard.score || 0, 'L1') + '18', color: scoreColor(selectedCard.score || 0, 'L1') }}>
                                        {selectedCard.score >= 3.5 ? 'Very Satisfied' : selectedCard.score >= 2.5 ? 'Satisfied' : 'Needs Improvement'}
                                    </div>
                                    <p className="text-xs text-gray-400 mt-2">
                                        Dikirim: <span className="font-semibold">{selectedCard.submittedAt}</span>
                                    </p>
                                </div>
                            ) : !selectedCard.hasQuestions ? (
                                <div className="py-10 flex flex-col items-center text-center">
                                    <div className="w-16 h-16 rounded-2xl bg-blue-50 border-2 border-dashed border-blue-200 flex items-center justify-center mb-4">
                                        <svg className="w-8 h-8 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                                    </div>
                                    <p className="text-base font-bold text-gray-700 mb-1">Questions not available yet</p>
                                    <p className="text-sm text-gray-400">This evaluation does not have questions yet. Please check back later.</p>
                                </div>
                            ) : (
                                <div>
                                    <div className="grid grid-cols-4 gap-2 mb-5">
                                        <div className="flex flex-col items-center gap-1 py-2 px-1 rounded-xl border border-red-200 bg-red-50">
                                            <span className="text-lg">😞</span><span className="text-sm font-bold text-red-500">1</span>
                                            <span className="text-[10px] font-semibold text-red-400 text-center leading-tight">Dissatisfied</span>
                                        </div>
                                        <div className="flex flex-col items-center gap-1 py-2 px-1 rounded-xl border border-amber-200 bg-amber-50">
                                            <span className="text-lg">😐</span><span className="text-sm font-bold text-amber-500">2</span>
                                            <span className="text-[10px] font-semibold text-amber-500 text-center leading-tight">Less<br />Satisfied</span>
                                        </div>
                                        <div className="flex flex-col items-center gap-1 py-2 px-1 rounded-xl border border-emerald-200 bg-emerald-50">
                                            <span className="text-lg">🙂</span><span className="text-sm font-bold text-emerald-500">3</span>
                                            <span className="text-[10px] font-semibold text-emerald-500 text-center leading-tight">Satisfied</span>
                                        </div>
                                        <div className="flex flex-col items-center gap-1 py-2 px-1 rounded-xl border border-blue-200 bg-blue-50">
                                            <span className="text-lg">😄</span><span className="text-sm font-bold text-[#2174C3]">4</span>
                                            <span className="text-[10px] font-semibold text-[#2174C3] text-center leading-tight">Very<br />Satisfied</span>
                                        </div>
                                    </div>

                                    <div className="space-y-3">
                                        {(selectedCard.questions || []).map((q, index) => {
                                            const qType = (q.type || '').trim().toLowerCase();
                                            return (
                                                <div key={q.id} className="q-card">
                                                    <p className="q-text">{index + 1}. {q.q}</p>
                                                    {(qType === 'rating' || qType === 'rating scale') ? (
                                                        <div className="rating-row">
                                                            {[1, 2, 3, 4].map(val => (
                                                                <button key={val} onClick={() => setRating(q.id, val)} className={ratingClass(q.id, val)}>{val}</button>
                                                            ))}
                                                        </div>
                                                    ) : (
                                                        <textarea value={l1Answers[q.id] || ''} onChange={e => setL1Answers(prev => ({ ...prev, [q.id]: e.target.value }))} className="comment-area" placeholder="Write your feedback here..."></textarea>
                                                    )}
                                                </div>
                                            );
                                        })}
                                    </div>

                                    <div className="flex justify-end gap-3 mt-6">
                                        <button onClick={() => setShowL1Modal(false)} className="bg-[#878D94] hover:bg-[#607D8B] text-white px-3 py-1 text-sm rounded font-medium transition-colors cursor-pointer">Cancel</button>
                                        <button onClick={() => submitResponse('L1')} className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-4 py-1 text-sm rounded font-medium transition-colors shadow cursor-pointer">Submit</button>
                                    </div>
                                </div>
                            )}

                            {(selectedCard.is_submitted || !selectedCard.hasQuestions) && (
                                <div className="flex justify-end mt-5">
                                    <button onClick={() => setShowL1Modal(false)} className="bg-[#878D94] hover:bg-[#607D8B] text-white px-3 py-1 text-sm rounded font-medium transition-colors cursor-pointer">Close</button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* L2 MODAL */}
            {showL2Modal && selectedCard && (
                <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[92vh] overflow-hidden flex flex-col animate-in zoom-in duration-300">
                        <div className="h-1.5 bg-gradient-to-r from-[#6EE7B7] via-[#34D399] to-[#10B981] flex-shrink-0"></div>
                        <div className="px-8 pt-6 pb-7 overflow-y-auto flex-1">
                            <div className="flex items-start justify-between mb-1">
                                <h2 className="text-xl font-bold text-gray-800 leading-tight">{selectedCard.title}</h2>
                                <span className="ml-3 mt-0.5 shrink-0 text-[11px] font-bold px-2.5 py-1 bg-emerald-100 text-emerald-700 rounded-full">L2</span>
                            </div>
                            <hr className="my-4 border-gray-200" />

                            {selectedCard.is_submitted ? (
                                <div>
                                    <div className="done-banner bg-gradient-to-br from-slate-50 to-gray-50 border border-gray-200 mb-2">
                                        <p className="text-sm font-semibold text-gray-500 mb-5">Your Post Test Result</p>
                                        <div className="flex justify-center mb-4">
                                            <div className="score-ring">
                                                <svg viewBox="0 0 120 120" width="120" height="120">
                                                    <circle className="track" cx="60" cy="60" r="50" />
                                                    <circle className="fill" cx="60" cy="60" r="50" stroke={scoreColor(selectedCard.score || 0, 'L2')} strokeDasharray={2 * Math.PI * 50} strokeDashoffset={2 * Math.PI * 50 * (1 - (selectedCard.score || 0) / l2MaxScore)} />
                                                </svg>
                                                <div className="score-num">
                                                    <span className="text-3xl font-bold" style={{ color: scoreColor(selectedCard.score || 0) }}>{selectedCard.score || 0}</span>
                                                    <span className="text-xs text-gray-400 font-medium">/ {l2MaxScore}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-bold mb-3" style={{ background: scoreColor(selectedCard.score || 0, 'L2') + '18', color: scoreColor(selectedCard.score || 0, 'L2') }}>
                                            {scoreLabel(selectedCard.score || 0)}
                                        </div>
                                        <p className="text-xs text-gray-400 mt-1">
                                            Submitted: <span className="font-semibold">{selectedCard.submittedAt}</span>
                                        </p>
                                    </div>
                                </div>
                            ) : !selectedCard.hasQuestions ? (
                                <div className="py-10 flex flex-col items-center text-center">
                                    <div className="w-16 h-16 rounded-2xl bg-emerald-50 border-2 border-dashed border-emerald-200 flex items-center justify-center mb-4">
                                        <svg className="w-8 h-8 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5"><path strokeLinecap="round" strokeLinejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                    </div>
                                    <p className="text-base font-bold text-gray-700 mb-1">Questions not available yet</p>
                                    <p className="text-sm text-gray-400">This post test does not have questions yet. Please check back later.</p>
                                </div>
                            ) : (
                                <div>
                                    <p className="text-sm text-gray-400 mb-4">Answer the following questions. Each question has only one correct answer.</p>
                                    <div className="space-y-4">
                                        {(selectedCard.questions || []).map((q, qi) => (
                                            <div key={q.id} className="mc-question-card">
                                                <p className="mc-q-text">
                                                    <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-[#2174C3] text-white text-xs font-bold mr-2 flex-shrink-0" style={{ verticalAlign: 'middle' }}>{qi + 1}</span>
                                                    <span>{q.q}</span>
                                                </p>
                                                <div>
                                                    {(q.opts || []).map((opt, oi) => {
                                                        const label = String.fromCharCode(65 + oi);
                                                        return (
                                                            <div key={opt.id} onClick={() => selectL2Answer(q.id, opt.id)} className={l2OptionClass(q.id, opt.id)}>
                                                                <div className="mc-radio"><div className="mc-radio-dot"></div></div>
                                                                <span className="mc-opt-label">{label}</span>
                                                                <span className="mc-opt-text">{opt.text}</span>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            </div>
                                        ))}
                                    </div>

                                    <div className="mt-5 mb-1">
                                        <div className="flex justify-between items-center mb-1.5">
                                            <span className="text-xs text-gray-400 font-medium">Progress</span>
                                            <span className="text-xs font-semibold text-[#2174C3]">{Object.values(l2Answers).filter(v => v !== null).length}/{selectedCard.questions?.length} answered</span>
                                        </div>
                                        <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                            <div className="h-full bg-[#2174C3] rounded-full transition-all duration-300" style={{ width: `${l2Progress * 100}%` }}></div>
                                        </div>
                                    </div>

                                    <div className="flex justify-end gap-3 mt-5">
                                        <button onClick={() => setShowL2Modal(false)} className="bg-[#878D94] hover:bg-[#607D8B] text-white px-3 py-1 text-sm rounded font-medium transition-colors cursor-pointer">Cancel</button>
                                        <button onClick={() => submitResponse('L2')} disabled={l2Progress < 1} className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-4 py-1 text-sm rounded font-medium transition-colors shadow cursor-pointer disabled:opacity-50 disabled:bg-gray-300">Submit</button>
                                    </div>
                                </div>
                            )}

                            {(selectedCard.is_submitted || !selectedCard.hasQuestions) && (
                                <div className="flex justify-end mt-5">
                                    <button onClick={() => setShowL2Modal(false)} className="bg-[#878D94] hover:bg-[#607D8B] text-white px-3 py-1 text-sm rounded font-medium transition-colors cursor-pointer">Close</button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* CUSTOM ALERT MODAL */}
            {alertModal.show && (
                <div className="fixed inset-0 z-[500] flex items-center justify-center p-4 bg-black/60 backdrop-blur-[2px] animate-fade-in">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden transform animate-scale-up">
                        <div className="p-8 text-center">
                            <div className="w-16 h-16 bg-amber-50 rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-amber-100">
                                <svg className="w-8 h-8 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold text-gray-800 mb-2">{alertModal.title}</h3>
                            <p className="text-sm text-gray-500 leading-relaxed">
                                {alertModal.message}
                            </p>
                        </div>
                        <div className="p-4 bg-gray-50 border-t border-gray-100 flex justify-center">
                            <button
                                onClick={() => setAlertModal(prev => ({ ...prev, show: false }))}
                                className="w-full py-2.5 bg-[#2174C3] hover:bg-[#1A5E9D] text-white font-bold rounded-xl transition-all shadow-md active:scale-95"
                            >
                                OK
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </MainLayout>
    );
}
