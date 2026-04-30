import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { getUserFromToken } from '../utils/auth';
import logoSmi from '../assets/logosmi.png';

const Navbar = () => {
    const [openTraining, setOpenTraining] = useState(false);
    const [openSettings, setOpenSettings] = useState(false);
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

    const isTrainingActive = () => {
        const paths = ['/training-master', '/evaluation', '/evaluation-employee', '/employee', '/hotel'];
        return paths.some(path => location.pathname.startsWith(path));
    };

    const isDashboardActive = () => {
        return location.pathname === '/dashboard' || location.pathname === '/';
    };

    const isSettingsActive = () => {
        const paths = ['/category', '/courses', '/vendor', '/tna'];
        return paths.some(path => location.pathname.startsWith(path));
    };

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        navigate('/login');
    };

    return (
        <header className="bg-[#215A92] text-white px-8 py-2 flex justify-between items-center shadow-md sticky top-0 z-[100]">
            <div className="flex items-center">
                <Link to="/dashboard" className="flex items-center space-x-2 cursor-pointer">
                    <img src={logoSmi} alt="Logo SMI" className="h-10 w-auto object-contain" />
                </Link>
            </div>
                
            <div className="flex items-center space-x-4 lg:space-x-6 text-sm font-semibold">
                {/* Training Dropdown */}
                <div className="relative">
                    <button 
                        onClick={() => { setOpenTraining(!openTraining); setOpenSettings(false); }}
                        className={`px-5 py-1.5 rounded-full flex items-center transition-all duration-200 focus:outline-none tracking-wide ${
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
                            className="absolute left-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-gray-100 z-50 overflow-hidden py-2 px-2 text-gray-700"
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
                                {!isRestricted && (
                                    <>
                                        <li>
                                            <Link to="/employee" className={`block px-5 py-2.5 hover:bg-gray-100 hover:text-[#2174C3] cursor-pointer transition-colors rounded-full text-left font-medium ${location.pathname === '/employee' ? 'bg-gray-100 text-[#2174C3] font-bold' : ''}`}>
                                                Employee
                                            </Link>
                                        </li>
                                        <li>
                                            <Link to="/hotel" className={`block px-5 py-2.5 hover:bg-gray-100 hover:text-[#2174C3] cursor-pointer transition-colors rounded-full text-left font-medium ${location.pathname === '/hotel' ? 'bg-gray-100 text-[#2174C3] font-bold' : ''}`}>
                                                Hotel
                                            </Link>
                                        </li>
                                    </>
                                )}
                            </ul>
                        </div>
                    )}
                </div>

                {/* Dashboard Link */}
                <Link to="/dashboard" 
                   className={`px-5 py-1.5 rounded-full flex items-center transition-all duration-200 tracking-wide ${
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
                <div className="relative">
                    <button 
                        onClick={() => { setOpenSettings(!openSettings); setOpenTraining(false); }}
                        className={`px-5 py-1.5 rounded-full flex items-center transition-all duration-200 font-semibold tracking-wide focus:outline-none ${
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
                            className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-gray-100 z-50 overflow-hidden py-2 px-2 text-gray-700"
                            onMouseLeave={() => setOpenSettings(false)}
                        >
                            <ul className="text-sm font-semibold space-y-1 text-left">
                                {!isRestricted && (
                                    <>
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
                                    </>
                                )}
                                <li>
                                    <Link to="/tna" className={`block px-5 py-2.5 hover:bg-gray-100 hover:text-[#2174C3] cursor-pointer transition-colors rounded-full font-medium ${currentPath === 'tna' ? 'bg-gray-100 text-[#2174C3] font-bold' : ''}`}>
                                        TNA
                                    </Link>
                                </li>
                            </ul>
                        </div>
                    )}
                </div>

                <div className="flex items-center space-x-3 ml-4">
                    <span className="hidden md:inline text-white font-semibold">Welcome, {user?.full_name || 'Guest'}</span>
                    <button 
                        onClick={handleLogout}
                        className="w-9 h-9 bg-gray-300 rounded-full border-2 border-white/50 overflow-hidden shrink-0 hover:ring-2 hover:ring-white transition-all"
                    >
                        <img src={`https://ui-avatars.com/api/?name=${encodeURIComponent(user?.full_name || 'Guest')}&background=random`} alt="User avatar" />
                    </button>
                </div>
            </div>
        </header>
    );
};

export default Navbar;
