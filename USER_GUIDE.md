# 📘 User Guide - Retail Investor Behavior Analysis System

**A Complete Guide to Analyzing Stock Market Behavioral Patterns**

---

## 📚 Table of Contents

1. [Quick Start (5 Minutes)](#-quick-start-5-minutes)
2. [Installation](#-installation)
3. [Understanding the System](#-understanding-the-system)
4. [Usage Methods](#-usage-methods)
5. [Step-by-Step Tutorials](#-step-by-step-tutorials)
6. [Understanding Outputs](#-understanding-outputs)
7. [Common Use Cases](#-common-use-cases)
8. [Troubleshooting](#-troubleshooting)
9. [FAQ](#-faq)
10. [Tips & Best Practices](#-tips--best-practices)

---

## ⚡ Quick Start (5 Minutes)

### For Absolute Beginners

```bash
# Step 1: Install Python (if not installed)
# Download from https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation

# Step 2: Open Command Prompt / Terminal

# Step 3: Navigate to project folder
cd path/to/stock-behavior-analysis

# Step 4: Install requirements
pip install -r requirements.txt

# Step 5: Run your first analysis
python main.py

# Done! Your analysis is complete!
```

**What just happened?**
- Downloaded stock data for Apple (AAPL) from last 6 months
- Detected emotional trading patterns (Panic, FOMO, Overconfidence)
- Created visualizations showing all patterns
- Generated insights and recommendations

**Check your results:**
- 📊 `AAPL_behavior_analysis.csv` - All data
- 📈 `investor_behavior_analysis.png` - Visualizations
- 💻 Console - Detailed insights

---

## 🛠️ Installation

### Prerequisites

- **Python 3.8 or higher** ([Download here](https://www.python.org/downloads/))
- **Internet connection** (for downloading stock data)
- **Text editor or IDE** (VSCode recommended)

### Step-by-Step Installation

#### Windows

```bash
# 1. Create project folder
mkdir stock-behavior-analysis
cd stock-behavior-analysis

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate

# 4. Install dependencies
pip install yfinance pandas numpy matplotlib seaborn scikit-learn vaderSentiment openpyxl xlrd missingno

# 5. Save requirements
pip freeze > requirements.txt
```

#### Mac/Linux

```bash
# 1. Create project folder
mkdir stock-behavior-analysis
cd stock-behavior-analysis

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies
pip install yfinance pandas numpy matplotlib seaborn scikit-learn vaderSentiment openpyxl xlrd missingno

# 5. Save requirements
pip freeze > requirements.txt
```

### Verify Installation

```bash
python -c "import yfinance; import pandas; print('✅ Installation successful!')"
```

If you see `✅ Installation successful!` - you're ready!

---

## 🧠 Understanding the System

### What Does This System Do?

This system analyzes stock market data to detect **emotional trading patterns** of retail investors:

1. **🔴 Panic Selling** - Detecting when investors sell out of fear during market drops
2. **🟢 FOMO Buying** - Detecting when investors buy out of fear of missing gains
3. **🟡 Overconfidence** - Detecting excessive trading without clear price direction

### Why Is This Useful?

- **Contrarian Opportunities**: When everyone panics, it might be a buying opportunity
- **Risk Assessment**: Understand market sentiment and volatility
- **Better Timing**: Identify overbought (FOMO) or oversold (Panic) conditions
- **Educational**: Learn how emotions drive markets

### How Does It Work?

```
📥 INPUT DATA
   ↓
🧹 DATA CLEANING (removes errors, handles missing values)
   ↓
🔧 FEATURE ENGINEERING (calculates volatility, volume spikes)
   ↓
🔍 BEHAVIOR DETECTION (identifies panic, FOMO, overconfidence)
   ↓
📊 VISUALIZATION (creates charts and graphs)
   ↓
💡 INSIGHTS (generates recommendations)
   ↓
📤 OUTPUT (CSV files, images, reports)
```

---

## 🎮 Usage Methods

### Method 1: Analyze Stocks from Yahoo Finance (Easiest)

**Use when:** You want to analyze any stock ticker using live data

**Steps:**
```bash
# 1. Open main.py in text editor
# 2. Find this section (around line 450):
TICKER = 'AAPL'  # Change to any ticker
PERIOD = '6mo'   # Change time period

# 3. Run
python main.py

# 4. Check results in current folder
```

**Example tickers to try:**
- `AAPL` - Apple
- `TSLA` - Tesla
- `MSFT` - Microsoft
- `RELIANCE.NS` - Reliance (India)
- `TCS.NS` - TCS (India)

---

### Method 2: Analyze Your Own CSV/Excel Files

**Use when:** You have stock data from broker, downloaded CSV, or custom data

**Steps:**
```bash
# 1. Place your file in data/raw/ folder
# 2. Run the file analyzer
python analyze_from_file.py

# 3. Choose option 3 (Analyze specific file)
# 4. Enter file path: data/raw/your_file.csv
# 5. Enter ticker name: YOUR_STOCK

# 6. Check results in output/ folder
```

**Your file should have these columns:**
- `Date` - Trading date
- `Open` - Opening price
- `High` - Highest price
- `Low` - Lowest price
- `Close` - Closing price
- `Volume` - Trading volume

**Example CSV format:**
```csv
Date,Open,High,Low,Close,Volume
2024-01-01,100.5,102.3,99.8,101.2,1500000
2024-01-02,101.3,103.5,100.9,102.8,1800000
```

---

### Method 3: Interactive Mode (User-Friendly)

**Use when:** You want guided step-by-step experience

```bash
python analyze_from_file.py
```

**Menu options:**
```
📋 Options:
   1. Interactive file analysis     ← Lists all files, you choose
   2. Batch analyze all files       ← Analyzes everything at once
   3. Analyze specific file         ← Direct file path
   4. Quick demo with sample data   ← Test with sample data
   5. Exit
```

---

### Method 4: Command Line (Advanced)

**Use when:** You want quick one-liner analysis

```bash
# Analyze single stock
python main.py --ticker TSLA --period 1y

# Clean a file
python -c "from data_cleaner import quick_clean; quick_clean('data/raw/file.csv')"

# Batch process
python -c "from file_processor import FileProcessor; from data_cleaner import StockDataCleaner; FileProcessor().batch_process(StockDataCleaner())"
```

---

## 📖 Step-by-Step Tutorials

### Tutorial 1: Analyze Apple Stock

**Goal:** Analyze AAPL for last 6 months and understand panic selling events

```bash
# Step 1: Open config.py or main.py
# Step 2: Change these lines:
TICKER = 'AAPL'
PERIOD = '6mo'

# Step 3: Run
python main.py

# Step 4: Open the generated image
# File: AAPL_behavior_analysis.png
```

**What to look for:**
- Red dots on price chart = Panic selling days
- Green dots = FOMO buying days
- Yellow dots = Overconfidence days

**Reading insights:**
```
🔴 PANIC SELLING DETECTED:
   📅 2024-08-05:
      Price Drop: -4.85%        ← Big drop
      Volume Spike: 3.2σ        ← Much higher trading
      Volatility: 4.12%         ← Market uncertainty
```

**This means:** On Aug 5, many investors sold in panic, creating potential buying opportunity

---

### Tutorial 2: Analyze Indian Stock (Reliance)

**Goal:** Analyze Reliance Industries for 1 year

```bash
# Step 1: Edit config.py
TICKER = 'RELIANCE.NS'  # .NS for NSE stocks
PERIOD = '1y'

# Step 2: Run
python main.py

# Step 3: Check results
# File: RELIANCE.NS_behavior_analysis.png
```

**Indian Stock Tickers:**
- Add `.NS` for NSE stocks: `RELIANCE.NS`, `TCS.NS`
- Add `.BO` for BSE stocks: `RELIANCE.BO`

---

### Tutorial 3: Clean and Analyze Custom CSV File

**Goal:** You have data from broker, clean it and analyze

```bash
# Step 1: Create sample data for testing
python create_sample_data.py

# Step 2: Run file analyzer
python analyze_from_file.py

# Step 3: Choose option 1 (Interactive)

# Step 4: You'll see:
📁 Available data files:
   1. sample_with_missing.csv (15.2 KB)
   2. sample_clean_data.csv (12.8 KB)

Enter file number: 1

# Step 5: Enter ticker name
Enter ticker name: TEST

# Step 6: Watch the magic!
```

**What happens:**
1. ✅ System loads your file
2. ✅ Detects and fixes missing values
3. ✅ Removes outliers and duplicates
4. ✅ Validates data quality (score: 0-100)
5. ✅ Analyzes behavioral patterns
6. ✅ Creates visualizations
7. ✅ Generates insights

---

### Tutorial 4: Batch Analyze Multiple Stocks

**Goal:** Compare behavior across multiple stocks

```bash
# Step 1: Place files in data/raw/
data/raw/
  ├── AAPL.csv
  ├── TSLA.csv
  └── MSFT.csv

# Step 2: Run batch analysis
python analyze_from_file.py

# Step 3: Choose option 2

# Step 4: Wait for completion

# Step 5: Check summary
# File: output/batch_analysis_summary.csv
```

**Summary table shows:**
| Stock | Panic Days | FOMO Days | Overconfidence | Avg Volatility |
|-------|-----------|-----------|----------------|----------------|
| AAPL  | 12        | 18        | 8              | 1.85%          |
| TSLA  | 25        | 32        | 15             | 3.42%          |
| MSFT  | 10        | 15        | 6              | 1.65%          |

**Interpretation:** TSLA is much more volatile and emotional!

---

## 📊 Understanding Outputs

### 1. CSV File (Complete Data)

**File:** `TICKER_behavior_analysis.csv`

**Contains:**
- All original data (Date, Open, High, Low, Close, Volume)
- Engineered features (Volatility, Volume Z-score, etc.)
- Behavior labels (Normal, Panic Selling, FOMO Buying, Overconfidence)
- Confidence scores (0-100% how confident the detection is)

**How to use:**
- Open in Excel/Google Sheets
- Filter by Behavior column
- Sort by Confidence_Score to find strongest signals

---

### 2. Visualization Image (9 Charts)

**File:** `investor_behavior_analysis.png` or `TICKER_comprehensive_analysis.png`

**Charts included:**

1. **Price with Behavior Zones**
   - Line chart of stock price
   - Colored dots show behavioral events
   - Red = Panic, Green = FOMO, Yellow = Overconfidence

2. **Volume Analysis**
   - Bar chart of daily volume
   - Line showing 20-day average
   - Spikes indicate emotional trading

3. **Volatility Index**
   - Shows market uncertainty over time
   - High volatility = more emotional trading
   - Red line = panic threshold

4. **Price Change Distribution**
   - Histogram showing how often prices move
   - Colored by behavior type
   - Shows which behaviors occur at what price changes

5. **Price vs Volume Scatter**
   - Each dot = one trading day
   - X-axis = price change
   - Y-axis = volume spike
   - Color = behavior type
   - Clusters show patterns

6. **Behavior Timeline**
   - When each behavior occurred
   - See patterns over time
   - Identify periods of market stress

7. **Momentum Indicator**
   - 5-day price momentum
   - Positive = uptrend
   - Negative = downtrend

8. **Daily Trading Range**
   - How much price varies each day
   - High range = uncertainty

9. **Weekly Heatmap**
   - Behavior frequency by week
   - Darker = more occurrences
   - Spot trends over time

---

### 3. Console Report (Text Output)

**What you see on screen:**

```
===============================================================================
                     🎯 DETAILED INSIGHTS & ANALYSIS
===============================================================================

📊 ANALYSIS PERIOD: ................ [Date range]
💰 PRICE STATISTICS: ............... [Price metrics]
📉 VOLATILITY ANALYSIS: ............ [Volatility stats]
🔍 BEHAVIORAL PATTERN ANALYSIS: .... [Behavior breakdown]
⚠️  HIGH-RISK BEHAVIOR DAYS: ....... [Top incidents]
💡 INVESTMENT INSIGHTS: ............ [Recommendations]
🎲 RISK ASSESSMENT: ................ [Risk level]
```

**How to read:**

- **Price Statistics**: Overall performance
- **Volatility**: Market stability
- **Behavior Breakdown**: % of each behavior
- **Top Incidents**: Most significant events
- **Recommendations**: Actionable insights
- **Risk Level**: Overall assessment (Low/Moderate/High)

---

### 4. Data Cleaning Report

**When analyzing files, you get:**

```
📋 DATA CLEANING REPORT
==================================================
📊 ORIGINAL DATA:
   Total rows: 250

🧹 CLEANING ACTIONS:
   Missing values found: 12
   Missing values handled: 12
   Duplicates removed: 3
   Outliers detected: 5
   Outliers removed: 5

✅ CLEANED DATA:
   Total rows: 242
   Rows removed: 8

🎯 DATA QUALITY SCORE: 92.5/100
   Rating: Excellent ⭐⭐⭐⭐⭐
```

**Quality Score Guide:**
- 90-100: Excellent ⭐⭐⭐⭐⭐ (Ready to use)
- 75-89: Good ⭐⭐⭐⭐ (Minor issues fixed)
- 60-74: Fair ⭐⭐⭐ (Significant cleaning done)
- Below 60: Poor ⭐⭐ (Major data issues)

---

## 🎯 Common Use Cases

### Use Case 1: Finding Buying Opportunities

**Scenario:** You want to find stocks after panic selling (potential bottom)

**Steps:**
```bash
# 1. Analyze stock
python main.py  # Set TICKER = 'AAPL'

# 2. Open CSV file
# 3. Filter: Behavior = "Panic Selling"
# 4. Sort by: Confidence_Score (descending)

# 5. Look for:
# - High confidence panic days
# - Check if fundamentals are still strong
# - Consider buying opportunity
```

**Investment Logic:**
- Panic selling often overdone
- Emotional selling creates value
- **But always verify fundamentals!**

---

### Use Case 2: Identifying Exit Points

**Scenario:** You hold a stock and want to know when FOMO is high

**Steps:**
```bash
# 1. Analyze your holding
TICKER = 'TSLA'  # Your stock
PERIOD = '6mo'

python main.py

# 2. Look for FOMO buying clusters
# 3. Check recent trends section
# 4. If seeing multiple FOMO days recently:
#    → Stock might be overbought
#    → Consider taking partial profits
```

---

### Use Case 3: Risk Assessment Before Investment

**Scenario:** Evaluating if stock is too volatile

**Steps:**
```bash
# 1. Analyze stock
python main.py

# 2. Check Risk Assessment section:
Risk Level: HIGH RISK ⚠️⚠️⚠️
High-Risk Days: 75 (30.0%)

# 3. Decision:
# - High risk (>30%) = Very volatile, risky
# - Moderate (20-30%) = Normal volatility
# - Low (<10%) = Stable stock
```

---

### Use Case 4: Comparing Multiple Stocks

**Scenario:** Choose between 3 stocks for investment

**Steps:**
```bash
# 1. Create files for each stock OR use batch mode

# 2. Run batch analysis
python analyze_from_file.py
# Choose option 2

# 3. Open: output/batch_analysis_summary.csv

# 4. Compare:
# - Panic_Selling_Days (fewer = more stable)
# - Avg_Volatility (lower = less risky)
# - Total_Return (higher = better performance)
```

---

### Use Case 5: Educational Learning

**Scenario:** Student learning behavioral finance

**Steps:**
```bash
# 1. Create sample data
python create_sample_data.py

# 2. Analyze different files
# - sample_with_missing.csv (learn data cleaning)
# - sample_with_outliers.xlsx (learn outlier detection)
# - sample_clean_data.csv (learn behavior detection)

# 3. Study the outputs
# 4. Modify thresholds in code to see changes
```

---

## 🔧 Troubleshooting

### Problem 1: "python not recognized"

**Error:**
```
'python' is not recognized as an internal or external command
```

**Solution:**
```bash
# Windows: Find Python path
where python

# If not found, reinstall Python
# Make sure to check "Add Python to PATH"
# Or use full path:
C:\Users\YourName\AppData\Local\Programs\Python\Python39\python.exe main.py

# Mac/Linux: Use python3
python3 main.py
```

---

### Problem 2: "No module named 'yfinance'"

**Error:**
```
ModuleNotFoundError: No module named 'yfinance'
```

**Solution:**
```bash
# Make sure virtual environment is activated
# You should see (venv) in terminal

# Activate it:
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Then install:
pip install yfinance
```

---

### Problem 3: "No data retrieved for ticker"

**Error:**
```
❌ Error fetching data: No data retrieved
```

**Solutions:**
1. Check ticker spelling: `AAPL` not `APPL`
2. For Indian stocks, add `.NS`: `RELIANCE.NS`
3. Check internet connection
4. Try different period: `1mo` instead of `6mo`
5. Verify stock exists on Yahoo Finance

---

### Problem 4: Plots not showing

**Error:**
Visualizations don't appear

**Solution:**
```python
# Add this at top of main.py:
import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg'
import matplotlib.pyplot as plt
```

---

### Problem 5: "File not found"

**Error:**
```
❌ File not found: data/raw/file.csv
```

**Solution:**
```bash
# 1. Check file location
ls data/raw/  # Mac/Linux
dir data\raw\  # Windows

# 2. Create folders if missing
mkdir -p data/raw  # Mac/Linux
mkdir data\raw  # Windows

# 3. Use full path
python analyze_from_file.py
# Enter: C:\Users\YourName\Documents\file.csv
```

---

### Problem 6: Poor data quality score

**Issue:**
```
🎯 DATA QUALITY SCORE: 45.2/100
   Rating: Needs Improvement ⭐⭐
```

**What this means:**
- Your data has major issues
- Many missing values
- Many duplicates or outliers

**Solution:**
1. Check your data source
2. System already cleaned it automatically
3. Review cleaning report to see what was fixed
4. If score still low, data might be incomplete

---

## ❓ FAQ

### Q1: What stocks can I analyze?

**A:** Any stock on Yahoo Finance:
- US stocks: `AAPL`, `TSLA`, `GOOGL`
- Indian stocks (NSE): Add `.NS` → `RELIANCE.NS`
- Indian stocks (BSE): Add `.BO` → `RELIANCE.BO`
- Other exchanges: Check Yahoo Finance for ticker format

---

### Q2: How far back can I analyze?

**A:** Time periods available:
- `1mo` - 1 month
- `3mo` - 3 months
- `6mo` - 6 months (recommended)
- `1y` - 1 year
- `2y` - 2 years
- `5y` - 5 years
- `max` - All available data

**Recommendation:** Use `6mo` to `1y` for best balance

---

### Q3: Can I use my own data files?

**A:** Yes! Your file needs:
- CSV or Excel format
- Columns: Date, Open, High, Low, Close, Volume
- Clean dates in format: YYYY-MM-DD

Place file in `data/raw/` and run `analyze_from_file.py`

---

### Q4: What do the behavior labels mean?

**A:**

| Behavior | Meaning | Investment Implication |
|----------|---------|----------------------|
| **Normal** | Regular trading | No special action |
| **Panic Selling** | Fear-driven selling | Potential buying opportunity |
| **FOMO Buying** | Greed-driven buying | Stock might be overbought |
| **Overconfidence** | Excessive trading | Market indecision, wait |

---

### Q5: How accurate is this system?

**A:** This is a **detection tool**, not a prediction tool:
- ✅ Accurately identifies abnormal trading patterns
- ✅ Highlights emotional market events
- ❌ Does NOT predict future prices
- ❌ Does NOT guarantee investment returns

**Always:**
- Verify with fundamental analysis
- Check company news
- Use as ONE input in decision-making

---

### Q6: Can I change detection thresholds?

**A:** Yes! Edit `config.py`:

```python
# Make panic detection more strict
PANIC_PRICE_THRESHOLD = -4.0  # Default: -2.5
PANIC_VOLUME_THRESHOLD = 2.0   # Default: 1.5

# Make FOMO detection more sensitive
FOMO_PRICE_THRESHOLD = 2.0     # Default: 2.5
```

---

### Q7: How do I analyze multiple stocks at once?

**A:** Use batch mode:
```bash
# Place all CSV files in data/raw/
# Run:
python analyze_from_file.py
# Choose option 2
```

Or create a script:
```python
stocks = ['AAPL', 'TSLA', 'MSFT', 'GOOGL']

for stock in stocks:
    # Edit config.py with stock ticker
    # Run main.py
    # Results auto-saved with ticker name
```

---

### Q8: What's the difference between main.py and analyze_from_file.py?

**A:**

| Feature | main.py | analyze_from_file.py |
|---------|---------|---------------------|
| Data source | Yahoo Finance | Your files |
| Data cleaning | Basic | Comprehensive |
| Quality report | No | Yes |
| File formats | - | CSV, Excel, JSON |
| Batch mode | No | Yes |
| Use when | Quick online analysis | Thorough file analysis |

---

### Q9: Is this system suitable for day trading?

**A:** **No.** This system:
- ✅ Good for: Swing trading, position sizing, risk assessment
- ❌ Not for: Day trading, high-frequency trading, minute-by-minute decisions
- Uses daily data, not intraday
- Behavioral patterns take days/weeks to develop

---

### Q10: Can I use this for my project/thesis?

**A:** Yes! This is designed for:
- ✅ Academic projects
- ✅ Data science portfolios
- ✅ Fintech demonstrations
- ✅ Learning behavioral finance

**Just cite appropriately and understand the code!**

---

## 💡 Tips & Best Practices

### ✅ DO:

1. **Start with well-known stocks** (AAPL, MSFT) to verify system works
2. **Use 6mo-1y period** for best pattern detection
3. **Check data quality score** before trusting results
4. **Compare multiple stocks** to understand relative risk
5. **Verify with news** why panic/FOMO occurred
6. **Use confidence scores** to filter weak signals
7. **Keep virtual environment activated** when running
8. **Save outputs** with clear file names

### ❌ DON'T:

1. **Don't rely solely on this** for investment decisions
2. **Don't ignore fundamentals** (earnings, debt, growth)
3. **Don't trade based on single panic/FOMO signal**
4. **Don't use on penny stocks** (low quality data)
5. **Don't analyze very short periods** (<1 month)
6. **Don't modify detection code** without understanding it
7. **Don't expect 100% accuracy** - markets are complex
8. **Don't share API keys** if you add them later

---

### 🎯 Analysis Workflow (Recommended)

```
1. Research → Pick stocks to analyze
   ↓
2. Download → Use main.py for online data
   ↓
3. Clean → Use analyze_from_file.py for your files
   ↓
4. Analyze → Review all outputs
   ↓
5. Compare → Batch analyze similar stocks
   ↓
6. Verify → Check news, fundamentals
   ↓
7. Decide → Make informed investment choice
   ↓
8. Document → Save analysis for records
```

---

### 📚 Learning Path

**Week 1:** Understand basics
- Run on 3-4 major stocks
- Read all outputs carefully
- Understand each behavior type

**Week 2:** Experiment
- Try different time periods
- Modify thresholds
- Compare similar sector stocks

**Week 3:** Advanced usage
- Batch process multiple stocks
- Clean your own data files
- Create custom analysis scripts

**Week 4:** Master
- Combine with fundamental analysis
- Track predictions vs reality
- Build investment strategy

---

### 🎓 For Students/Academics

**Project Ideas:**
1. Compare tech vs financial sector behavioral patterns
2. Study pandemic period panic selling events
3. Analyze correlation between news sentiment and FOMO
4. Compare Indian vs US market emotional patterns
5. Build a trading strategy based on panic buying

**Report Structure:**
1. Introduction (Why study behavior?)
2. Literature Review (Behavioral finance)
3. Methodology (Your detection logic)
4. Data & Cleaning (Quality scores)
5. Results (Visualizations, statistics)
6. Analysis (What patterns found?)
7. Limitations (What doesn't work?)
8. Future Work (How to improve?)
9. Conclusion

---

## 📞 Getting Help

### Check these first:
1. **This User Guide** - Most questions answered here
2. **README.md** - Technical setup details
3. **Code comments** - Inline explanations
4. **Console output** - Error messages are descriptive

### Still stuck?
1. Check Python version: `python --version` (need 3.8+)
2. Verify installation: `pip list`
3. Review error message carefully
4. Check file paths are correct
5. Ensure virtual environment is activated

---

## 🎉 Success Checklist

You know you're using the system correctly when:

- ✅ No errors during execution
- ✅ Data quality score > 80
- ✅ Visualizations look clear and colorful
- ✅ Behavior detection makes sense (not all one type)
- ✅ CSV file opens properly in Excel
- ✅ Insights match your understanding of the stock
- ✅ You can explain what panic selling means
- ✅ You understand limitations

---

## 🚀 Next Steps

**Beginner:** Master basic analysis
1. Analyze 10 different stocks
2. Understand all visualizations
3. Read every insight report

**Intermediate:** Customize and experiment
1. Modify detection thresholds
2. Add new features
3. Compare across sectors

**Advanced:** Build on top
1. Add real-time alerts
2. Integrate news sentiment
3. Build trading strategies
4. Create automated reports

---

**Happy Analyzing! 📊**

*Remember: This is a tool to understand market behavior, not a crystal ball for future prices. Always do your own research!*

---

**Version:** 1.0  
**Last Updated:** February 2025  
**Maintained by:** Data Science Team