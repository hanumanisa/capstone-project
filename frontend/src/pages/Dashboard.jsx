import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../components/MainLayout';
import { getUserFromToken } from '../utils/auth';
import api from '../api/axios';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';

// Register ChartJS modules
ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
);

const Dashboard = () => {
    const [user, setUser] = useState(null);
    const [cardData, setCardData] = useState({
        total_training: 0,
        total_hours: 0,
        average_hours: 0,
        l1_score: "0.00",
        l2_score: "0.00",
        tna_coverage: "0%"
    });
    const [adminData, setAdminData] = useState(null);
    const [search, setSearch] = useState("");
    const [division, setDivision] = useState("");
    const [course, setCourse] = useState("");
    const [year, setYear] = useState("2026");

    const [divisionsList, setDivisionsList] = useState([]);
    const [coursesList, setCoursesList] = useState([]);

    const navigate = useNavigate();

    useEffect(() => {
        const fetchLookups = async () => {
            try {
                const [divRes, courseRes] = await Promise.all([
                    api.get('/api/divisions/'),
                    api.get('/api/courses/')
                ]);
                setDivisionsList(divRes.data);
                setCoursesList(courseRes.data);
            } catch (err) {
                console.error("Failed to fetch lookups", err);
            }
        };
        fetchLookups();

        const userData = getUserFromToken();
        if (!userData) {
            navigate('/login');
        } else {
            setUser(userData);
            if (['Head of Division', 'Team Leader', 'Employee', 'Dean'].includes(userData.role)) {
                api.get('/api/dashboard/cards/')
                   .then(res => {
                       if(res.data) setCardData(res.data);
                   })
                   .catch(err => console.error("Error fetching dashboard cards", err));
            } else {
                const params = new URLSearchParams();
                if (search) params.append('search', search);
                if (division && division !== 'All Division') params.append('division', division);
                if (course && course !== 'All Course') params.append('course', course);
                params.append('year', year);

                api.get(`/api/dashboard/admin/?${params.toString()}`)
                   .then(res => setAdminData(res.data))
                   .catch(err => console.error("Error fetching admin dashboard", err));
            }
        }
    }, [navigate, search, division, course, year]);

    const isRestrictedRole = user && ['Head of Division', 'Team Leader', 'Employee', 'Dean'].includes(user.role);

    const stats = isRestrictedRole ? [
        { title: 'Total Training', val: cardData.total_training, icon: '📖', bgIcon: '#FEF3C7' },
        { title: 'Total Hours', val: cardData.total_hours, icon: '🕒', bgIcon: '#DCFCE7' },
        { title: 'Average Hours', val: cardData.average_hours, icon: '⌛', bgIcon: '#F9EAFF' },
        { title: 'Training Evaluation L1', val: cardData.l1_score, icon: '⭐', bgIcon: '#FEF3C7' },
        { title: 'Training Evaluation L2', val: cardData.l2_score, icon: '⭐', bgIcon: '#FEF3C7' },
        { title: 'TNA Program Coverage', val: cardData.tna_coverage, icon: '📋', bgIcon: '#E0E7FF' }
    ] : adminData ? [
        // Column 1
        { title: 'Total Training', val: adminData.stats.total_training, change: '16%', up: true, icon: '📖', bgIcon: '#FEF3C7' },
        { title: 'Online Training', val: adminData.stats.online_training, icon: '📉', bgIcon: '#E0E7FF' },
        // Column 2
        { title: 'Total Hours', val: adminData.stats.total_hours, change: '16%', up: false, icon: '🕒', bgIcon: '#DCFCE7' },
        { title: 'Soft Skill', val: adminData.stats.soft_skill, icon: '🧠', bgIcon: '#FCE7F3' },
        // Column 3
        { title: 'Total Learners', val: adminData.stats.total_learners, change: '16%', up: true, icon: '👥', bgIcon: '#FFFBEB' },
        { title: 'Hard Skill', val: adminData.stats.hard_skill, icon: '⚙️', bgIcon: '#E0F2FE' },
        // Column 4
        { title: 'Total Employee', val: adminData.stats.total_employee, change: '16%', up: false, icon: '👤', bgIcon: '#ECFEFF' },
        { title: 'ESG', val: adminData.stats.esg, icon: '🌱', bgIcon: '#DCFCE7' },
        // Column 5
        { title: 'Average Hours', val: adminData.stats.average_hours, change: '16%', up: true, icon: '⌛', bgIcon: '#F9EAFF' },
        { title: 'Training Evaluation L1', val: adminData.stats.l1_score, icon: '⭐', bgIcon: '#FEF3C7' },
        // Column 6
        { title: 'Budget Used', val: adminData.stats.budget_used, sub: `${adminData.stats.budget_remaining} Remaining`, icon: '💰', bgIcon: '#FEE2E2' },
        { title: 'Training Evaluation L2', val: adminData.stats.l2_score, icon: '⭐', bgIcon: '#FEF3C7' },
        // Column 7
        { title: 'Inhouse Training', val: adminData.stats.inhouse_training, icon: '💻', bgIcon: '#E0F2FE' },
        { title: 'TNA Learners Coverage', val: adminData.stats.tna_learners_coverage, icon: '👥', bgIcon: '#E0F2FE' },
        // Column 8
        { title: 'Knowledge Sharing', val: adminData.stats.knowledge_sharing, icon: '📈', bgIcon: '#FFEDD5' },
        { title: 'TNA Program Coverage', val: adminData.stats.tna_program_coverage, icon: '📋', bgIcon: '#E0E7FF' },
        // Column 9
        { title: 'Public Training', val: adminData.stats.public_training, icon: '📊', bgIcon: '#DCFCE7' },
        { title: 'Coming Soon', val: '-', icon: '⏳', bgIcon: '#F3F4F6' }
    ] : [];

    const chartLabels = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
    
    // Shared options for bar charts
    const commonBarOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { 
                display: false,
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                    padding: 20,
                    font: { size: 10, weight: '600' }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: '#F3F4F6',
                    drawBorder: false
                },
                ticks: {
                    color: '#9CA3AF',
                    font: { size: 10, weight: 'bold' }
                }
            },
            x: {
                grid: { display: false },
                ticks: {
                    color: '#9CA3AF',
                    font: { size: 10, weight: 'bold' }
                }
            }
        },
        elements: {
            bar: {
                borderRadius: 4
            }
        }
    };

    // Specific options for Budget Used (with 'M' suffix)
    const budgetOptions = {
        ...commonBarOptions,
        scales: {
            ...commonBarOptions.scales,
            y: {
                ...commonBarOptions.scales.y,
                ticks: {
                    ...commonBarOptions.scales.y.ticks,
                    callback: (value) => value === 0 ? 0 : value + 'M'
                }
            }
        }
    };

    // Options for grouped bars (with legend)
    const groupedBarOptions = {
        ...commonBarOptions,
        plugins: {
            ...commonBarOptions.plugins,
            legend: {
                display: true,
                position: 'bottom',
                align: 'center',
                labels: {
                    usePointStyle: true,
                    pointStyle: 'circle',
                    padding: 15,
                    font: { size: 9, weight: '600' },
                    color: '#4B5563'
                }
            }
        }
    };

    const doughnutOptions = {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
            legend: {
                display: true,
                position: 'left',
                labels: {
                    usePointStyle: true,
                    pointStyle: 'circle',
                    padding: 15,
                    font: { size: 10, weight: '600' },
                    color: '#4B5563'
                }
            }
        }
    };

    const datasets = adminData ? {
        averageHours: {
            labels: chartLabels,
            datasets: [{
                data: adminData.charts.averageHours,
                backgroundColor: '#BD509E',
                barPercentage: 0.5
            }]
        },
        budgetUsed: {
            labels: chartLabels,
            datasets: [{
                data: adminData.charts.budgetUsed,
                backgroundColor: '#E67E22',
                barPercentage: 0.5
            }]
        },
        totalTrainingCategory: {
            labels: chartLabels,
            datasets: [
                { label: 'Hard Skill', data: adminData.charts.totalTrainingCategory['Hard Skill'], backgroundColor: '#3498DB' },
                { label: 'Soft Skill', data: adminData.charts.totalTrainingCategory['Soft Skill'], backgroundColor: '#BD509E' },
                { label: 'ESG', data: adminData.charts.totalTrainingCategory['ESG'], backgroundColor: '#2ECC71' }
            ]
        },
        trainingCategoryHours: {
            labels: chartLabels,
            datasets: [
                { label: 'Hard Skill', data: adminData.charts.trainingCategoryHours['Hard Skill'], backgroundColor: '#3498DB' },
                { label: 'Soft Skill', data: adminData.charts.trainingCategoryHours['Soft Skill'], backgroundColor: '#BD509E' },
                { label: 'ESG', data: adminData.charts.trainingCategoryHours['ESG'], backgroundColor: '#2ECC71' }
            ]
        },
        presentaseKaryawan: {
            labels: ['Direktur', 'Kepala Divisi', 'Team Leader', 'Staff'],
            datasets: [{
                data: [
                    adminData.charts.presentaseKaryawan['Direktur'] || 0,
                    adminData.charts.presentaseKaryawan['Kepala Divisi'] || 0,
                    adminData.charts.presentaseKaryawan['Team Leader'] || 0,
                    adminData.charts.presentaseKaryawan['Staff'] || 0
                ],
                backgroundColor: ['#1E3A5F', '#D4AF37', '#2ECC71', '#A64D79'],
                borderWidth: 0
            }]
        },
        totalTrainingType: {
            labels: chartLabels,
            datasets: [
                { label: 'Inhouse Training', data: adminData.charts.totalTrainingType['Inhouse Training'], backgroundColor: '#3498DB' },
                { label: 'Knowledge Sharing', data: adminData.charts.totalTrainingType['Knowledge Sharing'], backgroundColor: '#E67E22' },
                { label: 'Public Training', data: adminData.charts.totalTrainingType['Public Training'], backgroundColor: '#2ECC71' },
                { label: 'Online Training', data: adminData.charts.totalTrainingType['Online Training'], backgroundColor: '#BD509E' }
            ]
        }
    } : {
        averageHours: {
            labels: chartLabels,
            datasets: [{
                data: [55, 68, 22, 63, 48, 66, 84, 84, 66, 66, 48, 84],
                backgroundColor: '#BD509E',
                barPercentage: 0.5
            }]
        },
        budgetUsed: {
            labels: chartLabels,
            datasets: [{
                data: [560, 680, 230, 630, 480, 660, 840, 840, 660, 660, 480, 840],
                backgroundColor: '#E67E22',
                barPercentage: 0.5
            }]
        },
        totalTrainingCategory: {
            labels: chartLabels,
            datasets: [
                { label: 'Hard Skill', data: [28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28], backgroundColor: '#3498DB' },
                { label: 'Soft Skill', data: [25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25], backgroundColor: '#BD509E' },
                { label: 'ESG', data: [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], backgroundColor: '#2ECC71' }
            ]
        },
        trainingCategoryHours: {
            labels: chartLabels,
            datasets: [
                { label: 'Hard Skill', data: [28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28], backgroundColor: '#3498DB' },
                { label: 'Soft Skill', data: [25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25], backgroundColor: '#BD509E' },
                { label: 'ESG', data: [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20], backgroundColor: '#2ECC71' }
            ]
        },
        presentaseKaryawan: {
            labels: ['Direktur', 'Kepala Divisi', 'Team Leader', 'Staff'],
            datasets: [{
                data: [45, 12, 13, 30],
                backgroundColor: ['#1E3A5F', '#D4AF37', '#2ECC71', '#A64D79'],
                borderWidth: 0
            }]
        },
        totalTrainingType: {
            labels: chartLabels,
            datasets: [
                { label: 'Inhouse Training', data: [28, 32, 28, 28, 38, 22, 28, 38, 34, 34, 38, 48], backgroundColor: '#3498DB' },
                { label: 'Knowledge Sharing', data: [20, 22, 20, 20, 28, 18, 22, 28, 25, 25, 28, 34], backgroundColor: '#E67E22' },
                { label: 'Public Training', data: [25, 25, 25, 25, 30, 24, 28, 30, 28, 28, 30, 38], backgroundColor: '#2ECC71' },
                { label: 'Online Training', data: [23, 28, 23, 23, 34, 25, 25, 34, 30, 30, 34, 42], backgroundColor: '#BD509E' }
            ]
        }
    };

    if (!user) return null;

    return (
        <MainLayout>
            {/* Filter Section */}
            <div className="bg-white p-3 rounded-xl shadow-sm border border-gray-100 flex flex-col sm:flex-row items-center mb-8 gap-3">
                <div className="relative w-full sm:w-1/3">
                    <input 
                        type="text" 
                        placeholder="Search" 
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-4 pr-10 py-2 rounded-lg border-none bg-gray-100 focus:bg-white focus:ring-1 focus:ring-[#2174C3] transition-all text-gray-600 placeholder-gray-400" 
                    />
                    <span className="absolute right-3 top-2.5 text-gray-400 pointer-events-none">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                        </svg>
                    </span>
                </div>

                <div className="relative w-full sm:w-48">
                    <select 
                        value={division} 
                        onChange={(e) => setDivision(e.target.value)}
                        className="w-full border-none rounded-lg px-4 py-2 text-sm text-gray-600 bg-gray-100 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#2174C3] appearance-none bg-no-repeat bg-right-4"
                        style={{
                            backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M19 9l-7 7-7-7'/%3e%3c/svg%3e")`,
                            backgroundSize: '20px 20px',
                            backgroundPosition: 'right 12px center'
                        }}
                    >
                        <option value="All Division">All Division</option>
                        {divisionsList.map((d, i) => (
                            <option key={i} value={d.division_name}>{d.division_name}</option>
                        ))}
                    </select>
                </div>

                <div className="relative w-full sm:w-48">
                    <select 
                        value={course} 
                        onChange={(e) => setCourse(e.target.value)}
                        className="w-full border-none rounded-lg px-4 py-2 text-sm text-gray-600 bg-gray-100 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#2174C3] appearance-none bg-no-repeat bg-right-4"
                        style={{
                            backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M19 9l-7 7-7-7'/%3e%3c/svg%3e")`,
                            backgroundSize: '20px 20px',
                            backgroundPosition: 'right 12px center'
                        }}
                    >
                        <option value="All Course">All Course</option>
                        {coursesList.map((c, i) => (
                            <option key={i} value={c.course_name}>{c.course_name}</option>
                        ))}
                    </select>
                </div>
                
                <div className="flex-1 flex justify-end items-center space-x-6">
                    <div className="font-bold flex space-x-4 text-sm tracking-wide">
                        <span 
                            onClick={() => setYear('2026')}
                            className={`cursor-pointer transition-colors ${year === '2026' ? 'text-[#2174C3]' : 'text-gray-300 hover:text-gray-400'}`}
                        >
                            2026
                        </span>
                        <span 
                            onClick={() => setYear('2025')}
                            className={`cursor-pointer transition-colors ${year === '2025' ? 'text-[#2174C3]' : 'text-gray-300 hover:text-gray-400'}`}
                        >
                            2025
                        </span>
                    </div>
                </div>
            </div>

            {/* Statistics Horizontal Scroll Section */}
            <div className="overflow-x-auto pb-4 mb-8 -mx-4 px-4 scrollbar-hide lg:mx-0 lg:px-0">
                <style dangerouslySetInnerHTML={{ __html: `
                    .scrollbar-hide::-webkit-scrollbar { display: none; }
                    .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
                `}} />
                <div className={`grid ${isRestrictedRole ? 'grid-rows-1' : 'grid-rows-2'} grid-flow-col gap-5 w-max`}>
                    {stats.map((item, idx) => (
                        <div 
                            key={idx} 
                            className="w-[210px] h-[140px] bg-white rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between p-5 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group cursor-default relative overflow-hidden"
                        >
                            {/* Subtle Background Accent */}
                            <div 
                                className="absolute -right-4 -bottom-4 w-20 h-20 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity duration-500 rounded-full"
                                style={{ backgroundColor: item.bgIcon }}
                            />

                            <div className="flex justify-between items-start relative z-10">
                                <h3 className="text-gray-400 text-[10px] font-extrabold uppercase leading-tight tracking-[0.1em]">{item.title}</h3>
                                <div 
                                    className="w-10 h-10 rounded-xl flex-shrink-0 flex items-center justify-center text-xl shadow-sm backdrop-blur-sm transition-transform duration-300 group-hover:scale-110 group-hover:rotate-3"
                                    style={{ 
                                        backgroundColor: `${item.bgIcon}80`, // Adding transparency for glass effect
                                        border: `1px solid ${item.bgIcon}`
                                    }}
                                >
                                    {item.icon}
                                </div>
                            </div>

                            <div className="mt-auto relative z-10">
                                <div className="text-3xl font-black text-[#1E2B4D] leading-none mb-2 tracking-tight group-hover:text-[#2174C3] transition-colors">
                                    {item.val}
                                </div>
                                <div className="flex flex-col">
                                    {item.change && (
                                        <div className="flex items-center text-[11px] font-bold">
                                            <span className={`flex items-center px-1.5 py-0.5 rounded-md ${item.up ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'}`}>
                                                <svg className={`w-3 h-3 mr-0.5 ${!item.up && 'rotate-180'}`} fill="currentColor" viewBox="0 0 20 20">
                                                    <path d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z"/>
                                                </svg>
                                                {item.change}
                                            </span>
                                            <span className="text-gray-400 font-medium ml-1.5">this month</span>
                                        </div>
                                    )}
                                    {item.sub && (
                                        <div className="text-[10px] font-bold text-red-500 mt-1 flex items-center">
                                            <span className="w-1 h-1 bg-red-500 rounded-full mr-1.5 animate-pulse"></span>
                                            {item.sub}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Dashboard Grid Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {/* 1. Average Hours */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-50 h-[380px] flex flex-col">
                    <h3 className="text-[#1E2B4D] font-extrabold mb-6 text-lg">Average Hours</h3>
                    <div className="flex-1 w-full min-h-0">
                        <Bar options={commonBarOptions} data={datasets.averageHours} />
                    </div>
                </div>

                {/* 2. Budget Used */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-50 h-[380px] flex flex-col">
                    <h3 className="text-[#1E2B4D] font-extrabold mb-6 text-lg">Budget Used</h3>
                    <div className="flex-1 w-full min-h-0">
                        <Bar options={budgetOptions} data={datasets.budgetUsed} />
                    </div>
                </div>

                {/* 3. Total Training Category */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-50 h-[380px] flex flex-col">
                    <h3 className="text-[#1E2B4D] font-extrabold mb-6 text-lg">Total Training Category</h3>
                    <div className="flex-1 w-full min-h-0">
                        <Bar options={groupedBarOptions} data={datasets.totalTrainingCategory} />
                    </div>
                </div>

                {/* 4. Training Category Hours */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-50 h-[380px] flex flex-col">
                    <h3 className="text-[#1E2B4D] font-extrabold mb-6 text-lg">Training Category Hours</h3>
                    <div className="flex-1 w-full min-h-0">
                        <Bar options={groupedBarOptions} data={datasets.trainingCategoryHours} />
                    </div>
                </div>

                {/* 5. Presentase Karyawan */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-50 h-[380px] flex flex-col">
                    <h3 className="text-[#1E2B4D] font-extrabold mb-6 text-lg">Presentase Karyawan</h3>
                    <div className="flex-1 w-full min-h-0 flex items-center justify-center relative">
                        <div className="w-full h-full relative">
                            <Doughnut options={doughnutOptions} data={datasets.presentaseKaryawan} />
                            {/* Inner label for doughnut */}
                            <div className="absolute inset-0 flex items-center justify-center pointer-events-none pl-[100px]">
                                <div className="text-center">
                                    <div className="text-2xl font-black text-[#1E2B4D]">100%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 6. Total Training Type */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-50 h-[380px] flex flex-col">
                    <h3 className="text-[#1E2B4D] font-extrabold mb-6 text-lg">Total Training Type</h3>
                    <div className="flex-1 w-full min-h-0">
                        <Bar options={groupedBarOptions} data={datasets.totalTrainingType} />
                    </div>
                </div>

                {/* Row 4: Category, Location, Vendors */}
                {/* 10. Training Category Table */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-50 h-[380px] flex flex-col overflow-hidden">
                    <h3 className="text-[#1E2B4D] font-extrabold mb-6 text-lg">Training Category</h3>
                    <div className="flex-1 overflow-auto">
                        <table className="w-full text-xs text-left">
                            <thead className="text-gray-400 font-bold">
                                <tr>
                                    <th className="pb-3 pr-2">Training Category</th>
                                    <th className="pb-3 pr-2">Learners</th>
                                    <th className="pb-3 pr-2">Hours</th>
                                    <th className="pb-3">Training Title</th>
                                </tr>
                            </thead>
                            <tbody className="text-[#1E2B4D]">
                                {adminData && adminData.tables && adminData.tables.category ? adminData.tables.category.map((cat, i) => (
                                    <tr key={i} className="bg-gray-50/50">
                                        <td className="py-3 px-2 rounded-l-lg border-b border-white">{cat.category}</td>
                                        <td className="py-3 px-2 border-b border-white">{cat.learners}</td>
                                        <td className="py-3 px-2 border-b border-white">{cat.hours}</td>
                                        <td className="py-3 px-2 rounded-r-lg border-b border-white">{cat.title_count}</td>
                                    </tr>
                                )) : null}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* 11. Training Location Table */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-50 h-[380px] flex flex-col overflow-hidden">
                    <h3 className="text-[#1E2B4D] font-extrabold mb-6 text-lg">Training Location</h3>
                    <div className="flex-1 overflow-auto">
                        <table className="w-full text-xs text-left">
                            <thead className="text-gray-400 font-bold">
                                <tr>
                                    <th className="pb-3 pr-2">Training Location</th>
                                    <th className="pb-3 pr-2">Learners</th>
                                    <th className="pb-3 pr-2">Hours</th>
                                    <th className="pb-3">Training Title</th>
                                </tr>
                            </thead>
                            <tbody className="text-[#1E2B4D]">
                                {adminData && adminData.tables && adminData.tables.location ? adminData.tables.location.map((loc, i) => (
                                    <tr key={i} className="bg-gray-50/50">
                                        <td className="py-3 px-2 rounded-l-lg border-b border-white">{loc.location}</td>
                                        <td className="py-3 px-2 border-b border-white">{loc.learners}</td>
                                        <td className="py-3 px-2 border-b border-white">{loc.hours}</td>
                                        <td className="py-3 px-2 rounded-r-lg border-b border-white">{loc.title_count}</td>
                                    </tr>
                                )) : null}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* 12. Training Vendors Table */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-50 h-[380px] flex flex-col overflow-hidden">
                    <h3 className="text-[#1E2B4D] font-extrabold mb-6 text-lg">Training Vendors</h3>
                    <div className="flex-1 overflow-auto">
                        <table className="w-full text-xs text-left">
                            <thead className="text-gray-400 font-bold">
                                <tr>
                                    <th className="pb-3 pr-2">Training Vendors</th>
                                    <th className="pb-3 pr-2">Learners</th>
                                    <th className="pb-3 pr-2">Hours</th>
                                    <th className="pb-3">Training Title</th>
                                </tr>
                            </thead>
                            <tbody className="text-[#1E2B4D]">
                                {adminData && adminData.tables && adminData.tables.vendors ? adminData.tables.vendors.map((vendor, i) => (
                                    <tr key={i} className="bg-gray-50/50">
                                        <td className="py-3 px-2 rounded-l-lg border-b border-white">{vendor.vendor}</td>
                                        <td className="py-3 px-2 border-b border-white">{vendor.learners}</td>
                                        <td className="py-3 px-2 border-b border-white">{vendor.hours}</td>
                                        <td className="py-3 px-2 rounded-r-lg border-b border-white">{vendor.title_count}</td>
                                    </tr>
                                )) : null}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Row 5: Division, Position, Cost */}
                {/* 13. Training Division Table */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-50 h-[380px] flex flex-col overflow-hidden">
                    <h3 className="text-[#1E2B4D] font-extrabold mb-6 text-lg">Training Division</h3>
                    <div className="flex-1 overflow-auto">
                        <table className="w-full text-xs text-left">
                            <thead className="text-gray-400 font-bold">
                                <tr>
                                    <th className="pb-3 pr-2">Training Division</th>
                                    <th className="pb-3 pr-2">Employee</th>
                                    <th className="pb-3 pr-2">Learners</th>
                                    <th className="pb-3">Hours</th>
                                </tr>
                            </thead>
                            <tbody className="text-[#1E2B4D]">
                                {adminData && adminData.tables && adminData.tables.division ? adminData.tables.division.map((div, i) => (
                                    <tr key={i} className="bg-gray-50/50">
                                        <td className="py-3 px-2 rounded-l-lg border-b border-white">{div.division}</td>
                                        <td className="py-3 px-2 border-b border-white">{div.employee}</td>
                                        <td className="py-3 px-2 border-b border-white">{div.learners}</td>
                                        <td className="py-3 px-2 rounded-r-lg border-b border-white">{div.hours}</td>
                                    </tr>
                                )) : null}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* 14. Training Position Table */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-50 h-[380px] flex flex-col overflow-hidden">
                    <h3 className="text-[#1E2B4D] font-extrabold mb-6 text-lg">Training Position</h3>
                    <div className="flex-1 overflow-auto">
                        <table className="w-full text-xs text-left">
                            <thead className="text-gray-400 font-bold">
                                <tr>
                                    <th className="pb-3 pr-2">Training Position</th>
                                    <th className="pb-3 pr-2">Employee</th>
                                    <th className="pb-3 pr-2">Learners</th>
                                    <th className="pb-3">Hours</th>
                                </tr>
                            </thead>
                            <tbody className="text-[#1E2B4D]">
                                {adminData && adminData.tables && adminData.tables.position ? adminData.tables.position.map((pos, i) => (
                                    <tr key={i} className="bg-gray-50/50">
                                        <td className="py-3 px-2 rounded-l-lg border-b border-white">{pos.position}</td>
                                        <td className="py-3 px-2 border-b border-white">{pos.employee}</td>
                                        <td className="py-3 px-2 border-b border-white">{pos.learners}</td>
                                        <td className="py-3 px-2 rounded-r-lg border-b border-white">{pos.hours}</td>
                                    </tr>
                                )) : null}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* 15. Training Cost Table */}
                <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-50 h-[380px] flex flex-col overflow-hidden">
                    <h3 className="text-[#1E2B4D] font-extrabold mb-6 text-lg">Training Cost</h3>
                    <div className="flex-1 overflow-auto">
                        <table className="w-full text-xs text-left">
                            <thead className="text-gray-400 font-bold">
                                <tr>
                                    <th className="pb-3 pr-2">Month</th>
                                    <th className="pb-3 pr-2">Realisation</th>
                                    <th className="pb-3 pr-2">Remaining</th>
                                    <th className="pb-3">Percentage</th>
                                </tr>
                            </thead>
                            <tbody className="text-[#1E2B4D]">
                                {adminData && adminData.tables && adminData.tables.cost ? adminData.tables.cost.map((c, i) => (
                                    <tr key={i} className="bg-gray-50/50">
                                        <td className="py-3 px-2 rounded-l-lg border-b border-white">{c.month}</td>
                                        <td className="py-3 px-2 border-b border-white">{c.realisation.toLocaleString()}</td>
                                        <td className="py-3 px-2 border-b border-white">{c.remaining.toLocaleString()}</td>
                                        <td className="py-3 px-2 rounded-r-lg border-b border-white">{c.percentage}</td>
                                    </tr>
                                )) : null}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </MainLayout>
    );
};

export default Dashboard;
