import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, User, ArrowRight, ShieldCheck, Sparkles, AlertCircle, CheckCircle, Eye, EyeOff } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { apiPost } from '../api';
import clsx from 'clsx';

const AuthPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [isLogin, setIsLogin] = useState(true);
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: ''
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        setError('');
    };

    const validateForm = () => {
        if (!formData.email || !formData.password) {
            setError('Email and password are required.');
            return false;
        }
        if (!isLogin) {
            if (!formData.name) {
                setError('Name is required for registration.');
                return false;
            }
            if (formData.password !== formData.confirmPassword) {
                setError('Passwords do not match.');
                return false;
            }
            if (formData.password.length < 6) {
                setError('Password must be at least 6 characters.');
                return false;
            }
        }
        return true;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validateForm()) return;

        setLoading(true);
        setError('');

        const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
        const payload = isLogin
            ? { email: formData.email, password: formData.password }
            : { name: formData.name, email: formData.email, password: formData.password };

        try {
            const data = await apiPost(endpoint, payload);

            if (data && data.token) {
                // Success
                localStorage.setItem('intelToken', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));

                setSuccess(isLogin ? 'Login successful. Redirecting...' : 'Registration successful. Welcome!');

                setTimeout(() => {
                    navigate('/dashboard');
                }, 1500);
            }
        } catch (err) {
            setError(err.message || 'Authentication failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-white dark:bg-[#050810] flex items-center justify-center p-6 relative overflow-hidden">
            {/* Background Decorations */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none opacity-20 dark:opacity-40">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/20 blur-[120px] rounded-full" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-violet-500/20 blur-[120px] rounded-full" />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-[480px] relative z-10"
            >
                {/* Logo Section */}
                <div className="text-center mb-10">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-[24px] bg-slate-900 dark:bg-white mb-6 shadow-2xl">
                        <ShieldCheck className="w-8 h-8 text-white dark:text-slate-900" />
                    </div>
                    <h1 className="text-3xl font-black text-slate-900 dark:text-white font-outfit uppercase tracking-tighter mb-2">
                        {isLogin ? 'Login' : 'Register'}
                    </h1>
                    <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">
                        {isLogin ? 'Login to your account.' : 'Create a new account.'}
                    </p>
                </div>

                {/* Form Card */}
                <div className="bg-white/80 dark:bg-white/[0.03] backdrop-blur-3xl p-10 rounded-[48px] border border-slate-100 dark:border-white/5 shadow-2xl">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <AnimatePresence mode="wait">
                            {!isLogin && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="space-y-2 overflow-hidden"
                                >
                                    <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest block ml-4">Full Name</label>
                                    <div className="relative group">
                                        <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
                                            <User className="w-4 h-4 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                                        </div>
                                        <input
                                            type="text"
                                            name="name"
                                            value={formData.name}
                                            onChange={handleChange}
                                            className="w-full h-14 pl-14 pr-6 rounded-2xl bg-slate-50 dark:bg-white/5 border border-transparent focus:border-indigo-500 focus:bg-white dark:focus:bg-slate-900 text-sm font-bold transition-all outline-none text-slate-900 dark:text-white"
                                            placeholder="Agent Name"
                                        />
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div className="space-y-2">
                            <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest block ml-4">Email Address</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
                                    <Mail className="w-4 h-4 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                                </div>
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    className="w-full h-14 pl-14 pr-6 rounded-2xl bg-slate-50 dark:bg-white/5 border border-transparent focus:border-indigo-500 focus:bg-white dark:focus:bg-slate-900 text-sm font-bold transition-all outline-none text-slate-900 dark:text-white"
                                    placeholder="agent@intel.network"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest block ml-4">Password</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
                                    <Lock className="w-4 h-4 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                                </div>
                                <input
                                    type={showPassword ? "text" : "password"}
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    className="w-full h-14 pl-14 pr-14 rounded-2xl bg-slate-50 dark:bg-white/5 border border-transparent focus:border-indigo-500 focus:bg-white dark:focus:bg-slate-900 text-sm font-bold transition-all outline-none text-slate-900 dark:text-white"
                                    placeholder="••••••••"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute inset-y-0 right-5 flex items-center text-slate-400 hover:text-slate-600 transition-colors"
                                >
                                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            </div>
                            {isLogin && (
                                <div className="flex justify-end pr-4">
                                    <button
                                        type="button"
                                        onClick={() => navigate('/forgot-password')}
                                        className="text-[10px] font-black text-slate-400 hover:text-indigo-500 uppercase tracking-widest transition-colors"
                                    >
                                        Forgot Password?
                                    </button>
                                </div>
                            )}
                        </div>

                        <AnimatePresence mode="wait">
                            {!isLogin && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="space-y-2 overflow-hidden"
                                >
                                    <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest block ml-4">Confirm Password</label>
                                    <div className="relative group">
                                        <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
                                            <Lock className="w-4 h-4 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                                        </div>
                                        <input
                                            type="password"
                                            name="confirmPassword"
                                            value={formData.confirmPassword}
                                            onChange={handleChange}
                                            className="w-full h-14 pl-14 pr-6 rounded-2xl bg-slate-50 dark:bg-white/5 border border-transparent focus:border-indigo-500 focus:bg-white dark:focus:bg-slate-900 text-sm font-bold transition-all outline-none text-slate-900 dark:text-white"
                                            placeholder="••••••••"
                                        />
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Messages */}
                        <AnimatePresence>
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="p-4 rounded-2xl bg-red-50 dark:bg-red-500/10 border border-red-100 dark:border-red-500/20 flex items-center gap-3 text-red-500"
                                >
                                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                                    <p className="text-[11px] font-bold uppercase tracking-tight">{error}</p>
                                </motion.div>
                            )}
                            {success && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-100 dark:border-emerald-500/20 flex items-center gap-3 text-emerald-500"
                                >
                                    <CheckCircle className="w-4 h-4 flex-shrink-0" />
                                    <p className="text-[11px] font-bold uppercase tracking-tight">{success}</p>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <button
                            type="submit"
                            disabled={loading || !!success}
                            className={clsx(
                                "w-full h-14 rounded-2xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-black uppercase tracking-[0.2em] text-[11px] flex items-center justify-center gap-2 shadow-xl transition-all active:scale-[0.98]",
                                loading && "opacity-70 cursor-not-allowed"
                            )}
                        >
                            {loading ? (
                                <div className="w-5 h-5 border-2 border-slate-400 border-t-white dark:border-slate-300 dark:border-t-slate-900 rounded-full animate-spin" />
                            ) : (
                                <>
                                    {isLogin ? 'Login' : 'Register'}
                                    <ArrowRight className="w-4 h-4" />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-8 text-center">
                        <button
                            onClick={() => {
                                setIsLogin(!isLogin);
                                setError('');
                                setSuccess('');
                            }}
                            className="text-[10px] font-black text-slate-400 hover:text-indigo-500 uppercase tracking-widest transition-colors flex items-center gap-2 mx-auto"
                        >
                            {isLogin ? "Don't have an account? Register" : "Already have an account? Login"}
                            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                        </button>
                    </div>
                </div>

                {/* Footer Notes */}
                <div className="mt-8 flex items-center justify-center gap-6 opacity-30 grayscale">
                    <div className="flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4" />
                        <span className="text-[8px] font-black uppercase tracking-widest">SSL Encrypted</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Lock className="w-4 h-4" />
                        <span className="text-[8px] font-black uppercase tracking-widest">PCI Compliant</span>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default AuthPage;
