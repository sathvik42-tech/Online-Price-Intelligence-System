import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, ShoppingBag, Trash2, Star, CheckCircle, Package, Truck, ExternalLink, ShieldCheck, Sparkles, AlertCircle } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import clsx from 'clsx';

const ComparisonPage = () => {
    const navigate = useNavigate();
    const [comparedItems, setComparedItems] = useState(() => {
        const saved = localStorage.getItem('compareBasket');
        return saved ? JSON.parse(saved) : [];
    });

    useEffect(() => {
        localStorage.setItem('compareBasket', JSON.stringify(comparedItems));
    }, [comparedItems]);

    const handleRemove = (url) => {
        setComparedItems(prev => prev.filter(item => item.product_url !== url));
    };

    const lowestPrice = Math.min(...comparedItems.map(item => parseFloat(item.price) || Infinity));

    if (comparedItems.length === 0) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-white dark:bg-[#050810]">
                <div className="w-24 h-24 rounded-[32px] bg-slate-50 dark:bg-white/5 flex items-center justify-center mb-8">
                    <Package className="w-10 h-10 text-slate-300" />
                </div>
                <h2 className="text-3xl font-black text-slate-900 dark:text-white font-outfit mb-4 uppercase tracking-tight">Basket Empty</h2>
                <p className="text-slate-500 dark:text-slate-400 mb-12 text-center max-w-sm font-medium">
                    You haven't selected any products for intelligence comparison yet.
                </p>
                <Link to="/results" className="btn-primary px-10 py-5 rounded-[24px] text-xs font-black uppercase tracking-widest">
                    Return to Results
                </Link>
            </div>
        );
    }

    const rows = [
        { label: 'Market Identification', key: 'title', type: 'text' },
        { label: 'Intel Price', key: 'price', type: 'price' },
        { label: 'Source Retailer', key: 'platform', type: 'platform' },
        { label: 'Reputation Index', key: 'rating', type: 'rating' },
        { label: 'Supply Status', key: 'availability', type: 'text' },
        { label: 'Action', key: 'url', type: 'action' }
    ];

    return (
        <div className="min-h-screen bg-white dark:bg-[#050810] pt-32 pb-24 px-6 md:px-12">
            <div className="max-w-7xl mx-auto">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-16 gap-8">
                    <div className="space-y-4">
                        <motion.button
                            onClick={() => navigate(-1)}
                            className="flex items-center gap-2 text-[10px] font-black text-indigo-500 uppercase tracking-widest hover:gap-3 transition-all mb-4"
                        >
                            <ArrowLeft className="w-4 h-4" /> Back to Intelligence
                        </motion.button>
                        <h1 className="text-5xl font-black text-slate-900 dark:text-white tracking-tight font-outfit leading-none mb-2">
                            Side-by-Side <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-500 uppercase tracking-tighter">Comparison</span>
                        </h1>
                        <p className="text-slate-500 dark:text-slate-400 font-medium max-w-xl">
                            Our neural engine has indexed {comparedItems.length} products for benchmark analysis.
                            The most optimized deal is highlighted in electromagnetic emerald.
                        </p>
                    </div>

                    <div className="flex gap-4 p-2 bg-slate-50 dark:bg-white/5 rounded-3xl border border-slate-100 dark:border-white/5">
                        <div className="px-6 py-3">
                            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Spread</p>
                            <p className="text-xl font-black text-slate-900 dark:text-white font-outfit">
                                ₹{(Math.max(...comparedItems.map(i => i.price)) - lowestPrice).toLocaleString('en-IN')}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="overflow-x-auto no-scrollbar -mx-6 px-6">
                    <div className="min-w-[1000px]">
                        <table className="w-full border-separate border-spacing-x-4 border-spacing-y-0">
                            <thead>
                                <tr>
                                    <th className="w-64"></th>
                                    {comparedItems.map((item, i) => (
                                        <th key={i} className="pb-8">
                                            <div className="relative group aspect-square rounded-[40px] bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/10 overflow-hidden mb-4 shadow-xl shadow-slate-200/50 dark:shadow-black/20">
                                                <img src={item.image} alt="" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" />
                                                <button
                                                    onClick={() => handleRemove(item.product_url)}
                                                    className="absolute top-4 right-4 w-10 h-10 rounded-2xl bg-white/90 dark:bg-slate-900/90 flex items-center justify-center text-red-500 hover:bg-red-500 hover:text-white transition-all shadow-lg backdrop-blur-md opacity-0 group-hover:opacity-100 scale-90 group-hover:scale-100"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100 dark:divide-white/5">
                                {rows.map((row, i) => (
                                    <tr key={i} className="group hover:bg-slate-50/50 dark:hover:bg-white/[0.01] transition-colors">
                                        <td className="py-8 pr-12 text-[11px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] align-top">
                                            {row.label}
                                        </td>
                                        {comparedItems.map((item, idx) => {
                                            const isLowest = row.key === 'price' && parseFloat(item.price) === lowestPrice;

                                            return (
                                                <td key={idx} className={clsx(
                                                    "py-8 px-6 rounded-[32px] transition-all",
                                                    isLowest && "bg-emerald-50 dark:bg-emerald-500/10 ring-2 ring-emerald-500/20"
                                                )}>
                                                    {row.type === 'text' && (
                                                        <p className="text-sm font-bold text-slate-900 dark:text-white leading-relaxed">
                                                            {item[row.key] || 'N/A'}
                                                        </p>
                                                    )}
                                                    {row.type === 'price' && (
                                                        <div>
                                                            <div className="flex items-center gap-2 mb-1">
                                                                <p className={clsx(
                                                                    "text-2xl font-black font-outfit",
                                                                    isLowest ? "text-emerald-600 dark:text-emerald-400" : "text-slate-900 dark:text-white"
                                                                )}>
                                                                    ₹{parseFloat(item.price).toLocaleString('en-IN')}
                                                                </p>
                                                                {isLowest && <Sparkles className="w-4 h-4 text-emerald-500" />}
                                                            </div>
                                                            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                                                Tax Incl.
                                                            </p>
                                                        </div>
                                                    )}
                                                    {row.type === 'platform' && (
                                                        <div className="flex items-center gap-3">
                                                            <div className="w-8 h-8 rounded-xl bg-slate-50 dark:bg-white/5 p-1.5 border border-slate-100 dark:border-white/10">
                                                                <img
                                                                    src={`https://logo.clearbit.com/${item.platform}.com`}
                                                                    onError={(e) => e.target.src = 'https://ui-avatars.com/api/?name=' + item.platform}
                                                                    className="w-full h-full object-contain"
                                                                />
                                                            </div>
                                                            <p className="text-xs font-black text-slate-900 dark:text-white uppercase tracking-widest">
                                                                {item.platform}
                                                            </p>
                                                        </div>
                                                    )}
                                                    {row.type === 'rating' && (
                                                        <div className="space-y-1">
                                                            <div className="flex items-center gap-1">
                                                                <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                                                                <p className="text-sm font-black text-slate-900 dark:text-white font-outfit">
                                                                    {item.rating || '4.2'}
                                                                </p>
                                                            </div>
                                                            <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">
                                                                Market Consensus
                                                            </p>
                                                        </div>
                                                    )}
                                                    {row.type === 'action' && (
                                                        <a
                                                            href={item.product_url}
                                                            target="_blank"
                                                            rel="noopener"
                                                            className="inline-flex items-center gap-2 px-6 py-3 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-2xl text-[10px] font-black uppercase tracking-widest hover:scale-105 active:scale-95 transition-all shadow-xl dark:shadow-black/50"
                                                        >
                                                            Get Deal <ExternalLink className="w-3 h-3" />
                                                        </a>
                                                    )}
                                                </td>
                                            );
                                        })}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div className="mt-24 grid md:grid-cols-3 gap-8">
                    {[
                        { icon: <ShieldCheck className="w-6 h-6" />, title: 'Price Protection', desc: 'Secure checkout protocols verified.' },
                        { icon: <CheckCircle className="w-6 h-6" />, title: 'In-Stock Verify', desc: 'Real-time inventory synchronization.' },
                        { icon: <Truck className="w-6 h-6" />, title: 'Global Logistics', desc: 'Calculated shipping metrics apply.' }
                    ].map((feat, i) => (
                        <div key={i} className="p-10 rounded-[40px] bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/5 space-y-4">
                            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-500">
                                {feat.icon}
                            </div>
                            <h4 className="text-lg font-black text-slate-900 dark:text-white font-outfit">{feat.title}</h4>
                            <p className="text-sm text-slate-500 dark:text-slate-400 font-medium leading-relaxed">{feat.desc}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ComparisonPage;
