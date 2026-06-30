import React, { useState, useEffect, useMemo, useRef, Suspense, lazy } from 'react';
import { useSearchParams, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Star, ExternalLink, TrendingDown, Package, AlertCircle, RotateCcw, CheckCircle, Truck, Tag, Sparkles, Filter, Info, ShieldCheck, Search, Heart, TrendingUp, Share2, Twitter, Facebook, MessageCircle, Copy, Check, Plus, X, ArrowRight, ShoppingBag } from 'lucide-react';
import { apiPost } from '../api';
import clsx from 'clsx';
const ProductTrendModal = lazy(() => import('../components/ProductTrendModal'));

const STORE_META = {
    amazon: { label: 'Amazon', logo: '/logos/amazon.png', color: '#FF9900' },
    ebay: { label: 'eBay', logo: '/logos/ebay.png', color: '#0064D2' },
    flipkart: { label: 'Flipkart', logo: '/logos/flipkart.png', color: '#2874F0' },
    snapdeal: { label: 'Snapdeal', logo: '/logos/snapdeal.png', color: '#E40046' },
    meesho: { label: 'Meesho', logo: '/logos/meesho.png', color: '#9B2C9B' },
};

const Logo = ({ src, alt, className }) => {
    const [error, setError] = useState(false);
    if (!src || error) {
        return (
            <div className={clsx("flex items-center justify-center bg-slate-100 dark:bg-white/10 rounded-lg overflow-hidden", className)}>
                <span className="text-[10px] font-black uppercase tracking-tighter text-slate-400">{alt}</span>
            </div>
        );
    }
    return <img src={src} alt={alt} className={className} onError={() => setError(true)} />;
};

const ComparisonSelectionBar = ({ selectedItems, onRemove, onCompare }) => {
    if (selectedItems.length === 0) return null;

    return (
        <motion.div
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 100, opacity: 0 }}
            className="fixed bottom-8 left-1/2 -translate-x-1/2 z-[100] w-full max-w-2xl px-6"
        >
            <div className="bg-slate-900/90 backdrop-blur-2xl border border-white/10 rounded-[32px] p-6 shadow-2xl flex items-center justify-between gap-8">
                <div className="flex items-center gap-4 overflow-x-auto no-scrollbar py-1">
                    {selectedItems.map((item, i) => (
                        <div key={i} className="relative group shrink-0">
                            <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 overflow-hidden">
                                <img src={item.image_url} alt="" loading="lazy" decoding="async" className="w-full h-full object-cover" />
                            </div>
                            <button
                                onClick={() => onRemove(item.product_url)}
                                className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-red-500 text-white flex items-center justify-center scale-0 group-hover:scale-100 transition-transform shadow-lg"
                            >
                                <X className="w-3 h-3" />
                            </button>
                        </div>
                    ))}
                    {[...Array(Math.max(0, 4 - selectedItems.length))].map((_, i) => (
                        <div key={`empty-${i}`} className="w-14 h-14 rounded-2xl bg-white/5 border border-white/5 border-dashed flex items-center justify-center">
                            <Plus className="w-4 h-4 text-white/20" />
                        </div>
                    ))}
                </div>

                <div className="flex items-center gap-6 shrink-0 border-l border-white/10 pl-8">
                    <div className="text-right">
                        <p className="text-[10px] font-black text-white/40 uppercase tracking-widest">Selected</p>
                        <p className="text-lg font-black text-white font-outfit">{selectedItems.length}/4</p>
                    </div>
                    <button
                        onClick={onCompare}
                        className="px-8 py-4 bg-indigo-500 hover:bg-indigo-400 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-xl shadow-indigo-500/20 transition-all active:scale-95 flex items-center gap-2"
                    >
                        Compare <ArrowRight className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </motion.div>
    );
};

function getStore(platform) {
    const key = platform?.toLowerCase() || '';
    return STORE_META[key] || { label: platform || 'Retailer', logo: '', color: '#6366F1' };
}

function formatPrice(val) {
    const num = parseFloat(val) || 0;
    // Round to whole numbers as requested for product prices
    const rounded = Math.round(num);
    return new Intl.NumberFormat('en-IN').format(rounded);
}

function StarRating({ rating }) {
    const val = parseFloat(rating) || 0;
    return (
        <div className="flex items-center gap-0.5">
            {[1, 2, 3, 4, 5].map((i) => (
                <Star
                    key={i}
                    className={`w-3 h-3 ${i <= val ? 'text-amber-400 fill-amber-400' : 'text-slate-200 dark:text-slate-700'}`}
                    strokeWidth={1.5}
                />
            ))}
            {val > 0 && <span className="text-[10px] font-black text-slate-400 ml-1">{val.toFixed(1)}</span>}
        </div>
    );
}

const ShareOptions = ({ product, onShare }) => {
    const [open, setOpen] = useState(false);
    const [copied, setCopied] = useState(false);
    const shareUrl = product.product_url;
    const title = product.title;

    const copyToClipboard = () => {
        navigator.clipboard.writeText(shareUrl);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="relative">
            <button 
                onClick={() => setOpen(!open)}
                className="p-2.5 rounded-lg bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/10 text-slate-400 hover:text-indigo-500 transition-all flex items-center justify-center"
                title="Share product"
            >
                <Share2 className="w-3.5 h-3.5" />
            </button>
            <AnimatePresence>
                {open && (
                    <>
                        <div className="fixed inset-0 z-[60]" onClick={() => setOpen(false)} />
                        <motion.div 
                            initial={{ opacity: 0, scale: 0.95, y: 10 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 10 }}
                            className="absolute right-0 bottom-full mb-2 z-[70] w-48 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-2xl shadow-2xl p-2"
                        >
                            <a 
                                href={`https://api.whatsapp.com/send?text=${encodeURIComponent(title + ' ' + shareUrl)}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-white/5 rounded-xl transition-colors text-xs font-bold text-slate-600 dark:text-slate-300"
                            >
                                <MessageCircle className="w-4 h-4 text-emerald-500" /> WhatsApp
                            </a>
                            <a 
                                href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(shareUrl)}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-white/5 rounded-xl transition-colors text-xs font-bold text-slate-600 dark:text-slate-300"
                            >
                                <Twitter className="w-4 h-4 text-sky-400" /> Twitter
                            </a>
                            <button 
                                onClick={copyToClipboard}
                                className="w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-white/5 rounded-xl transition-colors text-xs font-bold text-slate-600 dark:text-slate-300"
                            >
                                {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4 text-amber-500" />}
                                {copied ? 'Copied!' : 'Copy Link'}
                            </button>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
};

function StoreCard({ product, isLowest, index }) {
    const store = getStore(product.platform);
    const price = parseFloat(product.price) || 0;
    const rating = parseFloat(product.seller_rating) || 0;

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className={clsx(
                "group relative p-6 rounded-[32px] border transition-all duration-500 overflow-hidden",
                isLowest
                    ? "bg-gradient-to-r from-emerald-50 to-white dark:from-emerald-500/5 dark:to-slate-900 border-emerald-200 dark:border-emerald-500/30 shadow-xl shadow-emerald-500/10"
                    : "bg-white dark:bg-slate-900/40 border-slate-100 dark:border-white/5 hover:border-indigo-200 dark:hover:border-indigo-500/20 hover:shadow-lg"
            )}
        >
            <div className="flex flex-col lg:flex-row items-center gap-6">
                {/* Store Info Area */}
                <div className="flex flex-col items-center gap-3 w-full lg:w-32 shrink-0 lg:pr-6 lg:border-r border-slate-100 dark:border-white/5">
                    <div className="w-16 h-16 rounded-2xl bg-white dark:bg-white/5 p-2 border border-slate-100 dark:border-white/10 flex items-center justify-center shadow-sm">
                        <Logo src={store.logo} alt={store.label} className="w-full h-full object-contain" />
                    </div>
                    <div className="text-center">
                        <span className="block text-xs font-black text-slate-900 dark:text-white font-outfit uppercase tracking-wider">{store.label}</span>
                        <StarRating rating={rating} />
                    </div>
                </div>

                {/* Product/Details Area - Middle */}
                <div className="flex-1 min-w-0 flex flex-col gap-2 py-2">
                    <h4 className="text-base font-bold text-slate-800 dark:text-slate-200 line-clamp-2 lg:line-clamp-1 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                        {product.title}
                    </h4>
                    <div className="flex flex-wrap items-center gap-3">
                        <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-50 dark:bg-emerald-500/10 rounded-full">
                            <CheckCircle className="w-3 h-3 text-emerald-500" />
                            <span className="text-[9px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-tight">
                                {product.availability || 'In Stock'}
                            </span>
                        </div>
                        <div className="flex items-center gap-1.5 px-3 py-1 bg-slate-50 dark:bg-white/5 rounded-full">
                            <Truck className="w-3 h-3 text-slate-400" />
                            <span className="text-[9px] font-black text-slate-500 dark:text-slate-400 uppercase tracking-tight">
                                {parseFloat(product.shipping) === 0 ? 'Free Shipping' : `+₹${parseFloat(product.shipping).toLocaleString('en-IN')}`}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Pricing & Actions Area - Right */}
                <div className="flex flex-col items-center lg:items-end justify-center gap-4 w-full lg:w-auto lg:pl-6 lg:border-l border-slate-100 dark:border-white/5">
                    <div className="text-center lg:text-right">
                        <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-0.5">Best Offer</p>
                        <p className="text-2xl font-black text-slate-900 dark:text-white font-outfit leading-none">
                            ₹{formatPrice(product.price)}
                        </p>
                    </div>

                    <div className="flex flex-col gap-2 w-full sm:w-48 lg:w-40">
                        <motion.a
                            href={product.product_url}
                            target="_blank"
                            rel="noopener"
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className={clsx(
                                "px-6 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest flex items-center justify-center gap-2 transition-all shadow-md",
                                isLowest ? "bg-indigo-600 text-white shadow-indigo-500/20" : "bg-slate-900 dark:bg-white text-white dark:text-slate-900"
                            )}
                        >
                            Buy Now <ExternalLink className="w-3 h-3" />
                        </motion.a>
                        
                        <div className="grid grid-cols-3 gap-2">
                            <motion.button
                                onClick={() => product.onSetAlert(product)}
                                whileHover={{ y: -2 }}
                                className="p-2.5 rounded-lg bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/10 text-slate-600 dark:text-slate-400 hover:text-indigo-500 transition-all flex items-center justify-center text-[8px] font-black uppercase"
                                title="Set Price Alert"
                            >
                                <Sparkles className="w-3.5 h-3.5 mr-1" /> Alert
                            </motion.button>
                            <motion.button
                                onClick={() => product.onToggleCompare(product)}
                                whileHover={{ y: -2 }}
                                className={clsx(
                                    "p-2.5 rounded-lg border transition-all flex items-center justify-center text-[8px] font-black uppercase",
                                    product.isCompared
                                        ? "bg-indigo-50 border-indigo-500 text-white"
                                        : "bg-slate-50 dark:bg-white/5 border-slate-100 dark:border-white/10 text-slate-400"
                                )}
                                title="Compare Product"
                            >
                                <Copy className="w-3.5 h-3.5 mr-1" /> Compare
                            </motion.button>
                            <ShareOptions product={product} />
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}

const SCAN_PLATFORMS = [
    { key: 'amazon', label: 'Amazon', logo: '/logos/amazon.png', color: '#FF9900' },
    { key: 'ebay', label: 'eBay', logo: '/logos/ebay.png', color: '#0064D2' },
    { key: 'flipkart', label: 'Flipkart', logo: '/logos/flipkart.png', color: '#2874F0' },
    { key: 'snapdeal', label: 'Snapdeal', logo: '/logos/snapdeal.png', color: '#E40046' },
    { key: 'meesho', label: 'Meesho', logo: '/logos/meesho.png', color: '#9B2C9B' },
];

function ScanningLoader({ query, image }) {
    const [activeIdx, setActiveIdx] = React.useState(0);
    const [elapsed, setElapsed] = React.useState(0);

    React.useEffect(() => {
        const platformTimer = setInterval(() => {
            setActiveIdx(i => (i + 1) % SCAN_PLATFORMS.length);
        }, 1400);
        const elapsedTimer = setInterval(() => {
            setElapsed(s => s + 1);
        }, 1000);
        return () => { clearInterval(platformTimer); clearInterval(elapsedTimer); };
    }, []);

    const progress = Math.min((elapsed / 20) * 100, 95);

    return (
        <motion.div
            key="scanning"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="py-10 space-y-10"
        >
            <div className="flex flex-col items-center gap-8">
                {image && (
                    <motion.div 
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="w-48 h-48 rounded-[48px] overflow-hidden border-4 border-white/20 shadow-2xl bg-white/5"
                    >
                        <img src={image} alt="" className="w-full h-full object-cover" />
                    </motion.div>
                )}
                <div className="text-center space-y-3">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-indigo-50 dark:bg-indigo-900/30 rounded-full border border-indigo-100 dark:border-indigo-800/50">
                        <span className="w-2 h-2 bg-indigo-500 rounded-full animate-ping" />
                        <span className="text-[10px] font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-[0.2em]">Live Market Scan</span>
                    </div>
                    <h3 className="text-3xl font-black text-slate-900 dark:text-white font-outfit tracking-tight capitalize">
                        Scanning for &ldquo;{query}&rdquo;
                    </h3>
                </div>
            </div>

            <div className="flex flex-wrap justify-center gap-4">
                {SCAN_PLATFORMS.map((p, i) => {
                    const isActive = i === activeIdx;
                    const isDone = i < activeIdx;
                    return (
                        <motion.div
                            key={p.key}
                            animate={isActive ? { scale: [1, 1.08, 1], transition: { repeat: Infinity, duration: 0.7 } } : {}}
                            className={clsx(
                                'flex items-center gap-3 px-5 py-3 rounded-2xl border transition-all duration-500',
                                isActive
                                    ? 'bg-indigo-50 dark:bg-indigo-900/30 border-indigo-300 dark:border-indigo-600 shadow-lg shadow-indigo-200/50 dark:shadow-indigo-900/30'
                                    : isDone
                                        ? 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-700/40'
                                        : 'bg-slate-50 dark:bg-white/5 border-slate-100 dark:border-white/5 opacity-50'
                            )}
                        >
                            <div className="w-8 h-8 flex items-center justify-center rounded-xl bg-white dark:bg-white/10 p-1.5 border border-slate-100 dark:border-white/10">
                                <Logo src={p.logo} alt={p.label} className="w-full h-full object-contain" />
                            </div>
                            <span className={clsx('text-xs font-black', isActive ? 'text-indigo-600 dark:text-indigo-300' : isDone ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-500')}>
                                {isDone ? '✓ ' : ''}{p.label}
                            </span>
                        </motion.div>
                    );
                })}
            </div>

            <div className="space-y-2 max-w-md mx-auto">
                <div className="flex justify-between text-[10px] font-black text-slate-400 uppercase tracking-widest">
                    <span>Searching…</span>
                    <span>{elapsed}s</span>
                </div>
                <div className="w-full h-2 bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                        className="h-full bg-indigo-500"
                        initial={{ width: '0%' }}
                        animate={{ width: `${progress}%` }}
                    />
                </div>
            </div>
        </motion.div>
    );
}

const ResultsPage = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const location = useLocation();
    const query = searchParams.get('q') || '';

    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [statistics, setStatistics] = useState(null);
    const [uploadedImageUrl, setUploadedImageUrl] = useState(location.state?.uploadedImageUrl || '');
    const [page, setPage] = useState(1);
    const perPage = 20;
    const [pagination, setPagination] = useState({ total: 0, limit: perPage, offset: 0, has_more: false });
    const lastQueryRef = useRef('');

    const [isAlertModalOpen, setIsAlertModalOpen] = useState(false);
    const [selectedProduct, setSelectedProduct] = useState(null);
    const [alertLoading, setAlertLoading] = useState(false);
    const [alertTargetPrice, setAlertTargetPrice] = useState('');
    const [alertEmail, setAlertEmail] = useState('');
    const [alertSuccess, setAlertSuccess] = useState(false);
    const [isTrendModalOpen, setIsTrendModalOpen] = useState(false);
    const [trendProduct, setTrendProduct] = useState(null);
    const [comparedProducts, setComparedProducts] = useState(() => {
        const saved = localStorage.getItem('compareBasket');
        return saved ? JSON.parse(saved) : [];
    });

    useEffect(() => {
        localStorage.setItem('compareBasket', JSON.stringify(comparedProducts));
    }, [comparedProducts]);

    useEffect(() => {
        const loadPrediction = () => {
            try {
                // Priority 1: State from navigation
                if (location.state?.uploadedImageUrl) {
                    setUploadedImageUrl(location.state.uploadedImageUrl);
                    console.log('Got image from location state:', location.state.uploadedImageUrl);
                    return;
                }

                // Priority 2: History state safeguard
                if (window.history.state?.usr?.uploadedImageUrl) {
                    setUploadedImageUrl(window.history.state.usr.uploadedImageUrl);
                    return;
                }

                // Priority 3: Local storage fallback
                const lastPrediction = localStorage.getItem('last_prediction');
                if (lastPrediction) {
                    const data = JSON.parse(lastPrediction);
                    if (data.image_url) {
                        setUploadedImageUrl(data.image_url);
                    }
                }
            } catch (e) {
                console.error('Failed to load last prediction:', e);
            }
        };

        if (!query) return;
        loadPrediction();
        
        if (lastQueryRef.current !== query) {
            lastQueryRef.current = query;
            if (page !== 1) {
                setPage(1);
                return;
            }
        }
        fetchResults(query, page);
        
        window.addEventListener('storage', loadPrediction);
        return () => window.removeEventListener('storage', loadPrediction);
    }, [query, page, location.state]);

    const fetchResults = async (keyword, pageNum = 1) => {
        setLoading(true);
        setError(null);
        const offset = (pageNum - 1) * perPage;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000);

        try {
            const res = await fetch(
                `/api/compare-prices?product=${encodeURIComponent(keyword)}&limit=${perPage}&offset=${offset}&fast=true&async_mode=false`,
                { signal: controller.signal }
            );
            if (!res.ok) throw new Error(`Server error (${res.status})`);
            const data = await res.json();
            
            setProducts(data.products || []);
            setStatistics(data.statistics || null);
            setPagination(data.pagination || { total: 0, limit: perPage, offset, has_more: false });
            
        } catch (err) {
            setError(err.name === 'AbortError' ? 'Scan timed out' : err.message);
        } finally {
            clearTimeout(timeoutId);
            setLoading(false);
        }
    };

    const sortedProducts = useMemo(() =>
        [...products]
            .filter(p => parseFloat(p.price) > 0)
            .sort((a, b) => parseFloat(a.price) - parseFloat(b.price)),
        [products]
    );

    const handleSetAlertClick = (product) => {
        if (!localStorage.getItem('intelToken')) { navigate('/login'); return; }
        setSelectedProduct(product);
        setAlertTargetPrice(Math.round(parseFloat(product.price) * 0.9));
        setIsAlertModalOpen(true);
    };

    const handleAlertSubmit = async (e) => {
        e.preventDefault();
        setAlertLoading(true);
        try {
            await apiPost('/api/price-alert', {
                product_id: selectedProduct.product_url,
                product_name: selectedProduct.title,
                current_price: parseFloat(selectedProduct.price),
                target_price: parseFloat(alertTargetPrice)
            });
            setAlertSuccess(true);
            setTimeout(() => { setIsAlertModalOpen(false); setAlertSuccess(false); }, 2000);
        } catch (err) { alert(err.message); } finally { setAlertLoading(false); }
    };

    const handleAddToWishlist = async (product) => {
        if (!localStorage.getItem('intelToken')) { navigate('/navigate/login'); return; }
        try {
            await apiPost('/api/wishlist', {
                product_id: product.product_url,
                product_name: product.title,
                product_image: product.image_url,
                price: parseFloat(product.price),
                store: product.platform,
                product_link: product.product_url
            });
            alert('Added to wishlist!');
        } catch (err) { alert(err.message); }
    };

    const handleToggleCompare = (product) => {
        setComparedProducts(prev => {
            const exists = prev.find(p => p.product_url === product.product_url);
            if (exists) return prev.filter(p => p.product_url !== product.product_url);
            if (prev.length >= 4) return prev;
            return [...prev, product];
        });
    };

    const lowestPrice = parseFloat(sortedProducts[0]?.price) || 0;
    const highestPrice = parseFloat(sortedProducts[sortedProducts.length - 1]?.price) || 0;
    const savings = Math.max(0, highestPrice - lowestPrice);

    return (
        <div className="min-h-screen bg-white dark:bg-[#050810] transition-colors duration-500 relative flex flex-col">
            <header className="sticky top-0 z-50 bg-white/70 dark:bg-[#050810]/70 backdrop-blur-xl border-b border-slate-100 dark:border-white/5 px-6 py-4">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-6">
                        <button onClick={() => navigate(-1)} className="w-10 h-10 bg-slate-50 dark:bg-white/5 rounded-2xl flex items-center justify-center text-slate-500 hover:text-indigo-600 transition-all">
                            <ArrowLeft className="w-5 h-5" />
                        </button>
                        <div className="hidden sm:block">
                            <h1 className="text-xl font-black text-slate-900 dark:text-white font-outfit tracking-tight">Price Comparison Intelligence</h1>
                            <p className="text-[10px] font-black text-indigo-500 uppercase tracking-[0.2em]">Real-time market analysis</p>
                        </div>
                    </div>
                </div>
            </header>

            <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-12 grid lg:grid-cols-[320px_1fr] gap-12">
                <aside className="space-y-8">
                    <motion.div 
                        initial={{ opacity: 0, x: -30 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="glass-card p-8 rounded-[48px] bg-gradient-to-br from-indigo-600 to-violet-700 relative overflow-hidden shadow-2xl border border-white/20"
                    >
                        {/* Decorative background circle */}
                        <div className="absolute -top-24 -right-24 w-64 h-64 bg-white/10 rounded-full blur-3xl pointer-events-none" />
                        
                        <div className="relative z-10 space-y-6">
                            <div className="aspect-[4/3] rounded-[36px] overflow-hidden border-4 border-white/20 shadow-2xl relative bg-indigo-950/50 flex items-center justify-center group">
                                {/* Inner Glow */}
                                <div className="absolute inset-0 bg-gradient-to-tr from-indigo-500/10 to-transparent pointer-events-none" />
                                
                                {uploadedImageUrl ? (
                                    <img 
                                        src={uploadedImageUrl.startsWith('http') ? uploadedImageUrl : uploadedImageUrl.startsWith('/static') ? uploadedImageUrl : `/static/uploads/${uploadedImageUrl.split('/').pop()}`} 
                                        alt="Uploaded product" 
                                        className="w-full h-full object-contain p-4 transition-all duration-700 hover:scale-110 drop-shadow-[0_20px_60px_rgba(0,0,0,0.5)] z-10"
                                        onError={(e) => {
                                            console.error("AI Image failed to load:", uploadedImageUrl);
                                            // Final fallback: try just the filename if it looks like a path
                                            if (!e.target.dataset.retried) {
                                                e.target.dataset.retried = "true";
                                                const filename = uploadedImageUrl.split('/').pop();
                                                e.target.src = `/static/uploads/${filename}`;
                                            } else {
                                                e.target.style.opacity = '0';
                                                e.target.parentElement.classList.add('bg-indigo-900/40');
                                            }
                                        }}
                                    />
                                ) : (
                                    <div className="w-full h-full flex flex-col items-center justify-center text-white/20 gap-4">
                                        <div className="p-6 rounded-full bg-white/5 border border-white/10">
                                            <Package className="w-12 h-12 opacity-50" />
                                        </div>
                                        <span className="text-[10px] font-black uppercase tracking-[0.3em] opacity-40">Ready for Scan</span>
                                    </div>
                                )}
                                <div className="absolute top-4 left-4 z-20">
                                    <span className="px-3 py-1 bg-white/20 backdrop-blur-md rounded-full text-[8px] font-black text-white uppercase tracking-widest border border-white/10 flex items-center gap-1 shadow-lg">
                                        <Sparkles className="w-3 h-3 text-amber-300" /> AI Authenticated
                                    </span>
                                </div>
                            </div>
                            
                            <div className="space-y-2">
                                <h2 className="text-3xl font-black text-white font-outfit leading-tight capitalize">{query}</h2>
                                <p className="text-[11px] font-medium text-indigo-100/70 leading-relaxed font-outfit">
                                    Neural analysis multi-pattern matching successful across 2 major global index points.
                                </p>
                            </div>
                        </div>
                    </motion.div>

                    <div className="grid grid-cols-2 gap-4">
                        <motion.div 
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="p-5 rounded-[32px] bg-white dark:bg-white/5 border border-slate-100 dark:border-white/10 shadow-sm"
                        >
                            <p className="text-[8px] font-black text-slate-400 uppercase tracking-widest mb-1">Floor Price</p>
                            <p className="text-lg font-black text-slate-900 dark:text-white font-outfit">₹{formatPrice(lowestPrice)}</p>
                        </motion.div>
                        <motion.div 
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3 }}
                            className="p-5 rounded-[32px] bg-white dark:bg-white/5 border border-slate-100 dark:border-white/10 shadow-sm"
                        >
                            <p className="text-[8px] font-black text-slate-400 uppercase tracking-widest mb-1">Index Point</p>
                            <p className="text-lg font-black text-slate-900 dark:text-white font-outfit">₹{formatPrice(highestPrice)}</p>
                        </motion.div>
                    </div>

                    {savings > 0 && !loading && (
                        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="p-8 rounded-[40px] bg-emerald-500/10 border border-emerald-500/20 space-y-4">
                            <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">Potential Savings</p>
                            <p className="text-4xl font-black text-slate-900 dark:text-white font-outfit leading-none">₹{formatPrice(savings)}</p>
                            <div className="h-1 w-full bg-emerald-500/20 rounded-full overflow-hidden">
                                <motion.div initial={{ width: 0 }} animate={{ width: '100%' }} className="h-full bg-emerald-500" />
                            </div>
                        </motion.div>
                    )}
                </aside>

                <div className="space-y-8">
                    <AnimatePresence mode="wait">
                        {loading ? (
                            <ScanningLoader key="loading" query={query} image={uploadedImageUrl} />
                        ) : error ? (
                            <div className="py-20 text-center space-y-6">
                                <AlertCircle className="w-16 h-16 text-red-400 mx-auto" />
                                <h4 className="text-xl font-black text-slate-900 dark:text-white font-outfit">Scan Failed</h4>
                                <p className="text-slate-500 dark:text-slate-400">{error}</p>
                                <button onClick={() => fetchResults(query, page)} className="btn-primary px-8 py-4 rounded-2xl">Retry</button>
                            </div>
                        ) : sortedProducts.length === 0 ? (
                            <div className="py-24 text-center space-y-6 border-2 border-dashed border-slate-100 dark:border-white/10 rounded-[48px]">
                                <Package className="w-16 h-16 text-slate-200 dark:text-slate-700 mx-auto" />
                                <h4 className="text-xl font-black text-slate-900 dark:text-white font-outfit">No Results Found</h4>
                            </div>
                        ) : (
                            <div className="space-y-10">
                                {/* Best Value Hero - Neon Border Style */}
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="relative p-1 rounded-[44px] group"
                                >
                                    {/* Neon border gradient background */}
                                    <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 via-cyan-400 to-indigo-500 rounded-[44px] blur-sm opacity-50 group-hover:opacity-100 transition-opacity duration-500" />
                                    <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 via-cyan-400 to-indigo-500 rounded-[44px]" />
                                    
                                    <div className="relative bg-white dark:bg-[#0a1225] rounded-[41px] p-8 lg:p-10">
                                        <div className="flex flex-col md:flex-row gap-10 items-center">
                                            <div className="w-48 h-48 lg:w-56 lg:h-56 rounded-[36px] overflow-hidden bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/10 shrink-0 shadow-inner p-4">
                                                <img src={sortedProducts[0].image_url} alt="" className="w-full h-full object-contain" />
                                            </div>
                                            <div className="flex-1 text-center md:text-left space-y-6">
                                                <div className="flex justify-center md:justify-start items-center gap-3">
                                                    <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
                                                        <Sparkles className="w-3.5 h-3.5 text-emerald-500" />
                                                        <span className="text-[10px] font-black text-emerald-600 uppercase tracking-widest">Best Deal</span>
                                                    </div>
                                                    <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-indigo-500/10 border border-indigo-500/20 rounded-full">
                                                        <ShieldCheck className="w-3.5 h-3.5 text-indigo-500" />
                                                        <span className="text-[10px] font-black text-indigo-600 uppercase tracking-widest">Verified</span>
                                                    </div>
                                                </div>
                                                
                                                <h2 className="text-3xl lg:text-4xl font-black text-slate-900 dark:text-white font-outfit leading-tight">{sortedProducts[0].title}</h2>
                                                
                                                <div className="grid grid-cols-2 lg:grid-cols-2 gap-8 py-2">
                                                    <div>
                                                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Lowest Price</p>
                                                        <p className="text-4xl LG:text-5xl font-black text-emerald-600 dark:text-emerald-400 font-outfit tracking-tighter">₹{formatPrice(sortedProducts[0].price)}</p>
                                                    </div>
                                                    <div className="pl-8 border-l border-slate-100 dark:border-white/10">
                                                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Source</p>
                                                        <div className="flex items-center gap-3">
                                                            <div className="w-8 h-8 rounded-lg bg-slate-50 dark:bg-white/5 p-1.5 border border-slate-100 dark:border-white/10 flex items-center justify-center">
                                                                <Logo src={getStore(sortedProducts[0].platform).logo} alt={sortedProducts[0].platform} className="w-full h-full object-contain" />
                                                            </div>
                                                            <span className="text-2xl font-black text-slate-900 dark:text-white uppercase font-outfit tracking-wider">{sortedProducts[0].platform}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                                
                                                <div className="pt-4">
                                                    <motion.a 
                                                        href={sortedProducts[0].product_url} 
                                                        target="_blank" 
                                                        rel="noopener" 
                                                        whileHover={{ scale: 1.05, y: -2 }}
                                                        whileTap={{ scale: 0.95 }}
                                                        className="inline-flex items-center gap-4 px-12 py-5 bg-emerald-500 hover:bg-emerald-400 text-white rounded-[24px] text-xs font-black uppercase tracking-widest transition-all shadow-2xl shadow-emerald-500/40"
                                                    >
                                                        Claim Best Deal <ArrowRight className="w-5 h-5" />
                                                    </motion.a>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>

                                <div className="space-y-6">
                                    <div className="flex items-center justify-between px-6 py-4 bg-slate-50 dark:bg-white/5 rounded-[24px] border border-slate-100 dark:border-white/5">
                                        <div className="flex items-center gap-3">
                                            <Package className="w-5 h-5 text-slate-400" />
                                            <p className="text-xs font-black text-slate-800 dark:text-slate-200 uppercase tracking-wider">All Market Listings</p>
                                        </div>
                                        <p className="text-[10px] font-bold text-slate-400 uppercase">Ranked by price intelligence</p>
                                    </div>
                                    
                                    <div className="space-y-4">
                                        {sortedProducts.map((p, i) => (
                                            <StoreCard
                                                key={i}
                                                product={{
                                                    ...p,
                                                    onSetAlert: handleSetAlertClick,
                                                    onAddToWishlist: handleAddToWishlist,
                                                    onViewTrend: (p) => { setTrendProduct(p); setIsTrendModalOpen(true); },
                                                    onToggleCompare: handleToggleCompare,
                                                    isCompared: comparedProducts.some(cp => cp.product_url === p.product_url)
                                                }}
                                                isLowest={i === 0}
                                                index={i}
                                            />
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                    </AnimatePresence>
                </div>
            </main>

            {/* Modals & Overlays */}
            <AnimatePresence>
                {isAlertModalOpen && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-slate-900/60 backdrop-blur-sm" onClick={() => setIsAlertModalOpen(false)}>
                        <motion.div initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.9, y: 20 }} className="bg-white dark:bg-slate-900 w-full max-w-md rounded-[40px] p-8 shadow-2xl relative" onClick={(e) => e.stopPropagation()}>
                            {alertSuccess ? (
                                <div className="text-center py-8 space-y-4">
                                    <div className="w-16 h-16 bg-emerald-500 rounded-full flex items-center justify-center mx-auto text-white"><CheckCircle className="w-8 h-8" /></div>
                                    <h3 className="text-xl font-black text-slate-900 dark:text-white font-outfit">Alert Activated!</h3>
                                </div>
                            ) : (
                                <>
                                    <h3 className="text-2xl font-black text-slate-900 dark:text-white font-outfit mb-6">Set Price Alert</h3>
                                    <form onSubmit={handleAlertSubmit} className="space-y-4">
                                        <input type="number" required value={alertTargetPrice} onChange={(e) => setAlertTargetPrice(e.target.value)} placeholder="Target Price" className="w-full px-5 py-4 bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/10 rounded-2xl outline-none" />
                                        <input type="email" required value={alertEmail} onChange={(e) => setAlertEmail(e.target.value)} placeholder="Email" className="w-full px-5 py-4 bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/10 rounded-2xl outline-none" />
                                        <button type="submit" disabled={alertLoading} className="w-full btn-primary py-4 rounded-2xl font-black uppercase tracking-widest">Activate Alert</button>
                                    </form>
                                </>
                            )}
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            <Suspense fallback={null}>
                <ProductTrendModal isOpen={isTrendModalOpen} onClose={() => setIsTrendModalOpen(false)} productId={trendProduct?.product_url} productName={trendProduct?.title} />
            </Suspense>

            <ComparisonSelectionBar selectedItems={comparedProducts} onRemove={(url) => setComparedProducts(prev => prev.filter(p => p.product_url !== url))} onCompare={() => navigate('/compare')} />
        </div>
    );
};

export default ResultsPage;
