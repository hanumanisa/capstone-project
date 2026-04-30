import React from 'react';
import MainLayout from '../components/MainLayout';

const PlaceholderPage = ({ title }) => {
    return (
        <MainLayout>
            <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 min-h-[500px] flex flex-col items-center justify-center text-center">
                <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mb-6">
                    <svg className="w-10 h-10 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                </div>
                <h1 className="text-3xl font-bold text-slate-800 mb-2">{title}</h1>
                <p className="text-slate-500 max-w-md">
                    This page is currently under development. Please check back later for updates on {title.toLowerCase()} management.
                </p>
            </div>
        </MainLayout>
    );
};

export default PlaceholderPage;
