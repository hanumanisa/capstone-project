import { jwtDecode } from 'jwt-decode';

/**
 * Mendapatkan data user dari access token yang tersimpan di localStorage.
 * Mengembalikan null jika token tidak ada atau tidak valid.
 */
export const getUserFromToken = () => {
    const token = localStorage.getItem('access_token');
    if (!token) return null;

    try {
        const decoded = jwtDecode(token);
        
        // Memastikan token belum expired
        const currentTime = Date.now() / 1000;
        if (decoded.exp < currentTime) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            return null;
        }

        return {
            email: decoded.email,
            role: decoded.role,
            nik: decoded.nik || '-',
            full_name: decoded.full_name || '-',
            userId: decoded.user_id,
        };
    } catch (error) {
        console.error('Failed to decode token:', error);
        return null;
    }
};

/**
 * Mengecek apakah user sedang login dan token masih valid.
 */
export const isAuthenticated = () => {
    const user = getUserFromToken();
    return !!user;
};
