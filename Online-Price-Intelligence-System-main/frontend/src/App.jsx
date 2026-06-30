import React, { useState, useEffect, Suspense, lazy } from 'react';
import { Routes, Route, Link, useLocation, useNavigate, Navigate } from 'react-router-dom';
import { Sun, Moon, Menu, X, Home, Upload, User, BarChart2, Zap, Clock, Heart, LogOut, Settings, LayoutDashboard } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import logoNew from './assets/logo-new.png';

const LandingPage = lazy(() => import('./pages/LandingPage'));
const AuthPage = lazy(() => import('./pages/AuthPage'));
const UploadPage = lazy(() => import('./pages/UploadPage'));
const ResultsPage = lazy(() => import('./pages/ResultsPage'));
const SearchHistoryPage = lazy(() => import('./pages/SearchHistoryPage'));
const WishlistPage = lazy(() => import('./pages/WishlistPage'));
const ComparisonPage = lazy(() => import('./pages/ComparisonPage'));
const ForgotPasswordPage = lazy(() => import('./pages/ForgotPasswordPage'));
const ResetPasswordPage = lazy(() => import('./pages/ResetPasswordPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));

function App() {
    const [darkMode, setDarkMode] = useState(false);
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const location = useLocation();
    const navigate = useNavigate();

    useEffect(() => {
        if (darkMode) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }, [darkMode]);

    const toggleTheme = () => setDarkMode(!darkMode);

    const navLinks = [
        { name: 'Home', path: '/', icon: <Home className="w-4 h-4" /> },
        { name: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
        { name: 'Upload', path: '/upload', icon: <Upload className="w-4 h-4" /> },
        { name: 'History', path: '/history', icon: <Clock className="w-4 h-4" /> },
        { name: 'Wishlist', path: '/wishlist', icon: <Heart className="w-4 h-4" /> },
    ];

    const handleLogout = () => {
        localStorage.removeItem('user');
        localStorage.removeItem('intelToken');
        navigate('/login');
    };

    const ProtectedRoute = ({ children }) => {
        const token = localStorage.getItem('intelToken');
        if (!token) return <Navigate to="/login" replace />;
        return children;
    };

    return (
        <div className="min-h-screen flex flex-col transition-colors duration-300 bg-[#f8faff] dark:bg-[#0a0f1e]">

            {/* Header */}
            <header className="sticky top-0 z-50 bg-white/80 dark:bg-[#0a0f1e]/90 backdrop-blur-xl shadow-sm border-b border-blue-50 dark:border-white/5 transition-colors duration-300">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">

                        {/* Logo */}
                        <Link to="/" className="flex items-center gap-3 group">
                            <div className="w-9 h-9 rounded-xl overflow-hidden shadow-md ring-1 ring-blue-100 dark:ring-blue-900/50 flex-shrink-0">
                                <img src={logoNew} alt="Logo" className="w-full h-full object-contain bg-white dark:bg-gray-800 p-0.5" />
                            </div>
                            <span className="text-base font-extrabold bg-gradient-to-r from-blue-600 via-violet-500 to-blue-400 bg-clip-text text-transparent hidden sm:block leading-tight">
                                Online Product Price Intelligence System
                            </span>
                        </Link>

                        {/* Desktop Nav */}
                        <div className="hidden md:flex items-center gap-4">
                            <nav className="flex items-center space-x-1">
                                {navLinks.map((link) => {
                                    const isActive = location.pathname === link.path;
                                    return (
                                        <Link
                                            key={link.name}
                                            to={link.path}
                                            className={`relative flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 ${isActive
                                                ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
                                                : 'text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-white/5'
                                                }`}
                                        >
                                            {link.icon}
                                            {link.name}
                                            {isActive && (
                                                <motion.div
                                                    layoutId="nav-indicator"
                                                    className="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-blue-500"
                                                />
                                            )}
                                        </Link>
                                    );
                                })}

                                <div className="w-px h-5 bg-gray-200 dark:bg-gray-700 mx-2" />

                                <button
                                    onClick={toggleTheme}
                                    className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-white/10 transition-colors mr-2"
                                    aria-label="Toggle Theme"
                                >
                                    {darkMode
                                        ? <Moon className="w-4 h-4 text-blue-300" />
                                        : <Sun className="w-4 h-4 text-amber-500" />
                                    }
                                </button>
                            </nav>

                            {/* User Profile / Login */}
                            <div className="flex items-center gap-4">
                                {/* User Profile / Login */}
                                <div className="flex items-center gap-4">
                                    {localStorage.getItem('user') ? (
                                        <div className="flex items-center gap-3">
                                            <button
                                                onClick={() => navigate('/profile')}
                                                className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 hover:border-indigo-500 transition-all group shadow-sm"
                                            >
                                                <div className="w-6 h-6 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-500">
                                                    <User className="w-4 h-4" />
                                                </div>
                                                <div className="text-left">
                                                    <p className="text-[10px] font-black text-slate-900 dark:text-white uppercase leading-tight line-clamp-1">
                                                        {JSON.parse(localStorage.getItem('user')).name}
                                                    </p>
                                                    <p className="text-[8px] font-bold text-slate-400 uppercase tracking-tighter group-hover:text-indigo-500 transition-colors">
                                                        Profile
                                                    </p>
                                                </div>
                                            </button>
                                            <button
                                                onClick={handleLogout}
                                                className="p-2.5 rounded-2xl bg-red-500/10 text-red-500 border border-transparent hover:border-red-500/20 transition-all"
                                                title="Logout"
                                            >
                                                <LogOut className="w-4 h-4" />
                                            </button>
                                        </div>
                                    ) : (
                                        <button
                                            onClick={() => navigate('/login')}
                                            className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:opacity-90 transition-all shadow-lg"
                                        >
                                            <User className="w-4 h-4" />
                                            <span className="text-[10px] font-black uppercase tracking-widest">Login</span>
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Mobile: theme + hamburger */}
                        <div className="flex items-center gap-2 md:hidden">
                            <button
                                onClick={toggleTheme}
                                className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-white/10 transition-colors"
                            >
                                {darkMode ? <Moon className="w-4 h-4 text-blue-300" /> : <Sun className="w-4 h-4 text-amber-500" />}
                            </button>
                            <button
                                onClick={() => setIsMenuOpen(!isMenuOpen)}
                                className="p-2 rounded-xl text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-white/10 transition-all"
                            >
                                {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Mobile Dropdown */}
                <AnimatePresence>
                    {isMenuOpen && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="md:hidden bg-white dark:bg-[#0a0f1e] border-b border-blue-50 dark:border-white/5 overflow-hidden"
                        >
                            <div className="px-4 pt-2 pb-4 space-y-1">
                                {navLinks.map((link) => (
                                    <Link
                                        key={link.name}
                                        to={link.path}
                                        onClick={() => setIsMenuOpen(false)}
                                        className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${location.pathname === link.path
                                            ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
                                            : 'text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-white/5'
                                            }`}
                                    >
                                        {link.icon}
                                        {link.name}
                                    </Link>
                                ))}
                                {localStorage.getItem('intelToken') && (
                                    <button
                                        onClick={() => {
                                            setIsMenuOpen(false);
                                            handleLogout();
                                        }}
                                        className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-all"
                                    >
                                        <LogOut className="w-4 h-4" />
                                        Logout
                                    </button>
                                )}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </header>

            {/* Main */}
            <main className="flex-grow transition-colors duration-300">
                <Suspense
                    fallback={
                        <div className="max-w-7xl mx-auto px-6 py-16 text-sm font-bold text-slate-500 dark:text-slate-400">
                            Loading…
                        </div>
                    }
                >
                    <Routes>
                        <Route path="/" element={<LandingPage />} />
                        <Route path="/auth" element={<AuthPage />} />
                        <Route path="/login" element={<AuthPage />} />
                        <Route path="/register" element={<AuthPage />} />
                        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                        <Route path="/reset-password" element={<ResetPasswordPage />} />

                        {/* Protected routes */}
                        <Route path="/upload" element={<ProtectedRoute><UploadPage /></ProtectedRoute>} />
                        <Route path="/results" element={<ProtectedRoute><ResultsPage /></ProtectedRoute>} />
                        <Route path="/history" element={<ProtectedRoute><SearchHistoryPage /></ProtectedRoute>} />
                        <Route path="/wishlist" element={<ProtectedRoute><WishlistPage /></ProtectedRoute>} />
                        <Route path="/compare" element={<ProtectedRoute><ComparisonPage /></ProtectedRoute>} />
                        <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
                        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
                    </Routes>
                </Suspense>
            </main>

            {/* Footer */}
            <footer className="relative bg-white dark:bg-[#0a0f1e] border-t border-blue-50 dark:border-white/5 overflow-hidden transition-colors duration-300">
                {/* Gradient top border */}
                <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-400 to-transparent opacity-50" />
                <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
                    <div className="flex flex-col items-center gap-5">
                        {/* Branding row */}
                        <div className="flex items-center gap-2">
                            <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center">
                                <img src={logoNew} alt="Logo" className="w-6 h-6 object-contain" />
                            </div>
                            <span className="text-sm font-bold bg-gradient-to-r from-blue-500 to-violet-500 bg-clip-text text-transparent">
                                Online Product Price Intelligence System
                            </span>
                        </div>
                        <p className="text-gray-400 dark:text-gray-500 text-xs">
                            © {new Date().getFullYear()} All rights reserved. AI-powered price comparison.
                        </p>
                        <div className="flex gap-6 text-xs text-gray-400 dark:text-gray-500">
                            <a href="#" className="hover:text-blue-500 transition-colors">Privacy</a>
                            <a href="#" className="hover:text-blue-500 transition-colors">Terms</a>
                            <a href="#" className="hover:text-blue-500 transition-colors">Contact</a>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}

export default App;
