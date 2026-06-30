/**
 * useAuth — shared authentication state hook
 *
 * Centralises all auth-related localStorage access so no page needs to call
 * localStorage.getItem('intelToken') / localStorage.getItem('user') directly.
 *
 * Usage:
 *   const { user, token, isAuthenticated, login, logout } = useAuth();
 */
import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

export function useAuth() {
    const navigate = useNavigate();

    // Lazy-initialise from localStorage so the first render is always correct
    const [token, setToken] = useState(() => localStorage.getItem('intelToken') || '');
    const [user, setUser] = useState(() => {
        try {
            return JSON.parse(localStorage.getItem('user') || 'null');
        } catch {
            return null;
        }
    });

    /** Call after a successful login or registration */
    const login = useCallback((newToken, newUser) => {
        localStorage.setItem('intelToken', newToken);
        localStorage.setItem('user', JSON.stringify(newUser));
        setToken(newToken);
        setUser(newUser);
    }, []);

    /** Clear session and redirect to /login */
    const logout = useCallback(() => {
        localStorage.removeItem('intelToken');
        localStorage.removeItem('user');
        setToken('');
        setUser(null);
        navigate('/login');
    }, [navigate]);

    return {
        token,
        user,
        isAuthenticated: Boolean(token),
        login,
        logout,
    };
}
