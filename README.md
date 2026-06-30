# 🛒 Online Price Intelligence System

A full-stack web application that allows users to search for products and compare prices from multiple online marketplaces using APIs and web scraping. The system helps users find the best available prices for products by gathering and displaying pricing information from different e-commerce platforms.

---

## 📌 Features

- 🔍 Search products by name
- 💰 Compare product prices from multiple sources
- 🖼️ Product image support
- ⚡ Fast product search using optimized backend
- 🌐 REST API integration
- 📊 Price comparison dashboard
- 🗄️ Database support for storing product information
- 🔄 Image optimization and preprocessing
- 📈 Pagination support for large search results

---

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask
- REST APIs

### Database
- SQLite / SQL Database

### APIs & Tools
- eBay Browse API
- Amazon Product Data
- Web Scraping
- Requests Library

---

## 📂 Project Structure

```
Online-Price-Intelligence-System/
│
├── backend/
│   ├── app/
│   ├── routers/
│   ├── scrapers/
│   ├── utils/
│   └── tests/
│
├── demo.html
├── package.json
├── package-lock.json
├── README.md
└── requirements.txt
```

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sathvik42-tech/Online-Price-Intelligence-System.git
```

### 2. Navigate to the Project Folder

```bash
cd Online-Price-Intelligence-System
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file and add your API credentials.

Example:

```
EBAY_CLIENT_ID=your_client_id
EBAY_CLIENT_SECRET=your_client_secret
```

> **Note:** Do not upload your `.env` file to GitHub.

### 5. Run the Backend

```bash
python backend/app/main.py
```

or

```bash
python backend/app/main_optimized.py
```

---

## 💻 Usage

1. Start the backend server.
2. Open the frontend (`demo.html`) in your browser.
3. Enter a product name.
4. View products and compare prices from supported marketplaces.

---

## 📁 Key Modules

- Product Search
- eBay API Integration
- Amazon Scraper
- Image Optimization
- Database Operations
- Pagination
- Performance Profiling

---

## 🔒 Security

- Environment variables are stored in `.env`.
- API credentials are excluded from version control using `.gitignore`.

---

## 🎯 Future Enhancements

- Amazon API Integration
- Walmart Price Comparison
- Flipkart Integration
- User Authentication
- Search History
- Product Wishlist
- Email Price Alerts
- Price Trend Analysis
- Responsive UI Improvements

---

## 👨‍💻 Author

**Sathvik Gaddam**

- GitHub: https://github.com/sathvik42-tech

---

## 📄 License

This project is developed for educational and internship purposes.
