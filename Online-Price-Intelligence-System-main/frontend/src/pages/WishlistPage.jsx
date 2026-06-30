import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Heart, ExternalLink, Trash2, Package, AlertCircle, Sparkles, ShoppingBag } from 'lucide-react';
import { apiGet, apiDelete } from '../api';
import clsx from 'clsx';

const WishlistPage = () => {
    const navigate = useNavigate();
    const [wishlist, setWishlist] = useState([]);
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
        fetchWishlist(page);
    }, [user.id, page]);

    const fetchWishlist = async (nextPage = 1) => {
        setLoading(true);
        setError(null);
        try {
            const data = await apiGet(`/api/wishlist/${user.id}?page=${nextPage}&per_page=${perPage}`);
            setWishlist(data?.items || []);
            setPagination(data?.pagination || { page: nextPage, per_page: perPage, total: 0, has_more: false });
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const removeFromWishlist = async (id) => {
        try {
            await apiDelete(`/api/wishlist/${id}`);
            // Refresh current page (may shrink/shift results)
            fetchWishlist(page);
        } catch (err) {
            console.error('Failed to remove from wishlist:', err);
            alert('Failed to remove item from wishlist');
        }
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
                            <h1 className="text-xl font-black text-slate-900 dark:text-white font-outfit tracking-tight">Your Wishlist</h1>
                            <p className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.2em]">Curated Intelligence</p>
                        </div>
                    </div>
                </div>
            </header>

            <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-12">
                <AnimatePresence mode="wait">
                    {loading ? (
                        <div key="loading" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {[1, 2, 3, 4, 5, 6].map(i => (
                                <div key={i} className="h-48 bg-slate-50 dark:bg-white/5 rounded-[40px] animate-pulse" />
                            ))}
                        </div>
                    ) : error ? (
                        <div key="error" className="py-20 text-center space-y-6">
                            <div className="w-20 h-20 bg-red-50 dark:bg-red-900/20 rounded-[32px] flex items-center justify-center mx-auto text-red-400">
                                <AlertCircle className="w-10 h-10" />
                            </div>
                            <h4 className="text-xl font-black text-slate-900 dark:text-white font-outfit">Failed to Load Wishlist</h4>
                            <button onClick={fetchWishlist} className="btn-primary px-8 py-4 rounded-2xl text-[10px] uppercase font-black tracking-widest">Retry</button>
                        </div>
                    ) : wishlist.length === 0 ? (
                        <div key="empty" className="py-24 text-center space-y-6 border-2 border-dashed border-slate-100 dark:border-white/10 rounded-[48px]">
                            <Heart className="w-16 h-16 text-slate-200 dark:text-slate-700 mx-auto" strokeWidth={1} />
                            <div className="space-y-2">
                                <h4 className="text-xl font-black text-slate-900 dark:text-white font-outfit">Wishlist Empty</h4>
                                <p className="text-slate-500 dark:text-slate-400 font-medium">Capture products you love and save them here.</p>
                            </div>
                            <button onClick={() => navigate('/upload')} className="text-indigo-600 dark:text-indigo-400 font-black text-xs uppercase tracking-widest">Discover Products</button>
                        </div>
                    ) : (
                        <motion.div
                            key="grid"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                        >
                            {wishlist.map((item, i) => (
                                <motion.div
                                    key={item.id}
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: i * 0.05 }}
                                    className="group relative p-6 rounded-[40px] bg-white dark:bg-slate-900/50 border border-slate-100 dark:border-white/5 hover:border-indigo-200 dark:hover:border-indigo-500/20 transition-all duration-500 hover:shadow-2xl hover:shadow-indigo-500/5"
                                >
                                    <div className="flex gap-4 mb-4">
                                        <div className="w-20 h-20 rounded-2xl bg-white dark:bg-white/5 p-2 border border-slate-100 dark:border-white/10 flex items-center justify-center flex-shrink-0">
                                            {item.product_image ? (
                                                <img src={item.product_image} alt={item.product_name} loading="lazy" decoding="async" className="w-full h-full object-cover rounded-lg" />
                                            ) : (
                                                <Package className="w-8 h-8 text-slate-300" />
                                            )}
                                        </div>
                                        <div className="min-w-0">
                                            <h4 className="text-sm font-black text-slate-900 dark:text-white font-outfit leading-tight line-clamp-2 mb-1">
                                                {item.product_name}
                                            </h4>
                                            <p className="text-[10px] font-black text-indigo-500 uppercase tracking-widest">{item.store}</p>
                                        </div>
                                    </div>

                                    <div className="flex items-center justify-between mt-auto">
                                        <div>
                                            <p className="text-[9px] font-black text-slate-400 uppercase tracking-tighter mb-0.5">Price Saved</p>
                                            <p className="text-xl font-black text-slate-900 dark:text-white font-outfit">₹{parseFloat(item.price).toLocaleString('en-IN')}</p>
                                        </div>
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => removeFromWishlist(item.id)}
                                                className="w-10 h-10 rounded-xl flex items-center justify-center text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-all"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                            <motion.a
                                                href={item.product_link}
                                                target="_blank"
                                                rel="noopener"
                                                whileHover={{ scale: 1.05 }}
                                                whileTap={{ scale: 0.95 }}
                                                className="w-10 h-10 rounded-xl bg-slate-900 dark:bg-white flex items-center justify-center text-white dark:text-slate-900 shadow-lg transition-all"
                                            >
                                                <ExternalLink className="w-4 h-4" />
                                            </motion.a>
                                        </div>
                                    </div>

                                    <div className="absolute top-4 right-4 px-2 py-1 bg-emerald-500/10 text-emerald-500 text-[8px] font-black uppercase tracking-tighter rounded-md flex items-center gap-1">
                                        <Sparkles className="w-2.5 h-2.5" /> Tracked
                                    </div>
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
        </div>
    );
};

export default WishlistPage;
