import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { Upload, X, Loader, Search, ShoppingBag, Sparkles, ImageIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

const QUICK_SEARCHES = ['Apple iPhone 16', 'Niacinamide Serum', 'Dyson Airwrap', 'Bosch Dishwasher', 'Sony Headphones'];

const UploadPage = () => {
    const navigate = useNavigate();
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [editableLabel, setEditableLabel] = useState('');

    const getTimeGreeting = () => {
        const hour = new Date().getHours();
        if (hour < 12) return 'Good Morning!';
        if (hour < 18) return 'Good Afternoon!';
        return 'Good Evening!';
    };

    const onDrop = useCallback((acceptedFiles) => {
        const selectedFile = acceptedFiles[0];
        if (selectedFile) {
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
            setResults(null);
            setEditableLabel('');
            setError(null);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'image/*': [] },
        multiple: false,
    });

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        setError(null);
        const formData = new FormData();
        formData.append('file', file);
        try {
            const response = await fetch('/api/predict', { method: 'POST', body: formData });
            if (!response.ok) throw new Error('Failed to analyze image. Please try again.');
            const data = await response.json();
            setResults(data);

            // Persist the prediction results for the ResultsPage
            localStorage.setItem('last_prediction', JSON.stringify(data));

            // Prefer top_search_query (clean product name); fallback to label
            let finalLabel = '';
            if (data.top_search_query) {
                finalLabel = data.top_search_query;
            } else if (data.predictions?.length > 0) {
                const raw = data.predictions[0].search_query || data.predictions[0].label;
                finalLabel = raw.replace(/_/g, ' ');
            }
            setEditableLabel(finalLabel);

            // AUTO-REDIRECT: If we have a successful identification, go to results immediately
            if (finalLabel) {
                setTimeout(() => {
                    navigate(`/results?q=${encodeURIComponent(finalLabel)}`, {
                        state: {
                            uploadedImageUrl: data.image_url,
                            task_id: data.task_id
                        }
                    });
                }, 800); // Small delay so user sees the "Identification Result" briefly
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setUploading(false);
        }

    };

    const suggestionQueries = (results?.predictions || [])
        .map(p => (p?.search_query || p?.label || '').replace(/_/g, ' ').trim())
        .filter(Boolean)
        // dedupe while keeping order
        .filter((q, idx, arr) => arr.findIndex(x => x.toLowerCase() === q.toLowerCase()) === idx)
        .slice(0, 3);

    const clearFile = () => {
        setFile(null);
        setPreview(null);
        setResults(null);
        setError(null);
    };

    return (
        <div className="min-h-screen bg-[#f8faff] dark:bg-[#0a0f1e] transition-colors duration-500 relative overflow-hidden">
            {/* Background blobs */}
            <div className="pointer-events-none absolute inset-0 overflow-hidden">
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-violet-400/10 dark:bg-violet-600/5 rounded-full blur-3xl translate-x-1/2 -translate-y-1/4" />
                <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-blue-400/10 dark:bg-blue-600/5 rounded-full blur-3xl -translate-x-1/3 translate-y-1/4" />
            </div>

            <div className="relative max-w-3xl mx-auto px-6 py-20 text-center">

                {/* Greeting */}
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-10"
                >
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-50 dark:bg-blue-900/30 border border-blue-100 dark:border-blue-800/50 rounded-full mb-4">
                        <Sparkles className="w-3.5 h-3.5 text-blue-500" />
                        <span className="text-[10px] font-black text-blue-600 dark:text-blue-400 uppercase tracking-[0.2em]">AI-Powered</span>
                    </div>
                    <h1 className="text-4xl md:text-5xl font-black text-gray-900 dark:text-white tracking-tight mb-2">
                        {getTimeGreeting()}
                    </h1>
                    <p className="text-lg text-gray-500 dark:text-gray-400 font-medium max-w-xl mx-auto">
                        Ready to find the{' '}
                        <span className="gradient-text font-bold">lowest price</span>? Upload a photo and let our intelligence system handle the rest.
                    </p>
                </motion.div>

                <div className="space-y-8">
                    {/* Upload / Results Card */}
                    <AnimatePresence mode="wait">
                        {!results ? (
                            <motion.div
                                key="upload"
                                initial={{ opacity: 0, scale: 0.96 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.96 }}
                                {...getRootProps()}
                                className={clsx(
                                    'relative mx-auto max-w-lg aspect-video rounded-[32px] border-2 border-dashed flex flex-col items-center justify-center cursor-pointer transition-all duration-300 group overflow-hidden',
                                    isDragActive
                                        ? 'border-blue-400 bg-blue-50/80 dark:bg-blue-900/20 animate-pulse-glow'
                                        : 'border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 hover:border-blue-400 hover:bg-blue-50/30 dark:hover:bg-blue-900/10',
                                    preview ? 'border-solid border-blue-300 dark:border-blue-700' : ''
                                )}
                            >
                                <input {...getInputProps()} />
                                {/* Glow on hover */}
                                <div className="absolute inset-0 rounded-[32px] opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-br from-blue-400/5 to-violet-400/5 pointer-events-none" />

                                {preview ? (
                                    <div className="w-full h-full relative group/preview">
                                        <img src={preview} alt="Preview" className="w-full h-full object-cover" />
                                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover/preview:opacity-100 transition-opacity flex items-center justify-center">
                                            <div className="bg-white/90 rounded-2xl px-5 py-3 text-sm font-bold text-gray-900">
                                                Click or drag to change
                                            </div>
                                        </div>
                                        <button
                                            onClick={(e) => { e.stopPropagation(); clearFile(); }}
                                            className="absolute top-3 right-3 p-1.5 bg-white/90 dark:bg-gray-900/90 rounded-full shadow-lg text-red-500 hover:bg-red-50 transition-colors z-10"
                                        >
                                            <X className="w-4 h-4" />
                                        </button>
                                    </div>
                                ) : (
                                    <div className="p-8 text-center space-y-4">
                                        <div className="w-20 h-20 bg-blue-50 dark:bg-blue-900/30 rounded-3xl flex items-center justify-center mx-auto group-hover:scale-110 group-hover:bg-blue-100 dark:group-hover:bg-blue-800/40 transition-all duration-500 border border-blue-100 dark:border-blue-800/50">
                                            {isDragActive
                                                ? <ImageIcon className="w-8 h-8 text-blue-500 animate-bounce" />
                                                : <Upload className="w-8 h-8 text-blue-400 group-hover:text-blue-500 transition-colors" />
                                            }
                                        </div>
                                        <div>
                                            <p className="text-base font-bold text-gray-900 dark:text-white">
                                                {isDragActive ? 'Drop it here!' : 'Upload Product Photo'}
                                            </p>
                                            <p className="text-xs text-gray-400 mt-1 font-medium">
                                                Drag & drop or click — PNG, JPG, WEBP supported
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </motion.div>
                        ) : (
                            <motion.div
                                key="results"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className="bg-white dark:bg-white/5 rounded-[36px] p-8 shadow-2xl shadow-black/5 border border-gray-100 dark:border-white/10 relative"
                            >
                                <button
                                    onClick={clearFile}
                                    className="absolute top-4 right-4 w-8 h-8 bg-gray-100 dark:bg-white/10 rounded-full flex items-center justify-center text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                                <div className="flex flex-col items-center gap-6">
                                    <div className="relative">
                                        <div className="w-36 h-36 rounded-3xl overflow-hidden shadow-xl ring-4 ring-blue-100 dark:ring-blue-900/50">
                                            <img src={preview} alt="Analysed" className="w-full h-full object-cover" />
                                        </div>
                                        <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-gradient-to-br from-blue-500 to-violet-500 rounded-full flex items-center justify-center shadow-lg">
                                            <Sparkles className="w-4 h-4 text-white" />
                                        </div>
                                    </div>
                                    <div className="w-full max-w-md space-y-2">
                                        <p className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] text-center">
                                            AI Identification Result
                                        </p>
                                        <div className="relative">
                                            <span className="absolute left-5 top-1/2 -translate-y-1/2 text-blue-500">
                                                <Search className="w-4 h-4" />
                                            </span>
                                            <input
                                                type="text"
                                                value={editableLabel}
                                                onChange={(e) => setEditableLabel(e.target.value)}
                                                className="w-full pl-12 pr-4 py-4 bg-gray-50 dark:bg-white/5 border border-gray-100 dark:border-white/10 rounded-2xl text-center text-lg font-bold text-gray-900 dark:text-white glow-ring transition-all capitalize"
                                                placeholder="What is this product?"
                                            />
                                        </div>
                                        <p className="text-xs text-gray-400 text-center">Not quite right? Edit the label above.</p>

                                        {suggestionQueries.length > 0 && (
                                            <div className="pt-2 flex flex-wrap justify-center gap-2">
                                                {suggestionQueries.map((q) => (
                                                    <button
                                                        key={q}
                                                        type="button"
                                                        onClick={() => setEditableLabel(q)}
                                                        className="px-3 py-1.5 rounded-full text-[11px] font-black uppercase tracking-widest border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 text-gray-600 dark:text-gray-300 hover:border-blue-400 hover:text-blue-600 dark:hover:text-blue-300 transition-all"
                                                        title="Use this suggestion"
                                                    >
                                                        {q}
                                                    </button>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Action Button */}
                    <div className="max-w-md mx-auto space-y-3">
                        {!results ? (
                            <button
                                onClick={handleUpload}
                                disabled={!file || uploading}
                                className={clsx(
                                    'w-full py-4 rounded-2xl font-black text-sm uppercase tracking-widest text-white shadow-lg transition-all flex items-center justify-center gap-3 active:scale-95',
                                    !file
                                        ? 'bg-gray-200 dark:bg-white/10 text-gray-400 cursor-not-allowed'
                                        : uploading
                                            ? 'bg-gray-700 dark:bg-white/20'
                                            : 'btn-primary'
                                )}
                            >
                                {uploading ? (
                                    <>
                                        <Loader className="w-4 h-4 animate-spin" /> Analysing Image...
                                    </>
                                ) : (
                                    <>
                                        <Sparkles className="w-4 h-4" /> Identify Product
                                    </>
                                )}
                            </button>
                        ) : (
                            <button
                                onClick={() => navigate(`/results?q=${encodeURIComponent(editableLabel)}`, {
                                    state: {
                                        uploadedImageUrl: results?.image_url,
                                        task_id: results?.task_id
                                    }
                                })}
                                className="w-full py-4 btn-primary rounded-2xl font-black text-sm uppercase tracking-widest shadow-xl flex items-center justify-center gap-3 active:scale-95"
                            >
                                <ShoppingBag className="w-4 h-4" /> Analyse Market Prices
                            </button>
                        )}

                        {error && (
                            <motion.div
                                initial={{ opacity: 0, y: 8 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="p-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-2xl text-xs font-bold border border-red-100 dark:border-red-800/50"
                            >
                                {error}
                            </motion.div>
                        )}
                    </div>

                    {/* Quick Searches */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                        className="space-y-4"
                    >
                        <p className="text-xs font-bold text-gray-400 dark:text-gray-500 tracking-widest uppercase text-center">
                            Or search directly
                        </p>
                        <div className="flex flex-wrap justify-center gap-2.5">
                            {QUICK_SEARCHES.map(item => (
                                <button
                                    key={item}
                                    onClick={() => navigate(`/results?q=${encodeURIComponent(item)}`)}
                                    className="px-5 py-2.5 bg-white dark:bg-white/5 rounded-full border border-gray-200 dark:border-white/10 text-sm font-semibold text-gray-600 dark:text-gray-400 hover:border-blue-400 hover:text-blue-500 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all shadow-sm"
                                >
                                    {item}
                                </button>
                            ))}
                        </div>
                    </motion.div>

                    {/* Trending Section */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.7 }}
                        className="mt-16 space-y-6 text-left"
                    >
                        <div>
                            <h2 className="text-xl font-black text-gray-900 dark:text-white tracking-tight">Trending Now</h2>
                            <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">Most searched products this week</p>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {[
                                { photo: '1523275335684-37898b6baf30', label: 'Wearables' },
                                { photo: '1498050108023-c5249f4df085', label: 'Electronics' },
                                { photo: 'beauty_premium', label: 'Beauty', localSrc: '/images/beauty_category.png' },
                                { photo: '1549298916-b41d501d3772', label: 'Footwear' },
                            ].map((item, i) => (
                                <div
                                    key={i}
                                    className="aspect-[4/5] bg-gray-100 dark:bg-white/5 rounded-3xl overflow-hidden group cursor-pointer relative"
                                    onClick={() => navigate(`/results?q=${encodeURIComponent(item.label)}`)}
                                >
                                    <img
                                        src={item.localSrc || `https://images.unsplash.com/photo-${item.photo}?auto=format&fit=crop&q=80&w=300`}
                                        alt={item.label}
                                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                                    />
                                    <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/10 to-transparent flex items-end p-5">
                                        <p className="text-white font-black text-xs uppercase tracking-widest">{item.label}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </motion.div>
                </div>
            </div>
        </div>
    );
};

export default UploadPage;
