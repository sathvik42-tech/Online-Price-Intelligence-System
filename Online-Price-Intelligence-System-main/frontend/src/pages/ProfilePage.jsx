import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Mail, Calendar, Edit3, Save, X, Shield, Activity, Package, Star, ArrowLeft, CheckCircle, AlertCircle, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiGet, apiPost } from '../api';
import clsx from 'clsx';

const ProfilePage = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [isEditing, setIsEditing] = useState(false);
    const [editData, setEditData] = useState({ name: '', email: '' });
    const [saveLoading, setSaveLoading] = useState(false);

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            const token = localStorage.getItem('intelToken');
            if (!token) {
                navigate('/login');
                return;
            }

            const data = await apiGet('/api/user/profile');
            if (data) {
                setUser(data);
                setEditData({ name: data.name, email: data.email });
            }
        } catch (err) {
            setError(err.message || 'Failed to load profile');
        } finally {
            setLoading(false);
        }
    };

    const handleUpdate = async (e) => {
        e.preventDefault();
        setSaveLoading(true);
        setError('');
        setSuccess('');

        try {
            const data = await apiPost('/api/user/profile', editData);
            if (data && data.user) {
                setUser(data.user);
                localStorage.setItem('user', JSON.stringify(data.user));
                setSuccess('Profile updated successfully');
                setIsEditing(false);
            }
        } catch (err) {
            setError(err.message || 'Failed to update profile');
        } finally {
            setSaveLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#050810] flex items-center justify-center">
                <div className="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-white dark:bg-[#050810] pt-24 pb-12 px-6 relative overflow-hidden font-outfit">
            {/* Background Decorations */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none opacity-20 dark:opacity-40">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500/10 blur-[120px] rounded-full" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-violet-500/10 blur-[120px] rounded-full" />
            </div>

            <div className="max-w-4xl mx-auto relative z-10">
                <button
                    onClick={() => navigate('/results')}
                    className="flex items-center gap-2 text-[10px] font-black text-slate-400 hover:text-slate-900 dark:hover:text-white uppercase tracking-widest transition-all mb-8"
                >
                    <ArrowLeft className="w-4 h-4" /> Return to Terminal
                </button>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left Column: Avatar & Basic Info */}
                    <div className="lg:col-span-1 space-y-6">
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="bg-white/80 dark:bg-white/[0.03] backdrop-blur-3xl p-8 rounded-[40px] border border-slate-100 dark:border-white/5 shadow-2xl text-center"
                        >
                            <div className="relative inline-block mb-6">
                                <div className="w-24 h-24 rounded-[32px] bg-slate-900 dark:bg-white flex items-center justify-center text-white dark:text-slate-900 mx-auto border-[6px] border-slate-50 dark:border-white/5 shadow-xl">
                                    <User className="w-10 h-10" />
                                </div>
                                <div className="absolute -bottom-1 -right-1 w-8 h-8 rounded-full bg-emerald-500 border-4 border-white dark:border-[#0c1221] flex items-center justify-center">
                                    <Shield className="w-4 h-4 text-white" />
                                </div>
                            </div>
                            <h2 className="text-xl font-black text-slate-900 dark:text-white uppercase tracking-tight line-clamp-1">{user?.name}</h2>
                            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Authorized Agent</p>

                            <div className="mt-8 pt-8 border-t border-slate-100 dark:border-white/5 space-y-4">
                                <div className="flex items-center justify-between">
                                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Trust Store</span>
                                    <div className="flex gap-0.5">
                                        {[1, 2, 3, 4, 5].map(i => <Star key={i} className="w-3 h-3 fill-amber-400 text-amber-400" />)}
                                    </div>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Access Lvl</span>
                                    <span className="text-[10px] font-black text-indigo-500 uppercase tracking-widest">Premium Elite</span>
                                </div>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.1 }}
                            className="bg-indigo-600 p-8 rounded-[40px] shadow-2xl relative overflow-hidden group cursor-pointer"
                        >
                            <div className="absolute top-[-20%] right-[-20%] w-32 h-32 bg-white/10 blur-3xl rounded-full group-hover:scale-150 transition-transform duration-700" />
                            <Package className="w-8 h-8 text-white/50 mb-4" />
                            <h3 className="text-white font-black text-lg uppercase tracking-tight">Active Intel</h3>
                            <p className="text-white/70 text-xs font-bold uppercase tracking-widest mt-1">12 Tracked Products</p>
                        </motion.div>

                        <button
                            onClick={() => {
                                localStorage.removeItem('user');
                                localStorage.removeItem('intelToken');
                                navigate('/login');
                            }}
                            className="w-full p-8 rounded-[40px] bg-red-500/10 border border-red-500/20 text-red-500 flex items-center justify-center gap-4 hover:bg-red-500 hover:text-white transition-all duration-300 group shadow-xl shadow-red-500/5"
                        >
                            <div className="w-12 h-12 rounded-2xl bg-red-500/10 flex items-center justify-center group-hover:bg-white/20 transition-colors">
                                <LogOut className="w-6 h-6" />
                            </div>
                            <div className="text-left">
                                <p className="text-[10px] font-black uppercase tracking-widest leading-none">Termination</p>
                                <p className="text-sm font-black uppercase tracking-tighter mt-1">Decommission Session</p>
                            </div>
                        </button>
                    </div>

                    {/* Right Column: Profile Details */}
                    <div className="lg:col-span-2 space-y-6">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white/80 dark:bg-white/[0.03] backdrop-blur-3xl p-10 rounded-[48px] border border-slate-100 dark:border-white/5 shadow-2xl"
                        >
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 mb-10">
                                <div>
                                    <h3 className="text-2xl font-black text-slate-900 dark:text-white uppercase tracking-tighter">Identity Profile</h3>
                                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest mt-1">Manage your neural account details.</p>
                                </div>
                                <button
                                    onClick={() => setIsEditing(!isEditing)}
                                    className={clsx(
                                        "px-6 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest flex items-center gap-2 transition-all active:scale-95 shadow-lg",
                                        isEditing
                                            ? "bg-slate-100 dark:bg-white/5 text-slate-900 dark:text-white hover:bg-slate-200"
                                            : "bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:opacity-90"
                                    )}
                                >
                                    {isEditing ? <><X className="w-4 h-4" /> Cancel Override</> : <><Edit3 className="w-4 h-4" /> Edit Profile</>}
                                </button>
                            </div>

                            <form onSubmit={handleUpdate} className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest block ml-4">Full Name</label>
                                    <div className="relative group">
                                        <User className="absolute left-5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                                        <input
                                            type="text"
                                            disabled={!isEditing}
                                            value={editData.name}
                                            onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                                            className="w-full h-14 pl-14 pr-6 rounded-2xl bg-slate-50 dark:bg-white/5 border border-transparent focus:border-indigo-500 focus:bg-white dark:focus:bg-slate-900 text-sm font-bold transition-all outline-none text-slate-900 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest block ml-4">Email Address</label>
                                    <div className="relative group">
                                        <Mail className="absolute left-5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                                        <input
                                            type="email"
                                            disabled={!isEditing}
                                            value={editData.email}
                                            onChange={(e) => setEditData({ ...editData, email: e.target.value })}
                                            className="w-full h-14 pl-14 pr-6 rounded-2xl bg-slate-50 dark:bg-white/5 border border-transparent focus:border-indigo-500 focus:bg-white dark:focus:bg-slate-900 text-sm font-bold transition-all outline-none text-slate-900 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest block ml-4">Account Commissioned</label>
                                    <div className="relative">
                                        <Calendar className="absolute left-5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                                        <input
                                            type="text"
                                            disabled
                                            value={user ? new Date(user.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' }) : ''}
                                            className="w-full h-14 pl-14 pr-6 rounded-2xl bg-slate-100/50 dark:bg-white/2 border border-transparent text-sm font-bold transition-all outline-none text-slate-500 dark:text-slate-500 cursor-not-allowed"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest block ml-4">Neural Status</label>
                                    <div className="relative">
                                        <Activity className="absolute left-5 top-1/2 -translate-y-1/2 w-4 h-4 text-emerald-500" />
                                        <input
                                            type="text"
                                            disabled
                                            value="Protocol Active"
                                            className="w-full h-14 pl-14 pr-6 rounded-2xl bg-slate-100/50 dark:bg-white/2 border border-transparent text-sm font-black text-emerald-500 uppercase tracking-widest outline-none cursor-not-allowed"
                                        />
                                    </div>
                                </div>

                                <AnimatePresence>
                                    {isEditing && (
                                        <motion.div
                                            initial={{ opacity: 0, height: 0 }}
                                            animate={{ opacity: 1, height: 'auto' }}
                                            exit={{ opacity: 0, height: 0 }}
                                            className="md:col-span-2 pt-4"
                                        >
                                            <button
                                                type="submit"
                                                disabled={saveLoading}
                                                className="w-full h-14 rounded-2xl bg-indigo-600 text-white font-black uppercase tracking-[0.2em] text-[11px] flex items-center justify-center gap-2 shadow-xl hover:bg-indigo-700 transition-all active:scale-95 disabled:opacity-70"
                                            >
                                                {saveLoading ? <div className="w-5 h-5 border-2 border-indigo-300 border-t-white rounded-full animate-spin" /> : <><Save className="w-4 h-4" /> Save Optimization</>}
                                            </button>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </form>

                            {/* Notifications */}
                            <AnimatePresence>
                                {error && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="mt-6 p-4 rounded-2xl bg-red-50 dark:bg-red-500/10 border border-red-100 dark:border-red-500/20 flex items-center gap-3 text-red-500"
                                    >
                                        <AlertCircle className="w-4 h-4 flex-shrink-0" />
                                        <p className="text-[11px] font-bold uppercase tracking-tight">{error}</p>
                                    </motion.div>
                                )}
                                {success && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="mt-6 p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-100 dark:border-emerald-500/20 flex items-center gap-3 text-emerald-500"
                                    >
                                        <CheckCircle className="w-4 h-4 flex-shrink-0" />
                                        <p className="text-[11px] font-bold uppercase tracking-tight">{success}</p>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </motion.div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProfilePage;
