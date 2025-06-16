# 🛒 Amazon Scraper

<div align="center">

![Python](https://img.shields.io/badge/python-v3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg)

**Công cụ scraping Amazon products với giao diện đồ họa thân thiện - Tất cả tính năng trong một file duy nhất!**

</div>

## 📋 Mục lục

- [Tổng quan](#-tổng-quan)
- [Tính năng](#-tính-năng)
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Cài đặt](#-cài-đặt)
- [Cách sử dụng](#-cách-sử-dụng)
- [Dữ liệu được scrape](#-dữ-liệu-được-scrape)
- [Ví dụ kết quả](#-ví-dụ-kết-quả)
- [Xử lý lỗi](#-xử-lý-lỗi)
- [Đạo đức và bảo mật](#-đạo-đức-và-bảo-mật)
- [Hỗ trợ](#-hỗ-trợ)

## 🎯 Tổng quan

Amazon Scraper là một ứng dụng GUI được phát triển bằng Python, cho phép thu thập thông tin sản phẩm từ Amazon một cách dễ dàng và hiệu quả. Với giao diện đồ họa thân thiện, bạn có thể scrape thông tin chi tiết của từng sản phẩm hoặc thu thập danh sách sản phẩm từ kết quả tìm kiếm.

### 🌟 Điểm nổi bật
- **All-in-One**: Toàn bộ chức năng được tích hợp trong một file duy nhất
- **GUI Only**: Chỉ sử dụng giao diện đồ họa, không có command line
- **Real-time Tracking**: Theo dõi tiến độ scraping real-time
- **Smart Error Handling**: Xử lý lỗi thông minh với gợi ý khắc phục
- **Multiple Export Options**: Xuất dữ liệu JSON và mở trực tiếp trên browser

## ✨ Tính năng

### 🔗 Single Product Scraper
- Scrape thông tin chi tiết của một sản phẩm cụ thể
- Hỗ trợ tất cả miền Amazon quốc tế
- Thu thập 20+ thông số sản phẩm

### 🔍 Search Results Scraper  
- Scrape danh sách sản phẩm từ kết quả tìm kiếm
- Hỗ trợ scraping nhiều trang (1-5 trang)
- Thống kê tỷ lệ thành công và tổng số sản phẩm

### 🖥️ GUI Features
- Giao diện đẹp mắt với emoji và màu sắc
- Progress bar với status updates real-time
- Text area có thể scroll để hiển thị kết quả
- Các nút chức năng: Clear, Save, Open Browser, About

### 🛡️ Anti-Detection
- Rotation user agents tự động
- Random delays giữa các requests
- Headers giả lập browser thật
- Rate limiting để tránh overload

## 💻 Yêu cầu hệ thống

### Phần mềm
- **Python 3.6 hoặc mới hơn**
- **tkinter** (thường có sẵn với Python)
- **Internet connection** để truy cập Amazon

### Dependencies
```
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
```

## 📥 Cài đặt

### 1. Clone hoặc download repository
```bash
git clone https://github.com/thredeisacoder/Amazon-Scraper
cd Amazon-Scraper
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng
```bash
python amazon_scraper_gui.py
```

## 🚀 Cách sử dụng

### Quy trình cơ bản
1. **Chọn chế độ scraping**:
   - `Single Product`: Scrape một sản phẩm cụ thể
   - `Search Results`: Scrape danh sách từ tìm kiếm

2. **Nhập URL Amazon**: Copy URL từ browser và paste vào ô input

3. **Cấu hình**:
   - Với Search Results: Chọn số trang muốn scrape (1-5)

4. **Bắt đầu scraping**: Click nút "BẮT ĐẦU SCRAPE"

5. **Xem kết quả**: Theo dõi progress bar và xem kết quả trong text area

6. **Xuất dữ liệu**: Sử dụng các nút Save JSON, Open Browser

### URL Examples hợp lệ

**Single Product URLs:**
```
https://www.amazon.com/dp/B08N5WRWNW
https://www.amazon.com/gp/product/B08N5WRWNW
https://www.amazon.co.uk/dp/B08N5WRWNW
```

**Search Results URLs:**
```
https://www.amazon.com/s?k=wireless+headphones
https://www.amazon.com/s?k=laptop&ref=sr_pg_1
https://www.amazon.co.uk/s?k=cleaning+tools
```

## 📊 Dữ liệu được scrape

### 🔗 Single Product Mode

| Thông tin | Mô tả |
|-----------|-------|
| **Cơ bản** | Tên, giá, đánh giá, reviews |
| **Chi tiết** | ASIN, thương hiệu, màu sắc |
| **Kích thước** | Dimensions, weight, model |
| **Tình trạng** | Availability, shipping, seller |
| **Media** | Hình ảnh sản phẩm (5+ URLs) |
| **Nội dung** | Features, description, specs |
| **Phân loại** | Categories, bestseller rank |

### 🔍 Search Results Mode

- URL tìm kiếm, số trang, thời gian
- Tổng sản phẩm, tỷ lệ thành công  
- Title, price, rating, reviews của từng sản phẩm
- Trang số, vị trí trên trang

## 📋 Ví dụ kết quả

### Single Product Output
```
🎉 THÔNG TIN SẢN PHẨM AMAZON - SCRAPE THÀNH CÔNG!
======================================================================

📦 TÊN SẢN PHẨM:
Amazon Echo Dot (4th Gen) Smart speaker with Alexa - Charcoal

💰 GIÁ: $49.99

⭐ ĐÁNH GIÁ: 4.5/5 (89,234 reviews)

🏷️ ASIN: B08N5WRWNW

🏢 THƯƠNG HIỆU: Amazon

📦 TÌNH TRẠNG: In Stock
...
```

### Search Results Output
```
🎉 KẾT QUẢ SCRAPING SEARCH RESULTS - THÀNH CÔNG!
======================================================================

🔗 URL tìm kiếm: https://www.amazon.com/s?k=wireless+headphones
📄 Số trang đã scrape: 2
📦 Tổng số sản phẩm tìm thấy: 32
📊 Tỷ lệ scrape thành công: 96.9%

🛍️ SẢN PHẨM 1:
   📦 Sony WH-1000XM4 Wireless Noise Canceling Headphones
   💰 $279.99 | ⭐ 4.4/5 | 📝 45,123 reviews
...
```

## 🔧 Xử lý lỗi

### Lỗi thường gặp

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| `Invalid URL` | URL sai format | Kiểm tra URL Amazon đúng format |
| `Network Error` | Mất kết nối | Kiểm tra internet connection |
| `Empty Results` | HTML thay đổi | Thử URL khác hoặc cập nhật |
| `GUI Won't Start` | Thiếu tkinter | Cài đặt tkinter cho OS |

### Debug Steps
```bash
# Kiểm tra Python version
python --version

# Kiểm tra dependencies
pip list | grep -E "(requests|beautifulsoup4|lxml)"

# Reinstall dependencies
pip install -r requirements.txt
```

## 🛡️ Đạo đức và bảo mật

### ✅ Best Practices
- **Chỉ sử dụng cho mục đích học tập và nghiên cứu**
- **Tôn trọng robots.txt** của Amazon
- **Rate limiting** tự động để không overload server
- **Random delays** để mô phỏng hành vi người dùng thật

### ❌ Không nên làm
- Sử dụng cho mục đích thương mại
- Scrape với tần suất cao liên tục  
- Bỏ qua Terms of Service của Amazon
- Scrape dữ liệu cá nhân/nhạy cảm

## 📞 Hỗ trợ

### Troubleshooting Checklist
1. **Dependencies**: Đảm bảo đã cài đặt đầy đủ
2. **Python version**: Phiên bản 3.6 trở lên  
3. **Internet**: Kết nối ổn định
4. **URL format**: Đúng format Amazon URL
5. **Console errors**: Xem console để debug

## 📁 Cấu trúc dự án

```
Amazon-Scraper/
├── amazon_scraper_gui.py      # Main application
├── requirements.txt           # Python dependencies  
└── README.md                 # This documentation
```

## 📈 Version History

### v1.0.0 (Current)
- ✅ Complete GUI implementation
- ✅ Single product & search results scraping
- ✅ JSON export với file size info
- ✅ Browser integration
- ✅ Beautiful formatted output
- ✅ Comprehensive error handling
- ✅ Real-time progress tracking

---

<div align="center">

**🌟 Happy Scraping! 🌟**

*Sử dụng có trách nhiệm - Tôn trọng website policies*

[![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-red.svg)](https://github.com)
[![Python](https://img.shields.io/badge/Made%20with-Python-blue.svg)](https://python.org)

</div> 
