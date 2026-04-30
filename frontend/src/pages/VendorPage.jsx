import React, { useState, useEffect, useCallback } from 'react';
import MainLayout from '../components/MainLayout';
import { getUserFromToken } from '../utils/auth';
import api from '../api/axios';
import * as XLSX from 'xlsx';
import Toast from '../components/Toast';
import ConfirmModal from '../components/ConfirmModal';

const ITEMS_PER_PAGE = 50;

const VendorPage = () => {
    const [user, setUser] = useState(null);
    const [vendors, setVendors] = useState([]);
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
        vendor_id: '',
        vendor_name: '',
        provider_type: 'Internal',
        pic_name: '',
        speciality: '',
        address: '',
        city: '',
        province: '',
        country: '',
        postcode: '',
        phone: '',
        fax: '',
        email: '',
        web_address: '',
    });

    const isAdmin = user?.role === 'Super Administrator' || user?.role === 'Administrator';

    useEffect(() => {
        const userData = getUserFromToken();
        if (userData) setUser(userData);
    }, []);

    const fetchVendors = useCallback(async () => {
        setLoading(true);
        try {
            const params = {};
            if (searchTerm) params.search = searchTerm;
            const res = await api.get('/api/vendors/', { params });
            setVendors(res.data);
        } catch (err) {
            console.error('Failed to fetch vendors:', err);
        } finally {
            setLoading(false);
        }
    }, [searchTerm]);

    useEffect(() => {
        fetchVendors();
    }, [fetchVendors]);

    // ─── Pagination ─────────────────────────────────────────────────────
    const filteredVendors = vendors.filter(v => 
        v.vendor_name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
        v.vendor_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        v.provider_type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        v.speciality?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        v.province?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    const totalPages = Math.ceil(filteredVendors.length / ITEMS_PER_PAGE);
    const paginatedData = filteredVendors.slice(
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
            vendor_id: '', vendor_name: '', provider_type: 'Internal', pic_name: '', 
            speciality: '', address: '', city: '', province: '', country: '', 
            postcode: '', phone: '', fax: '', email: '', web_address: '' 
        });
        setShowModal(true);
    };

    const openEdit = (item) => {
        if (!isAdmin) return;
        setIsEdit(true);
        setFormData({ ...item });
        setShowModal(true);
    };

    const handleSave = async () => {
        if (!isAdmin) return;
        if (!formData.vendor_id || !formData.vendor_name) {
            setToast({ message: 'Vendor Code and Name are required!', type: 'error' });
            return;
        }
        setSaving(true);
        try {
            if (isEdit) {
                await api.patch(`/api/vendors/${formData.vendor_id}/`, formData);
            } else {
                await api.post('/api/vendors/', formData);
            }
            setShowModal(false);
            setToast({ 
                message: isEdit ? 'Vendor Update succesfully' : 'Vendor Added succesfully', 
                type: 'success' 
            });
            fetchVendors();
        } catch (err) {
            console.error('Save failed:', err);
            setToast({ message: 'Vendor Added Unsuccesfully', type: 'error' });
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
            await api.delete(`/api/vendors/${formData.vendor_id}/`);
            setShowModal(false);
            setShowDeleteConfirm(false);
            setToast({ message: 'Vendor Deleted succesfully', type: 'success' });
            fetchVendors();
        } catch (err) {
            console.error('Delete failed:', err);
            setToast({ message: 'Vendor Deleted Unsuccesfully', type: 'error' });
            setShowDeleteConfirm(false);
        }
    };

    const handleExport = () => {
        if (!vendors.length) {
            alert('Tidak ada data untuk diekspor.');
            return;
        }
        const exportData = vendors.map(v => ({
            'Vendor Code': v.vendor_id,
            'Vendor Name': v.vendor_name,
            'Vendor Type': v.provider_type,
            'PIC': v.pic_name,
            'Speciality': v.speciality,
            'Address': v.address,
            'City': v.city,
            'Province': v.province,
            'Country': v.country,
            'Postcode': v.postcode,
            'Phone': v.phone,
            'FAX': v.fax,
            'Email': v.email,
            'Web Address': v.web_address
        }));
        const ws = XLSX.utils.json_to_sheet(exportData);
        // Column widths
        const wscols = [
            { wch: 15 }, { wch: 30 }, { wch: 15 }, { wch: 20 },
            { wch: 30 }, { wch: 40 }, { wch: 15 }, { wch: 15 },
            { wch: 15 }, { wch: 10 }, { wch: 15 }, { wch: 15 },
            { wch: 25 }, { wch: 30 }
        ];
        ws['!cols'] = wscols;
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'Vendor Report');
        XLSX.writeFile(wb, 'Vendor Report.xlsx');
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
                            <span className="mr-1 text-lg font-bold">+</span> Vendor
                        </button>
                    )}
                </div>
            </div>

            <h1 className="text-4xl font-bold text-gray-800 tracking-tight mb-6">Vendor</h1>

            {/* ─── Table ───────────────────────────────────────────────── */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-auto max-h-[60vh]">
                <table className="w-full text-left text-sm min-w-[1500px]">
                    <thead className="bg-[#5C85BB] text-white text-xs uppercase tracking-wider sticky top-0 z-10">
                        <tr>
                            <th className="px-3 py-3">Vendor Code</th>
                            <th className="px-3 py-3">Vendor Name</th>
                            <th className="px-3 py-3">Vendor Type</th>
                            <th className="px-3 py-3">PIC</th>
                            <th className="px-3 py-3">Speciality</th>
                            <th className="px-3 py-3">Address</th>
                            <th className="px-3 py-3">City</th>
                            <th className="px-3 py-3">State / Province</th>
                            <th className="px-3 py-3">Country</th>
                            <th className="px-3 py-3">Postal Code</th>
                            <th className="px-3 py-3">Phone</th>
                            <th className="px-3 py-3">FAX</th>
                            <th className="px-3 py-3">Email</th>
                            <th className="px-3 py-3 text-right pr-4">Web Address</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {loading ? (
                            <tr><td colSpan="14" className="px-6 py-12 text-center text-gray-400">Loading...</td></tr>
                        ) : paginatedData.length === 0 ? (
                            <tr><td colSpan="14" className="px-6 py-12 text-center text-gray-400">No vendors found.</td></tr>
                        ) : (
                            paginatedData.map((item) => (
                                <tr key={item.vendor_id} className="hover:bg-blue-50/30 transition-colors align-top">
                                    <td className="px-3 py-4">
                                        {isAdmin ? (
                                            <button 
                                                onClick={() => openEdit(item)}
                                                className="text-[#2174C3] font-bold hover:underline cursor-pointer text-left"
                                            >
                                                {item.vendor_id}
                                            </button>
                                        ) : (
                                            <span className="text-gray-600 font-bold">{item.vendor_id}</span>
                                        )}
                                    </td>
                                    <td className="px-3 py-4 text-gray-800">{item.vendor_name}</td>
                                    <td className="px-3 py-4 text-gray-600">{item.provider_type}</td>
                                    <td className="px-3 py-4 text-gray-600">{item.pic_name}</td>
                                    <td className="px-3 py-4 text-gray-600 truncate max-w-[150px]" title={item.speciality}>{item.speciality}</td>
                                    <td className="px-3 py-4 text-gray-600 truncate max-w-[200px]" title={item.address}>{item.address}</td>
                                    <td className="px-3 py-4 text-gray-600">{item.city}</td>
                                    <td className="px-3 py-4 text-gray-600">{item.province}</td>
                                    <td className="px-3 py-4 text-gray-600">{item.country}</td>
                                    <td className="px-3 py-4 text-gray-600">{item.postcode}</td>
                                    <td className="px-3 py-4 text-gray-600 text-nowrap">{item.phone}</td>
                                    <td className="px-3 py-4 text-gray-600 text-nowrap">{item.fax}</td>
                                    <td className="px-3 py-4 text-blue-600">{item.email}</td>
                                    <td className="px-3 py-4 text-blue-600 text-right pr-4">{item.web_address}</td>
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

            {!loading && filteredVendors.length > 0 && (
                <div className="mt-3 text-right text-sm text-gray-400">
                    Showing {(currentPage - 1) * ITEMS_PER_PAGE + 1}–{Math.min(currentPage * ITEMS_PER_PAGE, filteredVendors.length)} of {filteredVendors.length} vendor
                </div>
            )}

            {/* ─── Add / Edit Modal ────────────────────────────────────── */}
            {showModal && (
                <div className="fixed inset-0 z-[150] flex items-center justify-center p-4 bg-black/40">
                    <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl overflow-y-auto max-h-[90vh] p-8">
                        <h2 className="text-3xl font-bold text-black mb-2">
                            {isEdit ? 'Edit Vendor' : 'Add Vendor'}
                        </h2>
                        <hr className="mb-8 border-gray-200" />
                        
                        <div className="space-y-6">
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold">Vendor Code</label>
                                <input 
                                    type="text" 
                                    value={formData.vendor_id}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, vendor_id: e.target.value })}
                                    disabled={isEdit}
                                    className="sm:col-span-2 bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] disabled:opacity-60"
                                />
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold">Vendor Name</label>
                                <input 
                                    type="text" 
                                    value={formData.vendor_name}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, vendor_name: e.target.value })}
                                    className="sm:col-span-2 bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3]"
                                />
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold">Vendor Type</label>
                                <div className="sm:col-span-2 flex space-x-8">
                                    <label className="flex items-center space-x-2 cursor-pointer text-black font-medium">
                                        <input 
                                            type="radio" 
                                            className="w-5 h-5 text-[#2174C3] focus:ring-[#2174C3] border-gray-300"
                                            value="Internal" 
                                            checked={formData.provider_type === 'Internal'}
                                            onChange={(e) => setFormData({ ...formData, provider_type: e.target.value })}
                                        /> <span>Internal</span>
                                    </label>
                                    <label className="flex items-center space-x-2 cursor-pointer text-black font-medium">
                                        <input 
                                            type="radio" 
                                            className="w-5 h-5 text-[#2174C3] focus:ring-[#2174C3] border-gray-300"
                                            value="External" 
                                            checked={formData.provider_type === 'Eksternal' || formData.provider_type === 'External'}
                                            onChange={(e) => setFormData({ ...formData, provider_type: 'Eksternal' })}
                                        /> <span>Eksternal</span>
                                    </label>
                                </div>
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold">PIC</label>
                                <input 
                                    type="text" 
                                    value={formData.pic_name}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, pic_name: e.target.value })}
                                    className="sm:col-span-2 bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3]"
                                />
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-start gap-2">
                                <label className="text-black font-semibold pt-2">Speciality</label>
                                <textarea 
                                    rows="2" 
                                    value={formData.speciality}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, speciality: e.target.value })}
                                    className="sm:col-span-2 bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3]"
                                ></textarea>
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-start gap-2">
                                <label className="text-black font-semibold pt-2">Address</label>
                                <textarea 
                                    rows="3" 
                                    value={formData.address}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                                    className="sm:col-span-2 bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3]"
                                ></textarea>
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold">City</label>
                                <input 
                                    type="text" 
                                    value={formData.city}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                                    className="sm:col-span-2 bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3]"
                                />
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold text-nowrap">State/Province</label>
                                <input 
                                    type="text" 
                                    value={formData.province}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, province: e.target.value })}
                                    className="sm:col-span-2 bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3]"
                                />
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold">Country</label>
                                <input 
                                    type="text" 
                                    value={formData.country}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                                    className="sm:col-span-2 bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3]"
                                />
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold">Postal Code</label>
                                <input 
                                    type="text" 
                                    value={formData.postcode}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, postcode: e.target.value })}
                                    className="sm:col-span-2 bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3]"
                                />
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold">Phone</label>
                                <input 
                                    type="text" 
                                    value={formData.phone}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                    className="sm:col-span-2 bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3]"
                                />
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold">FAX</label>
                                <input 
                                    type="text" 
                                    value={formData.fax}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, fax: e.target.value })}
                                    className="sm:col-span-2 bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3]"
                                />
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold">Email</label>
                                <input 
                                    type="email" 
                                    value={formData.email}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    className="sm:col-span-2 bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3]"
                                />
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                                <label className="text-black font-semibold">Web Address</label>
                                <input 
                                    type="text" 
                                    value={formData.web_address}
                                    style={{ color: '#000' }}
                                    onChange={(e) => setFormData({ ...formData, web_address: e.target.value })}
                                    className="sm:col-span-2 bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3]"
                                />
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
                message="Are you sure want to delete this Vendor?"
            />
        </MainLayout>
    );
};

export default VendorPage;
