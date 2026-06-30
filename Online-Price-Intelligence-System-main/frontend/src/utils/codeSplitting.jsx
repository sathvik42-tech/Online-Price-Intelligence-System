/**
 * Code Splitting and Lazy Loading Utilities
 *
 * Features:
 * - React.lazy for component code splitting
 * - Suspense boundaries with loading states
 * - Dynamic imports
 * - Performance monitoring
 */

import React, { Suspense, lazy } from 'react';

/**
 * Lazy Loading Wrapper Component
 * Provides loading state while code chunk loads
 */
export const LazyLoadSection = ({ 
  component: Component, 
  loading = <div className="loading">Loading...</div>,
  error = <div className="error">Failed to load</div>,
  delay = 200
}) => {
  return (
    <Suspense fallback={loading}>
      <ErrorBoundary fallback={error}>
        <Component />
      </ErrorBoundary>
    </Suspense>
  );
};


/**
 * Error Boundary for lazy loaded components
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Lazy loading error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <div>Failed to load component</div>;
    }

    return this.props.children;
  }
}


/**
 * Lazy loaded pages (heavy components)
 * These are loaded on-demand, not on initial page load
 */
export const lazyPages = {
  // Heavy components split into separate chunks
  DashboardPage: lazy(() => import('../pages/DashboardPage')),
  ResultsPage: lazy(() => import('../pages/ResultsPage')),
  ComparisonPage: lazy(() => import('../pages/ComparisonPage')),
  WishlistPage: lazy(() => import('../pages/WishlistPage')),
  SearchHistoryPage: lazy(() => import('../pages/SearchHistoryPage')),
  ProfilePage: lazy(() => import('../pages/ProfilePage')),
  
  // Charts and analytics (heavy)
  ProductTrendModal: lazy(() => import('../components/ProductTrendModal')),
  AnalyticsSection: lazy(() => import('../components/AnalyticsSection')),
  RecommendationsSection: lazy(() => import('../components/RecommendationsSection')),
};


/**
 * Lazy load component on demand
 * Usage: const MyComponent = useLazyLoad(() => import('./MyComponent'));
 */
export const useLazyLoad = (importFn) => {
  return lazy(importFn);
};


/**
 * Dynamic imports with retry logic
 * Useful for handling CDN failures
 */
export const dynamicImportWithRetry = (importFn, maxRetries = 3) => {
  return lazy(async () => {
    let lastError;
    
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await importFn();
      } catch (error) {
        lastError = error;
        
        // Wait before retrying (exponential backoff)
        await new Promise(resolve => 
          setTimeout(resolve, Math.pow(2, i) * 1000)
        );
      }
    }
    
    throw lastError;
  });
};


/**
 * Intersection Observer Hook for component visibility
 * Load component only when visible in viewport
 */
export const useComponentVisibility = (ref) => {
  const [isVisible, setIsVisible] = React.useState(false);

  React.useEffect(() => {
    if (!ref.current) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(entry.target);
        }
      },
      {
        threshold: 0.1,
        rootMargin: '50px'
      }
    );

    observer.observe(ref.current);

    return () => observer.disconnect();
  }, [ref]);

  return isVisible;
};


/**
 * Viewport-based Lazy Component Loader
 * Only loads component when it enters viewport
 */
export const LazyComponentLoader = ({ 
  component: Component,
  fallback = <div className="loading">Loading...</div>,
  errorFallback = <div>Error loading component</div>
}) => {
  const ref = React.useRef();
  const isVisible = useComponentVisibility(ref);

  return (
    <div ref={ref}>
      {isVisible ? (
        <Suspense fallback={fallback}>
          <ErrorBoundary fallback={errorFallback}>
            <Component />
          </ErrorBoundary>
        </Suspense>
      ) : (
        fallback
      )}
    </div>
  );
};


/**
 * Performance metrics for lazy loading
 */
export class LazyLoadingMetrics {
  constructor() {
    this.metrics = {};
  }

  startTimer(componentName) {
    this.metrics[componentName] = {
      startTime: performance.now()
    };
  }

  endTimer(componentName) {
    if (this.metrics[componentName]) {
      this.metrics[componentName].endTime = performance.now();
      this.metrics[componentName].duration = 
        this.metrics[componentName].endTime - 
        this.metrics[componentName].startTime;
      
      console.log(`${componentName} loaded in ${this.metrics[componentName].duration.toFixed(2)}ms`);
    }
  }

  getMetrics(componentName) {
    return this.metrics[componentName] || null;
  }

  getAllMetrics() {
    return this.metrics;
  }

  clear() {
    this.metrics = {};
  }
}


/**
 * React hooks for performance monitoring
 */
export const useComponentLoadingTime = (componentName) => {
  const metrics = new LazyLoadingMetrics();

  React.useEffect(() => {
    metrics.startTimer(componentName);
    
    return () => {
      metrics.endTimer(componentName);
    };
  }, [componentName, metrics]);
};


/**
 * Prefetch component to warm up cache
 * Use before user navigates to component
 */
export const prefetchComponent = (importFn) => {
  importFn()
    .then(() => console.log('Component prefetched'))
    .catch(err => console.error('Prefetch failed:', err));
};


/**
 * Loading spinner component
 * Shows while code chunk loads
 */
export const LoadingSpinner = ({ size = 'medium' }) => (
  <div className={`loading-spinner ${size}`}>
    <div className="spinner" />
    <p>Loading...</p>
  </div>
);


/**
 * Error fallback component
 */
export const ErrorFallback = ({ error = null }) => (
  <div className="error-container">
    <h3>Failed to load component</h3>
    {error && <p>{error.message}</p>}
    <button onClick={() => window.location.reload()}>
      Reload page
    </button>
  </div>
);


/**
 * Code splitting configuration helper
 * Use in Vite config or webpack
 */
export const codeSplittingConfig = {
  // Entry points for code splitting
  chunks: {
    vendor: ["react", "react-dom"],
    charts: ["react-chartjs-2", "chart.js"],
    ui: ["@mui/material"],
  },
  
  // Min chunk size (bytes)
  minChunkSize: 20000,
  
  // Route-based chunks
  routeChunks: {
    dashboard: "pages/DashboardPage",
    results: "pages/ResultsPage",
    comparison: "pages/ComparisonPage",
    wishlist: "pages/WishlistPage",
    profile: "pages/ProfilePage",
  }
};


export default {
  LazyLoadSection,
  LazyComponentLoader,
  ErrorBoundary,
  lazyPages,
  useLazyLoad,
  dynamicImportWithRetry,
  useComponentVisibility,
  LazyLoadingMetrics,
  useComponentLoadingTime,
  prefetchComponent,
  LoadingSpinner,
  ErrorFallback,
};
