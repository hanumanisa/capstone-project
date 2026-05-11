import React, { useState, useEffect, useCallback } from 'react';
import { Link, useLocation } from 'react-router-dom';
import MainLayout from '../components/MainLayout';
import { getUserFromToken } from '../utils/auth';
import api from '../api/axios';
import * as XLSX from 'xlsx';
import Toast from '../components/Toast';
import ConfirmModal from '../components/ConfirmModal';
import YearPicker from '../components/YearPicker';

const ITEMS_PER_PAGE = 50;

const CoursePage = () => {
    const location = useLocation();
    const [user, setUser] = useState(null);
    const [courses, setCourses] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedYear, setSelectedYear] = useState(new Date().getFullYear().toString());
    const [currentPage, setCurrentPage] = useState(1);
    const [showModal, setShowModal] = useState(false);
    const [isEdit, setIsEdit] = useState(false);
    const [saving, setSaving] = useState(false);
    const [formData, setFormData] = useState({
        course_id: '',
        course_category: '',
        course_name: '',
        description: '',
        is_active: true,
    });

    // ─── UI State ───────────────────────────────────────────────────────
    const [toast, setToast] = useState(null); // { message: string, type: 'success' | 'error' }
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

    const isAdmin = user?.role === 'Super Administrator' || user?.role === 'Administrator';

    useEffect(() => {
        const userData = getUserFromToken();
        if (userData) setUser(userData);
    }, []);

    // Fetch categories for dropdown
    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const res = await api.get('/api/course-categories/');
                setCategories(res.data);
            } catch (err) {
                console.error('Failed to fetch categories:', err);
            }
        };
        fetchCategories();
    }, []);

    // Fetch courses
    const fetchCourses = useCallback(async () => {
        setLoading(true);
        try {
            const params = {};
            if (searchTerm) params.search = searchTerm;
            if (selectedYear) params.year = selectedYear;
            const res = await api.get('/api/courses/', { params });
            setCourses(res.data);
        } catch (err) {
            console.error('Failed to fetch courses:', err);
        } finally {
            setLoading(false);
        }
    }, [searchTerm, selectedYear]);

    useEffect(() => {
        fetchCourses();
    }, [fetchCourses, selectedYear]);

    useEffect(() => {
        setCurrentPage(1);
    }, [searchTerm]);

    // ─── Pagination ─────────────────────────────────────────────────────
    const totalPages = Math.ceil(courses.length / ITEMS_PER_PAGE);
    const paginatedData = courses.slice(
        (currentPage - 1) * ITEMS_PER_PAGE,
        currentPage * ITEMS_PER_PAGE
    );

    const getPageNumbers = () => {
        const pages = [];
        const maxVisible = 5;
        let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
        let end = Math.min(totalPages, start + maxVisible - 1);
        if (end - start + 1 < maxVisible) {
            start = Math.max(1, end - maxVisible + 1);
        }
        for (let i = start; i <= end; i++) {
            pages.push(i);
        }
        return pages;
    };

    // ─── Modal Handlers ─────────────────────────────────────────────────
    const openAdd = () => {
        if (!isAdmin) return;
        setIsEdit(false);
        setFormData({ course_id: '', course_category: '', course_name: '', description: '', is_active: true });
        setShowModal(true);
    };

    const openEdit = (item) => {
        if (!isAdmin) return;
        setIsEdit(true);
        setFormData({
            course_id: item.course_id,
            course_category: item.course_category || '',
            course_name: item.course_name || '',
            description: item.description || '',
            is_active: item.is_active ?? true,
        });
        setShowModal(true);
    };

    const handleSave = async () => {
        if (!isAdmin) return;
        setSaving(true);
        try {
            if (isEdit) {
                await api.patch(`/api/courses/${formData.course_id}/`, {
                    course_category: formData.course_category,
                    course_name: formData.course_name,
                    description: formData.description,
                    is_active: formData.is_active,
                });
            } else {
                await api.post('/api/courses/', formData);
            }
            setShowModal(false);
            setToast({
                message: isEdit ? 'Course updated successfully' : 'Course added successfully',
                type: 'success'
            });
            fetchCourses();
        } catch (err) {
            console.error('Save failed:', err);
            setToast({ message: 'Failed to add course', type: 'error' });
        } finally {
            setSaving(false);
        }
    };

    const handleDeleteClick = () => {
        if (!isAdmin) return;
        setShowDeleteConfirm(true);
    };

    const handleConfirmDelete = async () => {
        try {
            await api.delete(`/api/courses/${formData.course_id}/`);
            setShowModal(false);
            setShowDeleteConfirm(false);
            setToast({ message: 'Course deleted successfully', type: 'success' });
            fetchCourses();
        } catch (err) {
            console.error('Delete failed:', err);
            setToast({ message: 'Failed to delete course', type: 'error' });
            setShowDeleteConfirm(false);
        }
    };

    const handleExport = () => {
        if (!courses.length) {
            alert('No data available to export.');
            return;
        }
        const exportData = courses.map(course => ({
            'Course Code': course.course_id,
            'Course Name': course.course_name,
            'Category': course.category_name,
            'Description': course.description,
            'Status': course.is_active ? 'Active' : 'Inactive'
        }));
        const ws = XLSX.utils.json_to_sheet(exportData);
        // Column widths
        const wscols = [
            { wch: 15 },
            { wch: 30 },
            { wch: 25 },
            { wch: 50 },
            { wch: 10 }
        ];
        ws['!cols'] = wscols;
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'Course Report');
        XLSX.writeFile(wb, 'Course Report.xlsx');
    };

    return (
        <MainLayout>
            {/* ─── Toolbar ─────────────────────────────────────────────── */}
            <div className="bg-white p-3 rounded-xl shadow-sm border border-gray-100 flex flex-col sm:flex-row justify-between items-center gap-3 mb-10 sticky top-0 z-30">
                <div className="relative w-full sm:w-1/3">
                    <input
                        id="search-course"
                        type="text"
                        placeholder="Search"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-4 pr-10 py-2 rounded-lg border-none bg-gray-100 focus:bg-white focus:ring-1 focus:ring-[#2174C3] transition-all text-gray-600 placeholder-gray-400"
                    />
                    <span className="absolute right-3 top-2.5 text-gray-400 pointer-events-none">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </span>
                </div>
                <div className="flex items-center space-x-6">
                    <YearPicker selectedYear={selectedYear} onYearChange={(y) => setSelectedYear(y)} />
                    <div className="flex items-center space-x-2">
                        {isAdmin && (
                            <button
                                onClick={handleExport}
                                className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white w-28 py-2 rounded-lg font-medium text-sm transition-all shadow-sm cursor-pointer border-none outline-none"
                            >
                                Report
                            </button>
                        )}
                        {isAdmin && (
                            <button
                                id="btn-add-course"
                                onClick={openAdd}
                                className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white w-28 py-1 rounded-lg font-medium flex items-center justify-center text-sm shadow-sm transition-all cursor-pointer border-none outline-none"
                            >
                                <span className="mr-1 text-lg font-bold">+</span> Course
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* ─── Header + Tabs ───────────────────────────────────────── */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-6 gap-4">
                <h1 className="text-4xl font-bold text-gray-800 tracking-tight">Course</h1>
                <div className="flex space-x-8 border-b border-gray-300">
                    <Link
                        to="/category"
                        className={`pb-3 px-1 font-bold text-xl transition-colors ${location.pathname === '/category'
                            ? 'text-[#2174C3] border-b-4 border-[#2174C3]'
                            : 'text-gray-400 hover:text-[#2174C3]'
                            }`}
                    >
                        Category
                    </Link>
                    <Link
                        to="/courses"
                        className={`pb-3 px-1 font-bold text-xl transition-colors ${location.pathname === '/courses'
                            ? 'text-[#2174C3] border-b-4 border-[#2174C3]'
                            : 'text-gray-400 hover:text-[#2174C3]'
                            }`}
                    >
                        Course
                    </Link>
                </div>
            </div>

            {/* ─── Table ───────────────────────────────────────────────── */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden transition-all h-[calc(100vh-350px)] flex flex-col">
                <div className="custom-scrollbar overflow-auto flex-1">
                    <table className="w-full text-left text-sm min-w-[800px]">
                        <thead className="bg-[#5C85BB] text-white text-xs uppercase tracking-wider sticky top-0 z-10">
                            <tr>
                                <th className="px-6 py-4 font-bold">Course Code</th>
                                <th className="px-6 py-4 font-bold">Course Name</th>
                                <th className="px-6 py-4 font-bold">Category</th>
                                <th className="px-6 py-4 font-bold">Description</th>
                                <th className="px-6 py-4 text-right font-bold">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {loading ? (
                                <tr>
                                    <td colSpan="5" className="px-6 py-12 text-center text-gray-400">
                                        <div className="flex items-center justify-center gap-2">
                                            <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                            </svg>
                                            Loading...
                                        </div>
                                    </td>
                                </tr>
                            ) : paginatedData.length === 0 ? (
                                <tr>
                                    <td colSpan="5" className="px-6 py-12 text-center text-gray-400">
                                        No data available
                                    </td>
                                </tr>
                            ) : (
                                paginatedData.map((item) => (
                                    <tr key={item.course_id} className="hover:bg-blue-50/30 transition-colors">
                                        <td className="px-6 py-4">
                                            {isAdmin ? (
                                                <button
                                                    onClick={() => openEdit(item)}
                                                    className="text-[#2174C3] font-bold hover:underline cursor-pointer"
                                                >
                                                    {item.course_id}
                                                </button>
                                            ) : (
                                                <span className="text-gray-700 font-bold">{item.course_id}</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 text-gray-700">{item.course_name}</td>
                                        <td className="px-6 py-4 text-gray-500">{item.category_name}</td>
                                        <td className="px-6 py-4 text-gray-700 max-w-sm truncate">{item.description}</td>
                                        <td className="px-6 py-4 text-right">
                                            <span
                                                className={`px-3 py-1 rounded-full text-xs font-bold ${item.is_active
                                                    ? 'bg-green-100 text-green-700'
                                                    : 'bg-red-100 text-red-700'
                                                    }`}
                                            >
                                                {item.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="sticky bottom-0 bg-[#F4F7FA]/95 backdrop-blur-sm py-4 flex flex-col items-end gap-2 z-20 mt-4 border-t border-gray-100">
                    <div className="flex items-center space-x-1">
                        <button
                            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            className="px-4 py-2 bg-[#E2E8F0] text-gray-500 rounded-md font-medium hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Previous
                        </button>
                        {getPageNumbers().map((page) => (
                            <button
                                key={page}
                                onClick={() => setCurrentPage(page)}
                                className={`px-4 py-2 rounded-md font-medium transition-colors ${currentPage === page
                                    ? 'bg-[#2174C3] text-white'
                                    : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
                                    }`}
                            >
                                {page}
                            </button>
                        ))}
                        <button
                            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                            disabled={currentPage === totalPages}
                            className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-md font-medium hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Next
                        </button>
                    </div>
                    <div className="text-xs text-gray-400 font-medium">
                        Showing {(currentPage - 1) * ITEMS_PER_PAGE + 1}–{Math.min(currentPage * ITEMS_PER_PAGE, courses.length)} of {courses.length} courses
                    </div>
                </div>
            )}

            {/* ─── Add / Edit Modal ────────────────────────────────────── */}
            {showModal && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50">
                    <div
                        className="bg-white rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden p-8"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <h2 className="text-3xl font-bold text-black mb-2">
                            {isEdit ? 'Edit Course' : 'Add Course'}
                        </h2>
                        <hr className="mb-8 border-gray-200" />

                        <div className="space-y-6">
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold">Course Code</label>
                                <input
                                    id="input-course-code"
                                    type="text"
                                    value={formData.course_id}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, course_id: e.target.value })}
                                    disabled={isEdit}
                                    placeholder="Enter course code e.g. GA26"
                                    className="sm:col-span-2 bg-gray-100 border-none rounded-lg p-3 focus:ring-2 focus:ring-[#2174C3] disabled:opacity-60"
                                />
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold">Category</label>
                                <select
                                    id="input-course-category"
                                    value={formData.course_category}
                                    onChange={(e) => setFormData({ ...formData, course_category: e.target.value })}
                                    className="sm:col-span-2 bg-gray-100 border-none rounded-lg p-3 focus:ring-2 focus:ring-[#2174C3]"
                                    style={{ color: '#000' }}
                                >
                                    <option value="">Select Category</option>
                                    {categories.map((cat) => (
                                        <option key={cat.course_category_id} value={cat.course_category_id}>
                                            {cat.course_category_id} – {cat.category_name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold">Course Name</label>
                                <input
                                    id="input-course-name"
                                    type="text"
                                    value={formData.course_name}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, course_name: e.target.value })}
                                    placeholder="Enter course name"
                                    className="sm:col-span-2 bg-gray-100 border-none rounded-lg p-3 focus:ring-2 focus:ring-[#2174C3]"
                                />
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-start gap-2">
                                <label className="text-black font-semibold pt-2">Description</label>
                                <textarea
                                    id="input-course-desc"
                                    rows="4"
                                    value={formData.description}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    placeholder="Enter course description"
                                    className="sm:col-span-2 bg-gray-100 border-none rounded-lg p-3 focus:ring-2 focus:ring-[#2174C3]"
                                />
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold">Status</label>
                                <div className="sm:col-span-2 flex space-x-8">
                                    <label className="flex items-center space-x-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            name="course-status"
                                            checked={formData.is_active === true}
                                            onChange={() => setFormData({ ...formData, is_active: true })}
                                            className="w-5 h-5 text-[#2174C3] border-gray-300 focus:ring-[#2174C3]"
                                        />
                                        <span className="text-black">Active</span>
                                    </label>
                                    <label className="flex items-center space-x-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            name="course-status"
                                            checked={formData.is_active === false}
                                            onChange={() => setFormData({ ...formData, is_active: false })}
                                            className="w-5 h-5 text-[#2174C3] border-gray-300 focus:ring-[#2174C3]"
                                        />
                                        <span className="text-black">Inactive</span>
                                    </label>
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-end space-x-2 mt-10">
                            {isEdit && (
                                <button
                                    id="btn-delete-course"
                                    onClick={handleDeleteClick}
                                    className="bg-[#F15E5E] hover:bg-[#D32F2F] text-white px-3 py-1 text-sm rounded font-medium transition-colors cursor-pointer"
                                >
                                    Delete
                                </button>
                            )}
                            <button
                                onClick={() => setShowModal(false)}
                                className="bg-[#878D94] hover:bg-[#607D8B] text-white px-3 py-1 text-sm rounded font-medium transition-colors cursor-pointer"
                            >
                                Cancel
                            </button>
                            <button
                                id="btn-save-course"
                                onClick={handleSave}
                                disabled={saving}
                                className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-4 py-1 text-sm rounded font-medium transition-colors shadow cursor-pointer disabled:opacity-50"
                            >
                                {saving ? 'Saving...' : 'Save'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* ─── Toast Notifications ─────────────────────────────────── */}
            {toast && (
                <Toast
                    message={toast.message}
                    type={toast.type}
                    onClose={() => setToast(null)}
                />
            )}

            {/* ─── Delete Confirmation ─────────────────────────────────── */}
            <ConfirmModal
                isOpen={showDeleteConfirm}
                onClose={() => setShowDeleteConfirm(false)}
                onConfirm={handleConfirmDelete}
                title="Confirm Delete"
                message="Are you sure want to delete this Course?"
            />
        </MainLayout>
    );
};

export default CoursePage;
