import React, { useState, useRef, useEffect } from 'react';

const YearPicker = ({ selectedYear, onYearChange }) => {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);
    
    // Generate years from current year - 5 to current year + 5
    const currentYear = new Date().getFullYear();
    const years = [];
    for (let i = currentYear - 5; i <= currentYear + 5; i++) {
        years.push(i);
    }

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    return (
        <div className="relative" ref={dropdownRef}>
            <div 
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center cursor-pointer group transition-all duration-200"
            >
                <span className="text-sm font-bold text-[#2174C3] group-hover:text-gray-400 transition-colors tracking-wide">
                    {selectedYear}
                </span>
            </div>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-2xl shadow-xl border border-gray-100 z-[100] p-4 overflow-hidden animate-in fade-in zoom-in duration-200">
                    <div className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3 px-2">Select Year</div>
                    <div className="grid grid-cols-3 gap-2">
                        {years.map(y => (
                            <div
                                key={y}
                                onClick={() => {
                                    onYearChange(y.toString());
                                    setIsOpen(false);
                                }}
                                className={`
                                    py-2 text-center rounded-xl text-sm font-bold transition-all cursor-pointer
                                    ${selectedYear === y.toString() 
                                        ? 'bg-[#2174C3] text-white shadow-md' 
                                        : 'text-gray-600 hover:bg-gray-100'
                                    }
                                `}
                            >
                                {y}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default YearPicker;
