import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '');
    const cdnBase = (env.VITE_CDN_BASE || '').trim();

    return {
        // If you deploy static assets behind a CDN, set `VITE_CDN_BASE` to that origin/path.
        base: mode === 'production' && cdnBase ? cdnBase : '/',
        plugins: [react()],
        
        // ============================================================================
        // BUILD OPTIMIZATION
        // ============================================================================
        build: {
            target: 'esnext',
            minify: 'terser',
            terserOptions: {
                compress: {
                    drop_console: true,
                    drop_debugger: true
                },
                format: {
                    comments: false
                }
            },
            
            rollupOptions: {
                output: {
                    manualChunks: {
                        'vendors-react': ['react', 'react-dom', 'react-router-dom'],
                        'vendors-chart': ['chart.js', 'react-chartjs-2'],
                        'auth': ['./src/pages/AuthPage.jsx', './src/pages/ResetPasswordPage.jsx'],
                        'dashboard': ['./src/pages/DashboardPage.jsx'],
                        'comparison': ['./src/pages/ComparisonPage.jsx', './src/pages/ResultsPage.jsx'],
                        'profiles': ['./src/pages/ProfilePage.jsx', './src/pages/WishlistPage.jsx'],
                    },
                    entryFileNames: 'js/[name]-[hash].js',
                    chunkFileNames: 'js/[name]-[hash].js',
                    assetFileNames: (assetInfo) => {
                        const info = assetInfo.name.split('.');
                        const ext = info[info.length - 1];
                        
                        if (/png|jpe?g|gif|svg/.test(ext)) {
                            return `images/[name]-[hash][extname]`;
                        } else if (/woff|woff2|eot|ttf|otf/.test(ext)) {
                            return `fonts/[name]-[hash][extname]`;
                        } else if (ext === 'css') {
                            return `css/[name]-[hash][extname]`;
                        }
                        return `[name]-[hash][extname]`;
                    }
                }
            },
            cssCodeSplit: true,
            sourcemap: false,
            assetsInlineLimit: 4096,
            reportCompressedSize: true,
            chunkSizeWarningLimit: 1000,
        },
        
        // ============================================================================
        // SERVER CONFIGURATION
        // ============================================================================
        server: {
            watch: {
                usePolling: false,
            },
            proxy: {
                '/api/auth': { target: 'http://localhost:5001', changeOrigin: true },
                '/api/user': { target: 'http://localhost:5001', changeOrigin: true },
                '/api/wishlist': { target: 'http://localhost:5001', changeOrigin: true },
                '/api/search-history': { target: 'http://localhost:5001', changeOrigin: true },
                '/api/price-alert': { target: 'http://localhost:5001', changeOrigin: true },
                '/api/analytics': { target: 'http://localhost:5001', changeOrigin: true },
                '/api': { target: 'http://localhost:8001', changeOrigin: true },
                '/static': { target: 'http://localhost:8001', changeOrigin: true },
            },
        },
    }
})
