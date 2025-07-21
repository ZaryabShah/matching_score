# Dynamic Target.com Product Scraper

A robust, dynamic scraper for Target.com that can handle any search query and never fails. Built with advanced error handling, rate limiting, and proxy support.

## Features

✅ **Dynamic Search**: Works with any search term/keyword  
✅ **Robust Error Handling**: Built to never fail  
✅ **Rate Limiting**: Avoids getting blocked  
✅ **Proxy Support**: Uses rotating proxies for reliability  
✅ **Rich Data Extraction**: Gets prices, ratings, images, availability  
✅ **Multiple Output Formats**: JSON files with timestamps  
✅ **CLI Interface**: Easy command-line usage  
✅ **Interactive Mode**: User-friendly prompts  

## Quick Start

### Option 1: Windows Batch File (Easiest)
```bash
# Search for "gaming chair"
run_target_search.bat "gaming chair"

# Interactive mode
run_target_search.bat
```

### Option 2: Python CLI
```bash
# Install dependencies
pip install -r requirements.txt

# Search for products
python target_search_cli.py "bluetooth speaker"

# With options
python target_search_cli.py "office chair" --max 50 --no-proxy

# Interactive mode
python target_search_cli.py
```

### Option 3: Python Script
```python
from dynamic_target_scraper import TargetScraper

# Initialize scraper
scraper = TargetScraper(proxy="your_proxy_url", use_proxy=True)

# Search and extract
products = scraper.search_and_extract("gaming chair", max_products=25)

# Results are automatically saved to JSON files
```

## Configuration

Edit `config.json` to customize:

```json
{
    "proxy": {
        "enabled": true,
        "url": "http://your_proxy_url"
    },
    "location": {
        "zip": "20109",
        "state": "VA",
        "store_id": "2323"
    },
    "scraping": {
        "min_delay": 1,
        "max_delay": 3,
        "max_retries": 3
    }
}
```

## File Structure

```
Product_matcher/
├── dynamic_target_scraper.py    # Main scraper class
├── target_search_cli.py         # Command-line interface
├── run_target_search.bat        # Windows batch file
├── config.json                  # Configuration file
├── requirements.txt             # Python dependencies
└── search_results/              # Output directory
    ├── target_search_gaming_chair_20250721_123456.json
    └── target_search_bluetooth_speaker_20250721_123457.json
```

## Output Format

Each search creates a JSON file with:

```json
{
    "metadata": {
        "search_term": "gaming chair",
        "total_found": 25,
        "timestamp": "2025-07-21T12:34:56"
    },
    "products": [
        {
            "tcin": "12345678",
            "title": "Gaming Chair with RGB Lighting",
            "price": "$199.99",
            "original_price": "$249.99",
            "brand": "SomeBrand",
            "rating": 4.5,
            "review_count": 127,
            "image_url": "https://...",
            "product_url": "https://...",
            "availability": "In Stock",
            "is_marketplace": false
        }
    ]
}
```

## Error Handling Features

- **Automatic Retries**: Failed requests are retried up to 3 times
- **Rate Limiting**: Random delays between requests (1-3 seconds)
- **Proxy Rotation**: Supports proxy usage for avoiding blocks
- **Graceful Degradation**: Continues working even if some data is missing
- **Comprehensive Logging**: Detailed logs for debugging

## Search Examples

```bash
# Electronics
python target_search_cli.py "laptop"
python target_search_cli.py "bluetooth headphones"
python target_search_cli.py "gaming mouse"

# Home & Garden
python target_search_cli.py "office chair"
python target_search_cli.py "kitchen appliances"
python target_search_cli.py "bed sheets"

# Fashion
python target_search_cli.py "winter jacket"
python target_search_cli.py "running shoes"
python target_search_cli.py "backpack"

# Any search term works!
python target_search_cli.py "your search here"
```
- Additional variant count

#### 🏷️ **Categories & Classification**
- Primary category
- Subcategories and tags
- Department classification
- Product type detection

#### 📺 **Advertising Information**
- Sponsored content detection
- Ad type identification
- Amazon brand sponsorship
- Ad tracking information

#### 🏆 **Badges & Certifications**
- Best Seller status
- Amazon's Choice badge
- Climate Pledge Friendly
- Sustainability features
- Quality indicators

#### 📊 **Additional Metadata**
- Position in search results
- Variant availability
- Prime eligibility
- Fulfillment information

## Installation

### Prerequisites
```bash
pip install beautifulsoup4 lxml
```

### Files Required
- `amazon_product_parser.py` - Main parser class
- `demo_parser.py` - Example usage script
- HTML file with Amazon search results

## Usage

### Basic Usage

```python
from amazon_product_parser import AmazonProductParser

# Initialize parser
parser = AmazonProductParser()

# Parse HTML file
result = parser.parse_html_file("amazon_response.html")

# Get results
products = result['products']
metadata = result['metadata']
total_found = result['total_products_found']

print(f"Found {total_found} products")
```

### Advanced Usage

```python
# Parse HTML content directly
html_content = open("amazon_page.html", 'r').read()
result = parser.parse_html_content(html_content)

# Save results to JSON
parser.save_to_json("products.json")

# Get parsing summary
summary = parser.get_summary()
print(f"Average rating: {summary['average_rating']}")
print(f"Price range: ${summary['price_range']['min']} - ${summary['price_range']['max']}")
```

### Running the Demo

```bash
python demo_parser.py
```

This will show:
- Parsing summary statistics
- Detailed breakdown of the first product
- All available data fields with examples

## Output Format

### JSON Structure
```json
{
  "products": [
    {
      "asin": "B07Q2PGH2T",
      "title": {
        "full_title": "Amazon Basics Swivel Foam Lounge Chair...",
        "short_title": "Amazon Basics Swivel Foam Lounge Chair...",
        "aria_label": "Sponsored Ad - Amazon Basics..."
      },
      "brand": {
        "name": "Amazon",
        "is_amazon_brand": true,
        "is_sponsored": true
      },
      "pricing": {
        "current_price": {
          "amount": 79.99,
          "currency": "USD"
        },
        "original_price": {
          "amount": 91.99,
          "currency": "USD"
        }
      },
      "images": {
        "primary": {
          "url": "https://m.media-amazon.com/images/...",
          "dimensions": {"width": 320, "height": 320}
        }
      },
      "reviews": {
        "rating": {"value": 4.3, "scale": 5},
        "count": 1987
      },
      "shipping": {
        "free_shipping": true,
        "prime_eligible": true,
        "delivery_date": {"primary": "Fri, Jul 25"}
      }
    }
  ],
  "metadata": {
    "search_query": "chairs living room",
    "total_results": "60",
    "page_type": "search_results"
  },
  "total_products_found": 60,
  "parsing_timestamp": "2025-01-21T01:20:19.123456"
}
```

### Summary Statistics
```json
{
  "total_products": 60,
  "sponsored_products": 12,
  "organic_products": 48,
  "average_rating": 4.24,
  "price_range": {"min": 47.32, "max": 1098.0},
  "products_with_reviews": 58,
  "products_with_images": 60,
  "free_shipping_count": 47
}
```

## Key Features

### 🔍 **Smart Data Extraction**
- Handles multiple HTML patterns and layouts
- Robust error handling for missing elements
- Automatic currency detection and conversion
- Price parsing with discount calculation

### 🛡️ **Reliability**
- Comprehensive error handling
- Validates extracted data
- Handles malformed HTML gracefully
- Detailed logging and debugging information

### 🔧 **Flexibility**
- Works with different Amazon page layouts
- Configurable output formats
- Extensible for additional data fields
- Support for different Amazon marketplaces

### 📊 **Analytics Ready**
- Structured JSON output
- Summary statistics generation
- Data validation and quality checks
- Easy integration with data analysis tools

## Use Cases

### 🛒 **E-commerce Analytics**
- Competitor price monitoring
- Product catalog analysis
- Market research and trends
- Inventory and availability tracking

### 📈 **Business Intelligence**
- Sales performance analysis
- Customer review sentiment
- Product positioning research
- Market share analysis

### 🤖 **Data Science & ML**
- Product recommendation systems
- Price prediction models
- Review analysis and NLP
- Computer vision with product images

### 🔍 **Research & Monitoring**
- Academic research on e-commerce
- Brand monitoring and tracking
- Product lifecycle analysis
- Consumer behavior studies

## Sample Output

Running the parser on Amazon search results for "chairs living room" extracted:

- **60 products** total
- **12 sponsored** products
- **48 organic** results
- **Average rating**: 4.24/5
- **Price range**: $47.32 - $1,098.00
- **58 products** with reviews
- **47 products** with free shipping

## Error Handling

The parser includes comprehensive error handling:
- Missing HTML elements
- Malformed price data
- Invalid image URLs
- Network timeouts
- File I/O errors

## Limitations

- Requires raw HTML content (not JavaScript-rendered pages)
- Amazon may change HTML structure over time
- Rate limiting considerations for bulk processing
- Some dynamic content may not be captured

## Contributing

Feel free to contribute improvements:
- Additional data field extraction
- Support for more Amazon marketplaces
- Enhanced error handling
- Performance optimizations

## License

This project is for educational and research purposes. Please respect Amazon's Terms of Service and robots.txt when using this parser.
#   m a t c h i n g _ s c o r e  
 