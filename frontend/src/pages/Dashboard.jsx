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
import {
    BookOpen,
    Clock,
    Users,
    User,
    Hourglass,
    CircleDollarSign,
    Layout,
    TrendingUp,
    BarChart3,
    MonitorPlay,
    Brain,
    Settings,
    Leaf,
    Star,
    UserCheck,
    ClipboardCheck,
    HelpCircle
} from 'lucide-react';
import YearPicker from '../components/YearPicker';


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
        stats: {
            total_training: 0,
            total_hours: "0",
            average_hours: "0",
            l1_score: "0.00",
            l2_score: "0.00",
            tna_coverage: "0%"
        },
        charts: null
    });
    const [adminData, setAdminData] = useState(null);
    const [search, setSearch] = useState("");
    const [division, setDivision] = useState("");
    const [course, setCourse] = useState("");
    const [year, setYear] = useState(new Date().getFullYear().toString());
    const [activeTab, setActiveTab] = useState('admin');

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
            const isRestrictedRole = !['Super Administrator', 'Administrator', 'Dean'].includes(userData.role) || activeTab === 'employee';

            if (isRestrictedRole) {
                const params = new URLSearchParams();
                params.append('year', year);
                if (search) params.append('search', search);
                if (activeTab === 'admin') {
                    params.append('view_mode', 'admin');
                } else {
                    params.append('view_mode', 'employee');
                }
                api.get(`/api/dashboard/cards/?${params.toString()}`)
                    .then(res => {
                        if (res.data) setCardData(res.data);
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
    }, [navigate, search, division, course, year, activeTab]);

    const isAdminDashboardRole = user && ['Administrator', 'Super Administrator', 'Dean', 'Head of Division', 'Team Leader'].includes(user.role);
    const isRestrictedRole = !['Super Administrator', 'Administrator', 'Dean'].includes(user?.role) || activeTab === 'employee';

    const stats = isRestrictedRole ? (cardData?.stats ? [
        { title: 'Total Training', val: cardData.stats.total_training, icon: BookOpen, bgIcon: '#F59E0B' },
        { title: 'Total Hours', val: cardData.stats.total_hours, icon: Clock, bgIcon: '#10B981' },
        { title: 'Average Hours', val: cardData.stats.average_hours, icon: Hourglass, bgIcon: '#8B5CF6' },
        { title: 'Training Evaluation L1', val: cardData.stats.l1_score, icon: Star, bgIcon: '#FBBF24' },
        { title: 'Training Evaluation L2', val: cardData.stats.l2_score, icon: Star, bgIcon: '#FBBF24' },
        { title: 'TNA Program Coverage', val: cardData.stats.tna_coverage, icon: ClipboardCheck, bgIcon: '#3B82F6' }
    ] : []) : adminData ? [
        // Column 1
        { title: 'Total Training', val: adminData.stats.total_training, change: adminData.stats.total_training_change, up: adminData.stats.total_training_up, icon: BookOpen, bgIcon: '#F59E0B' },
        { title: 'E-Learning', val: adminData.stats.e_learning, icon: MonitorPlay, bgIcon: '#8B5CF6' },
        // Column 2
        { title: 'Total Hours', val: adminData.stats.total_hours, change: adminData.stats.total_hours_change, up: adminData.stats.total_hours_up, icon: Clock, bgIcon: '#10B981' },
        { title: 'Soft Skill', val: adminData.stats.soft_skill, icon: Brain, bgIcon: '#EC4899' },
        // Column 3
        { title: 'Total Learners', val: adminData.stats.total_learners, change: adminData.stats.total_learners_change, up: adminData.stats.total_learners_up, icon: Users, bgIcon: '#FBBF24' },
        { title: 'Hard Skill', val: adminData.stats.hard_skill, icon: Settings, bgIcon: '#06B6D4' },
        // Column 4
        { title: 'Total Employee', val: adminData.stats.total_employee, change: adminData.stats.total_employee_change, up: adminData.stats.total_employee_up, icon: Users, bgIcon: '#06B6D4' },
        { title: 'ESG', val: adminData.stats.esg, icon: Leaf, bgIcon: '#10B981' },
        // Column 5
        { title: 'Average Hours', val: adminData.stats.average_hours, change: adminData.stats.average_hours_change, up: adminData.stats.average_hours_up, icon: Hourglass, bgIcon: '#8B5CF6' },
        { title: 'Training Evaluation L1', val: adminData.stats.l1_score, icon: Star, bgIcon: '#FBBF24' },
        // Column 6
        { title: 'Budget Used', val: adminData.stats.budget_used, sub: `${adminData.stats.budget_remaining} Remaining`, icon: CircleDollarSign, bgIcon: '#EF4444' },
        { title: 'Training Evaluation L2', val: adminData.stats.l2_score, icon: Star, bgIcon: '#FBBF24' },
        // Column 7
        { title: 'Inhouse Training', val: adminData.stats.inhouse_training, icon: Layout, bgIcon: '#3B82F6' },
        { title: 'TNA Learners Coverage', val: adminData.stats.tna_learners_coverage, icon: UserCheck, bgIcon: '#3B82F6' },
        // Column 8
        { title: 'Knowledge Sharing', val: adminData.stats.knowledge_sharing, icon: BarChart3, bgIcon: '#F97316' },
        { title: 'TNA Program Coverage', val: adminData.stats.tna_program_coverage, icon: ClipboardCheck, bgIcon: '#3B82F6' },
        // Column 9
        { title: 'Public Training', val: adminData.stats.public_training, icon: TrendingUp, bgIcon: '#10B981' },
        { title: 'Employee Training Reach', val: adminData.stats.training_reach, icon: UserCheck, bgIcon: '#3B82F6' }
    ] : [];

    const chartLabels = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

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

    const dashboardData = isRestrictedRole ? cardData : adminData;

    const datasets = (dashboardData && dashboardData.charts) ? {
        totalTraining: {
            labels: chartLabels,
            datasets: [{
                data: dashboardData.charts.summaryCombined['Total Training'],
                backgroundColor: '#F59E0B',
                barPercentage: 0.5
            }]
        },
        totalHours: {
            labels: chartLabels,
            datasets: [{
                data: dashboardData.charts.summaryCombined['Total Hours'],
                backgroundColor: '#10B981',
                barPercentage: 0.5
            }]
        },
        totalLearners: {
            labels: chartLabels,
            datasets: [{
                data: dashboardData.charts.summaryCombined['Total Learners'],
                backgroundColor: '#FBBF24',
                barPercentage: 0.5
            }]
        },
        averageHours: {
            labels: chartLabels,
            datasets: [{
                data: dashboardData.charts.averageHours,
                backgroundColor: '#8B5CF6',
                barPercentage: 0.5
            }]
        },
        budgetUsed: {
            labels: chartLabels,
            datasets: [{
                data: dashboardData.charts.budgetUsed || Array(12).fill(0),
                backgroundColor: '#EF4444',
                barPercentage: 0.5
            }]
        },
        totalTrainingCategory: {
            labels: chartLabels,
            datasets: [
                { label: 'Hard Skill', data: dashboardData.charts.totalTrainingCategory['Hard Skill'], backgroundColor: '#3498DB' },
                { label: 'Soft Skill', data: dashboardData.charts.totalTrainingCategory['Soft Skill'], backgroundColor: '#BD509E' },
                { label: 'ESG', data: dashboardData.charts.totalTrainingCategory['ESG'], backgroundColor: '#2ECC71' }
            ]
        },
        trainingTypeHours: {
            labels: chartLabels,
            datasets: [
                { label: 'Inhouse Training', data: dashboardData.charts.trainingTypeHours['Inhouse Training'], backgroundColor: '#3498DB' },
                { label: 'Knowledge Sharing', data: dashboardData.charts.trainingTypeHours['Knowledge Sharing'], backgroundColor: '#E67E22' },
                { label: 'Public Training', data: dashboardData.charts.trainingTypeHours['Public Training'], backgroundColor: '#2ECC71' },
                { label: 'E-Learning', data: dashboardData.charts.trainingTypeHours['E-Learning'], backgroundColor: '#8B5CF6' }
            ]
        },
        presentaseKaryawan: {
            labels: ['Direktur', 'Kepala Divisi', 'Team Leader', 'Staff'],
            datasets: [{
                data: dashboardData.charts.presentaseKaryawan ? [
                    dashboardData.charts.presentaseKaryawan['Direktur'] || 0,
                    dashboardData.charts.presentaseKaryawan['Kepala Divisi'] || 0,
                    dashboardData.charts.presentaseKaryawan['Team Leader'] || 0,
                    dashboardData.charts.presentaseKaryawan['Staff'] || 0
                ] : [0, 0, 0, 0],
                backgroundColor: ['#1E3A5F', '#D4AF37', '#2ECC71', '#A64D79'],
                borderWidth: 0
            }]
        },
        totalTrainingType: {
            labels: chartLabels,
            datasets: [
                { label: 'Inhouse Training', data: dashboardData.charts.totalTrainingType['Inhouse Training'], backgroundColor: '#3498DB' },
                { label: 'Knowledge Sharing', data: dashboardData.charts.totalTrainingType['Knowledge Sharing'], backgroundColor: '#E67E22' },
                { label: 'Public Training', data: dashboardData.charts.totalTrainingType['Public Training'], backgroundColor: '#2ECC71' },
                { label: 'E-Learning', data: dashboardData.charts.totalTrainingType['E-Learning'], backgroundColor: '#8B5CF6' }
            ]
        }
    } : {
        totalTraining: { labels: chartLabels, datasets: [] },
        totalHours: { labels: chartLabels, datasets: [] },
        totalLearners: { labels: chartLabels, datasets: [] },
        averageHours: { labels: chartLabels, datasets: [{ data: Array(12).fill(0), backgroundColor: '#BD509E' }] },
        budgetUsed: { labels: chartLabels, datasets: [{ data: Array(12).fill(0), backgroundColor: '#E67E22' }] },
        totalTrainingCategory: { labels: chartLabels, datasets: [] },
        trainingTypeHours: { labels: chartLabels, datasets: [] },
        presentaseKaryawan: { labels: [], datasets: [] },
        totalTrainingType: { labels: chartLabels, datasets: [] }
    };

    if (!user) return null;

    return (
        <MainLayout>
            {isAdminDashboardRole && (
                <div className="flex space-x-8 border-b border-gray-300 mb-6 px-4 sm:px-0">
                    <button
                        onClick={() => setActiveTab('admin')}
                        className={`pb-3 px-1 font-bold text-xl transition-colors ${activeTab === 'admin'
                            ? 'text-[#2174C3] border-b-4 border-[#2174C3]'
                            : 'text-gray-400 hover:text-[#2174C3]'
                            }`}
                    >
                        {['Super Administrator', 'Administrator', 'Dean'].includes(user?.role) ? 'Company Dashboard' : 'Division Dashboard'}
                    </button>
                    <button
                        onClick={() => setActiveTab('employee')}
                        className={`pb-3 px-1 font-bold text-xl transition-colors ${activeTab === 'employee'
                            ? 'text-[#2174C3] border-b-4 border-[#2174C3]'
                            : 'text-gray-400 hover:text-[#2174C3]'
                            }`}
                    >
                        My Dashboard
                    </button>
                </div>
            )}

            {/* Filter Section */}
            <div className="bg-white p-3 rounded-xl shadow-sm border border-gray-100 flex flex-col sm:flex-row items-center mb-8 gap-3 transition-all duration-300 sticky top-0 z-30">
                <div className="relative w-full sm:w-1/3">
                    <input
                        type="text"
                        placeholder="Search"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-4 pr-10 py-2 rounded-lg border-none bg-gray-100 focus:bg-white focus:ring-1 focus:ring-[#2174C3] transition-all text-gray-600 placeholder-gray-400 outline-none"
                    />
                    <span className="absolute right-3 top-2.5 text-gray-400 pointer-events-none">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                        </svg>
                    </span>
                </div>

                {!isRestrictedRole && (
                    <div className="relative w-full sm:w-48">
                        <select
                            value={division}
                            onChange={(e) => setDivision(e.target.value)}
                            className="w-full border-none rounded-lg pl-4 pr-10 py-2 text-sm text-gray-600 bg-gray-100 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#2174C3] appearance-none bg-no-repeat bg-right-4 outline-none"
                            style={{
                                backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M19 9l-7 7-7-7'/%3e%3c/svg%3e")`,
                                backgroundSize: '20px 20px',
                                backgroundPosition: 'right 12px center'
                            }}
                        >
                            <option value="">All Division</option>
                            {divisionsList.map((d, i) => (
                                <option key={i} value={d.division_name}>{d.division_name}</option>
                            ))}
                        </select>
                    </div>
                )}

                {!isRestrictedRole && (
                    <div className="relative w-full sm:w-48">
                        <select
                            value={course}
                            onChange={(e) => setCourse(e.target.value)}
                            className="w-full border-none rounded-lg pl-4 pr-10 py-2 text-sm text-gray-600 bg-gray-100 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#2174C3] appearance-none bg-no-repeat bg-right-4 outline-none"
                            style={{
                                backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M19 9l-7 7-7-7'/%3e%3c/svg%3e")`,
                                backgroundSize: '20px 20px',
                                backgroundPosition: 'right 12px center'
                            }}
                        >
                            <option value="">All Course</option>
                            {Array.from(new Set(coursesList.map(c => c.course_name)))
                                .sort()
                                .map((name, i) => (
                                    <option key={i} value={name}>{name}</option>
                                ))}
                        </select>
                    </div>
                )}

                <div className="flex-1 flex justify-end items-center space-x-6 shrink-0">
                    <YearPicker selectedYear={year} onYearChange={(y) => setYear(y)} />
                </div>
            </div>

            {/* Statistics Horizontal Scroll Section */}
            <div className="overflow-x-auto pb-4 mb-8 -mx-4 px-4 scrollbar-hide lg:mx-0 lg:px-0">
                <style dangerouslySetInnerHTML={{
                    __html: `
                    .scrollbar-hide::-webkit-scrollbar { display: none; }
                    .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
                `}} />
                <div className={isRestrictedRole
                    ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-6 w-full"
                    : "grid grid-rows-2 grid-flow-col gap-5 w-max mx-auto"
                }>
                    {stats.map((item, idx) => (
                        <div
                            key={idx}
                            className={`${isRestrictedRole ? 'w-full' : 'w-[210px]'} h-[140px] bg-white rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between p-5 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group cursor-default relative overflow-hidden`}
                        >
                            {/* Subtle Background Accent */}
                            <div
                                className="absolute -right-4 -bottom-4 w-20 h-20 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity duration-500 rounded-full"
                                style={{ backgroundColor: item.bgIcon }}
                            />

                            <div className="flex justify-between items-start relative z-10">
                                <h3 className="text-gray-400 text-[10px] font-extrabold uppercase leading-tight tracking-[0.1em]">{item.title}</h3>
                                <div
                                    className="w-12 h-12 rounded-full flex-shrink-0 flex items-center justify-center shadow-sm relative transition-all duration-300 group-hover:scale-110 overflow-hidden"
                                    style={{
                                        backgroundColor: `${item.bgIcon}15`,
                                    }}
                                >
                                    {/* Inner Glow Effect */}
                                    <div
                                        className="absolute inset-0 opacity-40"
                                        style={{
                                            background: `radial-gradient(circle at center, ${item.bgIcon} 0%, transparent 70%)`
                                        }}
                                    />
                                    <item.icon
                                        size={22}
                                        className="relative z-10 transition-transform duration-500 group-hover:rotate-12"
                                        style={{ color: item.bgIcon }}
                                        strokeWidth={2.5}
                                    />
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
                                                    <path d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" />
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

            {/* Charts Grid */}
            {dashboardData && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
                    <div className="bg-white p-8 rounded-[35px] shadow-sm border border-gray-100 h-[450px] flex flex-col">
                        <h3 className="text-[#1E2B4D] font-bold mb-6 text-xl">Total Training</h3>
                        <div className="flex-1 w-full min-h-0"><Bar options={commonBarOptions} data={datasets.totalTraining} /></div>
                    </div>

                    <div className="bg-white p-8 rounded-[35px] shadow-sm border border-gray-100 h-[450px] flex flex-col">
                        <h3 className="text-[#1E2B4D] font-bold mb-6 text-xl">Total Hours</h3>
                        <div className="flex-1 w-full min-h-0"><Bar options={commonBarOptions} data={datasets.totalHours} /></div>
                    </div>

                    {isRestrictedRole ? (
                        <div className="bg-white p-8 rounded-[35px] shadow-sm border border-gray-100 h-[450px] flex flex-col">
                            <h3 className="text-[#1E2B4D] font-bold mb-6 text-xl">Average Hours</h3>
                            <div className="flex-1 w-full min-h-0"><Bar options={commonBarOptions} data={datasets.averageHours} /></div>
                        </div>
                    ) : (
                        <div className="bg-white p-8 rounded-[35px] shadow-sm border border-gray-100 h-[450px] flex flex-col">
                            <h3 className="text-[#1E2B4D] font-bold mb-6 text-xl">Total Learners</h3>
                            <div className="flex-1 w-full min-h-0"><Bar options={commonBarOptions} data={datasets.totalLearners} /></div>
                        </div>
                    )}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {!isRestrictedRole && (
                    <>
                        <div className="bg-white p-8 rounded-[35px] shadow-sm border border-gray-100 h-[450px] flex flex-col">
                            <h3 className="text-[#1E2B4D] font-bold mb-6 text-xl">Average Hours</h3>
                            <div className="flex-1 w-full min-h-0"><Bar options={commonBarOptions} data={datasets.averageHours} /></div>
                        </div>

                        <div className="bg-white p-8 rounded-[35px] shadow-sm border border-gray-100 h-[450px] flex flex-col">
                            <h3 className="text-[#1E2B4D] font-bold mb-6 text-xl">Budget Used</h3>
                            <div className="flex-1 w-full min-h-0"><Bar options={budgetOptions} data={datasets.budgetUsed} /></div>
                        </div>
                    </>
                )}

                <div className="bg-white p-8 rounded-[35px] shadow-sm border border-gray-100 h-[450px] flex flex-col">
                    <h3 className="text-[#1E2B4D] font-bold mb-6 text-xl">Total Training Category</h3>
                    <div className="flex-1 w-full min-h-0"><Bar options={groupedBarOptions} data={datasets.totalTrainingCategory} /></div>
                </div>

                {!isRestrictedRole && (
                    <div className="bg-white p-8 rounded-[35px] shadow-sm border border-gray-100 h-[450px] flex flex-col">
                        <h3 className="text-[#1E2B4D] font-bold mb-6 text-xl">Presentase Karyawan</h3>
                        <div className="flex-1 w-full min-h-0 relative">
                            <Doughnut options={doughnutOptions} data={datasets.presentaseKaryawan} />
                        </div>
                    </div>
                )}

                <div className="bg-white p-8 rounded-[35px] shadow-sm border border-gray-100 h-[450px] flex flex-col">
                    <h3 className="text-[#1E2B4D] font-bold mb-6 text-xl">Total Training Type</h3>
                    <div className="flex-1 w-full min-h-0"><Bar options={groupedBarOptions} data={datasets.totalTrainingType} /></div>
                </div>

                <div className="bg-white p-8 rounded-[35px] shadow-sm border border-gray-100 h-[450px] flex flex-col">
                    <h3 className="text-[#1E2B4D] font-bold mb-6 text-xl">Training Type Hours</h3>
                    <div className="flex-1 w-full min-h-0"><Bar options={groupedBarOptions} data={datasets.trainingTypeHours} /></div>
                </div>
            </div>

            {/* Tables Grid */}
            {!isRestrictedRole && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                    {/* 10. Cost Table */}
                    <div className="bg-white p-8 rounded-2xl shadow-xl border border-gray-100 h-[450px] flex flex-col overflow-hidden">
                        <h3 className="text-[#1E2B4D] font-bold mb-6 text-xl">Cost</h3>
                        <div className="flex-1 overflow-auto pr-2 custom-scrollbar">
                            <table className="w-full text-xs text-left border-separate border-spacing-y-1">
                                <thead className="text-gray-400 font-medium sticky top-0 bg-white z-10">
                                    <tr>
                                        <th className="pb-4 pr-2 font-semibold">Month</th>
                                        <th className="pb-4 pr-2 text-right font-semibold">Paid</th>
                                        <th className="pb-4 pr-2 text-right font-semibold">Unpaid</th>
                                        <th className="pb-4 pr-2 text-center font-semibold">Total Realisation</th>
                                        <th className="pb-4 pr-2 text-center font-semibold">Remaining Budget</th>
                                        <th className="pb-4 text-center font-semibold">Utilization%</th>
                                    </tr>
                                </thead>
                                <tbody className="text-[#1E2B4D]">
                                    {adminData?.tables?.cost?.length > 0 ? (
                                        adminData.tables.cost.map((c, i) => (
                                            <tr key={i} className={i % 2 === 0 ? "bg-[#F8F9FD]" : "bg-white"}>
                                                <td className="py-3 px-4 rounded-l-xl font-medium">{c.month}</td>
                                                <td className="py-3 px-2 text-right">{c.paid.toLocaleString()}</td>
                                                <td className="py-3 px-2 text-right">{c.unpaid.toLocaleString()}</td>
                                                <td className="py-3 px-2 text-right">{c.realisation.toLocaleString()}</td>
                                                <td className="py-3 px-2 text-right">{c.remaining.toLocaleString()}</td>
                                                <td className="py-3 px-4 text-right font-bold rounded-r-xl">{c.utilization}</td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan="6" className="py-20 text-center text-gray-400 font-medium">No data available</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Table Factory for repeated patterns */}
                    {[
                        { id: 'course_category', title: 'Course Category', field: 'category' },
                        { id: 'course', title: 'Course', field: 'course' },
                        { id: 'training_type', title: 'Training Type', field: 'type' },
                        { id: 'training_category', title: 'Training Category', field: 'category' },
                        { id: 'location', title: 'Location', field: 'location' },
                        { id: 'vendors', title: 'Training Vendors', field: 'vendor' },
                        { id: 'division', title: 'Division', field: 'division' },
                        { id: 'position', title: 'Position', field: 'position' }
                    ].map(table => (
                        <div key={table.id} className="bg-white p-8 rounded-2xl shadow-xl border border-gray-100 h-[450px] flex flex-col overflow-hidden">
                            <h3 className="text-[#1E2B4D] font-bold mb-6 text-xl">{table.title}</h3>
                            <div className="flex-1 overflow-auto pr-2 custom-scrollbar">
                                <table className="w-full text-xs text-left border-separate border-spacing-y-1">
                                    <thead className="text-gray-400 font-medium sticky top-0 bg-white z-10">
                                        <tr>
                                            <th className="pb-4 pr-4 font-semibold">{table.title}</th>
                                            <th className="pb-4 pr-4 text-center font-semibold">Learners</th>
                                            <th className="pb-4 pr-4 text-center font-semibold">Hours</th>
                                            <th className="pb-4 text-center font-semibold">Training Title</th>
                                        </tr>
                                    </thead>
                                    <tbody className="text-[#1E2B4D]">
                                        {adminData?.tables?.[table.id]?.length > 0 ? (
                                            adminData.tables[table.id].map((row, i) => (
                                                <tr key={i} className={i % 2 === 0 ? "bg-[#F8F9FD]" : "bg-white"}>
                                                    <td className="py-3 px-4 rounded-l-xl font-medium">{row[table.field]}</td>
                                                    <td className="py-3 px-2 text-center">{row.learners}</td>
                                                    <td className="py-3 px-2 text-center">{row.hours}</td>
                                                    <td className="py-3 px-4 text-center rounded-r-xl">{row.title_count}</td>
                                                </tr>
                                            ))
                                        ) : (
                                            <tr>
                                                <td colSpan="4" className="py-20 text-center text-gray-400 font-medium">No data available</td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </MainLayout>
    );
};

export default Dashboard;
