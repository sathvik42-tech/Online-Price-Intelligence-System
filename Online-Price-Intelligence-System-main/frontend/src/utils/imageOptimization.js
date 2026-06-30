/**
 * Image Optimization Utilities
 *
 * Features:
 * - Responsive image sizing
 * - WebP format with fallback
 * - Lazy loading with Intersection Observer
 * - Progressive image loading
 * - Image compression hints
 */

export const ImageOptimization = {
  /**
   * Generate optimized image URLs for different screen sizes
   * Use with <picture> and <source> elements
   */
  getResponsiveImageSources: (baseUrl, productName) => {
    // Replace with your CDN URL or image optimization service
    const cdnUrl = process.env.REACT_APP_CDN_URL || process.env.REACT_APP_API_URL;
    
    return {
      // WebP format (best compression, modern browsers)
      webp: {
        small: `${cdnUrl}/images/webp/${productName}_300w.webp`,
        medium: `${cdnUrl}/images/webp/${productName}_600w.webp`,
        large: `${cdnUrl}/images/webp/${productName}_1200w.webp`,
      },
      // JPEG fallback
      jpeg: {
        small: `${cdnUrl}/images/jpg/${productName}_300w.jpg`,
        medium: `${cdnUrl}/images/jpg/${productName}_600w.jpg`,
        large: `${cdnUrl}/images/jpg/${productName}_1200w.jpg`,
      }
    };
  },

  /**
   * Get srcSet string for responsive images
   * Usage: <img srcSet={getSrcSet(url)} sizes="..." />
   */
  getSrcSet: (baseUrl) => {
    return `
      ${baseUrl}_300w.jpg 300w,
      ${baseUrl}_600w.jpg 600w,
      ${baseUrl}_1200w.jpg 1200w
    `.trim();
  },

  /**
   * Generate CDN image URL with optimization parameters
   * Assumes CDN supports query parameters (adjust for your provider)
   */
  getOptimizedUrl: (url, options = {}) => {
    const {
      width,
      height,
      quality = 80,
      format = 'auto', // auto, webp, jpg, png
      fit = 'cover'
    } = options;

    // Example for Cloudinary-style parameters
    const params = new URLSearchParams({
      w: width,
      h: height,
      q: quality,
      f: format,
      fit: fit
    });

    return `${url}?${params.toString()}`;
  },

  /**
   * Get blur-up placeholder while image loads
   * Creates LQIP (Low Quality Image Placeholder)
   */
  getPlaceholder: (color = '#f0f0f0') => {
    // Inline minimal SVG placeholder
    return `data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"%3E%3Crect fill="%23${color.replace('#', '')}"/%3E%3C/svg%3E`;
  },

  /**
   * Configuration for lazy loading images
   * Use with Intersection Observer
   */
  lazyLoadConfig: {
    rootMargin: '50px', // Start loading 50px before image enters viewport
    threshold: 0.01
  }
};


/**
 * Intersection Observer Hook for lazy loading
 * Loads images when they approach viewport
 */
export const useIntersectionObserver = (ref, threshold = 0.01) => {
  const [isVisible, setIsVisible] = React.useState(false);

  React.useEffect(() => {
    if (!ref.current) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          // Stop observing once loaded
          observer.unobserve(entry.target);
        }
      },
      {
        threshold,
        rootMargin: '50px' // Start loading 50px before visible
      }
    );

    observer.observe(ref.current);
    
    return () => observer.disconnect();
  }, [ref, threshold]);

  return isVisible;
};


/**
 * Lazy Loading Image Component
 *
 * Usage:
 * <LazyImage
 *   src="image.jpg"
 *   alt="Product"
 *   width={300}
 *   height={200}
 * />
 */
export const LazyImage = ({ 
  src, 
  alt, 
  width, 
  height,
  className = '',
  placeholder = true,
  onLoad = () => {}
}) => {
  const [imageSrc, setImageSrc] = React.useState(placeholder ? null : src);
  const [imageRef, setImageRef] = React.useState();
  const isVisible = useIntersectionObserver(imageRef);

  React.useEffect(() => {
    if (!isVisible && placeholder) return;

    const img = new Image();
    img.src = src;
    img.onload = () => {
      setImageSrc(src);
      onLoad();
    };
    img.onerror = () => {
      console.error(`Failed to load image: ${src}`);
      setImageSrc(src); // Still show it on error
    };
  }, [src, isVisible, placeholder, onLoad]);

  return (
    <img
      ref={setImageRef}
      src={imageSrc || ImageOptimization.getPlaceholder()}
      alt={alt}
      width={width}
      height={height}
      className={`${className} ${imageSrc ? 'loaded' : 'lazy-loading'}`}
      loading="lazy"
      decoding="async"
      style={{
        opacity: imageSrc ? 1 : 0.7,
        transition: 'opacity 0.3s ease-in'
      }}
    />
  );
};


/**
 * Progressive Image Loading Component
 * Loads low-quality first, then high-quality
 */
export const ProgressiveImage = ({
  placeholderSrc,
  src,
  alt,
  width,
  height,
  className = ''
}) => {
  const [imageSrc, setImageSrc] = React.useState(placeholderSrc);
  const [imageRef, setImageRef] = React.useState();
  const isVisible = useIntersectionObserver(imageRef);

  React.useEffect(() => {
    if (!isVisible) return;

    const img = new Image();
    img.src = src;
    img.onload = () => setImageSrc(src);
  }, [src, isVisible]);

  return (
    <img
      ref={setImageRef}
      src={imageSrc}
      alt={alt}
      width={width}
      height={height}
      className={className}
      loading="lazy"
      decoding="async"
      style={{
        filter: imageSrc === placeholderSrc ? 'blur(10px)' : 'none',
        transition: 'filter 0.3s ease-in'
      }}
    />
  );
};


/**
 * Responsive Image Component using <picture> element
 * Automatically serves optimal format (WebP or JPEG)
 */
export const ResponsiveImage = ({
  src,
  alt,
  width,
  height,
  className = ''
}) => {
  const imageRef = React.useRef();
  const isVisible = useIntersectionObserver(imageRef);

  const sources = ImageOptimization.getResponsiveImageSources(src, alt);

  return (
    <picture ref={imageRef}>
      {/* WebP format for modern browsers */}
      <source 
        srcSet={sources.webp.small}
        media="(max-width: 480px)"
        type="image/webp"
      />
      <source 
        srcSet={sources.webp.medium}
        media="(max-width: 1024px)"
        type="image/webp"
      />
      <source 
        srcSet={sources.webp.large}
        type="image/webp"
      />

      {/* JPEG fallback */}
      <source 
        srcSet={sources.jpeg.small}
        media="(max-width: 480px)"
      />
      <source 
        srcSet={sources.jpeg.medium}
        media="(max-width: 1024px)"
      />
      <source 
        srcSet={sources.jpeg.large}
      />

      <img
        src={sources.jpeg.medium}
        alt={alt}
        width={width}
        height={height}
        className={className}
        loading="lazy"
        decoding="async"
      />
    </picture>
  );
};


export default ImageOptimization;
