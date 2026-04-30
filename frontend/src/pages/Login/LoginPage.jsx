import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/axios';
import loginBg from '../../assets/login_bg.png';
import smiLogo from '../../assets/smi_logo.png';

const LoginPage = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await api.post('/api/login/', {
                username: username, // Our backend uses email as username
                password: password
            });

            const { access, refresh } = response.data;
            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);

            navigate('/dashboard');
        } catch (err) {
            console.error('Login failed:', err);
            setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen w-full font-sans antialiased text-slate-900 bg-white">
            {/* Left Side - Image */}
            <div className="hidden lg:flex lg:w-1/2 relative">
                <img
                    src={loginBg}
                    alt="Lobby Background"
                    className="absolute inset-0 w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-black/10"></div>
            </div>

            {/* Right Side - Form */}
            <div className="w-full lg:w-1/2 flex items-center justify-center p-8 md:p-12 lg:p-16">
                <div className="w-full max-w-md space-y-8">
                    {/* Card Container */}
                    <div className="bg-white p-8 md:p-10 rounded-2xl shadow-[0_10px_40px_-15px_rgba(0,0,0,0.1)] border border-slate-100 flex flex-col items-center">

                        {/* Logo */}
                        <div className="mb-8">
                            <img src={smiLogo} alt="SMI Logo" className="h-16 w-auto" />
                        </div>

                        {/* Title - Hidden in the reference but good for UX or can be removed */}
                        {/* <h2 className="text-2xl font-bold text-slate-800 text-center mb-6">Login</h2> */}

                        {error && (
                            <div className="w-full p-3 mb-4 text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleLogin} className="w-full space-y-6">
                            {/* Email Input */}
                            <div className="space-y-2">
                                <label
                                    htmlFor="email"
                                    className="block text-sm font-medium text-slate-600"
                                >
                                    Email
                                </label>
                                <input
                                    id="email"
                                    type="email"
                                    required
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    placeholder="Enter your email"
                                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all duration-200 placeholder:text-slate-400"
                                />
                            </div>

                            {/* Password Input */}
                            <div className="space-y-2">
                                <label
                                    htmlFor="password"
                                    className="block text-sm font-medium text-slate-600"
                                >
                                    Password
                                </label>
                                <input
                                    id="password"
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Enter your password"
                                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all duration-200 placeholder:text-slate-400"
                                />
                            </div>

                            {/* Submit Button */}
                            <button
    type="submit"
    disabled={loading}
    className="w-full py-3 px-4 bg-[#2174C3] hover:bg-blue-700 text-white font-semibold rounded-xl shadow-[0_4px_12px_-2px_rgba(37,99,235,0.3)] transition-all duration-200 active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed mt-4"
>
    {loading ? 'Logging in...' : 'Login'}
</button>
                        </form>
                    </div>

                    {/* Footer / Copyright */}
                    <div className="text-center text-slate-400 text-xs">
                        &copy; {new Date().getFullYear()} PT Sarana Multi Infrastruktur (Persero). All rights reserved.
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
