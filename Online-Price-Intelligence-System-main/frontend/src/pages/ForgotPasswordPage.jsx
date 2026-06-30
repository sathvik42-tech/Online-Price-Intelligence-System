import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, ArrowRight, ShieldCheck, Sparkles, AlertCircle, CheckCircle, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiPost } from '../api';
import clsx from 'clsx';

const ForgotPasswordPage = () => {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!email) {
            setError('Email address is required.');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const data = await apiPost('/api/auth/forgot-password', { email });
            setSuccess('Reset link sent to your email. Please check your inbox.');
        } catch (err) {
            setError(err.message || 'Failed to send reset link');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-white dark:bg-[#050810] flex items-center justify-center p-6 relative overflow-hidden font-outfit">
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
                <button
                    onClick={() => navigate('/login')}
                    className="flex items-center gap-2 text-[10px] font-black text-slate-400 hover:text-slate-900 dark:hover:text-white uppercase tracking-widest transition-all mb-10"
                >
                    <ArrowLeft className="w-3 h-3" /> Back to Terminal
                </button>

                <div className="text-center mb-10">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-[24px] bg-slate-900 dark:bg-white mb-6 shadow-2xl">
                        <ShieldCheck className="w-8 h-8 text-white dark:text-slate-900" />
                    </div>
                    <h1 className="text-3xl font-black text-slate-900 dark:text-white uppercase tracking-tighter mb-2">
                        Neural Reset
                    </h1>
                    <p className="text-sm text-slate-500 dark:text-slate-400 font-medium max-w-[280px] mx-auto">
                        Authorize a password override link for your intelligence profile.
                    </p>
                </div>

                <div className="bg-white/80 dark:bg-white/[0.03] backdrop-blur-3xl p-10 rounded-[48px] border border-slate-100 dark:border-white/5 shadow-2xl">
                    {!success ? (
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest block ml-4">Neural Address</label>
                                <div className="relative group">
                                    <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
                                        <Mail className="w-4 h-4 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                                    </div>
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="w-full h-14 pl-14 pr-6 rounded-2xl bg-slate-50 dark:bg-white/5 border border-transparent focus:border-indigo-500 focus:bg-white dark:focus:bg-slate-900 text-sm font-bold transition-all outline-none text-slate-900 dark:text-white"
                                        placeholder="agent@intel.network"
                                    />
                                </div>
                            </div>

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
                            </AnimatePresence>

                            <button
                                type="submit"
                                disabled={loading}
                                className={clsx(
                                    "w-full h-14 rounded-2xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-black uppercase tracking-[0.2em] text-[11px] flex items-center justify-center gap-2 shadow-xl transition-all active:scale-[0.98]",
                                    loading && "opacity-70 cursor-not-allowed"
                                )}
                            >
                                {loading ? (
                                    <div className="w-5 h-5 border-2 border-slate-400 border-t-white dark:border-slate-300 dark:border-t-slate-900 rounded-full animate-spin" />
                                ) : (
                                    <>
                                        Dispatch Link
                                        <ArrowRight className="w-4 h-4" />
                                    </>
                                )}
                            </button>
                        </form>
                    ) : (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="text-center py-6"
                        >
                            <div className="w-20 h-20 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto mb-6">
                                <CheckCircle className="w-10 h-10 text-emerald-500" />
                            </div>
                            <h3 className="text-xl font-black text-slate-900 dark:text-white uppercase mb-3">Transmission Sent</h3>
                            <p className="text-slate-500 dark:text-slate-400 text-sm mb-8 leading-relaxed">
                                A neural reset link has been dispatched to your address. It will remain active for 60 minutes.
                            </p>
                            <button
                                onClick={() => navigate('/login')}
                                className="text-[10px] font-black text-indigo-500 hover:text-indigo-400 uppercase tracking-widest transition-all inline-flex items-center gap-2"
                            >
                                Return to Login Access <Sparkles className="w-3.5 h-3.5" />
                            </button>
                        </motion.div>
                    )}
                </div>
            </motion.div>
        </div>
    );
};

export default ForgotPasswordPage;
