import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Clock, Search, RotateCcw, Package, AlertCircle, ChevronRight, Sparkles } from 'lucide-react';
import { apiGet } from '../api';
import clsx from 'clsx';

const SearchHistoryPage = () => {
    const navigate = useNavigate();
    const [history, setHistory] = useState([]);
    const [pagination, setPagination] = useState({ page: 1, per_page: 20, total: 0, has_more: false });
    const [page, setPage] = useState(1);
    const perPage = 20;
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    useEffect(() => {
        if (!user.id) {
            navigate('/login');
            return;
        }
        fetchHistory(page);
    }, [user.id, page]);

    const fetchHistory = async (nextPage = 1) => {
        setLoading(true);
        setError(null);
        try {
            const data = await apiGet(`/api/search-history/${user.id}?page=${nextPage}&per_page=${perPage}`);
            setHistory(data?.items || []);
            setPagination(data?.pagination || { page: nextPage, per_page: perPage, total: 0, has_more: false });
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSearchAgain = (query) => {
        navigate(`/results?q=${encodeURIComponent(query)}`);
    };

    return (
        <div className="min-h-screen bg-white dark:bg-[#050810] transition-colors duration-500 relative overflow-hidden flex flex-col">
            {/* Top Navigation Bar */}
            <header className="sticky top-0 z-50 bg-white/70 dark:bg-[#050810]/70 backdrop-blur-xl border-b border-slate-100 dark:border-white/5 px-6 py-4">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-6">
                        <button
                            onClick={() => navigate(-1)}
                            className="w-10 h-10 bg-slate-50 dark:bg-white/5 rounded-2xl flex items-center justify-center text-slate-500 hover:text-indigo-600 transition-all active:scale-90"
                        >
                            <ArrowLeft className="w-5 h-5" />
                        </button>
                        <div>
                            <h1 className="text-xl font-black text-slate-900 dark:text-white font-outfit tracking-tight">Search History</h1>
                            <p className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.2em]">Your Intelligence Trail</p>
                        </div>
                    </div>
                </div>
            </header>

            <main className="flex-1 max-w-4xl mx-auto w-full px-6 py-12">
                <AnimatePresence mode="wait">
                    {loading ? (
                        <div key="loading" className="space-y-4">
                            {[1, 2, 3, 4, 5].map(i => (
                                <div key={i} className="h-20 bg-slate-50 dark:bg-white/5 rounded-3xl animate-pulse" />
                            ))}
                        </div>
                    ) : error ? (
                        <div key="error" className="py-20 text-center space-y-6">
                            <div className="w-20 h-20 bg-red-50 dark:bg-red-900/20 rounded-[32px] flex items-center justify-center mx-auto text-red-400">
                                <AlertCircle className="w-10 h-10" />
                            </div>
                            <h4 className="text-xl font-black text-slate-900 dark:text-white font-outfit">Failed to Load History</h4>
                            <button onClick={fetchHistory} className="btn-primary px-8 py-4 rounded-2xl text-[10px] uppercase font-black tracking-widest">Retry</button>
                        </div>
                    ) : history.length === 0 ? (
                        <div key="empty" className="py-24 text-center space-y-6 border-2 border-dashed border-slate-100 dark:border-white/10 rounded-[48px]">
                            <Package className="w-16 h-16 text-slate-200 dark:text-slate-700 mx-auto" />
                            <div className="space-y-2">
                                <h4 className="text-xl font-black text-slate-900 dark:text-white font-outfit">Clear Trail</h4>
                                <p className="text-slate-500 dark:text-slate-400 font-medium">You haven't performed any searches yet.</p>
                            </div>
                            <button onClick={() => navigate('/')} className="text-indigo-600 dark:text-indigo-400 font-black text-xs uppercase tracking-widest">Start Scanning</button>
                        </div>
                    ) : (
                        <motion.div
                            key="list"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="space-y-4"
                        >
                            {history.map((entry, i) => (
                                <motion.div
                                    key={entry.id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.05 }}
                                    className="group p-6 rounded-[32px] bg-white dark:bg-slate-900/50 border border-slate-100 dark:border-white/5 hover:border-indigo-200 dark:hover:border-indigo-500/20 flex items-center justify-between transition-all duration-300"
                                >
                                    <div className="flex items-center gap-6">
                                        <div className="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-500/10 flex items-center justify-center text-indigo-500">
                                            <Search className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <h4 className="text-lg font-black text-slate-900 dark:text-white font-outfit leading-none mb-2 capitalize">
                                                {entry.search_query}
                                            </h4>
                                            <div className="flex items-center gap-2 text-slate-400">
                                                <Clock className="w-3 h-3" />
                                                <span className="text-[10px] font-bold uppercase tracking-widest">
                                                    {new Date(entry.search_time).toLocaleString()}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => handleSearchAgain(entry.search_query)}
                                        className="px-6 py-3 rounded-2xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 text-[10px] font-black uppercase tracking-widest flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-all active:scale-95"
                                    >
                                        Search Again <RotateCcw className="w-3 h-3" />
                                    </button>
                                    <ChevronRight className="w-5 h-5 text-slate-300 group-hover:hidden transition-all" />
                                </motion.div>
                            ))}
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Pagination */}
                {!loading && !error && pagination.total > pagination.per_page && (
                    <div className="mt-10 flex items-center justify-center gap-3">
                        <button
                            onClick={() => setPage((p) => Math.max(1, p - 1))}
                            disabled={page <= 1}
                            className="px-5 py-3 rounded-2xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 text-[10px] font-black uppercase tracking-widest disabled:opacity-40"
                        >
                            Prev
                        </button>
                        <div className="text-xs font-black text-slate-500 dark:text-slate-400">
                            Page {pagination.page} of {Math.max(1, Math.ceil(pagination.total / pagination.per_page))}
                        </div>
                        <button
                            onClick={() => setPage((p) => (pagination.has_more ? p + 1 : p))}
                            disabled={!pagination.has_more}
                            className="px-5 py-3 rounded-2xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 text-[10px] font-black uppercase tracking-widest disabled:opacity-40"
                        >
                            Next
                        </button>
                    </div>
                )}
            </main>

            {/* Bottom Accent */}
            <div className="fixed bottom-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 opacity-20" />
        </div>
    );
};

export default SearchHistoryPage;
