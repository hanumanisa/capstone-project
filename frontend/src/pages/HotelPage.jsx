import React, { useState, useEffect, useCallback } from 'react';
import MainLayout from '../components/MainLayout';
import { getUserFromToken } from '../utils/auth';
import api from '../api/axios';
import * as XLSX from 'xlsx';
import Toast from '../components/Toast';
import ConfirmModal from '../components/ConfirmModal';

const ITEMS_PER_PAGE = 50;

const HotelPage = () => {
    const [user, setUser] = useState(null);
    const [hotels, setHotels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [showModal, setShowModal] = useState(false);
    const [isEdit, setIsEdit] = useState(false);
    const [saving, setSaving] = useState(false);

    // ─── UI State ───────────────────────────────────────────────────────
    const [toast, setToast] = useState(null); // { message: string, type: 'success' | 'error' }
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    
    const [formData, setFormData] = useState({
        hotel_id: '',
        hotel_city: '',
        hotel_name: '',
        hotel_phone: '',
        price_estimation: '',
        hotel_star: 1,
    });

    const isAdmin = user?.role === 'Super Administrator' || user?.role === 'Administrator';

    useEffect(() => {
        const userData = getUserFromToken();
        if (userData) setUser(userData);
    }, []);

    const fetchHotels = useCallback(async () => {
        setLoading(true);
        try {
            const params = {};
            if (searchTerm) params.search = searchTerm;
            const res = await api.get('/api/hotels/', { params });
            setHotels(res.data);
        } catch (err) {
            console.error('Failed to fetch hotels:', err);
        } finally {
            setLoading(false);
        }
    }, [searchTerm]);

    useEffect(() => {
        fetchHotels();
    }, [fetchHotels]);

    // Format currency manually to match user's request (RpX.XXX.XXX,XX)
    const formatCurrency = (val) => {
        if (!val) return 'Rp0';
        const num = parseFloat(val);
        return 'Rp' + num.toLocaleString('id-ID', { minimumFractionDigits: 2 });
    };

    // ─── Pagination ─────────────────────────────────────────────────────
    const filteredHotels = hotels.filter(h => 
        h.hotel_name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
        h.hotel_city?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    const totalPages = Math.ceil(filteredHotels.length / ITEMS_PER_PAGE);
    const paginatedData = filteredHotels.slice(
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
        for (let i = start; i <= end; i++) pages.push(i);
        return pages;
    };

    // ─── Modal Handlers ─────────────────────────────────────────────────
    const openAdd = () => {
        if (!isAdmin) return;
        setIsEdit(false);
        setFormData({ 
            hotel_id: '', 
            hotel_city: '', 
            hotel_name: '', 
            hotel_phone: '', 
            price_estimation: '', 
            hotel_star: 1 
        });
        setShowModal(true);
    };

    const openEdit = (item) => {
        if (!isAdmin) return;
        setIsEdit(true);
        setFormData({
            hotel_id: item.hotel_id,
            hotel_city: item.hotel_city || '',
            hotel_name: item.hotel_name || '',
            hotel_phone: item.hotel_phone || '',
            price_estimation: item.price_estimation || '',
            hotel_star: item.hotel_star || 1,
        });
        setShowModal(true);
    };

    const handleSave = async () => {
        if (!isAdmin) return;
        setSaving(true);
        try {
            if (isEdit) {
                await api.patch(`/api/hotels/${formData.hotel_id}/`, formData);
            } else {
                await api.post('/api/hotels/', formData);
            }
            setShowModal(false);
            setToast({ 
                message: isEdit ? 'Hotel Update succesfully' : 'Hotel Added succesfully', 
                type: 'success' 
            });
            fetchHotels();
        } catch (err) {
            console.error('Save failed:', err);
            setToast({ message: 'Hotel Added Unsuccesfully', type: 'error' });
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
            await api.delete(`/api/hotels/${formData.hotel_id}/`);
            setShowModal(false);
            setShowDeleteConfirm(false);
            setToast({ message: 'Hotel Deleted succesfully', type: 'success' });
            fetchHotels();
        } catch (err) {
            console.error('Delete failed:', err);
            setToast({ message: 'Hotel Deleted Unsuccesfully', type: 'error' });
            setShowDeleteConfirm(false);
        }
    };

    const handleExport = () => {
        if (!hotels.length) {
            alert('Tidak ada data untuk diekspor.');
            return;
        }
        const exportData = hotels.map(h => ({
            'Hotel ID': h.hotel_id,
            'City': h.hotel_city,
            'Hotel Name': h.hotel_name,
            'Phone Number': h.hotel_phone,
            'Price Estimated': h.price_estimation,
            'Hotel Star': h.hotel_star
        }));
        const ws = XLSX.utils.json_to_sheet(exportData);
        // Column widths
        const wscols = [
            { wch: 15 }, { wch: 20 }, { wch: 30 }, { wch: 20 },
            { wch: 20 }, { wch: 10 }
        ];
        ws['!cols'] = wscols;
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'Hotel Report');
        XLSX.writeFile(wb, 'Hotel Report.xlsx');
    };

    return (
        <MainLayout>
            {/* ─── Toolbar ─────────────────────────────────────────────── */}
            <div className="bg-white px-4 py-3 rounded-xl shadow-sm border border-gray-100 flex flex-col sm:flex-row justify-between items-center gap-3 mb-8">
                <div className="relative w-full sm:w-1/3">
                    <input
                        type="text"
                        placeholder="Search"
                        value={searchTerm}
                        onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
                        className="w-full pl-4 pr-10 py-2 rounded-lg border-none bg-gray-100 focus:bg-white focus:ring-1 focus:ring-[#2174C3] transition-all text-gray-600 placeholder-gray-400 outline-none"
                    />
                    <span className="absolute right-3 top-2.5 text-gray-400 pointer-events-none">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </span>
                </div>
                
                <div className="flex items-center space-x-4">
                    <button 
                        onClick={handleExport}
                        className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white w-28 py-2 rounded-lg font-medium shadow-sm transition-all text-sm cursor-pointer"
                    >
                        Report
                    </button>
                    {isAdmin && (
                        <button 
                            onClick={openAdd} 
                            className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white w-28 py-1 rounded-lg font-medium flex items-center justify-center shadow-sm transition-all text-sm cursor-pointer"
                        >
                            <span className="mr-1 text-lg font-bold">+</span> Hotel
                        </button>
                    )}
                </div>
            </div>

            <h1 className="text-4xl font-bold text-gray-800 tracking-tight mb-6">Hotels</h1>

            {/* ─── Table ───────────────────────────────────────────────── */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-auto max-h-[60vh]">
                <table className="w-full text-left text-[11px] font-semibold min-w-[800px]">
                    <thead className="bg-[#5C85BB] text-white uppercase tracking-wider sticky top-0 z-10">
                        <tr>
                            <th className="px-4 py-3 text-center">Hotel ID</th>
                            <th className="px-4 py-3">City</th>
                            <th className="px-4 py-3">Hotel Name</th>
                            <th className="px-4 py-3">Phone Number</th>
                            <th className="px-4 py-3">Estimated Price per Night</th>
                            <th className="px-4 py-3 text-center">Hotel Star</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {loading ? (
                            <tr><td colSpan="6" className="px-6 py-12 text-center text-gray-400">Loading...</td></tr>
                        ) : paginatedData.length === 0 ? (
                            <tr><td colSpan="6" className="px-6 py-12 text-center text-gray-400">No hotels found.</td></tr>
                        ) : (
                            paginatedData.map((item) => (
                                <tr key={item.hotel_id} className="hover:bg-blue-50/30 transition-colors">
                                    <td className="px-4 py-4 text-center">
                                        {isAdmin ? (
                                            <button 
                                                onClick={() => openEdit(item)}
                                                className="text-[#2174C3] font-bold hover:underline cursor-pointer"
                                            >
                                                {item.hotel_id}
                                            </button>
                                        ) : (
                                            <span className="text-gray-600">{item.hotel_id}</span>
                                        )}
                                    </td>
                                    <td className="px-4 py-4 text-gray-600">{item.hotel_city}</td>
                                    <td className="px-4 py-4 text-gray-800">{item.hotel_name}</td>
                                    <td className="px-4 py-4 text-gray-600">{item.hotel_phone}</td>
                                    <td className="px-4 py-4 text-gray-600">{formatCurrency(item.price_estimation)}</td>
                                    <td className="px-4 py-4 text-center">
                                        <div className="flex justify-center space-x-0.5">
                                            {[...Array(parseInt(item.hotel_star || 0))].map((_, i) => (
                                                <svg key={i} className="w-4 h-4 text-yellow-400 fill-current" viewBox="0 0 20 20">
                                                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                                </svg>
                                            ))}
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* ─── Pagination ──────────────────────────────────────────── */}
            {!loading && totalPages > 1 && (
                <div className="flex justify-end items-center mt-8 space-x-1">
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
            )}

            {!loading && filteredHotels.length > 0 && (
                <div className="mt-3 text-right text-sm text-gray-400">
                    Showing {(currentPage - 1) * ITEMS_PER_PAGE + 1}–{Math.min(currentPage * ITEMS_PER_PAGE, filteredHotels.length)} of {filteredHotels.length} hotels
                </div>
            )}

            {/* ─── Add / Edit Modal ────────────────────────────────────── */}
            {showModal && (
                <div className="fixed inset-0 z-[150] flex items-center justify-center p-4 bg-black/40">
                    <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden p-10">
                        <h2 className="text-3xl font-bold text-[#212529] mb-4">
                            {isEdit ? 'Edit Hotel' : 'Add Hotel'}
                        </h2>
                        <hr className="mb-8 border-gray-200" />
                        
                        <div className="space-y-6">
                            <div className="grid grid-cols-3 items-center">
                                <label className="text-[#495057] font-semibold">Hotel ID</label>
                                <input 
                                    type="text" 
                                    value={formData.hotel_id}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, hotel_id: e.target.value })}
                                    disabled={isEdit}
                                    className="col-span-2 bg-[#F1F3F5] rounded-lg p-3 outline-none focus:ring-2 focus:ring-[#2174C3] disabled:opacity-60"
                                />
                            </div>
                            <div className="grid grid-cols-3 items-center">
                                <label className="text-[#495057] font-semibold">City</label>
                                <input 
                                    type="text" 
                                    value={formData.hotel_city}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, hotel_city: e.target.value })}
                                    className="col-span-2 bg-[#F1F3F5] rounded-lg p-3 outline-none focus:ring-2 focus:ring-[#2174C3]"
                                />
                            </div>
                            <div className="grid grid-cols-3 items-center">
                                <label className="text-[#495057] font-semibold">Hotel Name</label>
                                <input 
                                    type="text" 
                                    value={formData.hotel_name}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, hotel_name: e.target.value })}
                                    className="col-span-2 bg-[#F1F3F5] rounded-lg p-3 outline-none focus:ring-2 focus:ring-[#2174C3]"
                                />
                            </div>
                            <div className="grid grid-cols-3 items-center">
                                <label className="text-[#495057] font-semibold">Phone Number</label>
                                <input 
                                    type="text" 
                                    value={formData.hotel_phone}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, hotel_phone: e.target.value })}
                                    className="col-span-2 bg-[#F1F3F5] rounded-lg p-3 outline-none focus:ring-2 focus:ring-[#2174C3]"
                                />
                            </div>
                            <div className="grid grid-cols-3 items-center">
                                <label className="text-[#495057] font-semibold">Price per Night</label>
                                <input 
                                    type="number" 
                                    value={formData.price_estimation}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, price_estimation: e.target.value })}
                                    className="col-span-2 bg-[#F1F3F5] rounded-lg p-3 outline-none focus:ring-2 focus:ring-[#2174C3]"
                                />
                            </div>
                            <div className="grid grid-cols-3 items-center">
                                <label className="text-[#495057] font-semibold">Hotel Star</label>
                                <div className="col-span-2 flex items-center space-x-1">
                                    {[1, 2, 3, 4, 5].map(i => (
                                        <svg 
                                            key={i}
                                            onClick={() => setFormData({ ...formData, hotel_star: i })} 
                                            className={`w-8 h-8 cursor-pointer transition-colors ${i <= formData.hotel_star ? 'text-yellow-400' : 'text-gray-300'}`} 
                                            fill="currentColor" 
                                            viewBox="0 0 20 20"
                                        >
                                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                        </svg>
                                    ))}
                                </div>
                            </div>
                        </div>
                        
                        <div className="flex justify-end space-x-2 mt-10">
                            {isEdit && (
                                <button
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
                message="Are you sure want to delete this Hotel?"
            />
        </MainLayout>
    );
};

export default HotelPage;
