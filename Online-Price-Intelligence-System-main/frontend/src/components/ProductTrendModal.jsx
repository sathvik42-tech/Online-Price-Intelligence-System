import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, TrendingUp, AlertCircle, Clock, Loader2 } from 'lucide-react';
import { apiGet } from '../api';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

const ProductTrendModal = ({ isOpen, onClose, productId, productName }) => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (isOpen && productId) {
            fetchHistory();
        }
    }, [isOpen, productId]);

    const fetchHistory = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await apiGet(`/api/analytics/price-history?productId=${encodeURIComponent(productId)}`);
            setHistory(data || []);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const chartData = {
        labels: history.map(h => new Date(h.recorded_at).toLocaleDateString()),
        datasets: [
            {
                label: 'Market Price (₹)',
                data: history.map(h => parseFloat(h.price)),
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 3,
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
                tension: 0.4,
                fill: true,
            }
        ]
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false,
            },
            tooltip: {
                backgroundColor: '#0f172a',
                titleFont: { size: 12, weight: 'bold' },
                bodyFont: { size: 12 },
                padding: 12,
                cornerRadius: 12,
                displayColors: false,
                callbacks: {
                    label: (context) => `₹${context.parsed.y.toLocaleString('en-IN')}`
                }
            }
        },
        scales: {
            x: {
                grid: { display: false },
                ticks: { color: '#94a3b8', font: { size: 10, weight: '600' } }
            },
            y: {
                grid: { color: 'rgba(148, 163, 184, 0.1)', drawBorder: false },
                ticks: {
                    color: '#94a3b8',
                    font: { size: 10, weight: '600' },
                    callback: (value) => `₹${value.toLocaleString('en-IN')}`
                }
            }
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-[110] flex items-center justify-center p-6 bg-slate-900/60 backdrop-blur-sm"
                    onClick={onClose}
                >
                    <motion.div
                        initial={{ scale: 0.9, y: 20 }}
                        animate={{ scale: 1, y: 0 }}
                        exit={{ scale: 0.9, y: 20 }}
                        className="bg-white dark:bg-slate-900 w-full max-w-3xl rounded-[40px] p-8 shadow-2xl relative overflow-hidden flex flex-col max-h-[90vh]"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="flex justify-between items-start mb-8">
                            <div>
                                <div className="flex items-center gap-2 mb-1">
                                    <TrendingUp className="w-5 h-5 text-indigo-500" />
                                    <h3 className="text-2xl font-black text-slate-900 dark:text-white font-outfit tracking-tight">Price Analytics</h3>
                                </div>
                                <p className="text-xs font-black text-slate-400 uppercase tracking-widest leading-relaxed line-clamp-1 max-w-xl">
                                    {productName}
                                </p>
                            </div>
                            <button
                                onClick={onClose}
                                className="w-10 h-10 rounded-2xl bg-slate-50 dark:bg-white/5 flex items-center justify-center text-slate-400 hover:text-indigo-600 transition-all"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="flex-1 min-h-[400px] relative">
                            {loading ? (
                                <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
                                    <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
                                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Aggregating Historical Data...</p>
                                </div>
                            ) : error ? (
                                <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-8">
                                    <AlertCircle className="w-12 h-12 text-red-400 mb-4" />
                                    <h4 className="text-lg font-black text-slate-900 dark:text-white font-outfit mb-2">Analysis Failed</h4>
                                    <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">{error}</p>
                                    <button onClick={fetchHistory} className="btn-primary px-8 py-4 rounded-2xl text-[10px] uppercase font-black tracking-widest">Retry Scan</button>
                                </div>
                            ) : history.length < 2 ? (
                                <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-8">
                                    <Clock className="w-12 h-12 text-indigo-300 dark:text-indigo-900/50 mb-4" />
                                    <h4 className="text-xl font-black text-slate-900 dark:text-white font-outfit mb-2">Insufficient Intel</h4>
                                    <p className="text-sm text-slate-500 dark:text-slate-400 max-w-sm">
                                        We've just started tracking this product. Historical price curves will appear once more market data is captured.
                                    </p>
                                </div>
                            ) : (
                                <div className="h-full w-full">
                                    <Line data={chartData} options={chartOptions} />
                                </div>
                            )}
                        </div>

                        <div className="mt-8 pt-8 border-t border-slate-100 dark:border-white/5 flex items-center justify-between">
                            <div className="flex items-center gap-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                <span className="flex items-center gap-1.5 opacity-50"><TrendingUp className="w-3.5 h-3.5" /> 30-Day Window</span>
                                <span className="flex items-center gap-1.5 opacity-50"><Clock className="w-3.5 h-3.5" /> Real-time Indexing</span>
                            </div>
                            <p className="text-[10px] font-black text-indigo-500 uppercase tracking-widest">
                                System: Price Intelligence Engine v2.0
                            </p>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default ProductTrendModal;
