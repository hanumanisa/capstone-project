import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Navigate, useNavigate, Link, useLocation } from 'react-router-dom';
import MainLayout from '../components/MainLayout';
import { getUserFromToken } from '../utils/auth';
import api from '../api/axios';
import ConfirmModal from '../components/ConfirmModal';
import Toast from '../components/Toast';
import YearPicker from '../components/YearPicker';
import './TrainingEvaluationPage.css';

/**
 * TrainingEvaluationPage Component
 * Manages the L1 and L2 evaluation forms for administrators.
 */
export default function TrainingEvaluationPage() {
    const navigate = useNavigate();
    const location = useLocation();
    const user = getUserFromToken();
    const isAdmin = ['Super Administrator', 'Administrator', 'Dean'].includes(user?.role);
    const canEdit = ['Super Administrator', 'Administrator'].includes(user?.role);

    // --- UI Visibility State ---
    const [showTpl, setShowTpl] = useState(false);
    const [showEval, setShowEval] = useState(false);
    const [showResponse, setShowResponse] = useState(false);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [showSuccessMessage, setShowSuccessMessage] = useState(false);
    const [showDescModal, setShowDescModal] = useState(false);
    const [showTrainingDropdown, setShowTrainingDropdown] = useState(false);
    const [toast, setToast] = useState(null);

    // --- Data State ---
    const [allCards, setAllCards] = useState([]);
    const [selectedCard, setSelectedCard] = useState(null);
    const [realRespondents, setRealRespondents] = useState([]);
    const [trainingMasters, setTrainingMasters] = useState([]);
    const [isSaving, setIsSaving] = useState(false);
    const [cardToDelete, setCardToDelete] = useState(null);
    const [loading, setLoading] = useState(false);

    // --- Filter & Pagination State ---
    const [selectedMainTemplate, setSelectedMainTemplate] = useState('All_Templates');
    const [searchQuery, setSearchQuery] = useState('');
    const [activeYear, setActiveYear] = useState(new Date().getFullYear().toString());
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 50;

    const activeYearRef = useRef(activeYear);
    useEffect(() => {
        activeYearRef.current = activeYear;
    }, [activeYear]);

    // --- Form Management State ---
    const [selectedTemplate, setSelectedTemplate] = useState('L1_Templates');
    const [selectedTraining, setSelectedTraining] = useState('');
    const [trainingSearchQuery, setTrainingSearchQuery] = useState('');
    const [isEditingDeadline, setIsEditingDeadline] = useState(false);
    const [editDeadlineValue, setEditDeadlineValue] = useState('');

    // Form Inputs
    const [tplName, setTplName] = useState('');
    const [tplType, setTplType] = useState('L1_Templates');
    const [tplDesc, setTplDesc] = useState('');
    const [tplTrainingId, setTplTrainingId] = useState('');
    const [tplDeadline, setTplDeadline] = useState('');

    // Dynamic Rows
    const [evalRows, setEvalRows] = useState([{ q: '', type: 'Rating Scale', active: true, options: [], optionAnswers: [], scores: [] }]);
    const [l2Rows, setL2Rows] = useState([{ q: '', opts: ['', '', '', ''], optActive: [true, true, true, true], optVisible: [true, true, true, true], answer: 'A', score: 0 }]);

    const formatDeadline = (dateString) => {
        if (!dateString) return 'No limit';
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return dateString;
        
        const day = String(date.getDate()).padStart(2, '0');
        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const month = months[date.getMonth()];
        const year = date.getFullYear();
        
        return `${day}-${month}-${year}`;
    };

    // --- Data Loading Functions ---

    /** Fetches Training Master data for dropdowns */
    const loadTrainingMasters = async () => {
        const fetchYear = activeYear;
        try {
            const res = await api.get(`/api/training-master/?year=${fetchYear}&page_size=1000`);
            if (activeYearRef.current === fetchYear) {
                const data = Array.isArray(res.data) ? res.data : (res.data.results || []);
                const sortedData = data.sort((a, b) => (a.training_title || "").localeCompare(b.training_title || ""));
                setTrainingMasters(sortedData);
            }
        } catch (err) {
            console.error("Failed to fetch trainings", err);
        }
    };

    /** Fetches all Evaluation Forms and maps them to UI card format */
    const loadForms = async () => {
        const fetchYear = activeYear;
        setLoading(true);
        try {
            const res = await api.get(`/api/evaluation-forms/?year=${fetchYear}`);
            if (activeYearRef.current === fetchYear) {
                const data = Array.isArray(res.data) ? res.data : [];
                const mapping = data.map(item => {
                    const isL2 = item.form_type === 'L2' || (item.form_name && item.form_name.includes('[L2]'));
                    const year = item.year ? String(item.year) : (item.created_at ? new Date(item.created_at).getFullYear().toString() : fetchYear);

                    const card = {
                        id: item.form_id,
                        title: (item.form_name || '').replace('[L1] ', '').replace('[L2] ', ''),
                        type: isL2 ? 'L2' : 'L1',
                        year: year,
                        description: item.description || '',
                        deadline: item.deadline ? item.deadline.slice(0, 16) : '',
                        responses: item.responses_count || 0,
                        hasQuestions: item.questions && item.questions.length > 0,
                        trainingId: item.training_master,
                        trainingTitle: item.training_title
                    };

                    if (isL2) {
                        card.l2Questions = (item.questions || []).map(q => {
                            const correctIdx = (q.options || []).findIndex(o => o.is_correct);
                            return {
                                q: q.question_text,
                                options: q.options || [],
                                answer: correctIdx !== -1 ? String.fromCharCode(65 + correctIdx) : 'A',
                                score: q.score || 0,
                                optActive: (q.options || []).map(o => o.is_active !== false),
                                optVisible: (q.options || []).map(() => true)
                            };
                        });
                    } else {
                        card.l1Questions = (item.questions || []).map(q => ({
                            q: q.question_text,
                            type: q.question_type || 'Rating Scale',
                            active: q.is_active !== false
                        }));
                    }
                    return card;
                });
                setAllCards(mapping);
            }
        } catch (err) {
            console.error("Failed to fetch forms", err);
        } finally {
            if (activeYearRef.current === fetchYear) {
                setLoading(false);
            }
        }
    };

    useEffect(() => {
        loadForms();
        loadTrainingMasters();
        setCurrentPage(1);
    }, [searchQuery, selectedMainTemplate, activeYear]);

    // --- Memoized Computations ---

    const isL2 = selectedTemplate === 'L2_Templates';

    const tplNameDuplicate = useMemo(() => {
        if (!tplName.trim()) return false;
        const type = tplType === 'L1_Templates' ? 'L1' : 'L2';
        return allCards.some(c =>
            String(c.trainingId) === String(tplTrainingId) &&
            c.type === type &&
            (c.title || '').trim().toLowerCase() === tplName.trim().toLowerCase()
        );
    }, [tplName, tplType, tplTrainingId, allCards]);

    const filteredCards = useMemo(() => {
        return allCards.filter(c => {
            const matchYear = c.year === activeYear;
            const matchType = selectedMainTemplate === 'All_Templates' ? true
                : (selectedMainTemplate === 'L1_Templates' ? c.type === 'L1' : c.type === 'L2');
            const matchSearch = searchQuery.trim() === '' ? true : (c.title || '').toLowerCase().includes(searchQuery.toLowerCase());
            return matchYear && matchType && matchSearch;
        });
    }, [allCards, activeYear, selectedMainTemplate, searchQuery]);

    const totalPages = Math.max(1, Math.ceil(filteredCards.length / itemsPerPage));
    const paginatedCards = filteredCards.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);
    const pageNumbers = Array.from({ length: totalPages }, (_, i) => i + 1);

    const filteredTrainings = useMemo(() => {
        const type = isL2 ? 'L2' : 'L1';
        return allCards.filter(c => c.type === type && c.year === activeYear)
            .sort((a, b) => (a.title || "").localeCompare(b.title || ""));
    }, [allCards, isL2, activeYear]);

    const filteredTrainingOptions = useMemo(() => {
        if (!(trainingSearchQuery || '').trim()) return filteredTrainings;
        const query = trainingSearchQuery.toLowerCase();
        return filteredTrainings.filter(c =>
            (c.title || '').toLowerCase().includes(query) ||
            (c.trainingTitle || '').toLowerCase().includes(query)
        );
    }, [filteredTrainings, trainingSearchQuery]);

    const responseRespondentsPreview = useMemo(() => {
        return realRespondents.slice(0, 5);
    }, [realRespondents]);

    // --- Logic Functions ---

    /** Sets the current training for the evaluation builder */
    const selectTraining = (training) => {
        const type = training.type === 'L2' ? 'L2_Templates' : 'L1_Templates';
        const displayLabel = `${training.title} - ${training.trainingTitle}`;
        setSelectedTemplate(type);
        setSelectedTraining(displayLabel);
        setTrainingSearchQuery(displayLabel);
        setShowTrainingDropdown(false);
        loadTrainingQuestions(training, type);
    };

    /** Populates the builder rows with existing questions from a template/card */
    const loadTrainingQuestions = (training, forceType = null) => {
        const type = forceType || selectedTemplate;
        if (type === 'L2_Templates') {
            if (training.l2Questions && training.l2Questions.length > 0) {
                const mappedQuestions = training.l2Questions.map(q => ({
                    ...q,
                    optActive: q.options ? q.options.map(o => o.is_active !== false) : [true, true, true, true],
                    optVisible: q.options ? q.options.map(() => true) : [true, true, true, true],
                    opts: q.options ? q.options.map(o => o.option_text) : ['', '', '', '']
                }));
                setL2Rows(mappedQuestions);
            } else {
                setL2Rows([{ q: '', opts: ['', '', '', ''], optActive: [true, true, true, true], optVisible: [true, true, true, true], answer: 'A', score: 0 }]);
            }
        } else {
            if (training.l1Questions && training.l1Questions.length > 0) {
                setEvalRows(JSON.parse(JSON.stringify(training.l1Questions)));
            } else {
                setEvalRows([{ q: '', type: 'Rating', active: true, options: [], optionAnswers: [], scores: [] }]);
            }
        }
    };

    /** Opens the response summary for a specific evaluation */
    const openCardDetail = async (card) => {
        setSelectedCard(card);
        setShowDescModal(false);
        setIsEditingDeadline(false);
        setEditDeadlineValue(card.deadline || '');
        setRealRespondents([]);
        setShowResponse(true);

        try {
            const res = await api.get(`/api/evaluation-forms/${card.id}/respondents/`);
            const converted = (res.data || []).map(r => {
                return { ...r };
            });
            setRealRespondents(converted);
        } catch (err) {
            console.error("Failed to fetch respondents", err);
        }
    };

    /** Updates the deadline for the selected evaluation form */
    const updateDeadline = async () => {
        if (!selectedCard) return;
        try {
            await api.patch(`/api/evaluation-forms/${selectedCard.id}/`, {
                deadline: editDeadlineValue || null
            });
            setIsEditingDeadline(false);
            loadForms();
            setSelectedCard({ ...selectedCard, deadline: editDeadlineValue });
        } catch (err) {
            alert('Failed to update deadline');
            console.error(err);
        }
    };

    /** Generates and downloads an Excel file containing all respondents for the selected form */
    const exportToExcel = () => {
        if (!selectedCard) return;
        const respondents = realRespondents;

        let tableHTML = '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40"><head><meta charset="UTF-8"><!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet><x:Name>Responses</x:Name><x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet></x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]--></head><body>';
        tableHTML += '<h2>Data Responden Evaluasi</h2>';
        tableHTML += `<p><b>Evaluasi:</b> ${selectedCard?.title || '-'}</p>`;
        tableHTML += `<p><b>Training:</b> ${selectedCard?.trainingTitle || '-'}</p>`;
        tableHTML += `<p><b>Tipe:</b> ${selectedCard?.type || '-'}</p>`;
        tableHTML += '<table border="1">';
        tableHTML += '<tr>';
        tableHTML += '<th style="background-color:#2174C3;color:white;">No</th>';
        tableHTML += '<th style="background-color:#2174C3;color:white;">NIK</th>';
        tableHTML += '<th style="background-color:#2174C3;color:white;">Name</th>';
        if (selectedCard?.type === 'L2') {
            tableHTML += '<th style="background-color:#2174C3;color:white;">Score (0-100)</th>';
            tableHTML += '<th style="background-color:#2174C3;color:white;">Scale (1-4)</th>';
        } else {
            tableHTML += '<th style="background-color:#2174C3;color:white;">Score</th>';
        }
        tableHTML += '</tr>';

        respondents.forEach((r, i) => {
            tableHTML += '<tr>';
            tableHTML += `<td align="center">${i + 1}</td>`;
            tableHTML += `<td>${r.nik || 'N/A'}</td>`;
            tableHTML += `<td>${r.name}</td>`;
            if (selectedCard?.type === 'L2') {
                tableHTML += `<td align="center">${r.raw_score}</td>`;
                tableHTML += `<td align="center">${r.score}</td>`;
            } else {
                tableHTML += `<td align="center">${r.score}</td>`;
            }
            tableHTML += '</tr>';
        });

        tableHTML += '</table></body></html>';

        const blob = new Blob([tableHTML], { type: 'application/vnd.ms-excel;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const fileName = `${selectedCard.title}_${selectedCard.trainingTitle}_${selectedCard.type}_responses`.replace(/\s+/g, '_');
        a.download = `${fileName}.xls`;
        a.click();
        URL.revokeObjectURL(url);
    };

    /** Submits a new Evaluation Template header */
    const submitTemplate = async () => {
        if (!tplName.trim() || tplNameDuplicate) return;

        try {
            const typeValue = tplType === 'L1_Templates' ? 'L1' : 'L2';
            await api.post('/api/evaluation-forms/', {
                form_name: (typeValue === 'L1' ? '[L1] ' : '[L2] ') + tplName,
                form_type: typeValue,
                training_id: tplTrainingId,
                description: tplDesc,
                deadline: tplDeadline,
                is_active: true,
                questions: []
            });
            setShowTpl(false);
            setTplName('');
            setTplType('L1_Templates');
            setTplDesc('');
            setTplTrainingId('');
            setTplDeadline('');
            loadForms();
        } catch (err) {
            alert('Failed to save template');
            console.error(err);
        }
    };

    // --- Builder Helper Functions ---
    const addEvalRow = () => setEvalRows([...evalRows, { q: '', type: 'Rating', active: true, options: [], optionAnswers: [], scores: [] }]);
    const removeEvalRow = (index) => setEvalRows(evalRows.filter((_, i) => i !== index));
    const addL2Row = () => setL2Rows([...l2Rows, { q: '', opts: ['', '', '', ''], optActive: [true, true, true, true], optVisible: [true, true, true, true], answer: 'A', score: 0 }]);
    const removeL2Row = (index) => { if (l2Rows.length > 1) setL2Rows(l2Rows.filter((_, i) => i !== index)); };

    const removeL2Option = (rowIndex, optionIndex) => {
        const newRows = [...l2Rows];
        newRows[rowIndex].opts.splice(optionIndex, 1);
        newRows[rowIndex].optActive.splice(optionIndex, 1);
        newRows[rowIndex].optVisible.splice(optionIndex, 1);
        const labels = 'ABCDEFGHIJ';
        if (!newRows[rowIndex].opts[labels.indexOf(newRows[rowIndex].answer)]) {
            newRows[rowIndex].answer = 'A';
        }
        setL2Rows(newRows);
    };

    const onTemplateChange = (e) => {
        const newTemplate = e.target.value;
        setSelectedTemplate(newTemplate);
        setSelectedTraining('');
        setTrainingSearchQuery('');
        setShowTrainingDropdown(false);
        if (newTemplate === 'L2_Templates') {
            setL2Rows([{ q: '', opts: ['', '', '', ''], optActive: [true, true, true, true], optVisible: [true, true, true, true], answer: 'A', score: 0 }]);
        } else {
            setEvalRows([{ q: '', type: 'Rating', active: true, options: [], optionAnswers: [], scores: [] }]);
        }
    };

    const clearTrainingSearch = () => {
        setTrainingSearchQuery('');
        setSelectedTraining('');
        setShowTrainingDropdown(false);
        if (selectedTemplate === 'L2_Templates') {
            setL2Rows([{ q: '', opts: ['', '', '', ''], optActive: [true, true, true, true], optVisible: [true, true, true, true], answer: 'A', score: 0 }]);
        } else {
            setEvalRows([{ q: '', type: 'Rating Scale', active: true, options: [], optionAnswers: [], scores: [] }]);
        }
    };

    /** Finalizes and saves the entire evaluation form structure (questions & options) */
    const saveEvaluation = async () => {
        if (isSaving) return;
        if (!selectedTraining) {
            alert('Please select a training first');
            return;
        }
        const trainingIdx = allCards.findIndex(c => `${c.title} - ${c.trainingTitle}` === selectedTraining);
        if (trainingIdx === -1) return;
        let training = allCards[trainingIdx];

        let payloadQuestions = [];
        if (isL2) {
            const hasInvalidScore = l2Rows.some(row => row.q.trim() !== '' && Number(row.score) < 100);
            if (hasInvalidScore) {
                setToast({ message: 'Score must be 100', type: 'error' });
                return;
            }

            l2Rows.forEach(row => {
                if (row.q.trim() !== '') {
                    const allOptions = [];
                    row.opts.forEach((opt, index) => {
                        if (opt.trim() !== '') {
                            allOptions.push({
                                option_text: opt,
                                is_correct: String.fromCharCode(65 + index) === row.answer,
                                is_active: row.optActive[index] !== false
                            });
                        }
                    });
                    if (allOptions.length > 0) {
                        payloadQuestions.push({
                            question_text: row.q,
                            question_type: 'Multiple Choice',
                            evaluation_type: 'L2',
                            is_required: true,
                            score: row.score || 0,
                            options: allOptions
                        });
                    }
                }
            });
        } else {
            evalRows.forEach(row => {
                if (row.q.trim() !== '') {
                    payloadQuestions.push({
                        question_text: row.q,
                        question_type: row.type || 'Rating Scale',
                        evaluation_type: 'L1',
                        is_required: true,
                        is_active: row.active !== false
                    });
                }
            });
        }

        setIsSaving(true);
        try {
            await api.put(`/api/evaluation-forms/${training.id}/`, {
                form_name: (training.type === 'L1' ? '[L1] ' : '[L2] ') + training.title,
                form_type: training.type,
                questions: payloadQuestions
            });
            setShowEval(false);
            setShowSuccessMessage(true);
            setTimeout(() => setShowSuccessMessage(false), 3000);
            loadForms();
        } catch (err) {
            alert('Failed to save evaluation');
            console.error(err);
        } finally {
            setIsSaving(false);
        }
    };

    const openEvaluationFromResponse = () => {
        const card = selectedCard;
        if (!card) return;
        setShowResponse(false);
        setTimeout(() => {
            const displayLabel = `${card.title} - ${card.trainingTitle}`;
            const tplType = card.type === 'L1' ? 'L1_Templates' : 'L2_Templates';
            setSelectedTemplate(tplType);
            setSelectedTraining(displayLabel);
            setTrainingSearchQuery(displayLabel);
            setShowEval(true);
            loadTrainingQuestions(card, tplType);
        }, 100);
    };

    const openBlankEvaluation = () => {
        setSelectedTemplate('L1_Templates');
        setSelectedTraining('');
        setTrainingSearchQuery('');
        setShowTrainingDropdown(false);
        setEvalRows([{ q: '', type: 'Rating', active: true, options: [], optionAnswers: [], scores: [] }]);
        setL2Rows([{ q: '', opts: ['', '', '', ''], optActive: [true, true, true, true], optVisible: [true, true, true, true], answer: 'A', score: 0 }]);
        setShowEval(true);
    };

    const confirmDeleteCard = (card, e) => {
        e.stopPropagation();
        setCardToDelete(card);
        setShowDeleteConfirm(true);
    };

    const deleteCard = async () => {
        if (!cardToDelete) return;
        try {
            await api.delete(`/api/evaluation-forms/${cardToDelete.id}/`);
            setCardToDelete(null);
            setShowDeleteConfirm(false);
            loadForms();
        } catch (err) {
            alert('Failed to delete');
            console.error(err);
        }
    };

    if (user && !isAdmin) {
        return <Navigate to="/dashboard" replace />;
    }

    return (
        <MainLayout>
            <div className="relative">
                {/* Success Message */}
                {showSuccessMessage && (
                    <div className="fixed top-20 right-6 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-[300] flex items-center gap-2 animate-fade-in-down">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                        <span className="font-medium">Evaluation saved successfully!</span>
                    </div>
                )}

                {isAdmin && (
                    <div className="flex space-x-8 border-b border-gray-300 mb-6 px-4 sm:px-0 mt-4">
                        <Link
                            to="/evaluation"
                            className={`pb-3 px-1 font-bold text-xl transition-colors ${location.pathname === '/evaluation'
                                ? 'text-[#2174C3] border-b-4 border-[#2174C3]'
                                : 'text-gray-400 hover:text-[#2174C3]'
                                }`}
                        >
                            Company Evaluation
                        </Link>
                        <Link
                            to="/evaluation-employee"
                            className={`pb-3 px-1 font-bold text-xl transition-colors ${location.pathname === '/evaluation-employee'
                                ? 'text-[#2174C3] border-b-4 border-[#2174C3]'
                                : 'text-gray-400 hover:text-[#2174C3]'
                                }`}
                        >
                            My Evaluation
                        </Link>
                    </div>
                )}

                {/* Toolbar */}
                <div className="bg-white p-3 rounded-xl shadow-sm border border-gray-100 flex flex-col sm:flex-row items-center gap-3 mb-10 transition-all duration-300 sticky top-0 z-30">
                    <div className="relative w-full sm:w-1/3">
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                            placeholder="Search"
                            className="w-full pl-4 pr-10 py-2 rounded-lg border-none bg-gray-100 focus:bg-white focus:ring-1 focus:ring-[#2174C3] transition-all text-gray-600 placeholder-gray-400"
                        />
                        <span className="absolute right-3 top-2.5 text-gray-400 pointer-events-none">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                        </span>
                    </div>
                    <div className="relative w-full sm:w-48">
                        <select
                            value={selectedMainTemplate}
                            onChange={e => setSelectedMainTemplate(e.target.value)}
                            className="w-full border-none rounded-lg px-4 py-2 text-sm text-gray-600 bg-gray-100 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#2174C3] appearance-none bg-no-repeat bg-right-4"
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

                    <div className="flex-1 flex flex-col sm:flex-row items-center justify-end gap-6">
                        <YearPicker selectedYear={activeYear} onYearChange={(y) => setActiveYear(y)} />
                        <div className="flex gap-2">
                            {canEdit && (
                                <>
                                    <button onClick={() => setShowTpl(true)} className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-4 py-2 rounded-lg font-medium flex items-center text-sm transition-all shadow-sm cursor-pointer">
                                        <span className="mr-2 text-xl font-bold">+</span> Template
                                    </button>
                                    <button onClick={openBlankEvaluation} className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-4 py-2 rounded-lg font-medium flex items-center text-sm transition-all shadow-sm cursor-pointer">
                                        <span className="mr-2 text-xl font-bold">+</span> Evaluation
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                </div>

                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-6 gap-4">
                    <h1 className="text-4xl font-bold text-gray-800 tracking-tight">Training Evaluation</h1>
                </div>

                {/* Cards Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 mb-10">
                    {paginatedCards.length === 0 ? (
                        <div className="col-span-5 py-16 flex flex-col items-center text-gray-400">
                            <svg className="w-12 h-12 mb-3 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            <p className="text-sm font-medium">No data available</p>
                        </div>
                    ) : (
                        paginatedCards.map((card, i) => (
                            <CardItem key={i} card={card} canEdit={canEdit} onClick={() => openCardDetail(card)} onDelete={(e) => confirmDeleteCard(card, e)} />
                        ))
                    )}
                </div>

                {/* Pagination */}
                <div className="sticky bottom-0 bg-[#F4F7FA]/95 backdrop-blur-sm py-4 flex flex-col items-end gap-2 z-20 mt-4 border-t border-gray-100">
                        <div className="flex items-center space-x-1">
                            <button
                                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                disabled={currentPage === 1}
                                className={`px-4 py-2 rounded-md font-medium text-sm transition-all ${currentPage === 1 ? 'bg-[#E2E8F0] text-gray-400 cursor-not-allowed' : 'bg-[#E2E8F0] text-gray-600 hover:bg-gray-300'}`}
                            >
                                Previous
                            </button>
                            {pageNumbers.map(p => (
                                <button
                                    key={p}
                                    onClick={() => setCurrentPage(p)}
                                    className={`px-4 py-2 rounded-md font-medium text-sm transition-all ${p === currentPage ? 'bg-[#2174C3] text-white' : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'}`}
                                >
                                    {p}
                                </button>
                            ))}
                            <button
                                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                disabled={currentPage === totalPages}
                                className={`px-4 py-2 rounded-md font-medium text-sm transition-all ${currentPage === totalPages ? 'bg-white border border-gray-200 text-gray-400 cursor-not-allowed' : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'}`}
                            >
                                Next
                            </button>
                        </div>
                        <div className="text-xs text-gray-400 font-medium">
                            Showing {(currentPage - 1) * itemsPerPage + 1}–{Math.min(currentPage * itemsPerPage, filteredCards.length)} of {filteredCards.length} evaluations
                        </div>
                    </div>
                

                {/* MODALS */}

                {/* Template Modal */}
                {showTpl && (
                    <div className="fixed inset-0 z-[300] flex items-center justify-center p-4 bg-black/60">
                        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-10 relative">

                            <h2 className="text-3xl font-bold text-black mb-2">Templates Form</h2>
                            <hr className="mb-8 border-gray-100" />

                            <div className="space-y-6">
                                <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-4">
                                    <label className="text-black font-semibold">Select Training <span className="text-red-500">*</span></label>
                                    <div className="sm:col-span-2">
                                        <select
                                            value={tplTrainingId}
                                            onChange={e => setTplTrainingId(e.target.value)}
                                            className="w-full border-none rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-[#2174C3] transition-all bg-gray-100 text-black outline-none"
                                        >
                                            <option value="">Select Training</option>
                                            {trainingMasters.map(t => (
                                                <option key={t.training_id} value={t.training_id}>{t.training_title} ({t.training_code})</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-4">
                                    <label className="text-black font-semibold">Template Name <span className="text-red-500">*</span></label>
                                    <input
                                        type="text"
                                        value={tplName}
                                        onChange={e => setTplName(e.target.value)}
                                        placeholder="Enter template name"
                                        className="sm:col-span-2 bg-gray-100 border-none rounded-lg p-3 focus:ring-2 focus:ring-[#2174C3] outline-none text-sm text-black"
                                    />
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-4">
                                    <label className="text-black font-semibold">Template Type</label>
                                    <select
                                        value={tplType}
                                        onChange={e => setTplType(e.target.value)}
                                        className="sm:col-span-2 bg-gray-100 border-none rounded-lg p-3 focus:ring-2 focus:ring-[#2174C3] outline-none text-sm text-black"
                                    >
                                        <option value="L1_Templates">L1_Templates</option>
                                        <option value="L2_Templates">L2_Templates</option>
                                    </select>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-3 items-start gap-4">
                                    <label className="text-black font-semibold pt-2">Description</label>
                                    <textarea
                                        value={tplDesc}
                                        onChange={e => setTplDesc(e.target.value)}
                                        placeholder="Enter template description"
                                        className="sm:col-span-2 bg-gray-100 border-none rounded-lg p-3 h-32 resize-none focus:ring-2 focus:ring-[#2174C3] outline-none text-sm text-black"
                                    ></textarea>
                                </div>

                                <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-4">
                                    <label className="text-black font-semibold">Deadline</label>
                                    <input
                                        type="datetime-local"
                                        value={tplDeadline}
                                        onChange={e => setTplDeadline(e.target.value)}
                                        className="sm:col-span-2 bg-gray-100 border-none rounded-lg p-3 focus:ring-2 focus:ring-[#2174C3] outline-none text-sm text-black"
                                    />
                                </div>
                            </div>

                            <div className="mt-6 flex flex-col items-end space-y-2">
                                {!tplName.trim() && <p className="text-xs text-red-400">* Template name is required</p>}
                                {tplName.trim() && tplNameDuplicate && <p className="text-xs text-red-400">* Name "{tplName.trim()}" is already used for this training</p>}

                                <div className="flex justify-end space-x-2 mt-4">
                                    <button
                                        onClick={() => { setShowTpl(false); setTplName(''); }}
                                        className="bg-[#878D94] hover:bg-[#607D8B] text-white px-3 py-1 text-sm rounded font-medium transition-colors cursor-pointer"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={submitTemplate}
                                        disabled={!tplName.trim() || tplNameDuplicate || !tplTrainingId}
                                        className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-4 py-1 text-sm rounded font-medium transition-colors shadow cursor-pointer disabled:opacity-50 disabled:bg-gray-300"
                                    >
                                        Save
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Response Modal */}
                {showResponse && (
                    <div className="fixed inset-0 z-[300] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto">
                        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl relative max-h-[90vh] flex flex-col">
                            <div className="px-10 pt-10 pb-8 overflow-y-auto">


                                <h2 className="text-3xl font-bold text-black mb-2">Response</h2>

                                <hr className="mb-8 border-gray-100" />

                                {selectedCard?.description && (
                                    <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 mb-4">
                                        <h4 className="text-xs font-bold uppercase text-blue-800 mb-1">Description</h4>
                                        <div className="text-sm text-blue-900 line-clamp-2">
                                            {selectedCard.description.split('\n').map((line, i) => <p key={i}>{line}</p>)}
                                        </div>
                                        {selectedCard.description.length > 100 && (
                                            <button onClick={() => setShowDescModal(true)} className="text-blue-600 font-semibold text-xs mt-2 hover:underline">
                                                Read more...
                                            </button>
                                        )}
                                    </div>
                                )}

                                <div className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 mb-3">
                                    <div className="flex items-center gap-2">
                                        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                                        <div>
                                            <p className="text-xs font-medium text-gray-500">Tenggat Waktu / Deadline</p>
                                            {isEditingDeadline ? (
                                                <div className="flex items-center gap-2 mt-1">
                                                    <input type="datetime-local" value={editDeadlineValue} onChange={e => setEditDeadlineValue(e.target.value)} className="border border-gray-300 rounded px-2 py-1 text-sm bg-white" />
                                                    <button onClick={updateDeadline} className="text-xs bg-[#2174C3] text-white px-3 py-1.5 rounded hover:bg-[#1A5E9D]">Save</button>
                                                    <button onClick={() => setIsEditingDeadline(false)} className="text-xs bg-gray-200 text-gray-700 px-3 py-1.5 rounded hover:bg-gray-300">Cancel</button>
                                                </div>
                                            ) : (
                                                <div className="flex items-center gap-3">
                                                    <p className="text-sm font-semibold text-gray-800">{selectedCard?.deadline ? formatDeadline(selectedCard.deadline) : 'No limit'}</p>
                                                    {canEdit && (
                                                        <button onClick={() => setIsEditingDeadline(true)} className="text-[#2174C3] hover:text-[#1A5E9D] p-1 bg-white border border-[#2174C3] rounded shadow-sm transition-colors" title="Edit Deadline">
                                                            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
                                                        </button>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                <div className="bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 mb-5">
                                    <div className="flex items-center gap-2">
                                        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                                        <div>
                                            <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Nama Training / Training Name</p>
                                            <p className="text-sm font-extrabold text-black">{selectedCard?.trainingTitle || 'N/A'}</p>
                                        </div>
                                    </div>
                                </div>
                                <hr className="my-5 border-gray-200" />
                                <div className="flex items-center justify-between mb-6">
                                    <div className="bg-gray-100 rounded-xl px-6 py-4 flex items-center gap-4 min-w-[140px]">
                                        <div>
                                            <p className="text-sm text-gray-500 font-medium">Respons</p>
                                            <p className="text-3xl font-bold text-gray-800">{selectedCard?.responses || 0}</p>
                                        </div>
                                        <svg className="w-9 h-9 text-[#2174C3]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
                                        </svg>
                                    </div>
                                    <div className="flex gap-3">
                                        {canEdit && (
                                            <button onClick={openEvaluationFromResponse} className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-6 py-2.5 rounded-lg font-semibold text-sm transition-all shadow-sm flex items-center gap-2">
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                                Question
                                            </button>
                                        )}
                                        <button onClick={exportToExcel} className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-6 py-2.5 rounded-lg font-semibold text-sm transition-all shadow-sm flex items-center gap-2">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                                            Download Report
                                        </button>
                                    </div>
                                </div>
                                <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 mb-4">
                                    <svg className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                    <p className="text-xs text-amber-700 leading-relaxed">This table only displays the <strong>5 latest records</strong>. Click <strong>Download Report</strong> to view all respondent data.</p>
                                </div>
                                <div className="rounded-xl overflow-hidden border border-gray-200">
                                    <table className="w-full resp-table">
                                        <thead>
                                            <tr className="bg-gray-100 border-b border-gray-200">
                                                <th className="text-center py-3 px-4 text-sm font-bold text-black w-10">No</th>
                                                <th className="text-left py-3 px-4 text-sm font-bold text-black">Name</th>
                                                {selectedCard?.type === 'L2' ? (
                                                    <>
                                                        <th className="text-center py-3 px-4 text-sm font-bold text-black w-28">Raw Score</th>
                                                        <th className="text-center py-3 px-4 text-sm font-bold text-black w-28">Scale</th>
                                                    </>
                                                ) : (
                                                    <th className="text-center py-3 px-4 text-sm font-bold text-black w-28">Score</th>
                                                )}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {responseRespondentsPreview.length === 0 ? (
                                                <tr><td colSpan={selectedCard?.type === 'L2' ? "4" : "3"} className="text-center py-8 text-gray-400 text-sm">No respondent data yet</td></tr>
                                            ) : (
                                                responseRespondentsPreview.map((resp, i) => (
                                                    <tr key={i} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                                                        <td className="py-3 px-4 text-center text-sm text-black font-medium">{i + 1}</td>
                                                        <td className="py-3 px-4 text-sm text-black font-semibold">{resp.name}</td>
                                                        {selectedCard?.type === 'L2' ? (
                                                            <>
                                                                <td className="py-3 px-4 text-center text-sm font-black text-black">{resp.raw_score}</td>
                                                                <td className="py-3 px-4 text-center text-sm font-black text-[#2174C3]">{resp.score}</td>
                                                            </>
                                                        ) : (
                                                            <td className="py-3 px-4 text-center text-sm font-black text-black">{resp.score}</td>
                                                        )}
                                                    </tr>
                                                ))
                                            )}
                                        </tbody>
                                    </table>
                                </div>
                                <div className="flex justify-end mt-5">
                                    <button onClick={() => setShowResponse(false)} className="bg-[#878D94] hover:bg-[#607D8B] text-white px-3 py-1 text-sm rounded font-medium transition-colors cursor-pointer">Close</button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Description Modal (Child of Response) */}
                {showDescModal && (
                    <div className="fixed inset-0 z-[400] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                        <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col max-h-[80vh]">
                            <div className="px-6 py-4 border-b border-gray-100 bg-blue-50 flex items-center justify-between">
                                <h3 className="font-bold text-blue-900">Full Description</h3>
                                <button onClick={() => setShowDescModal(false)} className="text-blue-400 hover:text-blue-600 font-bold text-xl">&times;</button>
                            </div>
                            <div className="p-6 overflow-y-auto text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                                {selectedCard?.description}
                            </div>
                            <div className="px-6 py-4 border-t border-gray-100 flex justify-end">
                                <button onClick={() => setShowDescModal(false)} className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-5 py-2 rounded-lg text-sm transition-colors">
                                    Close
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Evaluation Modal */}
                {showEval && (
                    <div className="fixed inset-0 z-[300] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto">
                        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-[1400px] max-h-[95vh] p-10 relative flex flex-col">
                            <div className="shrink-0">
                                <h2 className="text-3xl font-bold text-black mb-2">{isL2 ? 'Evaluation Builder L2' : 'Evaluation Builder L1'}</h2>
                                <hr className="mb-8 border-gray-100" />

                                <div className="flex items-end gap-4 mb-8">
                                    <div className="flex flex-col gap-1.5">
                                        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Template</label>
                                        <select value={selectedTemplate} onChange={onTemplateChange} className="w-48 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 bg-white focus:ring-2 focus:ring-[#2174C3] focus:border-transparent outline-none transition">
                                            <option value="L1_Templates">L1_Templates</option>
                                            <option value="L2_Templates">L2_Templates</option>
                                        </select>
                                    </div>
                                    <div className="flex flex-col gap-1.5 relative">
                                        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Training</label>
                                        <div className="training-search-container">
                                            <div className="relative">
                                                <input
                                                    type="text"
                                                    value={trainingSearchQuery}
                                                    onClick={() => setShowTrainingDropdown(true)}
                                                    onChange={(e) => {
                                                        setTrainingSearchQuery(e.target.value);
                                                        setShowTrainingDropdown(true);
                                                    }}
                                                    placeholder="Search"
                                                    className="w-52 border border-gray-200 rounded-lg px-3 py-2 pr-8 text-sm text-gray-700 bg-white focus:ring-2 focus:ring-[#2174C3] focus:border-transparent outline-none transition" />
                                                {trainingSearchQuery && (
                                                    <button onClick={clearTrainingSearch} className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600">
                                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
                                                    </button>
                                                )}
                                            </div>
                                            {showTrainingDropdown && filteredTrainingOptions.length > 0 && (
                                                <div className="training-search-dropdown absolute top-full mt-1 w-full bg-white border border-gray-200 shadow z-50">
                                                    {filteredTrainingOptions.map((training, i) => (
                                                        <div key={i} onClick={() => selectTraining(training)} className="training-search-option p-2 hover:bg-gray-100 cursor-pointer text-sm">
                                                            {training.title} - <span className="text-gray-400 font-normal">{training.trainingTitle}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                    <div className="ml-auto flex items-center gap-2 text-sm text-gray-400">
                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                        <span>{isL2 ? l2Rows.length + ' questions' : evalRows.length + ' questions'}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="flex-1 overflow-y-auto custom-scrollbar pr-2">
                                {!isL2 ? (
                                    <>
                                        <div style={{ display: 'grid', gridTemplateColumns: '36px 1fr 140px 90px 36px', gap: '6px', padding: '0 2px', marginBottom: '0' }}>
                                            <div className="bg-[#D1D5DB] text-[#4B5563] text-[11px] font-bold py-1.5 px-2 rounded-t-md text-center">#</div>
                                            <div className="bg-[#D1D5DB] text-[#4B5563] text-[11px] font-bold py-1.5 px-3 rounded-t-md text-left">Question</div>
                                            <div className="bg-[#D1D5DB] text-[#4B5563] text-[11px] font-bold py-1.5 px-2 rounded-t-md text-center">Answer Type</div>
                                            <div className="bg-[#D1D5DB] text-[#4B5563] text-[11px] font-bold py-1.5 px-2 rounded-t-md text-center">Is Active</div>
                                            <div></div>
                                        </div>
                                        <div className="flex flex-col gap-2">
                                            {evalRows.map((row, index) => (
                                                <div key={index} className="l2-row-card" style={{ borderRadius: '0 0 10px 10px', marginBottom: '8px' }}>
                                                    <div style={{ display: 'grid', gridTemplateColumns: '36px 1fr 140px 90px 36px', gap: '6px', alignItems: 'center' }}>
                                                        <div className="row-num-badge">{index + 1}</div>
                                                        <input type="text" value={row.q} onChange={e => { const r = [...evalRows]; r[index].q = e.target.value; setEvalRows(r); }} className="w-full h-9 border border-gray-200 rounded-lg px-3 text-sm text-gray-700 bg-white focus:ring-2 focus:ring-[#2174C3] outline-none transition" placeholder="Enter a question" />
                                                        <select value={row.type} onChange={e => { const r = [...evalRows]; r[index].type = e.target.value; setEvalRows(r); }} className="w-full h-9 border border-gray-200 rounded-lg px-2 text-sm text-gray-700 bg-white focus:ring-2 focus:ring-[#2174C3] outline-none transition">
                                                            <option value="Rating Scale">Rating</option>
                                                            <option value="Comment">Comment</option>
                                                        </select>
                                                        <div className="flex justify-center">
                                                            <div className="border border-gray-200 rounded-lg bg-white w-full h-9 flex items-center justify-center">
                                                                <input type="checkbox" checked={row.active} onChange={e => { const r = [...evalRows]; r[index].active = e.target.checked; setEvalRows(r); }} className="w-4 h-4 text-[#2174C3] border-gray-300 rounded cursor-pointer" />
                                                            </div>
                                                        </div>
                                                        <button onClick={() => removeEvalRow(index)} className="del-row-btn" title="Delete">
                                                            <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                        <button onClick={addEvalRow} className="add-row-btn mt-3 w-full border-dashed border-2 py-2 rounded-lg text-gray-500 hover:text-blue-600 hover:border-blue-500 flex justify-center items-center gap-2">
                                            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
                                            Add Question
                                        </button>
                                    </>
                                ) : (
                                    <>
                                        <div style={{ display: 'grid', gridTemplateColumns: '44px 1fr 110px 1fr 80px 60px 60px', gap: '6px', padding: '0 2px', marginBottom: '0' }}>
                                            <div className="bg-[#D1D5DB] text-[#4B5563] text-[11px] font-bold py-1.5 px-2 rounded-t-md text-center">#</div>
                                            <div className="bg-[#D1D5DB] text-[#4B5563] text-[11px] font-bold py-1.5 px-3 rounded-t-md text-left">Question</div>
                                            <div className="bg-[#D1D5DB] text-[#4B5563] text-[11px] font-bold py-1.5 px-2 rounded-t-md text-center">Answer Type</div>
                                            <div className="bg-[#D1D5DB] text-[#4B5563] text-[11px] font-bold py-1.5 px-3 rounded-t-md text-left">Answer Options</div>
                                            <div className="bg-[#D1D5DB] text-[#4B5563] text-[11px] font-bold py-1.5 px-2 rounded-t-md text-center">Correct Answer</div>
                                            <div className="bg-[#D1D5DB] text-[#4B5563] text-[11px] font-bold py-1.5 px-2 rounded-t-md text-center">Score</div>
                                            <div className="bg-[#D1D5DB] text-[#4B5563] text-[11px] font-bold py-1.5 px-2 rounded-t-md text-center">Is Active</div>
                                        </div>
                                        <div className="flex flex-col gap-2">
                                            {l2Rows.map((row, index) => (
                                                <div key={index} className="l2-row-card" style={{ borderRadius: '0 0 10px 10px', marginBottom: '10px' }}>
                                                    <div style={{ display: 'grid', gridTemplateColumns: '44px 1fr 110px 1fr 80px 60px 60px', gap: '6px', alignItems: 'start' }}>
                                                        <div className="flex flex-col items-center">
                                                            <div className="row-num-badge" style={{ height: '36px' }}>{index + 1}</div>
                                                            <button onClick={() => removeL2Row(index)} className="del-question-btn" title="Delete this question">
                                                                <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
                                                            </button>
                                                        </div>
                                                        <input type="text" value={row.q} onChange={e => { const r = [...l2Rows]; r[index].q = e.target.value; setL2Rows(r); }} className="border border-gray-200 rounded-lg px-3 text-sm text-gray-700 bg-white focus:ring-2 focus:ring-[#2174C3] outline-none transition" style={{ height: '36px', width: '100%' }} placeholder="Enter a question" />
                                                        <div className="type-pill" style={{ height: '36px' }}>Multiple Choice</div>
                                                        <div className="opts-stack" style={{ gap: '4px' }}>
                                                            {row.opts.map((opt, oi) => (
                                                                <div key={oi} className="opt-row flex gap-1 items-center">
                                                                    <span className="opt-label-badge">{String.fromCharCode(65 + oi)}</span>
                                                                    <input type="text" value={opt} onChange={e => { const r = [...l2Rows]; r[index].opts[oi] = e.target.value; setL2Rows(r); }} className="opt-text-input" placeholder={'Option ' + String.fromCharCode(65 + oi)} />
                                                                    <button onClick={() => removeL2Option(index, oi)} className="del-row-btn" style={{ width: '28px', height: '28px', borderRadius: '6px' }}>
                                                                        <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
                                                                    </button>
                                                                </div>
                                                            ))}
                                                            <button onClick={() => { const r = [...l2Rows]; r[index].opts.push(''); r[index].optVisible.push(true); r[index].optActive.push(true); setL2Rows(r); }} className="flex items-center gap-1 text-[11px] font-medium text-[#2174C3] hover:text-[#1A5E9D] cursor-pointer border border-dashed border-[#BFDBFE] hover:border-[#2174C3] rounded-md px-2 py-1 bg-[#EFF6FF] hover:bg-[#DBEAFE] transition-all mt-1 w-max">
                                                                <svg width="11" height="11" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg> Add option
                                                            </button>
                                                        </div>
                                                        <div className="border border-gray-200 rounded-lg bg-white flex items-center justify-center" style={{ height: '36px' }}>
                                                            <select value={row.answer} onChange={e => { const r = [...l2Rows]; r[index].answer = e.target.value; r[index].score = 100; setL2Rows(r); }} className="ans-select" style={{ height: '28px', fontSize: '12px', padding: '3px 4px' }}>
                                                                {row.opts.map((o, vi) => <option key={vi} value={String.fromCharCode(65 + vi)}>{String.fromCharCode(65 + vi)}</option>)}
                                                            </select>
                                                        </div>
                                                        <div className="border border-gray-200 rounded-lg bg-white flex items-center justify-center" style={{ height: '36px' }}>
                                                            <input type="number" min="0" max="100" value={row.score} onChange={e => { const r = [...l2Rows]; r[index].score = e.target.value; setL2Rows(r); }} className="score-input" style={{ height: '28px', fontSize: '12px', padding: '3px 6px' }} />
                                                        </div>
                                                        <div className="opts-stack" style={{ gap: '4px' }}>
                                                            {row.opts.map((_, oi) => (
                                                                <div key={oi} className="border border-gray-200 rounded-md bg-white flex items-center justify-center" style={{ height: '28px' }}>
                                                                    <input type="checkbox" checked={row.optActive[oi]} onChange={e => { const r = [...l2Rows]; r[index].optActive[oi] = e.target.checked; setL2Rows(r); }} className="w-4 h-4 text-[#2174C3] border-gray-300 rounded cursor-pointer" />
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                    {Number(row.score) < 100 && (
                                                        <div className="text-red-500 text-xs mt-2 ml-[50px] mb-2 font-medium">Score must be 100</div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                        <button onClick={addL2Row} className="add-row-btn mt-3 w-full border-dashed border-2 py-2 rounded-lg text-gray-500 hover:text-blue-600 hover:border-blue-500 flex justify-center items-center gap-2">
                                            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg> Add Question
                                        </button>
                                    </>
                                )}
                            </div>

                            <div className="flex justify-end space-x-2 mt-8 pt-5 border-t border-gray-100 shrink-0">
                                <button onClick={() => setShowEval(false)} className="bg-[#878D94] hover:bg-[#607D8B] text-white px-3 py-1 text-sm rounded font-medium transition-colors cursor-pointer">Cancel</button>
                                <button onClick={saveEvaluation} disabled={isSaving} className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-4 py-1 text-sm rounded font-medium transition-colors shadow cursor-pointer disabled:opacity-50 disabled:bg-gray-400">
                                    {isSaving ? (
                                        <div className="flex items-center gap-1">
                                            <svg className="animate-spin h-3.5 w-3.5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                                            Saving...
                                        </div>
                                    ) : 'Save'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Delete Confirmation Modal */}
                <ConfirmModal
                    isOpen={showDeleteConfirm}
                    onClose={() => { setShowDeleteConfirm(false); setCardToDelete(null); }}
                    onConfirm={deleteCard}
                    title="Confirm Delete"
                    message={`Are you sure want to delete this Evaluation "${cardToDelete?.title}"?`}
                />

                {toast && (
                    <Toast
                        message={toast.message}
                        type={toast.type}
                        onClose={() => setToast(null)}
                    />
                )}
            </div>
        </MainLayout>
    );
}

// Sub-component for individual card item
function CardItem({ card, canEdit, onClick, onDelete }) {
    const [menuOpen, setMenuOpen] = useState(false);
    return (
        <div onClick={onClick} className="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all border border-gray-100 cursor-pointer relative">
            <div className={`aspect-video relative overflow-hidden ${card.type === 'L2' ? 'bg-gradient-to-br from-[#a8d5b5] via-[#c4e6cf] to-[#b2d9c0]' : 'bg-gradient-to-br from-[#aac8e4] via-[#c8dff0] to-[#b8d0e8]'}`}>
                <span className="bubble b1"></span><span className="bubble b2"></span>
                <span className="bubble b3"></span><span className="bubble b4"></span><span className="bubble b5"></span>
                <div className="absolute top-2 right-2">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${card.type === 'L2' ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'}`}>
                        {card.type}
                    </span>
                </div>
            </div>
            <div className="p-4">
                <h3 className="text-xs font-bold text-gray-800 leading-tight mb-3">{card.title}</h3>
                <div className="flex justify-between items-center relative">
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-tighter">{card.responses} Response</span>
                    {canEdit && (
                        <div onClick={e => e.stopPropagation()} className="relative">
                            <button onClick={() => setMenuOpen(!menuOpen)} onBlur={() => setTimeout(() => setMenuOpen(false), 200)} className="flex space-x-0.5 items-center px-1.5 py-1 rounded-md hover:bg-gray-100 transition-colors group">
                                <span className="w-1 h-1 bg-gray-300 group-hover:bg-gray-500 rounded-full transition-colors"></span>
                                <span className="w-1 h-1 bg-gray-300 group-hover:bg-gray-500 rounded-full transition-colors"></span>
                                <span className="w-1 h-1 bg-gray-300 group-hover:bg-gray-500 rounded-full transition-colors"></span>
                            </button>
                            {menuOpen && (
                                <div className="absolute bottom-full right-0 mb-1 w-40 bg-white rounded-lg shadow-xl border border-gray-100 z-50 overflow-hidden py-1 animate-fade-in">
                                    <button onMouseDown={(e) => { e.preventDefault(); e.stopPropagation(); onDelete(e); setMenuOpen(false); }} className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors font-medium">
                                        <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                        </svg>
                                        Delete
                                    </button>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

