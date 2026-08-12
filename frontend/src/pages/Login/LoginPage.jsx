import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/axios';
import loginBg from '../../assets/login_bg.png';
import smiLogo from '../../assets/smi_logo.png';

const LoginPage = () => {
    // Login States
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [showLoginPassword, setShowLoginPassword] = useState(false);
    
    // Forgot Password States
    const [showForgotModal, setShowForgotModal] = useState(false);
    const [forgotStep, setForgotStep] = useState(1); // 1: Request OTP, 2: Verify OTP
    const [forgotEmail, setForgotEmail] = useState('');
    const [forgotOtp, setForgotOtp] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [forgotError, setForgotError] = useState('');
    const [forgotMessage, setForgotMessage] = useState('');
    const [forgotLoading, setForgotLoading] = useState(false);
    const [showNewPassword, setShowNewPassword] = useState(false);

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

    const handleRequestOTP = async (e) => {
        e.preventDefault();
        setForgotError('');
        setForgotMessage('');
        setForgotLoading(true);

        try {
            const response = await api.post('/api/forgot-password/request/', {
                email: forgotEmail
            });
            setForgotMessage(response.data.message);
            setForgotStep(2);
        } catch (err) {
            setForgotError(err.response?.data?.detail || 'Gagal mengirim OTP. Silakan coba lagi.');
        } finally {
            setForgotLoading(false);
        }
    };

    const handleVerifyOTP = async (e) => {
        e.preventDefault();
        setForgotError('');
        setForgotMessage('');
        setForgotLoading(true);

        try {
            const response = await api.post('/api/forgot-password/reset/', {
                email: forgotEmail,
                otp: forgotOtp,
                new_password: newPassword
            });
            
            // Sukses ganti password
            setForgotMessage(response.data.message);
            setTimeout(() => {
                setShowForgotModal(false);
                setForgotStep(1);
                setForgotEmail('');
                setForgotOtp('');
                setNewPassword('');
                setForgotMessage('');
            }, 2000);
        } catch (err) {
            setForgotError(err.response?.data?.detail || 'OTP tidak valid atau kadaluarsa.');
        } finally {
            setForgotLoading(false);
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
                    <div className="bg-white p-8 md:p-10 rounded-2xl shadow-[0_10px_40px_-15px_rgba(0,0,0,0.1)] border border-slate-100 flex flex-col items-center relative">

                        {/* Logo */}
                        <div className="mb-8">
                            <img src={smiLogo} alt="SMI Logo" className="h-16 w-auto" />
                        </div>

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
                                <div className="relative">
                                    <input
                                        id="password"
                                        type={showLoginPassword ? "text" : "password"}
                                        required
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        placeholder="Enter your password"
                                        className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all duration-200 placeholder:text-slate-400 pr-12"
                                    />
                                    <button
                                        type="button"
                                        className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-600 transition-colors focus:outline-none"
                                        onClick={() => setShowLoginPassword(!showLoginPassword)}
                                    >
                                        {showLoginPassword ? (
                                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                              <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
                                            </svg>
                                        ) : (
                                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                              <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                                              <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                                            </svg>
                                        )}
                                    </button>
                                </div>
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
                        
                        {/* Forgot Password Link */}
                        <div className="mt-6 w-full text-center">
                            <button 
                                onClick={() => {
                                    setShowForgotModal(true);
                                    setForgotStep(1);
                                    setForgotError('');
                                    setForgotMessage('');
                                }}
                                className="text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors bg-transparent border-none cursor-pointer"
                            >
                                Lupa Password?
                            </button>
                        </div>

                    </div>

                    {/* Footer / Copyright */}
                    <div className="text-center text-slate-400 text-xs">
                        &copy; {new Date().getFullYear()} PT Sarana Multi Infrastruktur (Persero). All rights reserved.
                    </div>
                </div>
            </div>

            {/* Forgot Password Modal */}
            {showForgotModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
                    <div className="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden relative animate-in fade-in zoom-in-95 duration-200">
                        {/* Modal Header */}
                        <div className="flex items-center justify-between p-6 border-b border-slate-100">
                            <h3 className="text-lg font-bold text-slate-800">
                                {forgotStep === 1 ? 'Lupa Password' : 'Reset Password'}
                            </h3>
                            <button 
                                onClick={() => setShowForgotModal(false)}
                                className="text-slate-400 hover:text-slate-600 transition-colors p-2 rounded-full hover:bg-slate-100"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                </svg>
                            </button>
                        </div>

                        {/* Modal Body */}
                        <div className="p-6 space-y-6">
                            {forgotError && (
                                <div className="p-3 text-sm text-red-600 bg-red-50 rounded-xl border border-red-100">
                                    {forgotError}
                                </div>
                            )}
                            
                            {forgotMessage && (
                                <div className="p-3 text-sm text-emerald-600 bg-emerald-50 rounded-xl border border-emerald-100">
                                    {forgotMessage}
                                </div>
                            )}

                            {forgotStep === 1 ? (
                                <form onSubmit={handleRequestOTP} className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="block text-sm font-medium text-slate-600">Email Terdaftar</label>
                                        <p className="text-xs text-slate-500 mb-2">Kami akan mengirimkan kode verifikasi 6-digit ke email Anda.</p>
                                        <input
                                            type="email"
                                            required
                                            value={forgotEmail}
                                            onChange={(e) => setForgotEmail(e.target.value)}
                                            placeholder="Contoh: user@gmail.com"
                                            className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all duration-200"
                                        />
                                    </div>
                                    <button
                                        type="submit"
                                        disabled={forgotLoading}
                                        className="w-full py-3 px-4 bg-[#2174C3] hover:bg-blue-700 text-white font-semibold rounded-xl shadow-[0_4px_12px_-2px_rgba(37,99,235,0.3)] transition-all duration-200 active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed"
                                    >
                                        {forgotLoading ? 'Mengirim...' : 'Kirim Kode Verifikasi'}
                                    </button>
                                </form>
                            ) : (
                                <form onSubmit={handleVerifyOTP} className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="block text-sm font-medium text-slate-600">Kode Verifikasi (OTP)</label>
                                        <p className="text-xs text-slate-500 mb-2">Cek kotak masuk email Anda dan masukkan 6-digit kode OTP.</p>
                                        <input
                                            type="text"
                                            required
                                            maxLength="6"
                                            value={forgotOtp}
                                            onChange={(e) => setForgotOtp(e.target.value)}
                                            placeholder="------"
                                            className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all duration-200 text-center tracking-[0.5em] text-lg font-bold"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="block text-sm font-medium text-slate-600">Password Baru</label>
                                        <div className="relative">
                                            <input
                                                type={showNewPassword ? "text" : "password"}
                                                required
                                                value={newPassword}
                                                onChange={(e) => setNewPassword(e.target.value)}
                                                placeholder="Masukkan password baru"
                                                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all duration-200 pr-12"
                                            />
                                            <button
                                                type="button"
                                                className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-600 transition-colors focus:outline-none"
                                                onClick={() => setShowNewPassword(!showNewPassword)}
                                            >
                                                {showNewPassword ? (
                                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                                      <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
                                                    </svg>
                                                ) : (
                                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                                                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                                                    </svg>
                                                )}
                                            </button>
                                        </div>
                                    </div>
                                    <button
                                        type="submit"
                                        disabled={forgotLoading}
                                        className="w-full py-3 px-4 bg-[#2174C3] hover:bg-blue-700 text-white font-semibold rounded-xl shadow-[0_4px_12px_-2px_rgba(37,99,235,0.3)] transition-all duration-200 active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed"
                                    >
                                        {forgotLoading ? 'Memproses...' : 'Simpan Password Baru'}
                                    </button>
                                </form>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LoginPage;
