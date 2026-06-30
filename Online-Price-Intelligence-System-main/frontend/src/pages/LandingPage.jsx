import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ShoppingBag, Search, Zap, BarChart2, Shield, Sparkles, Globe, MousePointer2, Share2, Twitter, Facebook, MessageCircle } from 'lucide-react';
import { motion } from 'framer-motion';

const stats = [
    { value: '5+', label: 'Global Retailers' },
    { value: '99%', label: 'Accuracy Rate' },
    { value: '1.2M', label: 'Prices Scanned' },
];

const RETAILERS = [
    { name: 'Amazon', logo: 'https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://amazon.com&size=64' },
    { name: 'eBay', logo: 'https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://ebay.com&size=64' },
    { name: 'Flipkart', logo: 'https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://flipkart.com&size=64' },
    { name: 'Snapdeal', logo: 'https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://snapdeal.com&size=64' },
    { name: 'Meesho', logo: 'https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://meesho.com&size=64' },
];

const RecommendationsSection = () => {
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchRecommendations = async () => {
            const user = JSON.parse(localStorage.getItem('user') || '{}');

            if (!user.id) {
                setLoading(false);
                return;
            }

            try {
                const { apiGet } = await import('../api');
                const data = await apiGet(`/api/analytics/recommendations/${user.id}`);
                if (Array.isArray(data)) {
                    setRecommendations(data.slice(0, 6));
                }
            } catch (err) {
                console.error('Failed to fetch recommendations:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchRecommendations();
    }, []);

    if (!loading && recommendations.length === 0) return null;

    return (
        <section className="w-full max-w-7xl px-6 py-24 bg-slate-50/50 dark:bg-white/[0.02] rounded-[60px] my-12">
            <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
                <div className="space-y-4">
                    <p className="text-[11px] font-black text-indigo-500 uppercase tracking-[0.3em]">Curated For You</p>
                    <h2 className="text-4xl font-black text-slate-900 dark:text-white tracking-tight font-outfit">
                        Recommended Intelligence
                    </h2>
                    <p className="text-slate-500 dark:text-slate-400 font-medium max-w-lg">
                        Based on your recent search patterns, our neural engine identified these high-value opportunities.
                    </p>
                </div>
                <Link to="/results" className="text-indigo-600 dark:text-indigo-400 font-black text-xs uppercase tracking-widest flex items-center gap-2 hover:gap-3 transition-all">
                    View All Market Intel <ArrowRight className="w-4 h-4" />
                </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {loading ? (
                    [1, 2, 3].map(i => (
                        <div key={i} className="h-64 bg-slate-100 dark:bg-white/5 rounded-[40px] animate-pulse" />
                    ))
                ) : (
                    recommendations.map((product, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: i * 0.1 }}
                            className="group p-6 rounded-[40px] bg-white dark:bg-slate-900/50 border border-slate-100 dark:border-white/5 hover:border-indigo-200 dark:hover:border-indigo-500/20 transition-all duration-500"
                        >
                            <div className="aspect-square rounded-[32px] overflow-hidden bg-slate-50 dark:bg-white/5 mb-6 relative">
                                {product.image && (
                                    <img src={product.image} alt={product.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" />
                                )}
                                <div className="absolute top-4 left-4 px-3 py-1 bg-white/90 dark:bg-slate-900/90 rounded-lg text-indigo-600 dark:text-indigo-400 text-[10px] font-black uppercase tracking-widest backdrop-blur-md">
                                    {product.platform}
                                </div>
                            </div>
                            <h4 className="text-sm font-black text-slate-900 dark:text-white font-outfit line-clamp-2 mb-4 leading-relaxed">
                                {product.title}
                            </h4>
                            <div className="flex items-center justify-between mt-auto">
                                <p className="text-xl font-black text-slate-900 dark:text-white font-outfit">
                                    ₹{parseFloat(product.price).toLocaleString('en-IN')}
                                </p>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => {
                                            const msg = encodeURIComponent(`Check out this deal on ${product.title} for ₹${product.price}! ${product.product_url}`);
                                            window.open(`https://api.whatsapp.com/send?text=${msg}`, '_blank');
                                        }}
                                        className="p-2 rounded-xl bg-slate-50 dark:bg-white/5 text-slate-400 hover:text-[#25D366] transition-colors"
                                        title="Share on WhatsApp"
                                    >
                                        <MessageCircle className="w-3.5 h-3.5" />
                                    </button>
                                    <a
                                        href={product.product_url}
                                        target="_blank"
                                        rel="noopener"
                                        className="w-10 h-10 rounded-xl bg-slate-900 dark:bg-white flex items-center justify-center text-white dark:text-slate-900 shadow-lg group-hover:scale-110 transition-transform"
                                    >
                                        <ShoppingBag className="w-4 h-4" />
                                    </a>
                                </div>
                            </div>
                        </motion.div>
                    ))
                )}
            </div>
        </section>
    );
};

const LandingPage = () => {
    return (
        <div className="flex flex-col items-center bg-white dark:bg-[#050810] overflow-hidden">

            {/* ── Hero Section ─────────────────────────────────────────── */}
            <section className="relative w-full pt-32 pb-24 px-6 flex flex-col items-center text-center">
                {/* Advanced background gradients */}
                <div className="absolute inset-0 pointer-events-none">
                    <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/10 rounded-full blur-[120px] animate-pulse" />
                    <div className="absolute bottom-[20%] right-[-5%] w-[35%] h-[35%] bg-violet-500/10 rounded-full blur-[100px]" />
                </div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="relative z-10 mb-8 px-5 py-2 bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/20 rounded-full inline-flex items-center gap-2"
                >
                    <Sparkles className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                    <span className="text-[10px] font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-[0.25em]">
                        The Benchmark in Price Intelligence
                    </span>
                </motion.div>

                <motion.h1
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                    className="relative z-10 text-6xl md:text-8xl font-black mb-8 tracking-tighter text-slate-900 dark:text-white leading-[0.9] font-outfit"
                >
                    Shop Smarter. <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-500">Save Faster.</span>
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3, duration: 0.8 }}
                    className="relative z-10 text-lg md:text-xl text-slate-500 dark:text-slate-400 max-w-2xl mb-14 px-4 leading-relaxed font-medium"
                >
                    Deploy our neural engine to scan the global market in milliseconds.
                    Because the best price shouldn't be a secret.
                </motion.p>

                <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.5 }}
                    className="relative z-10 flex flex-col sm:flex-row items-center gap-5"
                >
                    <Link
                        to="/upload"
                        className="group px-12 py-5 btn-primary rounded-[24px] text-xs font-black uppercase tracking-[0.2em] flex items-center gap-4 shadow-2xl shadow-indigo-500/40"
                    >
                        Scan Product
                        <MousePointer2 className="w-4 h-4 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                    </Link>
                </motion.div>

                {/* Floating Mockup Preview */}
                <motion.div
                    initial={{ opacity: 0, y: 100 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.7, duration: 1 }}
                    className="hidden"
                >
                    <div className="relative rounded-[40px] overflow-hidden border border-slate-200 dark:border-white/10 shadow-[0_50px_100px_-20px_rgba(0,0,0,0.15)] dark:shadow-black/50 aspect-[21/9] bg-slate-50 dark:bg-slate-900/50">
                        {/* Abstract UI skeleton */}
                        <div className="absolute inset-0 p-8 flex flex-col gap-6 opacity-40 grayscale group-hover:grayscale-0 transition-all duration-700">
                            <div className="w-48 h-8 bg-slate-200 dark:bg-white/10 rounded-full" />
                            <div className="grid grid-cols-4 gap-6">
                                {[1, 2, 3, 4].map(i => (
                                    <div key={i} className="aspect-square bg-slate-200 dark:bg-white/10 rounded-3xl" />
                                ))}
                            </div>
                        </div>
                        <div className="absolute inset-0 bg-gradient-to-t from-white dark:from-[#050810] via-transparent to-transparent" />
                    </div>
                </motion.div>
            </section>

            {/* ── Stats Strip ─────────────────────────────────────────── */}
            <section className="w-full max-w-6xl px-6 py-12">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {stats.map((s, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: i * 0.1 }}
                            className="p-8 rounded-[32px] bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/5 text-center"
                        >
                            <p className="text-4xl font-black text-slate-900 dark:text-white mb-2 font-outfit">{s.value}</p>
                            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{s.label}</p>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* — Supported Retailers — */}
            <section className="w-full max-w-6xl px-6 pb-20">
                <div className="p-8 rounded-[40px] bg-white dark:bg-slate-900/50 border border-slate-100 dark:border-white/5">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
                        <div>
                            <p className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.3em]">Supported Retailers</p>
                            <h3 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight font-outfit mt-2">
                                Live price signals from trusted marketplaces
                            </h3>
                        </div>
                        <div className="flex flex-wrap gap-4">
                            {RETAILERS.map((r) => (
                                <div
                                    key={r.name}
                                    className="flex items-center gap-3 px-4 py-2 rounded-2xl bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/10"
                                >
                                    <div className="w-9 h-9 rounded-xl bg-white dark:bg-white/10 p-1.5 border border-slate-100 dark:border-white/10">
                                        <img src={r.logo} alt={r.name} loading="lazy" decoding="async" className="w-full h-full object-contain" />
                                    </div>
                                    <span className="text-xs font-black text-slate-700 dark:text-slate-200">{r.name}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* ── Recommendations Section ────────────────────────────── */}
            <RecommendationsSection />

            {/* ── Project Statement ────────────────────────────── */}
            <section className="w-full max-w-6xl py-32 px-6">
                <div className="grid md:grid-cols-2 gap-24 items-center">
                    <motion.div
                        initial={{ opacity: 0, x: -40 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        className="space-y-8"
                    >
                        <div className="space-y-4">
                            <p className="text-[11px] font-black text-indigo-500 uppercase tracking-[0.3em]">The Philosophy</p>
                            <h2 className="text-5xl font-black text-slate-900 dark:text-white tracking-tight leading-[1] font-outfit">
                                Eliminating Market <br />Asymmetry.
                            </h2>
                        </div>
                        <div className="space-y-6">
                            <p className="text-lg text-slate-500 dark:text-slate-400 leading-relaxed font-medium">
                                Consumers lose billions annually to non-transparent pricing. Our mission is to democratize market data through neural identification.
                            </p>
                            <div className="flex gap-4 items-center p-6 rounded-[24px] bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/5">
                                <div className="w-12 h-12 rounded-2xl bg-indigo-500 flex items-center justify-center text-white shadow-lg">
                                    <Globe className="w-6 h-6" />
                                </div>
                                <div>
                                    <p className="font-bold text-slate-900 dark:text-white">Global Reach</p>
                                    <p className="text-xs text-slate-500">Scanning retailers across 12 countries instantly.</p>
                                </div>
                            </div>
                        </div>
                        <Link
                            to="/upload"
                            className="inline-flex items-center gap-3 text-indigo-600 dark:text-indigo-400 font-black text-sm uppercase tracking-widest hover:gap-5 transition-all"
                        >
                            Explore Engine <ArrowRight className="w-5 h-5" />
                        </Link>
                    </motion.div>

                    <div className="relative">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true }}
                            className="relative aspect-square rounded-[48px] bg-indigo-600 flex items-center justify-center overflow-hidden shadow-2xl shadow-indigo-500/40"
                        >
                            <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-20" />
                            <ShoppingBag className="w-32 h-32 text-white/20 animate-pulse" />

                            {/* Animated overlay cards */}
                            <motion.div
                                animate={{ y: [0, -20, 0] }}
                                transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
                                className="absolute top-10 right-[-20px] glass-card p-6 shadow-2xl"
                            >
                                <div className="flex gap-4 items-center">
                                    <div className="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center">
                                        <Zap className="w-5 h-5 text-white" />
                                    </div>
                                    <div>
                                        <p className="text-[10px] font-black text-slate-400 uppercase">Saving</p>
                                        <p className="text-xl font-black text-slate-900 dark:text-white tracking-tight">₹14,200</p>
                                    </div>
                                </div>
                            </motion.div>
                        </motion.div>
                    </div>
                </div>
            </section>

            {/* ── Outcome Cards Section ─────────────────────────────── */}
            <section className="w-full bg-slate-50 dark:bg-white/[0.02] py-32 px-6">
                <div className="max-w-7xl mx-auto space-y-24">
                    <div className="text-center space-y-4">
                        <p className="text-[11px] font-black text-indigo-500 uppercase tracking-[0.3em]">Capabilities</p>
                        <h2 className="text-5xl font-black text-slate-900 dark:text-white tracking-tight font-outfit">
                            Project Outcomes
                        </h2>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {[
                            {
                                icon: <Search className="w-6 h-6" />,
                                title: 'Neural ID',
                                desc: 'Advanced classification identifies products with 99% accuracy from any angle.',
                                color: 'indigo'
                            },
                            {
                                icon: <BarChart2 className="w-6 h-6" />,
                                title: 'Market Logic',
                                desc: 'Live price aggregation across Amazon, eBay, BestBuy, Target and more.',
                                color: 'violet'
                            },
                            {
                                icon: <Shield className="w-6 h-6" />,
                                title: 'Total Security',
                                desc: 'Privacy-first architecture ensures your data and uploads stay yours.',
                                color: 'emerald'
                            }
                        ].map((card, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.1 }}
                                className="premium-card p-10 bg-white dark:bg-slate-900/50 rounded-[40px] border border-slate-100 dark:border-white/5 space-y-6 group"
                            >
                                <div className={`w-14 h-14 rounded-2xl bg-indigo-500 flex items-center justify-center text-white shadow-xl shadow-indigo-500/20 group-hover:scale-110 transition-transform`}>
                                    {card.icon}
                                </div>
                                <h3 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight font-outfit">{card.title}</h3>
                                <p className="text-slate-500 dark:text-slate-400 font-medium leading-relaxed">{card.desc}</p>
                            </motion.div>
                        ))}
                    </div>

                    {/* Final CTA Strip */}
                    <div className="relative p-16 rounded-[48px] bg-[#0F172A] overflow-hidden">
                        <div className="absolute top-0 right-0 w-full h-full opacity-10">
                            <div className="absolute top-[-50%] right-[-10%] w-[100%] h-[150%] bg-indigo-500 rounded-full blur-[150px]" />
                        </div>
                        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-12">
                            <div className="space-y-4 text-center md:text-left">
                                <h2 className="text-4xl font-black text-white tracking-tighter font-outfit">Ready to never overpay again?</h2>
                                <p className="text-slate-400 text-lg font-medium">Join 50,000+ smart shoppers today.</p>
                            </div>
                            <Link to="/upload" className="px-12 py-5 bg-white text-slate-900 rounded-[24px] text-xs font-black uppercase tracking-[0.2em] shadow-2xl hover:bg-slate-100 transition-all active:scale-95">
                                Start Scanning Free
                            </Link>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default LandingPage;
