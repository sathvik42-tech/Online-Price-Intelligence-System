"""
Image Optimization Module for Backend

Features:
- Image compression (JPEG, PNG, WebP)
- Responsive image generation (multiple sizes)
- Thumbnail generation
- Format conversion
- Metadata optimization
"""

import logging
from PIL import Image
from io import BytesIO
import os
from pathlib import Path
from typing import Dict, Tuple
import hashlib

logger = logging.getLogger(__name__)


class ImageOptimizer:
    """Optimize images for web delivery"""
    
    # Standard responsive sizes (in pixels)
    RESPONSIVE_SIZES = {
        'thumbnail': (150, 150),
        'small': (300, 300),
        'medium': (600, 600),
        'large': (1200, 900),
    }
    
    # Compression quality for different formats
    QUALITY_SETTINGS = {
        'JPEG': 80,
        'WebP': 80,
        'PNG': 95,
    }
    
    def __init__(self, upload_dir: str = None):
        self.upload_dir = upload_dir or 'backend/static/uploads'
        self.optimized_dir = os.path.join(self.upload_dir, 'optimized')
        
        # Create directories if needed
        os.makedirs(self.optimized_dir, exist_ok=True)
    
    def optimize_image(self, image_path: str) -> Dict[str, str]:
        """
        Optimize image to multiple sizes and formats
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict with URLs to optimized versions
        """
        try:
            image = Image.open(image_path)
            
            # Get image name without extension
            base_name = Path(image_path).stem
            results = {}
            
            # Generate multiple sizes
            for size_name, dimensions in self.RESPONSIVE_SIZES.items():
                # JPEG version
                jpeg_path = self._save_optimized(
                    image, dimensions, base_name, size_name, 'jpeg'
                )
                results[f'{size_name}_jpeg'] = jpeg_path
                
                # WebP version (better compression)
                webp_path = self._save_optimized(
                    image, dimensions, base_name, size_name, 'webp'
                )
                results[f'{size_name}_webp'] = webp_path
            
            logger.info(f"Image optimized successfully: {base_name}")
            return results
            
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return {}
    
    def _save_optimized(
        self,
        image: Image.Image,
        size: Tuple[int, int],
        base_name: str,
        size_name: str,
        format: str
    ) -> str:
        """Save optimized image version"""
        try:
            # Resize image
            img_resized = image.copy()
            img_resized.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Add padding if needed to maintain aspect ratio
            if img_resized.size != size:
                new_image = Image.new('RGB', size, (255, 255, 255))
                offset = (
                    (size[0] - img_resized.size[0]) // 2,
                    (size[1] - img_resized.size[1]) // 2
                )
                new_image.paste(img_resized, offset)
                img_resized = new_image
            
            # Save with optimization
            ext = 'webp' if format == 'webp' else format
            filename = f"{base_name}_{size_name}.{ext}"
            filepath = os.path.join(self.optimized_dir, filename)
            
            quality = self.QUALITY_SETTINGS.get(format.upper(), 80)
            
            if format.lower() == 'webp':
                img_resized.save(
                    filepath,
                    'WEBP',
                    quality=quality,
                    method=6  # Best compression method
                )
            else:
                img_resized.save(
                    filepath,
                    format.upper(),
                    quality=quality,
                    optimize=True
                )
            
            # Return URL path
            return f"/static/uploads/optimized/{filename}"
            
        except Exception as e:
            logger.error(f"Error saving optimized image: {e}")
            return ""
    
    def generate_thumbnail(
        self,
        image_path: str,
        size: Tuple[int, int] = (300, 300)
    ) -> str:
        """Generate thumbnail for quick loading"""
        try:
            image = Image.open(image_path)
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            base_name = Path(image_path).stem
            thumb_path = os.path.join(
                self.optimized_dir,
                f"{base_name}_thumb.webp"
            )
            
            image.save(
                thumb_path,
                'WEBP',
                quality=60,  # Lower quality for thumbnail
                method=6
            )
            
            return f"/static/uploads/optimized/{base_name}_thumb.webp"
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return ""
    
    def compress_image(
        self,
        image_data: bytes,
        format: str = 'JPEG',
        quality: int = 80
    ) -> bytes:
        """
        Compress image bytes
        
        Args:
            image_data: Raw image bytes
            format: Output format (JPEG, PNG, WEBP)
            quality: Compression quality (0-100)
            
        Returns:
            Compressed image bytes
        """
        try:
            image = Image.open(BytesIO(image_data))
            
            # Convert RGBA to RGB if saving as JPEG
            if format.upper() == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = rgb_image
            
            output = BytesIO()
            
            if format.lower() == 'webp':
                image.save(output, 'WEBP', quality=quality, method=6)
            else:
                image.save(output, format.upper(), quality=quality, optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error compressing image: {e}")
            return image_data
    
    def get_image_hash(self, image_path: str) -> str:
        """Generate hash for image deduplication"""
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error hashing image: {e}")
            return ""


# Global optimizer instance
optimizer = ImageOptimizer()


# Celery task for async image optimization
try:
    from .celery_app import celery_app
    
    @celery_app.task(bind=True)
    def optimize_product_image(self, image_path: str, product_id: str):
        """
        Async task to optimize product images
        
        Args:
            image_path: Path to image file
            product_id: Product identifier
        
        Returns:
            Dict with optimized image URLs
        """
        try:
            logger.info(f"Optimizing image for product: {product_id}")
            
            self.update_state(
                state='PROGRESS',
                meta={'status': 'Optimizing images...'}
            )
            
            result = optimizer.optimize_image(image_path)
            
            logger.info(f"Image optimization completed for: {product_id}")
            return {
                "product_id": product_id,
                "optimized_urls": result,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            raise

except ImportError:
    # Fallback if celery_app cannot be imported
    def optimize_product_image(image_path: str, product_id: str):
        """
        Fallback sync image optimization (when Celery is unavailable)
        
        Args:
            image_path: Path to image file
            product_id: Product identifier
        
        Returns:
            Dict with optimized image URLs
        """
        try:
            logger.info(f"Optimizing image for product: {product_id}")
            result = optimizer.optimize_image(image_path)
            logger.info(f"Image optimization completed for: {product_id}")
            return {
                "product_id": product_id,
                "optimized_urls": result,
                "status": "completed"
            }
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return {"status": "failed", "error": str(e)}


# Configuration for CDN integration
CDN_CONFIG = {
    "providers": {
        "cloudinary": {
            "base_url": "https://res.cloudinary.com/{cloud_name}/image/upload",
            "params": {
                "quality": "auto",
                "fetch_format": "auto",
                "width": "{width}",
                "height": "{height}",
                "crop": "fill",
            }
        },
        "imgix": {
            "base_url": "https://{domain}.imgix.net",
            "params": {
                "auto": "format,compress",
                "w": "{width}",
                "h": "{height}",
                "fit": "crop",
                "q": "80"
            }
        },
        "imagekit": {
            "base_url": "https://ik.imagekit.io/{image_id}",
            "params": {
                "tr": "w-{width},h-{height},q-80,f-auto"
            }
        },
        "aws_cloudfront": {
            "base_url": "https://{distribution_id}.cloudfront.net",
            "params": {
                # CloudFront uses Lambda@Edge for transformations
            }
        }
    },
    
    "recommended": {
        "small_images": "imgix",     # Fast, affordable
        "ecommerce": "cloudinary",   # Feature-rich
        "enterprise": "aws_cloudfront",  # Scalable
    }
}
