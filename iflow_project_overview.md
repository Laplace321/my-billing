# Bill Converter Project Overview

## Project Description
This is a Python-based bill conversion tool that converts Alipay, WeChat, and bank credit card billing data into a format compatible with MoneyPro. The tool supports multiple bill formats, intelligent classification, cross-platform transfer detection and deduplication, investment transaction filtering, and automatic recognition of salary and provident fund income.

## Key Features
1. **Multi-format Bill Support**: Parse CSV (Alipay), Excel (WeChat), and PDF (Bank) bill formats
2. **Intelligent Classification**: Automatically categorize transactions based on transaction descriptions
3. **Cross-platform Transfer Detection**: Identify and deduplicate cross-platform transfers
4. **Investment Transaction Filtering**: Filter out investment-related transactions
5. **Income Recognition**: Automatically identify salary and housing provident fund income
6. **Asset Recording**: Export current asset snapshots
7. **Incremental Data Import**: SQLite database supports incremental bill data import with deduplication
8. **Smart Deduplication**: Generate unique keys based on amount, date, source account, description, and agent

## Project Structure
```
.
├── asset_converter.py              # Asset information conversion script
├── bill_converter/                 # Main bill conversion module
│   ├── __init__.py
│   ├── alipay/                     # Alipay bill processing module
│   │   ├── __init__.py
│   │   └── parser.py
│   ├── bank/                       # Bank bill processing module
│   │   ├── __init__.py
│   │   └── parser.py
│   ├── cli.py                      # Command-line interface
│   ├── config.py                   # Configuration file
│   ├── data/                       # Data files
│   │   └── category_keywords.json  # Classification keywords
│   ├── main.py                     # Main program entry point
│   ├── moneypro/                   # MoneyPro format export module
│   │   ├── __init__.py
│   │   └── exporter.py
│   ├── tests/                      # Test modules
│   │   ├── __init__.py
│   │   └── test_alipay_parser.py
│   ├── utils/                      # Utility modules
│   │   ├── __init__.py
│   │   ├── converter.py
│   │   └── deduplicator.py
│   └── wechat/                     # WeChat bill processing module
│       ├── __init__.py
│       └── parser.py
├── metabase/                       # Metabase integration directory
│   ├── data/                       # Data directory (auto-generated)
│   ├── docker-compose.yml          # Docker deployment configuration
│   ├── import_data.py              # Data import script
│   └── nginx.conf                  # Nginx reverse proxy configuration
├── out/                            # Output directory
├── raw_assets/                     # Raw asset information directory
├── raw_bills/                      # Raw bill files directory
├── requirements.txt                # Project dependencies
├── run_complete_process.py         # Complete bill processing workflow script
├── setup.py                        # Package setup file
└── venv/                           # Virtual environment (git-ignored)
```

## Dependencies
- pandas>=1.3.0 (CSV processing)
- openpyxl>=3.0.0 (Excel file processing)
- PyPDF2>=3.0.0 (PDF processing)
- click>=8.0.0 (Command-line interface)
- chardet>=5.0.0 (Character encoding detection)
- pytest>=6.2.4 (Testing framework)
- black>=21.5b2 (Code formatting)
- flake8>=3.9.2 (Code checking)
- jieba>=0.42.1 (Chinese word segmentation)
- forex-python>=1.8 (Exchange rate retrieval)

## Installation
1. Clone the project:
   ```bash
   git clone <project-url>
   cd billing-converter
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Method 1: Step-by-step execution (recommended for debugging and learning)
1. **Process bill files**:
   ```bash
   python bill_converter/main.py --auto
   ```

2. **Process asset information**:
   ```bash
   python asset_converter.py
   ```

3. **Import data to Metabase**:
   ```bash
   cd metabase && python import_data.py
   ```

4. **Start Metabase service**:
   ```bash
   cd metabase && docker-compose up -d
   ```

### Method 2: One-click execution (recommended for daily use)
Use the integrated script to execute the complete bill processing workflow:
```bash
python run_complete_process.py
```

Options:
- `--no-services`: Process bills and import data without starting services
- `--manual-bills`: Manual bill processing (non-auto mode)

Access URL: https://billing.local

## Key Components

### 1. Bill Processing (`bill_converter/`)
- **Alipay Parser**: Handles CSV format Alipay bills
- **WeChat Parser**: Handles Excel format WeChat bills
- **Bank Parser**: Handles PDF format bank bills (initially supports CMB)
- **Converter**: Converts parsed data to MoneyPro format
- **Deduplicator**: Removes duplicate transactions across platforms

### 2. Asset Processing (`asset_converter.py`)
Converts raw asset information into timestamped CSV format with:
- Currency conversion to CNY
- Asset/Liability classification

### 3. Metabase Integration (`metabase/`)
- Imports processed bill data into SQLite database
- Provides Docker Compose configuration for Metabase deployment
- Uses Nginx as reverse proxy for domain access
- Default domain: `billing.local`

### 4. Complete Process (`run_complete_process.py`)
Orchestrates the entire workflow:
1. Process raw bill files
2. Process raw asset files
3. Import data to Metabase
4. Start Metabase services

## Configuration
The main configuration is in `bill_converter/config.py`:
- `MONEYPRO_FIELDS`: Fields supported by MoneyPro
- `DEFAULT_ACCOUNT_MAP`: Default account mappings
- `DEFAULT_OUTPUT_DIR`: Default output directory
- `DEFAULT_BILLS_DIR`: Default bills input directory
- `DEFAULT_ASSETS_DIR`: Default assets input directory

## Data Classification
The system uses keyword-based classification defined in `bill_converter/data/category_keywords.json`. Categories include:
- Food
- Clothing
- Transportation
- Family
- Housing
- Groceries
- Entertainment
- Shopping
- Education
- Medical
- Travel
- Digital
- Insurance
- Investment
- Debt
- Daily expenses
- Salary
- Housing provident fund

## Database Maintenance
If test data or duplicate records are accidentally written to the database, they can be cleaned with SQL:
```sql
-- Delete duplicate asset records (keep the one with minimum ROWID in each group)
DELETE FROM assets_records WHERE ROWID NOT IN (
    SELECT MIN(ROWID) 
    FROM assets_records 
    GROUP BY account_category, currency, amount, description, time, cny_amount, asset_liability
);

-- Delete test bill records
DELETE FROM billing_records WHERE category IN ('Test Category', 'New Category');
```

## HTTPS Access
- Uses self-signed SSL certificates for HTTPS
- All HTTP requests are automatically redirected to HTTPS
- Default access via HTTPS: https://billing.local
- Browser security warnings are normal for self-signed certificates

## Development Guidelines
- Use relative paths in configuration to ensure portability
- Follow the existing code structure and naming conventions
- Add new classification keywords to `category_keywords.json` when needed
- Write tests for new functionality in the `tests/` directory
- Use the provided code formatting tools (black, flake8) for consistency