import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import ConfirmModal from './ConfirmModal';

const TnaPeriodModal = ({ isOpen, onClose, period, onSave, setToast }) => {
    const [formData, setFormData] = useState({
        period_code: '',
        year: '',
        period_name: '',
        open_date: '',
        close_date: '',
        status: 'Open'
    });
    const [saving, setSaving] = useState(false);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

    useEffect(() => {
        if (period) {
            setFormData({
                period_code: period.period_code || '',
                year: period.year || new Date().getFullYear(),
                period_name: period.period_name || '',
                open_date: period.open_date || '',
                close_date: period.close_date || '',
                status: period.status || 'Open'
            });
        } else {
            setFormData({
                period_code: '',
                year: '',
                period_name: '',
                open_date: '',
                close_date: '',
                status: 'Open'
            });
        }
    }, [period]);

    if (!isOpen) return null;

    const handleSave = async () => {
        setSaving(true);
        try {
            const isEdit = !!period?.tna_period_id;
            if (isEdit) {
                await api.patch(`/api/tna-period/${period.tna_period_id}/`, formData);
            } else {
                await api.post('/api/tna-period/', formData);
            }
            setToast({ 
                message: isEdit ? 'TNA Period Update succesfully' : 'TNA Period Added succesfully', 
                type: 'success' 
            });
            onSave();
            onClose();
        } catch (err) {
            console.error('Failed to save TNA period:', err);
            setToast({ message: 'TNA Period Added Unsuccesfully', type: 'error' });
        } finally {
            setSaving(false);
        }
    };

    const handleDeleteClick = () => {
        setShowDeleteConfirm(true);
    };

    const handleConfirmDelete = async () => {
        try {
            await api.delete(`/api/tna-period/${period.tna_period_id}/`);
            setToast({ message: 'TNA Period Deleted succesfully', type: 'success' });
            onSave();
            onClose();
        } catch (err) {
            console.error('Failed to delete TNA period:', err);
            setToast({ message: 'TNA Period Deleted Unsuccesfully', type: 'error' });
        } finally {
            setShowDeleteConfirm(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden p-8 animate-in fade-in zoom-in duration-200">
                <h2 className="text-3xl font-bold text-gray-800 mb-2">
                    {period ? 'Edit TNA Period' : 'Add TNA Period'}
                </h2>
                <hr className="mb-8 border-gray-100" />
                
                <div className="space-y-6">
                    <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                        <label className="text-gray-600 font-bold">Period Code</label>
                        <input 
                            type="text" 
                            value={formData.period_code}
                            onChange={(e) => setFormData({...formData, period_code: e.target.value})}
                            className="sm:col-span-2 bg-gray-50 border border-gray-200 rounded-lg p-3 focus:ring-2 focus:ring-[#2174C3] outline-none transition-all text-black"
                            placeholder="e.g. TNA-2026"
                        />
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                        <label className="text-gray-600 font-bold">Year</label>
                        <input 
                            type="number" 
                            value={formData.year}
                            onChange={(e) => setFormData({...formData, year: e.target.value})}
                            className="sm:col-span-2 bg-gray-50 border border-gray-200 rounded-lg p-3 focus:ring-2 focus:ring-[#2174C3] outline-none transition-all text-black"
                        />
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                        <label className="text-gray-600 font-bold">Period Name</label>
                        <input 
                            type="text" 
                            value={formData.period_name}
                            onChange={(e) => setFormData({...formData, period_name: e.target.value})}
                            className="sm:col-span-2 bg-gray-50 border border-gray-200 rounded-lg p-3 focus:ring-2 focus:ring-[#2174C3] outline-none transition-all text-black"
                            placeholder="e.g. Training Needs Analysis 2026"
                        />
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 items-start gap-2">
                        <label className="text-gray-600 font-bold mt-3">Duration</label>
                        <div className="sm:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Open Date</label>
                                <input 
                                    type="date" 
                                    value={formData.open_date}
                                    onChange={(e) => setFormData({...formData, open_date: e.target.value})}
                                    className="w-full border border-gray-200 rounded-lg p-3 bg-gray-50 outline-none focus:ring-2 focus:ring-[#2174C3] transition-all text-black calendar-black"
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Close Date</label>
                                <input 
                                    type="date" 
                                    value={formData.close_date}
                                    onChange={(e) => setFormData({...formData, close_date: e.target.value})}
                                    className="w-full border border-gray-200 rounded-lg p-3 bg-gray-50 outline-none focus:ring-2 focus:ring-[#2174C3] transition-all text-black calendar-black"
                                />
                            </div>
                        </div>
                    </div>

                    <style dangerouslySetInnerHTML={{ __html: `
                        .calendar-black::-webkit-calendar-picker-indicator {
                            filter: brightness(0);
                            cursor: pointer;
                        }
                    `}} />

                    <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                        <label className="text-gray-600 font-bold">Status</label>
                        <div className="sm:col-span-2 flex space-x-8">
                            <label className="flex items-center space-x-2 cursor-pointer group">
                                <input 
                                    type="radio" 
                                    name="status" 
                                    value="Open" 
                                    checked={formData.status === 'Open'}
                                    onChange={(e) => setFormData({...formData, status: e.target.value})}
                                    className="w-5 h-5 text-[#2174C3] focus:ring-[#2174C3]"
                                />
                                <span className="text-black font-medium group-hover:text-[#2174C3] transition-colors">Open</span>
                            </label>
                            <label className="flex items-center space-x-2 cursor-pointer group">
                                <input 
                                    type="radio" 
                                    name="status" 
                                    value="Closed" 
                                    checked={formData.status === 'Closed'}
                                    onChange={(e) => setFormData({...formData, status: e.target.value})}
                                    className="w-5 h-5 text-[#2174C3] focus:ring-[#2174C3]"
                                />
                                <span className="text-black font-medium group-hover:text-[#2174C3] transition-colors">Closed</span>
                            </label>
                        </div>
                    </div>
                </div>

                <div className="flex justify-end space-x-2 mt-10">
                    {period && (
                        <button 
                            id="btn-delete-period"
                            onClick={handleDeleteClick}
                            className="bg-[#F15E5E] hover:bg-[#D32F2F] text-white px-3 py-1 text-sm rounded font-medium transition-colors cursor-pointer"
                        >
                            Delete
                        </button>
                    )}
                    <button 
                        onClick={onClose}
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

            {/* ─── Delete Confirmation ─────────────────────────────────── */}
            <ConfirmModal
                isOpen={showDeleteConfirm}
                onClose={() => setShowDeleteConfirm(false)}
                onConfirm={handleConfirmDelete}
                title="Confirm Delete"
                message="Are you sure you want to delete this TNA period?"
            />
        </div>
    );
};

export default TnaPeriodModal;
