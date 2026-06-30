import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LayoutDashboard, Heart, Clock, Bell, ArrowRight, Sparkles, TrendingUp, ShieldCheck, Zap } from 'lucide-react';
import { apiGet } from '../api';
import clsx from 'clsx';

const DashboardPage = () => {
    const navigate = useNavigate();
    const [wishlist, setWishlist] = useState([]);
    const [history, setHistory] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    useEffect(() => {
        if (!user.id) {
            navigate('/login');
            return;
        }
        fetchDashboardData();
    }, [user.id]);

    const fetchDashboardData = async () => {
        try {
            const [wishlistData, historyData, alertData] = await Promise.all([
                apiGet(`/api/wishlist/${user.id}?page=1&per_page=20`),
                apiGet(`/api/search-history/${user.id}?page=1&per_page=20`),
                apiGet(`/api/price-alert/user/${user.id}?page=1&per_page=20`)
            ]);

            setWishlist(wishlistData?.items?.slice(0, 4) || []); // Preview first 4
            setHistory(historyData?.items?.slice(0, 10) || []); // Last 10 searches
            setAlerts(alertData?.items?.slice(0, 3) || []); // First 3 alerts
        } catch (err) {
            console.error('Failed to load dashboard data:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-white dark:bg-[#050810] transition-colors duration-500 pb-20">
            <main className="max-w-7xl mx-auto px-6 py-12 md:py-20 space-y-20">
                <header>
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex flex-col md:flex-row md:items-end justify-between gap-8"
                    >
                        <div className="space-y-4">
                            <div className="flex items-center gap-3 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 w-fit">
                                <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
                                <span className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.2em]">Operational Overview</span>
                            </div>
                            <h1 className="text-4xl md:text-5xl font-black text-slate-900 dark:text-white font-outfit tracking-tight">
                                Welcome back, <span className="text-indigo-500">{user.name}</span>
                            </h1>
                            <p className="text-slate-500 dark:text-slate-400 font-medium max-w-xl text-lg">
                                Your intelligence dashboard provides a real-time summary of your market surveillance.
                            </p>
                        </div>
                        <div className="flex items-center gap-4">
                            <button
                                onClick={() => navigate('/upload')}
                                className="px-8 py-4 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-xl transition-all active:scale-95 flex items-center gap-2"
                            >
                                New Scan <Zap className="w-4 h-4" />
                            </button>
                        </div>
                    </motion.div>
                </header>

                {/* Dashboard Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">

                    {/* Left Column: Wishlist & Alerts */}
                    <div className="lg:col-span-8 space-y-12">

                        {/* Wishlist Section */}
                        <section className="space-y-6">
                            <div className="flex items-center justify-between">
                                <h3 className="text-xl font-black text-slate-900 dark:text-white font-outfit flex items-center gap-3">
                                    <Heart className="w-5 h-5 text-red-500" /> Intelligence Archive
                                </h3>
                                <Link to="/wishlist" className="text-[10px] font-black text-indigo-500 uppercase tracking-widest hover:underline">View All</Link>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {loading ? (
                                    [1, 2].map(i => <div key={i} className="h-40 bg-slate-50 dark:bg-white/5 rounded-[32px] animate-pulse" />)
                                ) : wishlist.length > 0 ? (
                                    wishlist.map((item) => (
                                        <motion.div
                                            key={item.id}
                                            whileHover={{ y: -5 }}
                                            className="p-5 rounded-[32px] bg-white dark:bg-slate-900/50 border border-slate-100 dark:border-white/5 flex gap-4"
                                        >
                                            <div className="w-20 h-20 rounded-2xl bg-slate-50 dark:bg-white/5 p-2 border border-slate-100 dark:border-white/10 flex-shrink-0">
                                                <img src={item.product_image} alt="" className="w-full h-full object-contain" />
                                            </div>
                                            <div className="flex-1 min-w-0 flex flex-col justify-between py-1">
                                                <h4 className="text-sm font-black text-slate-900 dark:text-white font-outfit truncate">{item.product_name}</h4>
                                                <div>
                                                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{item.store}</p>
                                                    <p className="text-lg font-black text-slate-900 dark:text-white font-outfit">₹{parseFloat(item.price).toLocaleString('en-IN')}</p>
                                                </div>
                                            </div>
                                        </motion.div>
                                    ))
                                ) : (
                                    <div className="col-span-full py-12 text-center border-2 border-dashed border-slate-100 dark:border-white/5 rounded-[32px]">
                                        <p className="text-slate-400 font-medium">No archived intelligence found.</p>
                                    </div>
                                )}
                            </div>
                        </section>

                        {/* Price Alerts Section */}
                        <section className="space-y-6">
                            <div className="flex items-center justify-between">
                                <h3 className="text-xl font-black text-slate-900 dark:text-white font-outfit flex items-center gap-3">
                                    <Bell className="w-5 h-5 text-amber-500" /> Active Surveillance
                                </h3>
                            </div>

                            <div className="space-y-4">
                                {loading ? (
                                    <div className="h-24 bg-slate-50 dark:bg-white/5 rounded-[32px] animate-pulse" />
                                ) : alerts.length > 0 ? (
                                    alerts.map((alert) => (
                                        <div key={alert.id} className="p-6 rounded-[32px] bg-amber-500/5 border border-amber-500/10 flex items-center justify-between gap-6">
                                            <div className="flex items-center gap-4">
                                                <div className="w-12 h-12 rounded-2xl bg-amber-500 flex items-center justify-center text-white shadow-lg shadow-amber-500/20">
                                                    <TrendingUp className="w-6 h-6" />
                                                </div>
                                                <div>
                                                    <h4 className="text-sm font-black text-slate-900 dark:text-white font-outfit line-clamp-1">{alert.product_name}</h4>
                                                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Target: ₹{parseFloat(alert.target_price).toLocaleString('en-IN')}</p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-[10px] font-black text-amber-500 uppercase tracking-widest mb-1">Current</p>
                                                <p className="text-xl font-black text-slate-900 dark:text-white font-outfit">₹{parseFloat(alert.current_price).toLocaleString('en-IN')}</p>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <div className="py-12 text-center border-2 border-dashed border-slate-100 dark:border-white/5 rounded-[32px]">
                                        <p className="text-slate-400 font-medium">No active price alerts set.</p>
                                    </div>
                                )}
                            </div>
                        </section>
                    </div>

                    {/* Right Column: Search History */}
                    <div className="lg:col-span-4 space-y-6">
                        <div className="flex items-center justify-between">
                            <h3 className="text-xl font-black text-slate-900 dark:text-white font-outfit flex items-center gap-3">
                                <Clock className="w-5 h-5 text-indigo-500" /> Neural Memories
                            </h3>
                            <Link to="/history" className="text-[10px] font-black text-indigo-500 uppercase tracking-widest hover:underline">View All</Link>
                        </div>

                        <div className="p-8 rounded-[40px] bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/5 space-y-6">
                            {loading ? (
                                [1, 2, 3].map(i => <div key={i} className="h-10 bg-white dark:bg-white/5 rounded-xl animate-pulse" />)
                            ) : history.length > 0 ? (
                                history.map((entry) => (
                                    <div
                                        key={entry.id}
                                        className="flex items-center justify-between group cursor-pointer"
                                        onClick={() => navigate(`/results?q=${encodeURIComponent(entry.search_query)}`)}
                                    >
                                        <div className="flex items-center gap-3 overflow-hidden">
                                            <div className="w-8 h-8 rounded-lg bg-white dark:bg-white/10 flex items-center justify-center flex-shrink-0 text-slate-400 group-hover:text-indigo-500 transition-colors">
                                                <LayoutDashboard className="w-4 h-4" />
                                            </div>
                                            <p className="text-sm font-bold text-slate-600 dark:text-slate-400 truncate capitalize group-hover:text-slate-900 dark:group-hover:text-white transition-colors">
                                                {entry.search_query}
                                            </p>
                                        </div>
                                        <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-indigo-500 group-hover:translate-x-1 transition-all" />
                                    </div>
                                ))
                            ) : (
                                <p className="text-center text-slate-400 py-8 italic font-medium">Clear search trail.</p>
                            )}
                        </div>
                    </div>
                </div>

                {/* System Status Footer card */}
                <section>
                    <div className="p-8 rounded-[48px] bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/5 flex flex-col md:flex-row items-center justify-between gap-8">
                        <div className="flex items-center gap-6">
                            <div className="w-16 h-16 rounded-3xl bg-indigo-500 flex items-center justify-center text-white shadow-2xl shadow-indigo-500/40">
                                <ShieldCheck className="w-8 h-8" />
                            </div>
                            <div>
                                <h4 className="text-xl font-black text-slate-900 dark:text-white font-outfit">Security Protocol Active</h4>
                                <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">All intelligence data is encrypted and private.</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-8">
                            <div className="text-center">
                                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Active Scrapers</p>
                                <p className="text-sm font-black text-emerald-500 uppercase tracking-tighter">5 Operational</p>
                            </div>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
};

export default DashboardPage;
