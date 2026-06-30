import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { BrowserRouter } from 'react-router-dom'
import ErrorBoundary from './ErrorBoundary.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <ErrorBoundary>
            <BrowserRouter>
                <App />
            </BrowserRouter>
        </ErrorBoundary>
    </React.StrictMode>,
)

// Lightweight frontend profiling (dev-only): basic navigation timing from the Performance API.
if (import.meta.env.DEV) {
    window.addEventListener('load', () => {
        try {
            const nav = performance.getEntriesByType('navigation')?.[0];
            if (!nav) return;
            // These help spot regressions quickly during development.
            console.log('[perf] ttfb_ms=', Math.round(nav.responseStart - nav.requestStart));
            console.log('[perf] dom_content_loaded_ms=', Math.round(nav.domContentLoadedEventEnd));
            console.log('[perf] load_ms=', Math.round(nav.loadEventEnd));
        } catch {
            // ignore
        }
    });
}
