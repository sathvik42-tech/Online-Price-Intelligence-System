# Web Scraping Documentation: Amazon India

This document provides technical details and considerations for the web scraping implementation targeting Amazon India product pages.

## 1. Platform Information
- **Platform Name:** Amazon India
- **Region:** India (.in)

## 2. Test Configuration
- **Test Product URL:** [https://www.amazon.in/dp/B0GH6VRLMP](https://www.amazon.in/dp/B0GH6VRLMP)
- **HTTP Status Code Observed:** 200 (Success)

## 3. Tech Stack
- **Language:** Python
- **Libraries:** 
  - `requests`: For handling HTTP requests.
  - `BeautifulSoup` (bs4): For parsing HTML content.
  - `time`: For implementing request throttling.

## 4. Extraction Logic
The following CSS selectors are used for data extraction via `select_one()`:
- **Title:** `span#productTitle`
- **Price:** `span.a-offscreen`
- **Rating:** `span.a-icon-alt`

## 5. Implementation Details
- **Headers:** To simulate a real browser and avoid immediate blocking, the following headers are included:
  - `User-Agent`: Modern Chrome browser string.
  - `Accept-Language`: Set to `en-US,en;q=0.9`.
- **Delay:** A **3-second delay** (`time.sleep(3)`) is implemented before parsing the response to respect server resources and reduce the footprint of the scraper.

## 6. Challenges and Limitations
- **Bot Detection:** Amazon employs sophisticated anti-bot measures. Frequent requests or lack of JS execution may lead to **503 Service Unavailable** errors or CAPTCHA challenges.
- **Dynamic Content:** Some elements (like dynamic pricing or stock info) might be loaded via JavaScript after the initial HTML is served, which `requests` cannot capture.
- **Region-Specific URLs:** Selectors and page structures can vary slightly between different Amazon domains (e.g., .com vs .in).

## 7. Legal and Ethical Considerations
> [!IMPORTANT]
> This scraper is developed with high ethical standards in mind:
> - **Public Data Only:** Only publicly available product information is accessed.
> - **No Authentication:** No login credentials or private user data are used or requested.
> - **Throttling:** Rate limiting is respected via the 3-second delay to prevent server strain.
> - **Educational Use:** This implementation is for **academic/internship purposes only** and is not intended for high-volume commercial scraping.
