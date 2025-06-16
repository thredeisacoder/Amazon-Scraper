#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon Product Scraper - GUI Edition
Giao diện đồ họa cho scraping Amazon products
Gộp tất cả tính năng vào 1 file - CHỈ SỬ DỤNG GUI

Requires: requests, beautifulsoup4, lxml, tkinter
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
from urllib.parse import urlparse, urlencode, parse_qs
import threading
import os
from datetime import datetime
import webbrowser
import sys

# ===================================================================
# CORE AMAZON SCRAPER CLASS
# ===================================================================

class AmazonScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # Rotate user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        # Headers to mimic real browser
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def get_random_headers(self):
        """Get random headers to avoid detection"""
        headers = self.headers.copy()
        headers['User-Agent'] = random.choice(self.user_agents)
        return headers

    def validate_amazon_url(self, url):
        """Validate if the URL is an Amazon product URL"""
        parsed_url = urlparse(url)
        amazon_domains = ['amazon.com', 'amazon.co.uk', 'amazon.de', 'amazon.fr', 'amazon.it', 'amazon.es', 'amazon.jp']
        
        if not any(domain in parsed_url.netloc for domain in amazon_domains):
            return False
        
        # Check if it's a product URL (contains /dp/ or /gp/product/)
        if '/dp/' in url or '/gp/product/' in url:
            return True
        
        return False

    def extract_product_info(self, soup):
        """Extract product information from BeautifulSoup object"""
        product_info = {}
        
        try:
            # Product title
            title_selectors = [
                '#productTitle',
                '.product-title',
                'h1.a-size-large',
                'h1#title'
            ]
            
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    product_info['title'] = title_element.get_text().strip()
                    break
            
            # ASIN (Amazon Standard Identification Number)
            asin_patterns = [
                r'/dp/([A-Z0-9]{10})',
                r'/gp/product/([A-Z0-9]{10})',
                r'data-asin="([A-Z0-9]{10})"'
            ]
            page_content = str(soup)
            for pattern in asin_patterns:
                asin_match = re.search(pattern, page_content)
                if asin_match:
                    product_info['asin'] = asin_match.group(1)
                    break
            
            # Brand
            brand_selectors = [
                '#bylineInfo',
                '.a-row .a-link-normal[href*="/stores/"]',
                'tr:contains("Brand") td.a-span9',
                '.po-brand .po-break-word',
                '#brand'
            ]
            
            for selector in brand_selectors:
                brand_element = soup.select_one(selector)
                if brand_element:
                    brand_text = brand_element.get_text().strip()
                    if brand_text and not brand_text.lower().startswith('visit'):
                        product_info['brand'] = brand_text.replace('Brand: ', '').replace('Visit the ', '').replace(' Store', '')
                        break
            
            # Product price
            price_selectors = [
                '.a-price-whole',
                '.a-price .a-offscreen',
                '#price_inside_buybox',
                '.a-price-range',
                '#ap_desktop_sns_detail_page .a-price .a-offscreen'
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text().strip()
                    # Clean price text
                    price_text = re.sub(r'[^\d.,]', '', price_text)
                    product_info['price'] = price_text
                    break
            
            # Product rating
            rating_selectors = [
                '.a-icon-alt',
                '[data-hook="average-star-rating"] .a-icon-alt',
                '.a-star-medium .a-icon-alt'
            ]
            
            for selector in rating_selectors:
                rating_element = soup.select_one(selector)
                if rating_element:
                    rating_text = rating_element.get('alt', '') or rating_element.get_text()
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        product_info['rating'] = rating_match.group(1)
                        break
            
            # Number of reviews
            review_selectors = [
                '#acrCustomerReviewText',
                '[data-hook="total-review-count"]',
                '.a-link-normal .a-size-base'
            ]
            
            for selector in review_selectors:
                review_element = soup.select_one(selector)
                if review_element:
                    review_text = review_element.get_text().strip()
                    review_match = re.search(r'([\d,]+)', review_text)
                    if review_match:
                        product_info['review_count'] = review_match.group(1)
                        break
            
            # Product images
            img_selectors = [
                '#landingImage',
                '.a-dynamic-image',
                '#imgTagWrapperId img'
            ]
            
            images = []
            for selector in img_selectors:
                img_elements = soup.select(selector)
                for img in img_elements:
                    src = img.get('src') or img.get('data-src')
                    if src and src.startswith('http'):
                        images.append(src)
            
            if images:
                product_info['images'] = list(set(images))  # Remove duplicates
            
            # Product description/features
            feature_selectors = [
                '#feature-bullets ul li',
                '.a-unordered-list .a-list-item',
                '#productDescription p'
            ]
            
            features = []
            for selector in feature_selectors:
                feature_elements = soup.select(selector)
                for feature in feature_elements:
                    text = feature.get_text().strip()
                    if text and len(text) > 10:  # Filter out short/empty text
                        features.append(text)
                if features:  # If we found features, break
                    break
            
            if features:
                product_info['features'] = features[:5]  # Limit to first 5 features
            
            # Availability
            availability_selectors = [
                '#availability span',
                '.a-size-medium.a-color-success',
                '.a-size-medium.a-color-price'
            ]
            
            for selector in availability_selectors:
                avail_element = soup.select_one(selector)
                if avail_element:
                    product_info['availability'] = avail_element.get_text().strip()
                    break
            
            # Technical Specifications / Product Details
            product_info['specifications'] = {}
            
            # Method 1: Technical Details table
            tech_table = soup.select_one('#productDetails_techSpec_section_1')
            if tech_table:
                rows = tech_table.select('tr')
                for row in rows:
                    cols = row.select('td')
                    if len(cols) >= 2:
                        key = cols[0].get_text().strip()
                        value = cols[1].get_text().strip()
                        if key and value:
                            product_info['specifications'][key] = value
            
            # Method 2: Feature bullets for specifications
            detail_bullets = soup.select('#feature-bullets ul li, .a-unordered-list.a-nostyle li')
            for bullet in detail_bullets:
                text = bullet.get_text().strip()
                if ':' in text and len(text) < 200:  # Likely a specification
                    parts = text.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if key and value and not key.lower().startswith('make sure'):
                            product_info['specifications'][key] = value
            
            # Method 3: Product Overview section
            overview_section = soup.select_one('#poExpander')
            if overview_section:
                overview_rows = overview_section.select('.po-display-name')
                overview_values = overview_section.select('.po-break-word')
                for i, row in enumerate(overview_rows):
                    if i < len(overview_values):
                        key = row.get_text().strip()
                        value = overview_values[i].get_text().strip()
                        if key and value:
                            product_info['specifications'][key] = value
            
            # Method 4: Additional Information table
            additional_info = soup.select('#productDetails_detailBullets_sections1 tr')
            for row in additional_info:
                th = row.select_one('th')
                td = row.select_one('td')
                if th and td:
                    key = th.get_text().strip()
                    value = td.get_text().strip()
                    if key and value:
                        product_info['specifications'][key] = value
            
            # Extract specific important fields from specifications
            specs = product_info.get('specifications', {})
            
            # Color
            color_keys = ['Color', 'Colour', 'Color Name', 'Item Color']
            for key in color_keys:
                if key in specs:
                    product_info['color'] = specs[key]
                    break
            
            # Material
            material_keys = ['Material', 'Materials', 'Item Material', 'Frame Material', 'Fabric Type']
            for key in material_keys:
                if key in specs:
                    product_info['material'] = specs[key]
                    break
            
            # Size/Dimensions
            size_keys = ['Size', 'Dimensions', 'Item Dimensions', 'Package Dimensions', 'Product Dimensions']
            for key in size_keys:
                if key in specs:
                    product_info['dimensions'] = specs[key]
                    break
            
            # Weight
            weight_keys = ['Weight', 'Item Weight', 'Package Weight', 'Shipping Weight']
            for key in weight_keys:
                if key in specs:
                    product_info['weight'] = specs[key]
                    break
            
            # Model Number
            model_keys = ['Model Number', 'Model', 'Item model number', 'Part Number']
            for key in model_keys:
                if key in specs:
                    product_info['model_number'] = specs[key]
                    break
            
            # Department/Category
            category_selectors = [
                '#wayfinding-breadcrumbs_feature_div a',
                '.a-breadcrumb a',
                '[data-hook="breadcrumb"] a'
            ]
            
            categories = []
            for selector in category_selectors:
                category_links = soup.select(selector)
                for link in category_links:
                    cat_text = link.get_text().strip()
                    if cat_text and cat_text not in categories:
                        categories.append(cat_text)
            
            if categories:
                product_info['categories'] = categories
                product_info['primary_category'] = categories[-1] if categories else None
            
            # Best Sellers Rank
            rank_element = soup.select_one('#SalesRank, .a-icon-badge')
            if rank_element:
                rank_text = rank_element.get_text().strip()
                if 'Best Sellers Rank' in rank_text or '#' in rank_text:
                    product_info['bestsellers_rank'] = rank_text
            
            # Prime eligibility
            prime_elements = soup.select('.a-icon-prime, [data-csa-c-content-id="prime-sash"]')
            if prime_elements:
                product_info['prime_eligible'] = True
            else:
                product_info['prime_eligible'] = False
            
            # Product description (detailed)
            description_selectors = [
                '#productDescription p',
                '#aplus_feature_div',
                '.a-section.a-spacing-medium.apm-A1sMoFEeI'
            ]
            
            descriptions = []
            for selector in description_selectors:
                desc_elements = soup.select(selector)
                for desc in desc_elements:
                    desc_text = desc.get_text().strip()
                    if desc_text and len(desc_text) > 20 and desc_text not in descriptions:
                        descriptions.append(desc_text)
            
            if descriptions:
                product_info['detailed_description'] = descriptions
            
            # Variations (size, color options)
            variations = {}
            
            # Color variations
            color_swatches = soup.select('.imgSwatch, .a-button-text .a-size-base')
            if color_swatches:
                color_options = []
                for swatch in color_swatches:
                    color_name = swatch.get('title') or swatch.get_text().strip()
                    if color_name and color_name not in color_options:
                        color_options.append(color_name)
                if color_options:
                    variations['colors'] = color_options
            
            # Size variations
            size_select = soup.select('#native_dropdown_selected_size_name option, .a-size-base.a-color-base')
            if size_select:
                size_options = []
                for size in size_select:
                    size_name = size.get_text().strip()
                    if size_name and size_name not in ['Select', 'Choose', ''] and size_name not in size_options:
                        size_options.append(size_name)
                if size_options:
                    variations['sizes'] = size_options
            
            if variations:
                product_info['variations'] = variations
            
            # Shipping information
            shipping_element = soup.select_one('#deliveryBlockMessage, .a-spacing-top-base .a-color-price')
            if shipping_element:
                shipping_text = shipping_element.get_text().strip()
                if 'delivery' in shipping_text.lower() or 'shipping' in shipping_text.lower():
                    product_info['shipping_info'] = shipping_text
            
            # Seller information
            seller_element = soup.select_one('#sellerProfileTriggerId, .a-size-small.mbcMerchantName')
            if seller_element:
                seller_text = seller_element.get_text().strip()
                if seller_text:
                    product_info['seller'] = seller_text
            
        except Exception as e:
            print(f"Error extracting product info: {e}")
        
        return product_info

    def scrape_product(self, url):
        """Main method to scrape product from Amazon URL"""
        
        # Validate URL
        if not self.validate_amazon_url(url):
            return {
                'error': 'Invalid Amazon product URL. Please provide a valid Amazon product link.'
            }
        
        try:
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            # Make request with random headers
            response = self.session.get(url, headers=self.get_random_headers())
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product information
            product_info = self.extract_product_info(soup)
            
            # Add URL and timestamp
            product_info['url'] = url
            product_info['scraped_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            return product_info
            
        except requests.exceptions.RequestException as e:
            return {
                'error': f'Network error: {str(e)}'
            }
        except Exception as e:
            return {
                'error': f'Scraping error: {str(e)}'
            }

# ===================================================================
# AMAZON SEARCH SCRAPER CLASS
# ===================================================================

class AmazonSearchScraper:
    def __init__(self):
        self.session = requests.Session()
        self.base_scraper = AmazonScraper()
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def get_random_headers(self):
        """Get random headers to avoid detection"""
        headers = self.headers.copy()
        headers['User-Agent'] = random.choice(self.user_agents)
        return headers

    def validate_search_url(self, url):
        """Validate if the URL is an Amazon search URL"""
        parsed_url = urlparse(url)
        amazon_domains = ['amazon.com', 'amazon.co.uk', 'amazon.de', 'amazon.fr', 'amazon.it', 'amazon.es', 'amazon.jp']
        
        if not any(domain in parsed_url.netloc for domain in amazon_domains):
            return False
        
        # Check if it's a search URL (contains /s? or has 'k=' parameter)
        if '/s?' in url or 'k=' in url:
            return True
        
        return False

    def build_page_url(self, base_url, page_num):
        """Build URL for specific page number"""
        if page_num == 1:
            return base_url
        
        # Parse the URL and add page parameter
        parsed_url = urlparse(base_url)
        query_params = parse_qs(parsed_url.query)
        
        # Add page parameter
        query_params['page'] = [str(page_num)]
        
        # Reconstruct URL
        new_query = urlencode(query_params, doseq=True)
        new_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{new_query}"
        
        return new_url

    def extract_product_links(self, soup):
        """Extract product links from search results page"""
        product_links = []
        
        # Various selectors for product links
        selectors = [
            'h2.a-size-mini a',
            '.s-result-item h3 a',
            '[data-component-type="s-search-result"] h3 a',
            '.s-product-image-container a',
            'a.a-link-normal.s-underline-text'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and ('/dp/' in href or '/gp/product/' in href):
                    # Convert relative URL to absolute
                    if href.startswith('/'):
                        href = 'https://www.amazon.com' + href
                    product_links.append(href)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in product_links:
            # Clean URL (remove tracking parameters after dp/ASIN)
            clean_link = re.sub(r'(/dp/[A-Z0-9]{10}).*', r'\1', link)
            if clean_link not in seen:
                seen.add(clean_link)
                unique_links.append(clean_link)
        
        return unique_links

    def scrape_search_results(self, search_url, max_pages=1, progress_callback=None):
        """Scrape products from Amazon search results"""
        
        if not self.validate_search_url(search_url):
            return {
                'error': 'Invalid Amazon search URL. Please provide a valid Amazon search link.'
            }
        
        all_products = []
        total_scraped = 0
        
        try:
            for page_num in range(1, max_pages + 1):
                if progress_callback:
                    progress_callback(f"Đang scrape trang {page_num}/{max_pages}...")
                
                # Build URL for current page
                page_url = self.build_page_url(search_url, page_num)
                
                # Add delay between pages
                if page_num > 1:
                    time.sleep(random.uniform(2, 4))
                
                # Get search results page
                response = self.session.get(page_url, headers=self.get_random_headers())
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract product links
                product_links = self.extract_product_links(soup)
                
                if not product_links:
                    if progress_callback:
                        progress_callback(f"Không tìm thấy sản phẩm ở trang {page_num}")
                    break
                
                if progress_callback:
                    progress_callback(f"Tìm thấy {len(product_links)} sản phẩm ở trang {page_num}")
                
                # Scrape each product
                page_products = []
                for i, product_url in enumerate(product_links, 1):  # Scrape ALL products on page
                    if progress_callback:
                        progress_callback(f"Trang {page_num}: Scraping sản phẩm {i}/{len(product_links)}")
                    
                    try:
                        # Use the base scraper to get product details
                        product_data = self.base_scraper.scrape_product(product_url)
                        
                        if 'error' not in product_data:
                            product_data['page_number'] = page_num
                            product_data['position_on_page'] = i
                            page_products.append(product_data)
                            total_scraped += 1
                        
                        # Add delay between products
                        time.sleep(random.uniform(1, 2))
                        
                    except Exception as e:
                        if progress_callback:
                            progress_callback(f"Lỗi scraping {product_url}: {str(e)}")
                        continue
                
                all_products.extend(page_products)
                
                if progress_callback:
                    progress_callback(f"Hoàn thành trang {page_num}: {len(page_products)} sản phẩm")
            
            # Prepare final result
            result = {
                'search_url': search_url,
                'total_pages_scraped': max_pages,
                'total_products': len(all_products),
                'products': all_products,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'summary': {
                    'pages_processed': page_num,
                    'products_found': total_scraped,
                    'success_rate': f"{(total_scraped/max(len(product_links)*max_pages, 1)*100):.1f}%" if product_links else "0%"
                }
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                'error': f'Network error: {str(e)}'
            }
        except Exception as e:
            return {
                'error': f'Scraping error: {str(e)}'
            }

# ===================================================================
# GUI INTERFACE CLASS
# ===================================================================

class AmazonScraperGUI:
    def __init__(self, root):
        self.root = root
        self.scraper = AmazonScraper()
        self.search_scraper = AmazonSearchScraper()
        self.current_result = None
        
        # Configure main window
        self.root.title("Amazon Product Scraper - GUI Edition")
        self.root.geometry("950x750")
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        self.setup_styles()
        
        # Create GUI elements
        self.create_widgets()
        
        # Center window
        self.center_window()
        
        # Add welcome message
        self.show_welcome()

    def setup_styles(self):
        """Setup custom styles for the GUI"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('Title.TLabel', 
                           font=('Arial', 18, 'bold'), 
                           background='#f0f0f0',
                           foreground='#2c3e50')
        
        self.style.configure('Header.TLabel', 
                           font=('Arial', 12, 'bold'), 
                           background='#f0f0f0',
                           foreground='#34495e')

    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🛒 Amazon Product Scraper", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 25))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, text="Giao diện đồ họa cho scraping Amazon - Gộp tất cả tính năng", style='Header.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # URL Input Section
        url_frame = ttk.LabelFrame(main_frame, text="📝 Nhập URL Amazon", padding="20")
        url_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        url_frame.columnconfigure(0, weight=1)
        
        # Scrape Mode Selection
        mode_frame = ttk.Frame(url_frame)
        mode_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.scrape_mode = tk.StringVar(value="single")
        single_radio = ttk.Radiobutton(mode_frame, text="🔗 Scrape 1 sản phẩm chi tiết", 
                                      variable=self.scrape_mode, value="single",
                                      command=self.on_mode_change)
        single_radio.grid(row=0, column=0, padx=(0, 30))
        
        search_radio = ttk.Radiobutton(mode_frame, text="🔍 Scrape search results (nhiều sản phẩm)", 
                                      variable=self.scrape_mode, value="search",
                                      command=self.on_mode_change)
        search_radio.grid(row=0, column=1)
        
        # URL Entry
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=('Arial', 11), width=60)
        self.url_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 15))
        
        # Pages input (for search mode)
        self.pages_var = tk.StringVar(value="1")
        self.pages_label = ttk.Label(url_frame, text="Số trang:")
        self.pages_entry = ttk.Entry(url_frame, textvariable=self.pages_var, width=8)
        
        # Scrape Button
        self.scrape_button = ttk.Button(url_frame, text="🔍 BẮT ĐẦU SCRAPE", command=self.start_scraping)
        self.scrape_button.grid(row=1, column=1)
        
        # Example URL
        self.example_label = ttk.Label(url_frame, text="Ví dụ: https://www.amazon.com/dp/B08N5WRWNW", 
                                     foreground='#7f8c8d')
        self.example_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(8, 0))
        
        # Progress Section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress Bar
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 15))
        
        # Status Label
        self.status_var = tk.StringVar(value="✅ Sẵn sàng scrape sản phẩm Amazon")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var, font=('Arial', 10))
        self.status_label.grid(row=0, column=1)
        
        # Results Section
        results_frame = ttk.LabelFrame(main_frame, text="📊 Kết quả Scraping", padding="20")
        results_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Results Text Area
        self.results_text = scrolledtext.ScrolledText(results_frame, height=18, font=('Consolas', 9), wrap=tk.WORD)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buttons Section
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=3, pady=(15, 0))
        
        # Clear Button
        self.clear_button = ttk.Button(buttons_frame, text="🗑️ Xóa kết quả", command=self.clear_results)
        self.clear_button.grid(row=0, column=0, padx=(0, 15))
        
        # Save Button
        self.save_button = ttk.Button(buttons_frame, text="💾 Lưu JSON", command=self.save_results, state='disabled')
        self.save_button.grid(row=0, column=1, padx=(0, 15))
        
        # Open Browser Button
        self.browser_button = ttk.Button(buttons_frame, text="🌐 Mở trình duyệt", command=self.open_in_browser, state='disabled')
        self.browser_button.grid(row=0, column=2, padx=(0, 15))
        
        # About Button
        self.about_button = ttk.Button(buttons_frame, text="ℹ️ Về chương trình", command=self.show_about)
        self.about_button.grid(row=0, column=3)
        
        # Configure main frame row weights
        main_frame.rowconfigure(4, weight=1)

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def show_welcome(self):
        """Show welcome message"""
        welcome_text = """🎉 CHÀO MỪNG ĐÉN VỚI AMAZON SCRAPER GUI!

✨ Chương trình này gộp tất cả tính năng scraping Amazon vào một giao diện đồ họa duy nhất:

🔗 SINGLE PRODUCT MODE:
   • Scrape thông tin chi tiết 1 sản phẩm Amazon
   • Bao gồm: giá, đánh giá, hình ảnh, thông số kỹ thuật, v.v.

🔍 SEARCH RESULTS MODE:
   • Scrape nhiều sản phẩm từ kết quả tìm kiếm
   • Hỗ trợ scrape nhiều trang (1-5 trang)
   • Thống kê tổng hợp

📋 HƯỚNG DẪN SỬ DỤNG:
   1. Chọn chế độ scraping (Single product hoặc Search results)
   2. Nhập URL Amazon hợp lệ
   3. Nhấn "BẮT ĐẦU SCRAPE"
   4. Xem kết quả và lưu file JSON

⚠️ LƯU Ý:
   • Chỉ sử dụng cho mục đích học tập
   • Tôn trọng robots.txt của Amazon
   • Không spam requests

🚀 Hãy bắt đầu bằng cách nhập URL Amazon và chọn chế độ scraping!"""
        
        self.results_text.insert(1.0, welcome_text)

    def on_mode_change(self):
        """Handle scrape mode change"""
        mode = self.scrape_mode.get()
        
        if mode == "single":
            # Hide pages input
            self.pages_label.grid_remove()
            self.pages_entry.grid_remove()
            self.scrape_button.grid(row=1, column=1)
            self.example_label.config(text="Ví dụ: https://www.amazon.com/dp/B08N5WRWNW")
            
        else:  # search mode
            # Show pages input
            self.pages_label.grid(row=1, column=1, padx=(15, 8))
            self.pages_entry.grid(row=1, column=2, padx=(0, 15))
            self.scrape_button.grid(row=1, column=3)
            self.example_label.config(text="Ví dụ: https://www.amazon.com/s?k=cleaning+tools")

    def start_scraping(self):
        """Start scraping in a separate thread"""
        url = self.url_var.get().strip()
        mode = self.scrape_mode.get()
        
        if not url:
            messagebox.showwarning("⚠️ Cảnh báo", "Vui lòng nhập URL Amazon!")
            return
        
        # Get number of pages for search mode
        max_pages = 1
        if mode == "search":
            try:
                pages_str = self.pages_var.get().strip()
                if pages_str:
                    max_pages = int(pages_str)
                    if max_pages < 1 or max_pages > 5:
                        messagebox.showwarning("⚠️ Cảnh báo", "Số trang phải từ 1-5!")
                        return
            except ValueError:
                messagebox.showwarning("⚠️ Cảnh báo", "Số trang phải là số nguyên!")
                return
        
        # Disable button and start progress
        self.scrape_button.config(state='disabled', text="⏳ Đang scrape...")
        self.progress.start(10)
        
        if mode == "single":
            self.status_var.set("🔄 Đang scrape sản phẩm... Vui lòng đợi...")
            # Start single product scraping
            thread = threading.Thread(target=self.scrape_product, args=(url,))
        else:
            self.status_var.set(f"🔄 Đang scrape search results ({max_pages} trang)... Vui lòng đợi...")
            # Start search results scraping
            thread = threading.Thread(target=self.scrape_search_results, args=(url, max_pages))
        
        thread.daemon = True
        thread.start()

    def scrape_product(self, url):
        """Scrape product in background thread"""
        try:
            result = self.scraper.scrape_product(url)
            
            # Update GUI in main thread
            self.root.after(0, self.on_scrape_complete, result)
            
        except Exception as e:
            error_result = {'error': f'Unexpected error: {str(e)}'}
            self.root.after(0, self.on_scrape_complete, error_result)

    def scrape_search_results(self, url, max_pages):
        """Scrape search results in background thread"""
        try:
            def progress_callback(message):
                self.root.after(0, lambda: self.status_var.set(f"🔄 {message}"))
            
            result = self.search_scraper.scrape_search_results(url, max_pages, progress_callback)
            
            # Update GUI in main thread
            self.root.after(0, self.on_scrape_complete, result)
            
        except Exception as e:
            error_result = {'error': f'Unexpected error: {str(e)}'}
            self.root.after(0, self.on_scrape_complete, error_result)

    def on_scrape_complete(self, result):
        """Handle scraping completion"""
        # Stop progress and re-enable button
        self.progress.stop()
        self.scrape_button.config(state='normal', text="🔍 BẮT ĐẦU SCRAPE")
        
        # Store result
        self.current_result = result
        
        # Display results
        if 'error' in result:
            self.status_var.set(f"❌ Lỗi: {result['error']}")
            self.display_error(result['error'])
            self.save_button.config(state='disabled')
            self.browser_button.config(state='disabled')
        else:
            # Check if it's search results or single product
            if 'products' in result:
                self.status_var.set(f"✅ Scrape thành công! {result['total_products']} sản phẩm được tìm thấy")
                self.display_search_results(result)
            else:
                self.status_var.set("✅ Scrape thành công! Sản phẩm đã được phân tích")
                self.display_results(result)
            self.save_button.config(state='normal')
            self.browser_button.config(state='normal')

    def display_results(self, result):
        """Display single product scraping results"""
        self.results_text.delete(1.0, tk.END)
        
        # Format results nicely
        output = "="*70 + "\n"
        output += "🎉 THÔNG TIN SẢN PHẨM AMAZON - SCRAPE THÀNH CÔNG!\n"
        output += "="*70 + "\n\n"
        
        if 'title' in result:
            output += f"📦 TÊN SẢN PHẨM:\n{result['title']}\n\n"
        
        if 'price' in result:
            output += f"💰 GIÁ: {result['price']}\n\n"
        
        if 'rating' in result:
            output += f"⭐ ĐÁNH GIÁ: {result['rating']}/5"
            if 'review_count' in result:
                output += f" ({result['review_count']} reviews)"
            output += "\n\n"
        
        if 'availability' in result:
            output += f"📦 TÌNH TRẠNG: {result['availability']}\n\n"
        
        if 'asin' in result:
            output += f"🏷️ ASIN: {result['asin']}\n\n"
        
        if 'brand' in result:
            output += f"🏢 THƯƠNG HIỆU: {result['brand']}\n\n"
        
        if 'color' in result:
            output += f"🎨 MÀU SẮC: {result['color']}\n\n"
        
        if 'material' in result:
            output += f"🧱 CHẤT LIỆU: {result['material']}\n\n"
        
        if 'dimensions' in result:
            output += f"📏 KÍCH THƯỚC: {result['dimensions']}\n\n"
        
        if 'weight' in result:
            output += f"⚖️ TRỌNG LƯỢNG: {result['weight']}\n\n"
        
        if 'model_number' in result:
            output += f"🔢 MÃ MODEL: {result['model_number']}\n\n"
        
        if 'primary_category' in result:
            output += f"📂 DANH MỤC: {result['primary_category']}\n\n"
        
        if 'prime_eligible' in result:
            prime_status = "✅ Có" if result['prime_eligible'] else "❌ Không"
            output += f"⚡ AMAZON PRIME: {prime_status}\n\n"
        
        if 'bestsellers_rank' in result:
            output += f"🏆 XẾP HẠNG BESTSELLER: {result['bestsellers_rank']}\n\n"
        
        if 'seller' in result:
            output += f"🏪 NGƯỜI BÁN: {result['seller']}\n\n"
        
        if 'shipping_info' in result:
            output += f"🚚 THÔNG TIN VẬN CHUYỂN: {result['shipping_info']}\n\n"
        
        if 'variations' in result and result['variations']:
            output += "🎛️ CÁC TÙY CHỌN:\n"
            if 'colors' in result['variations']:
                output += f"   🎨 Màu sắc có sẵn: {', '.join(result['variations']['colors'][:8])}\n"
            if 'sizes' in result['variations']:
                output += f"   📏 Kích cỡ có sẵn: {', '.join(result['variations']['sizes'][:8])}\n"
            output += "\n"
        
        if 'features' in result and result['features']:
            output += "🔍 ĐẶC ĐIỂM CHÍNH:\n"
            for i, feature in enumerate(result['features'][:7], 1):
                feature_clean = feature[:150] + "..." if len(feature) > 150 else feature
                output += f"   {i}. {feature_clean}\n"
            output += "\n"
        
        if 'specifications' in result and result['specifications']:
            output += "📋 THÔNG SỐ KỸ THUẬT:\n"
            spec_count = 0
            for key, value in result['specifications'].items():
                if spec_count < 12:  # Show up to 12 specs
                    value_clean = value[:100] + "..." if len(value) > 100 else value
                    output += f"   • {key}: {value_clean}\n"
                    spec_count += 1
            if len(result['specifications']) > 12:
                output += f"   ... và {len(result['specifications']) - 12} thông số khác\n"
            output += "\n"
        
        if 'detailed_description' in result and result['detailed_description']:
            output += "📝 MÔ TẢ CHI TIẾT:\n"
            for i, desc in enumerate(result['detailed_description'][:3], 1):
                desc_short = desc[:250] + "..." if len(desc) > 250 else desc
                output += f"   {i}. {desc_short}\n"
            output += "\n"
        
        if 'categories' in result and result['categories']:
            output += f"📁 DANH MỤC ĐẦY ĐỦ:\n   {' > '.join(result['categories'])}\n\n"
        
        if 'images' in result and result['images']:
            output += f"🖼️ HÌNH ẢNH SẢN PHẨM ({len(result['images'])} ảnh):\n"
            for i, img_url in enumerate(result['images'][:5], 1):
                output += f"   {i}. {img_url}\n"
            if len(result['images']) > 5:
                output += f"   ... và {len(result['images']) - 5} ảnh khác\n"
            output += "\n"
        
        if 'url' in result:
            output += f"🔗 URL GỐC: {result['url']}\n\n"
        
        if 'scraped_at' in result:
            output += f"⏰ THỜI GIAN SCRAPE: {result['scraped_at']}\n\n"
        
        output += "="*70 + "\n"
        output += "💾 Dữ liệu đã sẵn sàng để lưu thành file JSON!\n"
        output += "🌐 Có thể mở URL trong trình duyệt để xem sản phẩm!\n"
        output += "🔄 Thử scrape sản phẩm khác hoặc search results!\n"
        
        self.results_text.insert(1.0, output)

    def display_search_results(self, result):
        """Display search results"""
        self.results_text.delete(1.0, tk.END)
        
        # Format search results nicely
        output = "="*70 + "\n"
        output += "🎉 KẾT QUẢ SCRAPING SEARCH RESULTS - THÀNH CÔNG!\n"
        output += "="*70 + "\n\n"
        
        output += f"🔗 URL tìm kiếm: {result['search_url']}\n"
        output += f"📄 Số trang đã scrape: {result['total_pages_scraped']}\n"
        output += f"📦 Tổng số sản phẩm tìm thấy: {result['total_products']}\n"
        output += f"⏰ Thời gian scrape: {result['scraped_at']}\n"
        
        if 'summary' in result:
            output += f"📊 Tỷ lệ scrape thành công: {result['summary']['success_rate']}\n"
        
        output += "\n" + "="*70 + "\n"
        output += "📋 DANH SÁCH SẢN PHẨM\n"
        output += "="*70 + "\n\n"
        
        # Display products
        for i, product in enumerate(result['products'][:25], 1):  # Show first 25
            output += f"🛍️ SẢN PHẨM {i}:\n"
            
            if 'title' in product:
                title = product['title'][:90] + "..." if len(product['title']) > 90 else product['title']
                output += f"   📦 {title}\n"
            
            # Product details in compact format
            details = []
            if 'price' in product:
                details.append(f"💰 {product['price']}")
            if 'rating' in product:
                details.append(f"⭐ {product['rating']}/5")
            if 'review_count' in product:
                details.append(f"📝 {product['review_count']} reviews")
            if 'page_number' in product:
                details.append(f"📄 Trang {product['page_number']}")
            if 'position_on_page' in product:
                details.append(f"🔢 Vị trí {product['position_on_page']}")
            
            if details:
                output += f"   {' | '.join(details)}\n"
            
            if 'availability' in product:
                output += f"   📦 Tình trạng: {product['availability']}\n"
            
            if 'brand' in product:
                output += f"   🏢 Thương hiệu: {product['brand']}\n"
            
            if 'url' in product:
                output += f"   🔗 {product['url']}\n"
            
            output += "\n"
        
        if len(result['products']) > 25:
            output += f"... và {len(result['products']) - 25} sản phẩm khác (xem trong file JSON)\n\n"
        
        output += "="*70 + "\n"
        output += "💾 Dữ liệu đã sẵn sàng để lưu thành file JSON!\n"
        output += "🌐 Có thể mở search URL trong trình duyệt!\n"
        output += "🔄 Thử với từ khóa tìm kiếm khác hoặc scrape single product!\n"
        
        self.results_text.insert(1.0, output)

    def display_error(self, error_message):
        """Display error message"""
        self.results_text.delete(1.0, tk.END)
        
        output = "="*70 + "\n"
        output += "❌ LỖI SCRAPING\n"
        output += "="*70 + "\n\n"
        output += f"❗ Chi tiết lỗi: {error_message}\n\n"
        output += "🔧 GỢI Ý KHẮC PHỤC:\n"
        output += "• ✅ Kiểm tra URL có đúng định dạng Amazon không\n"
        output += "• ✅ Đảm bảo kết nối internet ổn định\n"
        output += "• ✅ Thử lại sau vài phút nếu bị rate limit\n"
        output += "• ✅ Sử dụng URL sản phẩm Amazon hợp lệ\n"
        output += "• ✅ Thử với URL khác hoặc chế độ khác\n\n"
        output += "📋 VÍ DỤ URL HỢP LỆ:\n"
        output += "🔗 Single Product:\n"
        output += "   • https://www.amazon.com/dp/B08N5WRWNW\n"
        output += "   • https://www.amazon.com/gp/product/B08N5WRWNW\n\n"
        output += "🔍 Search Results:\n"
        output += "   • https://www.amazon.com/s?k=cleaning+tools\n"
        output += "   • https://www.amazon.com/s?k=wireless+headphones\n\n"
        output += "💡 MẸO: Hãy thử copy URL trực tiếp từ thanh địa chỉ trình duyệt!\n"
        
        self.results_text.insert(1.0, output)

    def clear_results(self):
        """Clear results text area"""
        self.results_text.delete(1.0, tk.END)
        self.show_welcome()
        self.status_var.set("✅ Đã xóa kết quả. Sẵn sàng scrape sản phẩm mới.")
        self.current_result = None
        self.save_button.config(state='disabled')
        self.browser_button.config(state='disabled')

    def save_results(self):
        """Save results to JSON file"""
        if not self.current_result:
            messagebox.showwarning("⚠️ Cảnh báo", "Không có dữ liệu để lưu!")
            return
        
        # Generate filename based on result type
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if 'products' in self.current_result:
            # Search results
            default_filename = f"amazon_search_results_{timestamp}.json"
        else:
            # Single product
            default_filename = f"amazon_product_{timestamp}.json"
        
        # Ask user for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=default_filename,
            title="Lưu kết quả scraping Amazon"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.current_result, f, ensure_ascii=False, indent=2)
                
                # Show success message with file info
                file_size = os.path.getsize(filename) / 1024  # KB
                product_count = ""
                if 'products' in self.current_result:
                    product_count = f" ({self.current_result['total_products']} sản phẩm)"
                
                messagebox.showinfo("✅ Thành công", 
                                  f"Đã lưu dữ liệu{product_count} vào:\n{filename}\n\nKích thước file: {file_size:.1f} KB")
                self.status_var.set(f"✅ Đã lưu: {os.path.basename(filename)} ({file_size:.1f} KB)")
                
            except Exception as e:
                messagebox.showerror("❌ Lỗi", f"Không thể lưu file:\n{str(e)}")

    def open_in_browser(self):
        """Open the scraped product URL in browser"""
        if not self.current_result:
            messagebox.showwarning("⚠️ Cảnh báo", "Không có URL để mở!")
            return
        
        try:
            # Check if it's search results or single product
            if 'products' in self.current_result:
                # For search results, open the search URL
                url = self.current_result.get('search_url')
                url_type = "search URL"
            else:
                # For single product, open the product URL
                url = self.current_result.get('url')
                url_type = "product URL"
            
            if not url:
                messagebox.showwarning("⚠️ Cảnh báo", "Không có URL để mở!")
                return
            
            webbrowser.open(url)
            self.status_var.set(f"🌐 Đã mở {url_type} trong trình duyệt")
            
        except Exception as e:
            messagebox.showerror("❌ Lỗi", f"Không thể mở trình duyệt:\n{str(e)}")

    def show_about(self):
        """Show about dialog"""
        about_text = """🛒 Amazon Product Scraper - GUI Edition v1.0

Chương trình scrape thông tin sản phẩm Amazon 
với giao diện đồ họa thân thiện - Gộp tất cả tính năng!

✨ TÍNH NĂNG:
• 🔗 Scrape thông tin chi tiết sản phẩm Amazon
• 🔍 Scrape nhiều sản phẩm từ search results  
• 🖥️ Giao diện đồ họa đầy đủ với tkinter
• 💾 Lưu kết quả dưới dạng JSON
• 🌐 Mở sản phẩm trong trình duyệt
• 🌍 Hỗ trợ nhiều domain Amazon (.com, .co.uk, .de, etc.)
• 📊 Theo dõi tiến độ scraping
• ⚡ Rate limiting tự động
• 🛡️ Tất cả trong 1 file duy nhất!

🎯 THÔNG TIN ĐƯỢC SCRAPE:
• Tên, giá, đánh giá, reviews
• ASIN, thương hiệu, màu sắc, chất liệu  
• Kích thước, trọng lượng, model
• Tình trạng, shipping, seller
• Đặc điểm, mô tả, thông số kỹ thuật
• Hình ảnh, danh mục, variations
• Prime eligibility, bestseller rank

⚠️ LƯU Ý:
• Chỉ sử dụng cho mục đích học tập
• Tôn trọng robots.txt và ToS của Amazon
• Không spam requests
• Thêm delay hợp lý giữa requests

🔧 Phát triển bởi: AI Assistant
📅 Năm: 2024

🌟 Enjoy scraping responsibly! 🌟"""
        
        messagebox.showinfo("ℹ️ Về chương trình", about_text)

# ===================================================================
# MAIN FUNCTION - CHỈ GUI
# ===================================================================

def main():
    """Main function - GUI only version"""
    # Check dependencies
    try:
        print("🔍 Đang kiểm tra dependencies...")
        import requests
        import bs4
        print("✅ Dependencies check: OK")
    except ImportError as e:
        print(f"❌ Thiếu thư viện cần thiết: {e}")
        print("📥 Cài đặt bằng lệnh:")
        print("   pip install requests beautifulsoup4 lxml")
        messagebox.showerror("❌ Lỗi Dependencies", 
                           f"Thiếu thư viện: {e}\n\nHãy chạy lệnh:\npip install requests beautifulsoup4 lxml")
        sys.exit(1)
    
    print("🚀 Khởi động Amazon Scraper GUI...")
    
    # Create and run GUI
    try:
        root = tk.Tk()
        app = AmazonScraperGUI(root)
        
        # Handle window closing
        def on_closing():
            if messagebox.askokcancel("🚪 Thoát", "Bạn có muốn thoát Amazon Scraper?"):
                print("👋 Đã thoát Amazon Scraper GUI.")
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        print("✅ GUI khởi động thành công!")
        print("📋 Hướng dẫn sử dụng có trong giao diện.")
        
        # Start GUI main loop
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Không thể khởi động GUI: {e}"
        print(f"❌ {error_msg}")
        messagebox.showerror("❌ Lỗi GUI", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main() 