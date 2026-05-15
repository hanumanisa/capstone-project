import Swal from 'sweetalert2';

const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 3000,
    timerProgressBar: true,
    customClass: {
        popup: 'premium-toast-popup',
        title: 'premium-toast-title'
    },
    didOpen: (toast) => {
        toast.addEventListener('mouseenter', Swal.stopTimer);
        toast.addEventListener('mouseleave', Swal.resumeTimer);
    }
});

export const notify = {
    success: (msg) => {
        Toast.fire({
            icon: 'success',
            title: msg,
            background: '#F0FDF4',
            color: '#166534',
            iconColor: '#22C55E'
        });
    },
    error: (msg) => {
        Toast.fire({
            icon: 'error',
            title: msg,
            background: '#FEF2F2',
            color: '#991B1B',
            iconColor: '#EF4444'
        });
    },
    confirm: async (title, text) => {
        const result = await Swal.fire({
            title: title || 'Apakah Anda yakin?',
            text: text || "Tindakan ini tidak dapat dibatalkan!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#1E5084',
            cancelButtonColor: '#E74C3C',
            confirmButtonText: 'Ya, Lanjutkan!',
            cancelButtonText: 'Batal',
            fontFamily: 'Lexend',
            borderRadius: '1.5rem',
            background: '#FFFFFF',
            customClass: {
                popup: 'premium-swal-popup',
                title: 'premium-swal-title',
                confirmButton: 'premium-swal-confirm',
                cancelButton: 'premium-swal-cancel'
            }
        });
        return result.isConfirmed;
    },
    alert: (title, text, icon = 'info') => {
        Swal.fire({
            title,
            text,
            icon,
            confirmButtonColor: '#1E5084',
            borderRadius: '1.5rem',
            fontFamily: 'Lexend'
        });
    }
};
