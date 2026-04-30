import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { getUserFromToken } from '../utils/auth';
import ConfirmModal from './ConfirmModal';

const TnaMasterModal = ({ isOpen, onClose, tnaRecord, onSave, setToast }) => {
    const [user, setUser] = useState(null);
    const [periods, setPeriods] = useState([]);
    const [categories, setCategories] = useState([]);
    const [courses, setCourses] = useState([]);
    const [employees, setEmployees] = useState([]);
    
    const [formData, setFormData] = useState({
        tna_id: '',
        tna_period: '',
        course_category: '',
        course: '',
        group_name: 1,
        created_by: '',
    });
    
    const [participants, setParticipants] = useState([{ nik: '' }]);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

    useEffect(() => {
        const userData = getUserFromToken();
        if (userData) setUser(userData);
    }, []);

    const isAdmin = user?.role === 'Super Administrator' || user?.role === 'Administrator';

    // ─── 1. Fetch Basic Data ──────────────────────────────────────────────────
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const [resP, resC, resCo, resE] = await Promise.all([
                    api.get('/api/tna-period/'),
                    api.get('/api/course-categories/'),
                    api.get('/api/courses/'),
                    api.get('/api/employee/')
                ]);
                setPeriods(resP.data);
                setCategories(resC.data);
                setCourses(resCo.data);
                setEmployees(resE.data);
            } catch (err) {
                console.error('Failed to fetch modal data:', err);
            } finally {
                setLoading(false);
            }
        };

        if (isOpen) {
            fetchData();
        }
    }, [isOpen]);

    // ─── 2. Initialization with Full Master Data Fetch ───────────────────────
    useEffect(() => {
        if (!isOpen) return;

        if (tnaRecord?.tna_id) {
            const fetchFullTna = async () => {
                setLoading(true);
                try {
                    // Fetch Master Data
                    const resMaster = await api.get(`/api/tna-master/${tnaRecord.tna_id}/`);
                    const master = resMaster.data;
                    
                    setFormData({
                        tna_id: master.tna_id || '',
                        tna_period: master.tna_period || '',
                        course_category: master.course_category || '',
                        course: master.course || '',
                        group_name: master.group_name || 1,
                        created_by: master.created_by || '',
                    });

                    // Fetch Participants
                    const resPart = await api.get(`/api/tna-participant/?tna_id=${tnaRecord.tna_id}`);
                    if (resPart.data.length > 0) {
                        setParticipants(resPart.data.map(p => ({ nik: p.nik })));
                    } else {
                        setParticipants([{ nik: '' }]);
                    }
                } catch (err) {
                    console.error('Failed to fetch full TNA data:', err);
                } finally {
                    setLoading(false);
                }
            };
            fetchFullTna();
        } else {
            setFormData({
                tna_id: '',
                tna_period: '',
                course_category: '',
                course: '',
                group_name: 1,
                created_by: '',
            });
            setParticipants([{ nik: '' }]);
        }
    }, [tnaRecord, isOpen]);

    // ─── 3. Dynamic Participant Switching Logic ───────────────────────────────
    const handleGroupSwitch = async (newGroupName) => {
        if (!isAdmin || !formData.course || !formData.tna_period) {
            setFormData(prev => ({ ...prev, group_name: newGroupName }));
            return;
        }

        try {
            const resMaster = await api.get('/api/tna-master/', {
                params: {
                    period: formData.tna_period,
                    course: formData.course,
                    group_name: newGroupName
                }
            });

            if (resMaster.data.length > 0) {
                const matchedTna = resMaster.data[0];
                setFormData({
                    tna_id: matchedTna.tna_id,
                    tna_period: matchedTna.tna_period,
                    course_category: matchedTna.course_category,
                    course: matchedTna.course,
                    group_name: matchedTna.group_name,
                    created_by: matchedTna.created_by
                });
                
                const resPart = await api.get('/api/tna-participant/', {
                    params: { tna_id: matchedTna.tna_id }
                });
                setParticipants(resPart.data.length > 0 ? resPart.data.map(p => ({ nik: p.nik })) : [{ nik: '' }]);
            } else {
                setFormData(prev => ({ ...prev, group_name: newGroupName, tna_id: '' }));
                setParticipants([{ nik: '' }]);
            }
        } catch (err) {
            console.error('Failed to switch group:', err);
            setFormData(prev => ({ ...prev, group_name: newGroupName }));
        }
    };

    if (!isOpen) return null;

    const handleAddParticipant = () => {
        setParticipants([...participants, { nik: '' }]);
    };

    const handleRemoveParticipant = (index) => {
        if (participants.length > 1) {
            const newP = [...participants];
            newP.splice(index, 1);
            setParticipants(newP);
        }
    };

    const handleParticipantChange = (index, value) => {
        const newP = [...participants];
        newP[index].nik = value;
        setParticipants(newP);
    };

    const handleSave = async () => {
        if (!formData.tna_id) {
            setToast({ message: 'TNA ID is required', type: 'error' });
            return;
        }
        if (!formData.created_by) {
            setToast({ message: 'Created By is required', type: 'error' });
            return;
        }
        
        setSaving(true);
        try {
            let masterExists = false;
            try {
                await api.get(`/api/tna-master/${formData.tna_id}/`);
                masterExists = true;
            } catch (e) {
                masterExists = false;
            }

            if (masterExists) {
                await api.patch(`/api/tna-master/${formData.tna_id}/`, formData);
            } else {
                await api.post('/api/tna-master/', formData);
            }
            
            const currentRes = await api.get(`/api/tna-participant/?tna_id=${formData.tna_id}`);
            for (const p of currentRes.data) {
                await api.delete(`/api/tna-participant/${p.tna_participant_id}/`);
            }

            for (const p of participants) {
                if (p.nik) {
                    await api.post('/api/tna-participant/', {
                        tna: formData.tna_id,
                        nik: p.nik
                    });
                }
            }

            const isUpdate = !!tnaRecord?.tna_id;
            setToast({ 
                message: isUpdate ? 'TNA Update succesfully' : 'TNA Added succesfully', 
                type: 'success' 
            });
            onSave();
            onClose();
        } catch (err) {
            console.error('Failed to save TNA:', err);
            setToast({ message: 'TNA Added Unsuccesfully', type: 'error' });
        } finally {
            setSaving(false);
        }
    };

    const handleDeleteClick = () => {
        setShowDeleteConfirm(true);
    };

    const handleConfirmDelete = async () => {
        try {
            await api.delete(`/api/tna-master/${formData.tna_id}/`);
            setToast({ message: 'TNA Deleted succesfully', type: 'success' });
            onSave();
            onClose();
        } catch (err) {
            console.error('Failed to delete TNA:', err);
            setToast({ message: 'TNA Deleted Unsuccesfully', type: 'error' });
        } finally {
            setShowDeleteConfirm(false);
        }
    };

    const administratorList = employees.filter(e => e.role === 'Administrator');

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm overflow-y-auto">
            <div className="bg-white rounded-2xl w-full max-w-[1200px] shadow-2xl p-0 my-8 animate-in slide-in-from-bottom-4 duration-300 overflow-hidden">
                <div className="p-8 pb-4">
                    <h2 className="text-3xl font-bold mb-2 text-gray-800 tracking-tight">
                        Training Needs Analysis
                    </h2>
                </div>

                <div className="px-8 pb-8">
                    <div className="border border-gray-100 rounded-xl overflow-hidden mb-6">
                        <div className="bg-gray-100 flex text-[10px] font-bold text-gray-400 uppercase tracking-widest border-b border-gray-200">
                            <div className="w-[20%] p-3 border-r border-gray-200">Tna Period</div>
                            <div className="w-[20%] p-3 border-r border-gray-200">Category</div>
                            <div className="w-[25%] p-3 border-r border-gray-200">Courses</div>
                            <div className="w-[10%] p-3 border-r border-gray-200 text-center">Group</div>
                            <div className="w-[15%] p-3 border-r border-gray-200">Tna ID</div>
                            <div className="w-[10%] p-3 text-center">Add</div>
                        </div>
                        <div className="flex bg-white items-start">
                            <div className="w-[20%] p-3 border-r border-gray-50">
                                <select 
                                    value={formData.tna_period}
                                    onChange={(e) => setFormData({...formData, tna_period: e.target.value})}
                                    className="w-full border border-gray-200 rounded-lg p-2 bg-gray-50 underline-none focus:ring-2 focus:ring-[#2174C3] transition-all text-sm text-black"
                                >
                                    <option value="">Select Period</option>
                                    {periods.map(p => (
                                        <option key={p.tna_period_id} value={p.tna_period_id}>{p.period_code}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="w-[20%] p-3 border-r border-gray-50">
                                <select 
                                    value={formData.course_category}
                                    onChange={(e) => setFormData({...formData, course_category: e.target.value})}
                                    className="w-full border border-gray-200 rounded-lg p-2 bg-gray-50 outline-none focus:ring-2 focus:ring-[#2174C3] transition-all text-sm text-black"
                                >
                                    <option value="">Select Category</option>
                                    {categories.map(c => (
                                        <option key={c.course_category_id} value={c.course_category_id}>{c.category_name}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="w-[25%] p-3 border-r border-gray-50">
                                <select 
                                    value={formData.course}
                                    onChange={(e) => setFormData({...formData, course: e.target.value})}
                                    className="w-full border border-gray-200 rounded-lg p-2 bg-gray-50 outline-none focus:ring-2 focus:ring-[#2174C3] transition-all text-sm text-black"
                                >
                                    <option value="">Select Course</option>
                                    {courses
                                        .filter(c => !formData.course_category || c.course_category === formData.course_category)
                                        .map(c => (
                                            <option key={c.course_id} value={c.course_id}>{c.course_name}</option>
                                        ))
                                    }
                                </select>
                            </div>
                            <div className="w-[10%] p-3 border-r border-gray-50">
                                <select 
                                    value={formData.group_name}
                                    onChange={(e) => handleGroupSwitch(parseInt(e.target.value))}
                                    className="w-full border border-gray-200 rounded-lg p-2 bg-gray-50 outline-none focus:ring-2 focus:ring-[#2174C3] transition-all text-sm text-black text-center"
                                >
                                    {[1,2,3,4,5,6].map(v => (
                                        <option key={v} value={v}>{v}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="w-[15%] p-3 border-r border-gray-50">
                                <input 
                                    type="text" 
                                    placeholder="ID"
                                    value={formData.tna_id}
                                    onChange={(e) => setFormData({...formData, tna_id: e.target.value})}
                                    className="w-full border border-gray-200 rounded-lg p-2 bg-gray-100 outline-none focus:ring-2 focus:ring-[#2174C3] transition-all text-sm text-black"
                                />
                            </div>
                            <div className="w-[10%] p-3 flex justify-center">
                                <button 
                                    onClick={handleAddParticipant}
                                    className="bg-blue-50 hover:bg-[#2174C3] text-[#2174C3] hover:text-white w-8 h-8 rounded-lg font-bold transition-all flex items-center justify-center border border-blue-100 shadow-sm cursor-pointer"
                                >
                                    <span className="text-xl">+</span>
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="border border-gray-100 rounded-xl overflow-hidden">
                        <div className="bg-gray-100 flex text-[10px] font-bold text-gray-400 uppercase tracking-widest border-b border-gray-200">
                            <div className="w-[50%] p-3 border-r border-gray-200">Employee</div>
                            <div className="w-[40%] p-3 border-r border-gray-200">Created By</div>
                            <div className="w-[10%] p-3 text-center">Del</div>
                        </div>
                        <div className="max-h-[300px] overflow-y-auto custom-scrollbar">
                            {participants.map((participant, idx) => (
                                <div key={idx} className="flex bg-white items-center border-b border-gray-50 last:border-0 hover:bg-gray-50/30 transition-all">
                                    <div className="w-[50%] p-3 border-r border-gray-50">
                                        <select 
                                            value={participant.nik}
                                            onChange={(e) => handleParticipantChange(idx, e.target.value)}
                                            className="w-full border border-gray-200 rounded-lg p-2 outline-none focus:ring-2 focus:ring-[#2174C3] transition-all text-sm text-black"
                                        >
                                            <option value="">Select Employee</option>
                                            {employees.map(e => (
                                                <option key={e.nik} value={e.nik}>{e.nik} — {e.full_name}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <div className="w-[40%] p-3 border-r border-gray-50">
                                        {idx === 0 ? (
                                            <select 
                                                value={formData.created_by}
                                                onChange={(e) => setFormData({...formData, created_by: e.target.value})}
                                                className="w-full border border-gray-200 rounded-lg p-2 outline-none focus:ring-2 focus:ring-[#2174C3] transition-all text-sm text-black"
                                            >
                                                <option value="">Select Creator</option>
                                                {administratorList.map(e => (
                                                    <option key={e.nik} value={e.nik}>{e.full_name}</option>
                                                ))}
                                            </select>
                                        ) : (
                                            <div className="text-gray-300 text-xs px-2 flex items-center h-full">Same as above</div>
                                        )}
                                    </div>
                                    <div className="w-[10%] p-3 flex justify-center">
                                        <button 
                                            onClick={() => handleRemoveParticipant(idx)}
                                            disabled={participants.length === 1}
                                            className="bg-red-50 hover:bg-red-500 text-red-500 hover:text-white w-7 h-7 flex items-center justify-center rounded-lg transition-all disabled:opacity-30 border border-red-50 cursor-pointer"
                                        >
                                            <span className="mb-0.5 text-lg font-bold">—</span>
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="bg-gray-50 px-8 py-5 flex justify-end items-center border-t border-gray-100 space-x-2">
                    {isAdmin && formData.tna_id && (
                        <button 
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
                        className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-4 py-1 text-sm rounded font-medium transition-colors shadow-lg cursor-pointer disabled:opacity-50"
                    >
                        {saving ? 'Saving...' : 'Save'}
                    </button>
                </div>

                <style dangerouslySetInnerHTML={{ __html: `
                    .custom-scrollbar::-webkit-scrollbar {
                        width: 4px;
                        height: 4px;
                    }
                    .custom-scrollbar::-webkit-scrollbar-track {
                        background: transparent;
                    }
                    .custom-scrollbar::-webkit-scrollbar-thumb {
                        background: #CBD5E0;
                        border-radius: 10px;
                    }
                    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                        background: #A0AEC0;
                    }
                `}} />
            </div>

            {/* ─── Delete Confirmation ─────────────────────────────────── */}
            <ConfirmModal
                isOpen={showDeleteConfirm}
                onClose={() => setShowDeleteConfirm(false)}
                onConfirm={handleConfirmDelete}
                title="Confirm Delete"
                message="Are you sure you want to delete this TNA and all its participants?"
            />
        </div>
    );
};

export default TnaMasterModal;
