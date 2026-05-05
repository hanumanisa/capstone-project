import React, { useState, useEffect, useCallback } from 'react';
import MainLayout from '../components/MainLayout';
import api from '../api/axios';
import * as XLSX from 'xlsx';

const ITEMS_PER_PAGE = 50;

const EmployeePage = () => {
    const [employees, setEmployees] = useState([]);
    const [divisions, setDivisions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedDivision, setSelectedDivision] = useState('All Division');
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalCount, setTotalCount] = useState(0);
    const [showAttendanceModal, setShowAttendanceModal] = useState(false);
    const [selectedEmployee, setSelectedEmployee] = useState(null);

    const openAttendanceDetail = (emp) => {
        setSelectedEmployee(emp);
        setShowAttendanceModal(true);
    };

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const [empRes, divRes] = await Promise.all([
                api.get(`/api/employee/?page=${currentPage}&search=${searchTerm}&division=${selectedDivision === 'All Division' ? '' : selectedDivision}`),
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
    }, [currentPage, searchTerm, selectedDivision]);

    const handleExport = () => {
        if (!employees.length) {
            alert('Tidak ada data untuk diekspor.');
            return;
        }
        const exportData = employees.map(emp => ({
            'NIK': emp.nik,
            'Nama': emp.full_name,
            'Division': emp.division_name,
            'Level': emp.level,
            'Position': emp.position_name,
            'Special Position': emp.special_position || '-',
            'Attendance': emp.attendance,
            'Inhouse Training': emp.inhouse_training,
            'Public Training': emp.public_training,
            'Knowledge Sharing': emp.knowledge_sharing,
            'E-Learning': emp.elearning,
            'IHT + Public': emp.iht_plus_public,
            'Hours': emp.total_hours,
            'Inhouse Tr. Hours': emp.inhouse_hours,
            'Public Tr. Hours': emp.public_hours,
            'KS Hours': emp.ks_hours,
            'E-Learning Hours': emp.elearning_hours,
            'TNA Count': emp.tna_count,
            'TNA Fulfilled': emp.tna_fulfilled
        }));
        const ws = XLSX.utils.json_to_sheet(exportData);
        const wscols = [
            { wch: 10 }, { wch: 30 }, { wch: 25 }, { wch: 10 },
            { wch: 25 }, { wch: 20 }, { wch: 12 }, { wch: 18 },
            { wch: 18 }, { wch: 18 }, { wch: 15 }, { wch: 15 },
            { wch: 10 }, { wch: 18 }, { wch: 18 }, { wch: 15 },
            { wch: 18 }, { wch: 12 }, { wch: 15 }
        ];
        ws['!cols'] = wscols;
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'Employee Report');
        XLSX.writeFile(wb, 'Employee Report.xlsx');
    };

    const handleDivisionExport = () => {
        if (!employees.length) {
            alert('Tidak ada data untuk diekspor.');
            return;
        }

        const wb = XLSX.utils.book_new();
        const header = [['NIK', 'Nama', 'Total Hours', 'Training Title']];
        const rows = [];
        const merges = [];

        let currentRow = 1; // Start after header

        employees.forEach(emp => {
            const details = emp.attendance_details || [];
            const numRows = details.length || 1;

            if (details.length === 0) {
                rows.push([emp.nik, emp.full_name, emp.total_hours, '-']);
                currentRow++;
            } else {
                details.forEach((d, idx) => {
                    rows.push([
                        emp.nik,
                        emp.full_name,
                        emp.total_hours,
                        d.title
                    ]);
                });

                if (numRows > 1) {
                    merges.push({ s: { r: currentRow, c: 0 }, e: { r: currentRow + numRows - 1, c: 0 } }); // NIK
                    merges.push({ s: { r: currentRow, c: 1 }, e: { r: currentRow + numRows - 1, c: 1 } }); // Nama
                    merges.push({ s: { r: currentRow, c: 2 }, e: { r: currentRow + numRows - 1, c: 2 } }); // Total Hours
                }
                currentRow += numRows;
            }
        });

        const ws = XLSX.utils.aoa_to_sheet([...header, ...rows]);
        ws['!merges'] = merges;
        
        // Add styling for borders and alignment if possible (xlsx basic has limits)
        ws['!cols'] = [
            { wch: 12 }, { wch: 35 }, { wch: 15 }, { wch: 70 }
        ];

        XLSX.utils.book_append_sheet(wb, ws, 'Division Report');
        XLSX.writeFile(wb, `Division Report_${selectedDivision}.xlsx`);
    };

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
            <div className="bg-white px-4 py-3 rounded-xl shadow-sm border border-gray-100 flex flex-col sm:flex-row items-center gap-4 mb-8">
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
                        <option>All Division</option>
                        {divisions.map(div => (
                            <option key={div.division_id} value={div.division_name}>{div.division_name}</option>
                        ))}
                    </select>
                </div>
                
                <div className="flex-1 flex justify-end gap-2">
                    <button 
                        onClick={handleExport}
                        className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-4 py-2 rounded-lg font-medium shadow-sm transition-all text-sm cursor-pointer whitespace-nowrap"
                    >
                        Employee Report
                    </button>
                    <button 
                        onClick={handleDivisionExport}
                        className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-4 py-2 rounded-lg font-medium shadow-sm transition-all text-sm cursor-pointer whitespace-nowrap"
                    >
                        Division Report
                    </button>
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
                                <th className="px-4 py-3 text-center">IHT + Public</th>
                                <th className="px-4 py-3 text-center">Hours</th>
                                <th className="px-4 py-3 text-center">Inhouse Tr. Hours</th>
                                <th className="px-4 py-3 text-center">Public Tr. Hours</th>
                                <th className="px-4 py-3 text-center">KS Hours</th>
                                <th className="px-4 py-3 text-center">E-Learning Hours</th>
                                <th className="px-4 py-3 text-center">TNA Count</th>
                                <th className="px-4 py-3 text-center">TNA Fulfilled</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 bg-white">
                            {loading ? (
                                <tr><td colSpan="19" className="px-6 py-12 text-center text-gray-400">Loading...</td></tr>
                            ) : paginatedData.length === 0 ? (
                                <tr><td colSpan="19" className="px-6 py-12 text-center text-gray-400">No employees found.</td></tr>
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
                                        <td className="px-4 py-3 text-center text-gray-600">{item.iht_plus_public}</td>
                                        <td className="px-4 py-3 text-center font-bold text-gray-600">{item.total_hours}</td>
                                        <td className="px-4 py-3 text-center text-gray-600">{item.inhouse_hours}</td>
                                        <td className="px-4 py-3 text-center text-gray-600">{item.public_hours}</td>
                                        <td className="px-4 py-3 text-center text-gray-600">{item.ks_hours}</td>
                                        <td className="px-4 py-3 text-center text-gray-600">{item.elearning_hours}</td>
                                        <td className="px-4 py-3 text-center text-gray-600">{item.tna_count}</td>
                                        <td className="px-4 py-3 text-center text-gray-600">{item.tna_fulfilled}</td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Pagination (Matching HotelPage style) */}
            {!loading && totalPages > 1 && (
                <div className="flex flex-col items-end mt-8 gap-2">
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
        </MainLayout>
    );
};

export default EmployeePage;
