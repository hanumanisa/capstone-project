import React, { useState, useEffect, useCallback } from 'react';
import MainLayout from '../components/MainLayout';
import api from '../api/axios';
import { getUserFromToken } from '../utils/auth';
import * as XLSX from 'xlsx';
import TnaPeriodModal from '../components/TnaPeriodModal';
import TnaMasterModal from '../components/TnaMasterModal';
import Toast from '../components/Toast';
import ConfirmModal from '../components/ConfirmModal';

import YearPicker from '../components/YearPicker';

const ITEMS_PER_PAGE = 50;

const TnaPage = () => {
    const [user, setUser] = useState(null);
    const [participants, setParticipants] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [divisionFilter, setDivisionFilter] = useState('All Division');
    const [courseFilter, setCourseFilter] = useState('All Course');
    const [activeYear, setActiveYear] = useState(new Date().getFullYear().toString());
    const [activeView, setActiveView] = useState("admin");
    const [currentPage, setCurrentPage] = useState(1);

    // Modals state
    const [showPeriodModal, setShowPeriodModal] = useState(false);
    const [showTnaModal, setShowTnaModal] = useState(false);
    const [selectedPeriod, setSelectedPeriod] = useState(null);
    const [selectedTna, setSelectedTna] = useState(null);

    // ─── UI State ───────────────────────────────────────────────────────
    const [toast, setToast] = useState(null);

    // Filter data
    const [divisions, setDivisions] = useState([]);
    const [courses, setCourses] = useState([]);

    useEffect(() => {
        const userData = getUserFromToken();
        if (userData) setUser(userData);

        const fetchFilters = async () => {
            try {
                const [resD, resC] = await Promise.all([
                    api.get('/api/divisions/'),
                    api.get('/api/courses/')
                ]);
                setDivisions(resD.data);
                setCourses(resC.data);
            } catch (err) {
                console.error('Failed to fetch filters:', err);
            }
        };
        fetchFilters();
    }, []);

    const isManagerialRole = user && ['Super Administrator', 'Administrator', 'Dean', 'Head of Division', 'Team Leader'].includes(user.role);
    const isMyTna = !isManagerialRole || activeView === 'employee';

    const fetchParticipants = useCallback(async () => {
        setLoading(true);
        try {
            const params = {
                search: searchTerm,
            };
            if (!isMyTna && divisionFilter && divisionFilter !== 'All Division') params.division = divisionFilter;
            if (!isMyTna && courseFilter && courseFilter !== 'All Course') params.course_name = courseFilter;
            if (activeYear) params.year = activeYear;
            params.view_mode = activeView;

            const res = await api.get('/api/tna-participant/', { params });
            setParticipants(res.data);
        } catch (err) {
            console.error('Failed to fetch participants:', err);
        } finally {
            setLoading(false);
        }
    }, [searchTerm, divisionFilter, courseFilter, activeYear, activeView, isMyTna]);

    useEffect(() => {
        fetchParticipants();
    }, [fetchParticipants]);

    const isAdmin = user && ['Super Administrator', 'Administrator'].includes(user.role) && activeView === 'admin';

    // ─── Filter Logic ─────────────────────────────────────────────────────
    const filteredParticipants = participants;

    // ─── Pagination ─────────────────────────────────────────────────────
    const totalPages = Math.ceil(filteredParticipants.length / ITEMS_PER_PAGE);
    const paginatedParticipants = filteredParticipants.slice(
        (currentPage - 1) * ITEMS_PER_PAGE,
        currentPage * ITEMS_PER_PAGE
    );

    const handleEditTna = (tnaId) => {
        if (!isAdmin) return;
        setSelectedTna({ tna_id: tnaId });
        setShowTnaModal(true);
    };

    const handleExport = () => {
        if (!participants.length) {
            alert('No data available to export.');
            return;
        }
        const exportData = participants.map(item => ({
            'Course Category': item.category_name,
            'Course Name': item.course_name,
            'NIK': item.nik,
            'Name of Employee': item.employee_name,
            'Division': item.division_name,
            'Position': item.position_name,
            'TNA Fulfillment': item.tna_fulfilled,
            'Fulfillment Training': item.fulfillment_trainings || '-',
        }));
        const ws = XLSX.utils.json_to_sheet(exportData);
        // Column widths
        const wscols = [
            { wch: 25 }, { wch: 35 }, { wch: 15 }, { wch: 30 },
            { wch: 25 }, { wch: 25 }, { wch: 15 }, { wch: 35 }
        ];
        ws['!cols'] = wscols;
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'TNA Report');
        XLSX.writeFile(wb, 'TNA Report.xlsx');
    };

    return (
        <MainLayout>
            {isManagerialRole && (
                <div className="flex space-x-8 border-b border-gray-300 mb-6 px-4 sm:px-0">
                    <button
                        onClick={() => setActiveView('admin')}
                        className={`pb-3 px-1 font-bold text-xl transition-colors ${activeView === 'admin'
                            ? 'text-[#2174C3] border-b-4 border-[#2174C3]'
                            : 'text-gray-400 hover:text-[#2174C3]'
                            }`}
                    >
                        {['Super Administrator', 'Administrator', 'Dean'].includes(user?.role) ? 'Company TNA' : 'Division TNA'}
                    </button>
                    <button
                        onClick={() => setActiveView('employee')}
                        className={`pb-3 px-1 font-bold text-xl transition-colors ${activeView === 'employee'
                            ? 'text-[#2174C3] border-b-4 border-[#2174C3]'
                            : 'text-gray-400 hover:text-[#2174C3]'
                            }`}
                    >
                        My TNA
                    </button>
                </div>
            )}
            <div className="animate-in fade-in duration-500">
                {/* ─── Toolbar ─────────────────────────────────────────────── */}
                <div className="bg-white p-3 rounded-xl shadow-sm border border-gray-100 flex flex-col sm:flex-row items-center gap-3 mb-8 transition-all hover:shadow-md sticky top-0 z-30">
                    <div className="relative w-full sm:w-1/3">
                        <input
                            type="text"
                            placeholder="Search"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-4 pr-10 py-2 rounded-lg border-none bg-gray-100 focus:bg-white focus:ring-1 focus:ring-[#2174C3] transition-all text-gray-600 placeholder-gray-400"
                        />
                        <span className="absolute right-3 top-2.5 text-gray-400 pointer-events-none">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                            </svg>
                        </span>
                    </div>

                    {!isMyTna && !['Head of Division', 'Team Leader', 'Employee'].includes(user?.role) && (
                        <div className="relative w-full sm:w-48">
                            <select
                                value={divisionFilter}
                                onChange={(e) => setDivisionFilter(e.target.value)}
                                className="w-full border-none rounded-lg pl-4 pr-10 py-2 text-sm text-gray-600 bg-gray-100 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#2174C3] appearance-none bg-no-repeat bg-right-4"
                                style={{
                                    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M19 9l-7 7-7-7'/%3e%3c/svg%3e")`,
                                    backgroundSize: '20px 20px',
                                    backgroundPosition: 'right 12px center'
                                }}
                            >
                                <option value="All Division">All Division</option>
                                {divisions.map((d, i) => (
                                    <option key={i} value={d.division_name}>{d.division_name}</option>
                                ))}
                            </select>
                        </div>
                    )}

                    {!isMyTna && (
                        <div className="relative w-full sm:w-48">
                            <select
                                value={courseFilter}
                                onChange={(e) => setCourseFilter(e.target.value)}
                                className="w-full border-none rounded-lg pl-4 pr-10 py-2 text-sm text-gray-600 bg-gray-100 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#2174C3] appearance-none bg-no-repeat bg-right-4"
                                style={{
                                    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M19 9l-7 7-7-7'/%3e%3c/svg%3e")`,
                                    backgroundSize: '20px 20px',
                                    backgroundPosition: 'right 12px center'
                                }}
                            >
                                <option value="All Course">All Course</option>
                                {Array.from(new Set(courses.map(c => c.course_name)))
                                    .sort()
                                    .map((name, i) => (
                                        <option key={i} value={name}>{name}</option>
                                    ))}
                            </select>
                        </div>
                    )}

                    <div className="flex-1 flex justify-end items-center space-x-6 shrink-0">
                        <YearPicker selectedYear={activeYear} onYearChange={(y) => setActiveYear(y)} />
                        {isAdmin && (
                            <div className="flex gap-2">
                                <button
                                    onClick={() => { setSelectedPeriod(null); setShowPeriodModal(true); }}
                                    className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white w-28 py-1 rounded-lg font-medium flex items-center justify-center text-sm shadow-sm transition-all cursor-pointer"
                                >
                                    <span className="mr-1 text-lg font-bold">+</span> Period
                                </button>
                                <button
                                    onClick={() => { setSelectedTna(null); setShowTnaModal(true); }}
                                    className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white w-28 py-1 rounded-lg font-medium flex items-center justify-center text-sm shadow-sm transition-all cursor-pointer"
                                >
                                    <span className="mr-1 text-lg font-bold">+</span> TNA
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                <div className="flex justify-between items-end mb-8">
                    <div>
                        <h1 className="text-4xl font-bold text-gray-800 tracking-tight">Training Needs Analysis</h1>
                    </div>
                    <button
                        onClick={handleExport}
                        className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white w-28 py-2 rounded-lg font-medium shadow-sm transition-all text-sm cursor-pointer"
                    >
                        Report
                    </button>
                </div>

                <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden transition-all h-[calc(100vh-350px)] flex flex-col">
                    <div className="custom-scrollbar overflow-auto flex-1">
                        <table className="w-full text-left text-sm table-auto border-separate border-spacing-0">
                            <thead className="bg-[#5C85BB] text-white text-xs uppercase tracking-widest sticky top-0 z-20">
                                <tr>
                                    <th className="px-6 py-5 font-bold whitespace-nowrap border-b border-blue-200 bg-[#5C85BB]">Course Category</th>
                                    <th className="px-6 py-5 font-bold whitespace-nowrap border-b border-blue-200 bg-[#5C85BB]">Course Name</th>
                                    <th className="px-6 py-5 font-bold whitespace-nowrap border-b border-blue-200 bg-[#5C85BB]">NIK</th>
                                    <th className="px-6 py-5 font-bold whitespace-nowrap border-b border-blue-200 bg-[#5C85BB]">Name of Employee</th>
                                    <th className="px-6 py-5 font-bold whitespace-nowrap border-b border-blue-200 bg-[#5C85BB]">Division</th>
                                    <th className="px-6 py-5 font-bold whitespace-nowrap border-b border-blue-200 bg-[#5C85BB]">Position</th>
                                    <th className="px-6 py-5 font-bold whitespace-nowrap text-center border-b border-blue-200 bg-[#5C85BB]">TNA Fulfillment</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-50 whitespace-nowrap">
                                {loading ? (
                                    <tr>
                                        <td colSpan="7" className="px-6 py-20 text-center">
                                            <div className="flex flex-col items-center justify-center space-y-3">
                                                <div className="w-10 h-10 border-4 border-blue-100 border-t-[#2174C3] rounded-full animate-spin"></div>
                                                <span className="text-gray-400 font-medium">Analyzing TNA Data...</span>
                                            </div>
                                        </td>
                                    </tr>
                                ) : paginatedParticipants.length === 0 ? (
                                    <tr>
                                        <td colSpan="7" className="px-6 py-20 text-center text-gray-400 font-medium">No data available</td>
                                    </tr>
                                ) : (
                                    paginatedParticipants.map((item) => (
                                        <tr key={item.tna_participant_id} className="hover:bg-blue-50/50 transition-all group">
                                            <td className="px-6 py-4 text-gray-600">{item.category_name}</td>
                                            <td
                                                className={`px-6 py-4 font-semibold text-[#2174C3] transition-colors ${isAdmin ? 'cursor-pointer hover:underline hover:text-[#1A5E9D]' : ''}`}
                                                onClick={() => handleEditTna(item.tna)}
                                            >
                                                {item.course_name}
                                            </td>
                                            <td className="px-6 py-4 text-gray-600">{item.nik}</td>
                                            <td className="px-6 py-4 text-gray-600">{item.employee_name}</td>
                                            <td className="px-6 py-4 text-gray-600">{item.division_name}</td>
                                            <td className="px-6 py-4 text-gray-600">{item.position_name}</td>
                                            <td className="px-6 py-4 text-center text-gray-600">{item.tna_fulfilled}</td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Pagination */}
                {totalPages > 1 ? (
                    <div className="sticky bottom-0 bg-[#F4F7FA]/95 backdrop-blur-sm py-4 flex flex-col items-end gap-2 z-20 mt-4 border-t border-gray-100">
                        <div className="flex items-center space-x-1">
                            <button
                                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                className="px-4 py-2 bg-[#E2E8F0] text-gray-500 rounded-md font-medium hover:bg-gray-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                disabled={currentPage === 1}
                            >Previous</button>

                            {(() => {
                                const pages = [];
                                const maxVisible = 5;
                                let start = Math.max(1, currentPage - 2);
                                let end = Math.min(totalPages, start + maxVisible - 1);

                                if (end - start + 1 < maxVisible) {
                                    start = Math.max(1, end - maxVisible + 1);
                                }

                                if (start > 1) {
                                    pages.push(
                                        <button key={1} onClick={() => setCurrentPage(1)} className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-md font-medium hover:bg-gray-50 transition-all">1</button>
                                    );
                                    if (start > 2) pages.push(<span key="sep1" className="px-2 text-gray-400">...</span>);
                                }

                                for (let i = start; i <= end; i++) {
                                    pages.push(
                                        <button
                                            key={i}
                                            onClick={() => setCurrentPage(i)}
                                            className={`px-4 py-2 rounded-md font-medium transition-all ${currentPage === i ? 'bg-[#2174C3] text-white' : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'}`}
                                        >{i}</button>
                                    );
                                }

                                if (end < totalPages) {
                                    if (end < totalPages - 1) pages.push(<span key="sep2" className="px-2 text-gray-400">...</span>);
                                    pages.push(
                                        <button key={totalPages} onClick={() => setCurrentPage(totalPages)} className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-md font-medium hover:bg-gray-50 transition-all">{totalPages}</button>
                                    );
                                }

                                return pages;
                            })()}

                            <button
                                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-md font-medium hover:bg-gray-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                disabled={currentPage === totalPages}
                            >Next</button>
                        </div>
                        <div className="text-xs text-gray-400 font-medium">
                            Showing {((currentPage - 1) * ITEMS_PER_PAGE) + 1}–{Math.min(currentPage * ITEMS_PER_PAGE, filteredParticipants.length)} of {filteredParticipants.length} TNA
                        </div>
                    </div>
                ) : (
                    filteredParticipants.length > 0 && (
                        <div className="sticky bottom-0 bg-[#F4F7FA]/95 backdrop-blur-sm py-4 flex justify-end items-center z-20 mt-4 border-t border-gray-100">
                            <div className="text-xs text-gray-400 font-medium">
                                Showing 1–{filteredParticipants.length} of {filteredParticipants.length} TNA
                            </div>
                        </div>
                    )
                )}
            </div>

            {/* Modals */}
            <TnaPeriodModal
                isOpen={showPeriodModal}
                onClose={() => setShowPeriodModal(false)}
                period={selectedPeriod}
                onSave={fetchParticipants}
                setToast={setToast}
            />
            <TnaMasterModal
                isOpen={showTnaModal}
                onClose={() => setShowTnaModal(false)}
                tnaRecord={selectedTna}
                onSave={fetchParticipants}
                setToast={setToast}
            />

            {/* ─── Toast Notifications ─────────────────────────────────── */}
            {toast && (
                <Toast
                    message={toast.message}
                    type={toast.type}
                    onClose={() => setToast(null)}
                />
            )}

        </MainLayout>
    );
};

export default TnaPage;
