/**
 * Frontend Performance Monitoring
 *
 * Tracks:
 * - Page load time
 * - Component rendering time
 * - API response times
 * - Memory usage
 * - Core Web Vitals (LCP, FID, CLS)
 */

/**
 * Web Vitals Monitoring
 */
export const measureWebVitals = () => {
  // Largest Contentful Paint (LCP)
  const lcpObserver = new PerformanceObserver((list) => {
    const entries = list.getEntries();
    const lastEntry = entries[entries.length - 1];
    console.log('LCP (Largest Contentful Paint):', lastEntry.renderTime || lastEntry.loadTime);
  });
  
  lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

  // First Input Delay (FID)
  const fidObserver = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      console.log('FID (First Input Delay):', entry.processingDuration);
    }
  });
  
  fidObserver.observe({ entryTypes: ['first-input'] });

  // Cumulative Layout Shift (CLS)
  let clsValue = 0;
  const clsObserver = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      if (!entry.hadRecentInput) {
        clsValue += entry.value;
        console.log('CLS (Cumulative Layout Shift):', clsValue);
      }
    }
  });
  
  clsObserver.observe({ entryTypes: ['layout-shift'] });

  return {
    stop: () => {
      lcpObserver.disconnect();
      fidObserver.disconnect();
      clsObserver.disconnect();
    }
  };
};


/**
 * Page Load Performance Metrics
 */
export class PerformanceMonitor {
  constructor() {
    this.marks = {};
    this.measures = {};
  }

  // Mark time point
  mark(name) {
    performance.mark(name);
    this.marks[name] = performance.now();
  }

  // Measure interval between marks
  measure(name, startMark, endMark) {
    try {
      performance.measure(name, startMark, endMark);
      const measure = performance.getEntriesByName(name)[0];
      this.measures[name] = measure.duration;
      return measure.duration;
    } catch (e) {
      console.error(`Failed to measure ${name}:`, e);
      return null;
    }
  }

  // Get all navigation timings
  getNavigationMetrics() {
    const navigation = performance.getEntriesByType('navigation')[0];
    if (!navigation) return null;

    return {
      dns: navigation.domainLookupEnd - navigation.domainLookupStart,
      tcp: navigation.connectEnd - navigation.connectStart,
      ttfb: navigation.responseStart - navigation.requestStart,
      download: navigation.responseEnd - navigation.responseStart,
      domInteractive: navigation.domInteractive - navigation.fetchStart,
      domComplete: navigation.domComplete - navigation.fetchStart,
      loadComplete: navigation.loadEventEnd - navigation.fetchStart,
    };
  }

  // Get resource timing specifics
  getResourceMetrics() {
    const resources = performance.getEntriesByType('resource');
    return resources.reduce((acc, resource) => {
      acc[resource.name] = {
        duration: resource.duration,
        size: resource.transferSize,
        cached: resource.transferSize === 0,
      };
      return acc;
    }, {});
  }

  // Get paint timings
  getPaintMetrics() {
    const paints = performance.getEntriesByType('paint');
    return paints.reduce((acc, paint) => {
      acc[paint.name] = paint.startTime;
      return acc;
    }, {});
  }

  // Generate report
  generateReport() {
    return {
      navigation: this.getNavigationMetrics(),
      resources: this.getResourceMetrics(),
      paints: this.getPaintMetrics(),
      measures: this.measures,
    };
  }

  // Log summary
  logSummary() {
    const nav = this.getNavigationMetrics();
    if (nav) {
      console.group('Performance Metrics');
      console.log(`DNS: ${nav.dns.toFixed(2)}ms`);
      console.log(`TCP: ${nav.tcp.toFixed(2)}ms`);
      console.log(`TTFB: ${nav.ttfb.toFixed(2)}ms`);
      console.log(`Download: ${nav.download.toFixed(2)}ms`);
      console.log(`DOM Interactive: ${nav.domInteractive.toFixed(2)}ms`);
      console.log(`Page Load Complete: ${nav.loadComplete.toFixed(2)}ms`);
      console.groupEnd();
    }
  }
}


/**
 * React Hook for Performance Tracking
 */
export const usePerformanceMonitor = (componentName) => {
  React.useEffect(() => {
    const monitor = new PerformanceMonitor();
    monitor.mark(`${componentName}-start`);

    return () => {
      monitor.mark(`${componentName}-end`);
      const duration = monitor.measure(
        `${componentName}`,
        `${componentName}-start`,
        `${componentName}-end`
      );
      
      if (duration) {
        console.log(`${componentName} rendered in ${duration.toFixed(2)}ms`);
      }
    };
  }, [componentName]);
};


/**
 * API Call Performance Tracking
 */
export class APIPerformanceTracker {
  constructor() {
    this.calls = {};
  }

  startCall(url) {
    const timestamp = performance.now();
    this.calls[url] = this.calls[url] || [];
    this.calls[url].push({ start: timestamp });
  }

  endCall(url, status) {
    const timestamp = performance.now();
    if (this.calls[url] && this.calls[url].length > 0) {
      const lastCall = this.calls[url][this.calls[url].length - 1];
      lastCall.end = timestamp;
      lastCall.duration = timestamp - lastCall.start;
      lastCall.status = status;
      
      console.log(`API ${url}: ${lastCall.duration.toFixed(2)}ms (${status})`);
    }
  }

  getSummary(url) {
    if (!this.calls[url]) return null;

    const durations = this.calls[url].map(c => c.duration);
    return {
      calls: durations.length,
      min: Math.min(...durations),
      max: Math.max(...durations),
      avg: durations.reduce((a, b) => a + b, 0) / durations.length,
    };
  }

  getAllSummaries() {
    return Object.entries(this.calls).reduce((acc, [url, calls]) => {
      acc[url] = this.getSummary(url);
      return acc;
    }, {});
  }
}

// Global API tracker
export const apiTracker = new APIPerformanceTracker();


/**
 * Memory Usage Monitoring
 */
export const monitorMemory = () => {
  if (!performance.memory) {
    console.warn('Memory monitoring not available in this browser');
    return null;
  }

  const memory = performance.memory;
  const usage = {
    usedJSHeapSize: (memory.usedJSHeapSize / 1048576).toFixed(2),
    totalJSHeapSize: (memory.totalJSHeapSize / 1048576).toFixed(2),
    jsHeapSizeLimit: (memory.jsHeapSizeLimit / 1048576).toFixed(2),
    percentUsed: ((memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100).toFixed(2),
  };

  console.log('Memory Usage:', usage);
  return usage;
};


/**
 * Long Task Detection
 */
export const detectLongTasks = () => {
  if ('PerformanceObserver' in window) {
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          console.warn(`Long task detected: ${(entry.duration).toFixed(2)}ms`);
        }
      });

      observer.observe({ entryTypes: ['longtask'] });
      return observer;
    } catch {
      console.log('Long task observation not supported');
      return null;
    }
  }
};


/**
 * Session Replay Performance Helper
 * Captures performance issues for debugging
 */
export class PerformanceIssueReporter {
  constructor() {
    this.issues = [];
  }

  reportSlowComponent(componentName, duration, threshold = 1000) {
    if (duration > threshold) {
      this.issues.push({
        type: 'slow_component',
        component: componentName,
        duration,
        timestamp: new Date().toISOString(),
      });
    }
  }

  reportSlowAPI(url, duration, threshold = 3000) {
    if (duration > threshold) {
      this.issues.push({
        type: 'slow_api',
        url,
        duration,
        timestamp: new Date().toISOString(),
      });
    }
  }

  reportHighMemory(percentUsed, threshold = 80) {
    if (percentUsed > threshold) {
      this.issues.push({
        type: 'high_memory',
        percentUsed,
        timestamp: new Date().toISOString(),
      });
    }
  }

  sendToServer(endpoint) {
    if (this.issues.length > 0) {
      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          issues: this.issues,
          userAgent: navigator.userAgent,
          timestamp: new Date().toISOString(),
        })
      }).catch(err => console.error('Failed to report issues:', err));
    }
  }

  getIssues() {
    return this.issues;
  }

  clear() {
    this.issues = [];
  }
}


export const issueReporter = new PerformanceIssueReporter();


export default {
  measureWebVitals,
  PerformanceMonitor,
  usePerformanceMonitor,
  APIPerformanceTracker,
  apiTracker,
  monitorMemory,
  detectLongTasks,
  PerformanceIssueReporter,
  issueReporter,
};
