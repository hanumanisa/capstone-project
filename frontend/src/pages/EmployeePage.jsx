import React, { useState, useEffect, useCallback } from 'react';
import MainLayout from '../components/MainLayout';
import api from '../api/axios';
import * as XLSX from 'xlsx';
import YearPicker from '../components/YearPicker';
import { getUserFromToken } from '../utils/auth';


const ITEMS_PER_PAGE = 50;

const EmployeePage = () => {
    const [employees, setEmployees] = useState([]);
    const [divisions, setDivisions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedDivision, setSelectedDivision] = useState('All Division');
    const [user, setUser] = useState(null);

    useEffect(() => {
        const userData = getUserFromToken();
        if (userData) {
            setUser(userData);
        }
    }, []);

    useEffect(() => {
        if (employees.length > 0 && user && ['Head of Division', 'Team Leader'].includes(user.role) && selectedDivision === 'All Division') {
            setSelectedDivision(employees[0].division_name);
        }
    }, [employees, user, selectedDivision]);
    const [selectedYear, setSelectedYear] = useState(new Date().getFullYear().toString());
    const [activeView, setActiveView] = useState("admin");
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalCount, setTotalCount] = useState(0);
    const [showAttendanceModal, setShowAttendanceModal] = useState(false);
    const [showTnaModal, setShowTnaModal] = useState(false);
    const [selectedEmployee, setSelectedEmployee] = useState(null);
    const [exporting, setExporting] = useState(false);

    const openAttendanceDetail = (emp) => {
        setSelectedEmployee(emp);
        setShowAttendanceModal(true);
    };

    const openTnaDetail = (emp) => {
        setSelectedEmployee(emp);
        setShowTnaModal(true);
    };

    const isManagerialRole = user && ['Super Administrator', 'Administrator', 'Dean', 'Head of Division', 'Team Leader'].includes(user.role);
    const isMyData = !isManagerialRole || activeView === 'employee';

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const [empRes, divRes] = await Promise.all([
                api.get(`/api/employee/?page=${currentPage}&search=${searchTerm}&division=${isMyData ? '' : (selectedDivision === 'All Division' ? '' : selectedDivision)}&year=${selectedYear}&view_mode=${activeView}`),
                api.get('/api/divisions/')
            ]);

            if (empRes.data.results) {
                setEmployees(empRes.data.results);
                setTotalCount(empRes.data.count);
                setTotalPages(Math.ceil(empRes.data.count / ITEMS_PER_PAGE));
            } else {
                setEmployees(empRes.data);
                setTotalCount(empRes.data.length);
                setTotalPages(Math.ceil(empRes.data.length / ITEMS_PER_PAGE));
            }
            setDivisions(divRes.data);
        } catch (err) {
            console.error('Failed to fetch data:', err);
        } finally {
            setLoading(false);
        }
    }, [currentPage, searchTerm, selectedDivision, selectedYear, activeView, isMyData]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    // Since we use backend pagination, filteredData is just for local search/filtering if needed,
    // but we primarily rely on the backend now.
    const paginatedData = employees;

    const getPageNumbers = () => {
        const pages = [];
        const maxVisible = 5;
        let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
        let end = Math.min(totalPages, start + maxVisible - 1);
        if (end - start + 1 < maxVisible) {
            start = Math.max(1, end - maxVisible + 1);
        }
        for (let i = start; i <= end; i++) pages.push(i);
        return pages;
    };

    return (
        <MainLayout>
            {isManagerialRole && (
                <div className="flex space-x-8 border-b border-gray-300 mb-6 px-4 sm:px-0 mt-4">
                    <button
                        onClick={() => setActiveView('admin')}
                        className={`pb-3 px-1 font-bold text-xl transition-colors ${activeView === 'admin'
                            ? 'text-[#2174C3] border-b-4 border-[#2174C3]'
                            : 'text-gray-400 hover:text-[#2174C3]'
                            }`}
                    >
                        {['Super Administrator', 'Administrator', 'Dean'].includes(user?.role) ? 'Company Employees' : 'Division Employees'}
                    </button>
                    <button
                        onClick={() => setActiveView('employee')}
                        className={`pb-3 px-1 font-bold text-xl transition-colors ${activeView === 'employee'
                            ? 'text-[#2174C3] border-b-4 border-[#2174C3]'
                            : 'text-gray-400 hover:text-[#2174C3]'
                            }`}
                    >
                        My Data
                    </button>
                </div>
            )}
            <div className="bg-white p-3 rounded-xl shadow-sm border border-gray-100 flex flex-col sm:flex-row justify-between items-center gap-3 mb-8 sticky top-0 z-30">
                <div className="relative w-full sm:w-1/3">
                    <input
                        type="text"
                        placeholder="Search"
                        value={searchTerm}
                        onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
                        className="w-full pl-4 pr-10 py-2 rounded-lg border-none bg-gray-100 focus:bg-white focus:ring-1 focus:ring-[#2174C3] transition-all text-gray-600 placeholder-gray-400 outline-none hover:bg-gray-200/50"
                    />
                    <span className="absolute right-3 top-2.5 text-gray-400 pointer-events-none">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </span>
                </div>

                {/* Search bar all division samakan dengan dashboard style */}
                {!isMyData && (!user || !['Head of Division', 'Team Leader'].includes(user.role)) && (
                    <div className="relative w-full sm:w-60">
                        <select
                            value={selectedDivision}
                            onChange={(e) => { setSelectedDivision(e.target.value); setCurrentPage(1); }}
                            className="w-full border-none rounded-lg px-4 py-2 text-sm text-gray-600 bg-gray-100 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#2174C3] appearance-none bg-no-repeat bg-right-4"
                            style={{
                                backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M19 9l-7 7-7-7'/%3e%3c/svg%3e")`,
                                backgroundSize: '20px 20px',
                                backgroundPosition: 'right 12px center'
                            }}
                        >
                            <option value="All Division">All Division</option>
                            {divisions.map((div, i) => (
                                <option key={i} value={div.division_name}>{div.division_name}</option>
                            ))}
                        </select>
                    </div>
                )}

                <div className="flex-1 flex items-center justify-end gap-6">
                    <YearPicker selectedYear={selectedYear} onYearChange={(y) => { setSelectedYear(y); setCurrentPage(1); }} />
                    <div className="flex gap-2">
                    </div>
                </div>
            </div>

            <h1 className="text-4xl font-bold text-gray-800 tracking-tight mb-6">Employees</h1>

            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden transition-all h-[calc(100vh-350px)] flex flex-col">
                <div className="custom-scrollbar overflow-auto flex-1">
                    <table className="w-full text-left text-sm min-w-[2000px] border-collapse">
                        <thead className="bg-[#5C85BB] text-white text-xs uppercase tracking-wider sticky top-0 z-20">
                            <tr>
                                <th className="px-4 py-3 text-center sticky left-0 z-30 bg-[#5C85BB] w-[100px]">NIK</th>
                                <th className="px-4 py-3 sticky left-[100px] z-30 bg-[#5C85BB] border-r border-white/20">Nama</th>
                                <th className="px-4 py-3">Division</th>
                                <th className="px-4 py-3">Level</th>
                                <th className="px-4 py-3">Position</th>
                                <th className="px-4 py-3">Special Position</th>
                                <th className="px-4 py-3 text-center">Attendance</th>
                                <th className="px-4 py-3 text-center">Inhouse Training</th>
                                <th className="px-4 py-3 text-center">Public Training</th>
                                <th className="px-4 py-3 text-center">Knowledge Sharing</th>
                                <th className="px-4 py-3 text-center">E-Learning</th>
                                <th className="px-4 py-3 text-center">Total Hours</th>
                                <th className="px-4 py-3 text-center">Inhouse Tr. Hours</th>
                                <th className="px-4 py-3 text-center">Public Tr. Hours</th>
                                <th className="px-4 py-3 text-center">KS Hours</th>
                                <th className="px-4 py-3 text-center">E-Learning Hours</th>
                                <th className="px-4 py-3 text-center">TNA</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 bg-white">
                            {loading ? (
                                <tr><td colSpan="17" className="px-6 py-12 text-center text-gray-400">Loading...</td></tr>
                            ) : paginatedData.length === 0 ? (
                                <tr><td colSpan="17" className="px-6 py-12 text-center text-gray-400 font-medium">No data available</td></tr>
                            ) : (
                                paginatedData.map((item) => (
                                    <tr key={item.nik} className="hover:bg-blue-50/30 transition-colors">
                                        <td className="px-4 py-3 text-center font-bold text-gray-600 sticky left-0 z-10 bg-white group-hover:bg-blue-50/30 w-[100px]">{item.nik}</td>
                                        <td className="px-4 py-3 text-gray-600 font-bold sticky left-[100px] z-10 bg-white group-hover:bg-blue-50/30 border-r border-gray-100">{item.full_name}</td>
                                        <td className="px-4 py-3 text-gray-600">{item.division_name}</td>
                                        <td className="px-4 py-3 text-gray-600">{item.level}</td>
                                        <td className="px-4 py-3 text-gray-600">{item.position_name}</td>
                                        <td className="px-4 py-3 text-gray-500 italic">{item.special_position || '-'}</td>
                                        <td className="px-4 py-3 text-center font-bold">
                                            <button
                                                onClick={() => openAttendanceDetail(item)}
                                                className="text-[#2174C3] cursor-pointer"
                                             >
                                                 {item.attendance}
                                             </button>
                                         </td>
                                         <td className="px-4 py-3 text-center text-gray-600">{item.inhouse_training}</td>
                                         <td className="px-4 py-3 text-center text-gray-600">{item.public_training}</td>
                                         <td className="px-4 py-3 text-center text-gray-600">{item.knowledge_sharing}</td>
                                         <td className="px-4 py-3 text-center text-gray-600">{item.elearning}</td>
                                         <td className="px-4 py-3 text-center font-bold text-gray-600">{item.total_hours}</td>
                                         <td className="px-4 py-3 text-center text-gray-600">{item.inhouse_hours}</td>
                                         <td className="px-4 py-3 text-center text-gray-600">{item.public_hours}</td>
                                         <td className="px-4 py-3 text-center text-gray-600">{item.ks_hours}</td>
                                         <td className="px-4 py-3 text-center text-gray-600">{item.elearning_hours}</td>
                                         <td className="px-4 py-3 text-center font-bold">
                                             <button
                                                 onClick={() => openTnaDetail(item)}
                                                 className="text-[#2174C3] cursor-pointer"
                                             >
                                                 {item.tna_count}
                                             </button>
                                         </td>
                                     </tr>
                                 ))
                             )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Pagination */}
            {!loading && (
                totalPages > 1 ? (
                    <div className="sticky bottom-0 bg-[#F4F7FA]/95 backdrop-blur-sm py-4 flex flex-col items-end gap-2 z-20 mt-4 border-t border-gray-100">
                        <div className="flex items-center space-x-1">
                            <button
                                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                disabled={currentPage === 1}
                                className="px-4 py-2 bg-[#E2E8F0] text-gray-500 rounded-md font-medium hover:bg-gray-300 transition-colors disabled:opacity-50"
                            >
                                Previous
                            </button>
                            {getPageNumbers().map(page => (
                                <button
                                    key={page}
                                    onClick={() => setCurrentPage(page)}
                                    className={`px-4 py-2 rounded-md font-medium transition-colors ${currentPage === page ? 'bg-[#2174C3] text-white' : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'}`}
                                >
                                    {page}
                                </button>
                            ))}
                            <button
                                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                disabled={currentPage === totalPages}
                                className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-md font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
                            >
                                Next
                            </button>
                        </div>
                        <div className="text-xs text-gray-400 font-medium">
                            Showing {(currentPage - 1) * ITEMS_PER_PAGE + 1}–{Math.min(currentPage * ITEMS_PER_PAGE, totalCount)} of {totalCount} employees
                        </div>
                    </div>
                ) : (
                    totalCount > 0 && (
                        <div className="sticky bottom-0 bg-[#F4F7FA]/95 backdrop-blur-sm py-4 flex justify-end items-center z-20 mt-4 border-t border-gray-100">
                            <div className="text-xs text-gray-400 font-medium">
                                Showing 1–{totalCount} of {totalCount} employees
                            </div>
                        </div>
                    )
                )
            )}


            {/* Attendance Detail Modal */}
            {showAttendanceModal && selectedEmployee && (
                <div className="fixed inset-0 z-[150] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-in zoom-in duration-300">
                        <div className="px-10 py-6 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                            <div className="flex flex-col">
                                <h3 className="font-bold text-gray-800 text-lg">Attendance Details</h3>
                                <p className="text-sm text-[#2174C3] font-semibold">{selectedEmployee.full_name} ({selectedEmployee.nik})</p>
                            </div>

                        </div>
                        <div className="p-6 max-h-[60vh] overflow-y-auto">
                            {selectedEmployee.attendance_details?.length > 0 ? (
                                <table className="w-full text-sm">
                                    <thead className="bg-gray-50 text-gray-500 uppercase text-[10px] font-bold">
                                        <tr>
                                            <th className="px-4 py-3 text-left">Training Title</th>
                                            <th className="px-4 py-2 text-center w-24">Hours</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-100">
                                        {selectedEmployee.attendance_details.map((detail, idx) => (
                                            <tr key={idx} className="hover:bg-gray-50 transition-colors">
                                                <td className="px-4 py-4 text-gray-700 font-bold leading-relaxed">{detail.title}</td>
                                                <td className="px-4 py-4 text-center">
                                                    <span className="bg-blue-50 text-[#2174C3] px-3 py-1 rounded-full font-bold text-xs">
                                                        {detail.hours.toFixed(1)}h
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            ) : (
                                <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                                    <svg className="w-12 h-12 mb-3 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                    <p className="font-medium">No attendance records found.</p>
                                </div>
                            )}
                        </div>
                        <div className="px-6 py-4 border-t border-gray-100 flex justify-end bg-gray-50">
                            <button onClick={() => setShowAttendanceModal(false)} className="bg-[#878D94] hover:bg-[#607D8B] text-white px-3 py-1 text-sm rounded font-medium transition-colors cursor-pointer">
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* TNA Detail Modal */}
            {showTnaModal && selectedEmployee && (
                <div className="fixed inset-0 z-[150] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-in zoom-in duration-300">
                        <div className="px-10 py-6 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                            <div className="flex flex-col">
                                <h3 className="font-bold text-gray-800 text-lg">TNA Details</h3>
                                <p className="text-sm text-[#2174C3] font-semibold">{selectedEmployee.full_name} ({selectedEmployee.nik})</p>
                            </div>
                        </div>
                        <div className="p-6 max-h-[60vh] overflow-y-auto">
                            {selectedEmployee.tna_details?.length > 0 ? (
                                <table className="w-full text-sm">
                                    <thead className="bg-gray-50 text-gray-500 uppercase text-[10px] font-bold">
                                        <tr>
                                            <th className="px-4 py-3 text-left">Nama TNA</th>
                                            <th className="px-4 py-2 text-center w-28">Fulfillment</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-100">
                                        {selectedEmployee.tna_details.map((detail, idx) => (
                                            <tr key={idx} className="hover:bg-gray-50 transition-colors">
                                                <td className="px-4 py-4 text-gray-700 font-bold leading-relaxed">{detail.course_name}</td>
                                                <td className="px-4 py-4 text-center">
                                                    <span className={`px-3 py-1 rounded-full font-bold text-xs ${
                                                        detail.fulfilled === 1 
                                                            ? 'bg-green-50 text-green-600' 
                                                            : 'bg-red-50 text-red-600'
                                                    }`}>
                                                        {detail.fulfilled}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            ) : (
                                <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                                    <svg className="w-12 h-12 mb-3 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                                    <p className="font-medium">No TNA records found.</p>
                                </div>
                            )}
                        </div>
                        <div className="px-6 py-4 border-t border-gray-100 flex justify-end bg-gray-50">
                            <button onClick={() => setShowTnaModal(false)} className="bg-[#878D94] hover:bg-[#607D8B] text-white px-3 py-1 text-sm rounded font-medium transition-colors cursor-pointer">
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </MainLayout>
    );
};

export default EmployeePage;
