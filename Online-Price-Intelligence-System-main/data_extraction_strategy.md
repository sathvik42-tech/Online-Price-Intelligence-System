# Data Extraction Strategy

This document outlines the technical approach for extracting product data from major e-commerce platforms for the Online Price Intelligence System.

## Platform Selectors & Logic

| Platform | Title Selector | Price Selector | Rating Selector | Availability Logic |
| :--- | :--- | :--- | :--- | :--- |
| **Amazon** | `h2 a span`, `h2` | `.a-price-whole`, `.a-offscreen` | `.a-icon-alt`, `span[aria-label*="stars"]` | Check for "Add to Cart" or "Currently unavailable" |
| **eBay** | `.s-item__title` | `.s-item__price` | `.s-item__seller-info`, `.x-star-rating` | Check for "Out of Stock" labels |
| **Walmart** | `span[data-automation-id="product-title"]` | `div[data-automation-id="product-price"]` | `span.w_iUBy` (if available) | Check for "In stock" / "Out of stock" text |

## Common Implementation Details

### Anti-Bot Measures
- **Throttling**: A 3-5 second randomized delay between requests.
- **User-Agent Rotation**: Utilizing a pool of modern browser headers.
- **Automation Masking**: Using `undetected-chromedriver` or `selenium-stealth` to bypass basic bot detection.
- **Headless Toggle**: Ability to run in visible mode if headless is blocked.

### Data Normalization
All extracted data is passed through `utils/normalization.py` to:
1. Convert prices to a clean float.
2. Normalize product names (lowercase, remove special characters).
3. Standardize seller ratings to a 0-5 scale.

## Fallback Mechanism
1. **Primary**: Official API (where credentials available).
2. **Secondary**: Selenium-based stealth scraping.
3. **Tertiary**: Mock data/Cache (if both fail) with an error log.

## Legal & Ethical Compliance
- Scripts respect `robots.txt` where possible.
- Extraction is limited to public product data.
- No harvesting of personal user data.
- Rate limits are strictly enforced to avoid server strain.
