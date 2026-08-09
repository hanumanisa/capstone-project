import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { getUserFromToken } from '../utils/auth';
import logoSmi from '../assets/logosmi.png';
import ConfirmModal from './ConfirmModal';

const Navbar = () => {
    const [openTraining, setOpenTraining] = useState(false);
    const [openSettings, setOpenSettings] = useState(false);
    const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
    const [user, setUser] = useState(null);
    const navigate = useNavigate();
    const location = useLocation();

    const currentPath = location.pathname.split('/').pop() || 'dashboard';

    useEffect(() => {
        const userData = getUserFromToken();
        if (userData) {
            setUser(userData);
        }
    }, []);

    const restrictedRoles = ['Employee', 'Team Leader', 'Head of Division'];
    const isRestricted = user && restrictedRoles.includes(user.role);
    const canViewEmployee = user && (!isRestricted || ['Head of Division', 'Team Leader'].includes(user.role));

    const isTrainingActive = () => {
        const paths = ['/training-master', '/evaluation', '/evaluation-employee', '/employee', '/hotel'];
        if (isRestricted) paths.push('/tna');
        return paths.some(path => location.pathname.startsWith(path));
    };

    const isDashboardActive = () => {
        return location.pathname === '/dashboard' || location.pathname === '/';
    };

    const isSettingsActive = () => {
        const paths = ['/category', '/courses', '/vendor'];
        if (!isRestricted) paths.push('/tna');
        return paths.some(path => location.pathname.startsWith(path));
    };

    const handleLogout = () => {
        setShowLogoutConfirm(true);
    };

    const confirmLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        navigate('/login');
    };

    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    useEffect(() => {
        setMobileMenuOpen(false);
    }, [location.pathname]);

    return (
        <>
            <header className="bg-[#215A92] text-white shadow-md z-[100] transition-all duration-300">
                <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-2 flex justify-between items-center">
                    <div className="flex items-center">
                        <Link to="/dashboard" className="flex items-center space-x-2 cursor-pointer transition-transform hover:scale-105 active:scale-95">
                            <img src={logoSmi} alt="Logo SMI" className="h-8 sm:h-10 w-auto object-contain" />
                        </Link>
                    </div>
                        
                    {/* Desktop Menu */}
                    <div className="hidden lg:flex items-center space-x-4 xl:space-x-6 text-sm font-semibold">
                        {/* Training Dropdown */}
                        <div className="relative">
                            <button 
                                onClick={() => { setOpenTraining(!openTraining); setOpenSettings(false); }}
                                className={`px-4 xl:px-5 py-1.5 rounded-full flex items-center transition-all duration-200 focus:outline-none tracking-wide ${
                                    isTrainingActive() 
                                    ? 'bg-white/30 ring-1 ring-white/50 shadow-sm' 
                                    : 'bg-transparent hover:bg-white/10'
                                }`}
                            >
                                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"></path>
                                </svg>
                                Training
                                <svg className={`w-4 h-4 ml-2 transition-transform duration-200 ${openTraining ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                                </svg>
                            </button>

                            {openTraining && (
                                <div 
                                    className="absolute left-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-gray-100 z-50 overflow-hidden py-2 px-2 text-gray-700 animate-fade-in"
                                    onMouseLeave={() => setOpenTraining(false)}
                                >
                                    <ul className="text-sm font-semibold space-y-1">
                                        <li>
                                            <Link to="/training-master" className={`block px-5 py-2.5 hover:bg-gray-100 hover:text-[#2174C3] cursor-pointer transition-colors rounded-full text-left font-medium ${location.pathname === '/training-master' ? 'bg-gray-100 text-[#2174C3] font-bold' : ''}`}>
                                                Training Master
                                            </Link>
                                        </li>
                                        <li>
                                            {isRestricted ? (
                                                <Link to="/evaluation-employee" className={`block px-5 py-2.5 hover:bg-gray-100 hover:text-[#2174C3] cursor-pointer transition-colors rounded-full text-left font-medium ${location.pathname === '/evaluation-employee' ? 'bg-gray-100 text-[#2174C3] font-bold' : ''}`}>
                                                    Training Evaluation
                                                </Link>
                                            ) : (
                                                <Link to="/evaluation" className={`block px-5 py-2.5 hover:bg-gray-100 hover:text-[#2174C3] cursor-pointer transition-colors rounded-full text-left font-medium ${location.pathname === '/evaluation' ? 'bg-gray-100 text-[#2174C3] font-bold' : ''}`}>
                                                    Training Evaluation
                                                </Link>
                                            )}
                                        </li>
                                        {canViewEmployee && (
                                            <li>
                                                <Link to="/employee" className={`block px-5 py-2.5 hover:bg-gray-100 hover:text-[#2174C3] cursor-pointer transition-colors rounded-full text-left font-medium ${location.pathname === '/employee' ? 'bg-gray-100 text-[#2174C3] font-bold' : ''}`}>
                                                    Employee
                                                </Link>
                                            </li>
                                        )}
                                        {!isRestricted && (
                                            <li>
                                                <Link to="/hotel" className={`block px-5 py-2.5 hover:bg-gray-100 hover:text-[#2174C3] cursor-pointer transition-colors rounded-full text-left font-medium ${location.pathname === '/hotel' ? 'bg-gray-100 text-[#2174C3] font-bold' : ''}`}>
                                                    Venue
                                                </Link>
                                            </li>
                                        )}
                                        {isRestricted && (
                                            <li>
                                                <Link to="/tna" className={`block px-5 py-2.5 hover:bg-gray-100 hover:text-[#2174C3] cursor-pointer transition-colors rounded-full text-left font-medium ${location.pathname === '/tna' ? 'bg-gray-100 text-[#2174C3] font-bold' : ''}`}>
                                                    TNA
                                                </Link>
                                            </li>
                                        )}
                                    </ul>
                                </div>
                            )}
                        </div>

                        {/* Dashboard Link */}
                        <Link to="/dashboard" 
                           className={`px-4 xl:px-5 py-1.5 rounded-full flex items-center transition-all duration-200 tracking-wide ${
                               isDashboardActive() 
                               ? 'bg-white/30 ring-1 ring-white/50 shadow-sm' 
                               : 'bg-transparent hover:bg-white/10'
                           }`}
                        >
                            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z"></path>
                                <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z"></path>
                            </svg>
                            Dashboard
                        </Link>
                        
                        {/* Settings Dropdown */}
                        {!isRestricted && (
                            <div className="relative">
                                <button 
                                    onClick={() => { setOpenSettings(!openSettings); setOpenTraining(false); }}
                                    className={`px-4 xl:px-5 py-1.5 rounded-full flex items-center transition-all duration-200 font-semibold tracking-wide focus:outline-none ${
                                        isSettingsActive() 
                                        ? 'bg-white/30 ring-1 ring-white/50 shadow-sm' 
                                        : 'bg-transparent hover:bg-white/10'
                                    }`}
                                >
                                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                                        <path fill="white" d="M19.14,12.94a7.43,7.43,0,0,0,.05-.94,7.43,7.43,0,0,0-.05-.94l2.11-1.65a.5.5,0,0,0,.12-.64l-2-3.46a.5.5,0,0,0-.62-.22l-2.49,1a7.28,7.28,0,0,0-1.63-.94l-.38-2.65A.5.5,0,0,0,13.76,2H10.24a.5.5,0,0,0-.49.41L9.37,5.06a7.28,7.28,0,0,0-1.63.94l-2.49-1a.5.5,0,0,0-.6.22l-2,3.46a.5.5,0,0,0,.12.64L4.86,11.06a7.43,7.43,0,0,0-.05.94,7.43,7.43,0,0,0,.05.94L2.75,14.59a.5.5,0,0,0-.12.64l2,3.46a.5.5,0,0,0,.6.22l2.49-1a7.28,7.28,0,0,0,1.63.94l.38,2.65a.5.5,0,0,0,.49.41h3.52a.5.5,0,0,0,.49-.41l.38-2.65a7.28,7.28,0,0,0,1.63-.94l2.49,1a.5.5,0,0,0,.6-.22l2-3.46a.5.5,0,0,0-.12-.64ZM12,15.5A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z"/>
                                    </svg>
                                    Settings
                                    <svg className={`w-4 h-4 ml-2 transition-transform duration-200 ${openSettings ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                                    </svg>
                                </button>
                                {openSettings && (
                                    <div 
                                        className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-gray-100 z-50 overflow-hidden py-2 px-2 text-gray-700 animate-fade-in"
                                        onMouseLeave={() => setOpenSettings(false)}
                                    >
                                        <ul className="text-sm font-semibold space-y-1 text-left">
                                            <li>
                                                <Link to="/category" className={`block px-5 py-2.5 hover:bg-gray-100 hover:text-[#2174C3] cursor-pointer transition-colors rounded-full font-medium ${currentPath === 'category' ? 'bg-gray-100 text-[#2174C3] font-bold' : ''}`}>
                                                    Training Category
                                                </Link>
                                            </li>
                                            <li>
                                                <Link to="/vendor" className={`block px-5 py-2.5 hover:bg-gray-100 hover:text-[#2174C3] cursor-pointer transition-colors rounded-full font-medium ${currentPath === 'vendor' ? 'bg-gray-100 text-[#2174C3] font-bold' : ''}`}>
                                                    Training Vendor
                                                </Link>
                                            </li>
                                            <li>
                                                <Link to="/tna" className={`block px-5 py-2.5 hover:bg-gray-100 hover:text-[#2174C3] cursor-pointer transition-colors rounded-full font-medium ${currentPath === 'tna' ? 'bg-gray-100 text-[#2174C3] font-bold' : ''}`}>
                                                    TNA
                                                </Link>
                                            </li>
                                        </ul>
                                    </div>
                                )}
                            </div>
                        )}

                        <div className="flex items-center space-x-3 ml-4">
                            <span className="hidden xl:inline text-white font-semibold">Welcome, {user?.full_name || 'Guest'}</span>
                            <button 
                                onClick={handleLogout}
                                className="w-9 h-9 bg-gray-300 rounded-full border-2 border-white/50 overflow-hidden shrink-0 hover:ring-2 hover:ring-white transition-all shadow-sm"
                            >
                                <img src={`https://ui-avatars.com/api/?name=${encodeURIComponent(user?.full_name || 'Guest')}&background=random`} alt="User avatar" />
                            </button>
                        </div>
                    </div>

                    {/* Mobile Hamburger Toggle */}
                    <div className="lg:hidden flex items-center space-x-3">
                        <button 
                            onClick={handleLogout}
                            className="w-8 h-8 bg-gray-300 rounded-full border border-white/30 overflow-hidden shrink-0"
                        >
                            <img src={`https://ui-avatars.com/api/?name=${encodeURIComponent(user?.full_name || 'Guest')}&background=random`} alt="User avatar" />
                        </button>
                        <button 
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors focus:outline-none"
                        >
                            {mobileMenuOpen ? (
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            ) : (
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7"></path>
                                </svg>
                            )}
                        </button>
                    </div>
                </div>

                {/* Mobile Menu Content */}
                {mobileMenuOpen && (
                    <div className="lg:hidden bg-[#1A4B7A] border-t border-white/10 animate-fade-in shadow-inner">
                        <nav className="px-4 py-4 space-y-2">
                            <Link to="/dashboard" className={`flex items-center space-x-3 p-3 rounded-xl ${isDashboardActive() ? 'bg-white/20' : 'hover:bg-white/10'}`}>
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z"></path>
                                    <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z"></path>
                                </svg>
                                <span className="font-semibold">Dashboard</span>
                            </Link>
                            
                            <div className="space-y-1">
                                <div className="px-3 py-2 text-xs font-bold uppercase text-white/50 tracking-wider">Training</div>
                                <Link to="/training-master" className={`block p-3 pl-8 rounded-xl ${location.pathname === '/training-master' ? 'bg-white/20' : 'hover:bg-white/10'}`}>
                                    Training Master
                                </Link>
                                {isRestricted ? (
                                    <Link to="/evaluation-employee" className={`block p-3 pl-8 rounded-xl ${location.pathname === '/evaluation-employee' ? 'bg-white/20' : 'hover:bg-white/10'}`}>
                                        Training Evaluation
                                    </Link>
                                ) : (
                                    <Link to="/evaluation" className={`block p-3 pl-8 rounded-xl ${location.pathname === '/evaluation' ? 'bg-white/20' : 'hover:bg-white/10'}`}>
                                        Training Evaluation
                                    </Link>
                                )}
                                {canViewEmployee && (
                                    <Link to="/employee" className={`block p-3 pl-8 rounded-xl ${location.pathname === '/employee' ? 'bg-white/20' : 'hover:bg-white/10'}`}>
                                        Employee
                                    </Link>
                                )}
                                {!isRestricted && (
                                    <Link to="/hotel" className={`block p-3 pl-8 rounded-xl ${location.pathname === '/hotel' ? 'bg-white/20' : 'hover:bg-white/10'}`}>
                                        Venue
                                    </Link>
                                )}
                                {isRestricted && (
                                    <Link to="/tna" className={`block p-3 pl-8 rounded-xl ${currentPath === 'tna' ? 'bg-white/20' : 'hover:bg-white/10'}`}>
                                        TNA
                                    </Link>
                                )}
                            </div>

                            {!isRestricted && (
                                <div className="space-y-1">
                                    <div className="px-3 py-2 text-xs font-bold uppercase text-white/50 tracking-wider">Settings</div>
                                    <Link to="/category" className={`block p-3 pl-8 rounded-xl ${currentPath === 'category' ? 'bg-white/20' : 'hover:bg-white/10'}`}>
                                        Training Category
                                    </Link>
                                    <Link to="/vendor" className={`block p-3 pl-8 rounded-xl ${currentPath === 'vendor' ? 'bg-white/20' : 'hover:bg-white/10'}`}>
                                        Training Vendor
                                    </Link>
                                    <Link to="/tna" className={`block p-3 pl-8 rounded-xl ${currentPath === 'tna' ? 'bg-white/20' : 'hover:bg-white/10'}`}>
                                        TNA
                                    </Link>
                                </div>
                            )}
                            
                            <div className="pt-4 border-t border-white/10">
                                <button 
                                    onClick={handleLogout}
                                    className="w-full flex items-center justify-center space-x-2 p-3 bg-red-500/20 hover:bg-red-500/30 text-red-100 rounded-xl transition-colors font-semibold"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                                    </svg>
                                    <span>Logout</span>
                                </button>
                            </div>
                        </nav>
                    </div>
                )}
            </header>

        <ConfirmModal
            isOpen={showLogoutConfirm}
            onClose={() => setShowLogoutConfirm(false)}
            onConfirm={confirmLogout}
            title="Confirm Logout"
            message="Are you sure want to logout from the system?"
            confirmText="Logout"
        />
    </>
    );
};

export default Navbar;
