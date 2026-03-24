"""
===============================================================================
ENHANCED STOCK BEHAVIOR ANALYSIS SYSTEM
With Data Cleaning and File Processing
===============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
import warnings
import os
warnings.filterwarnings('ignore')

# Import cleaning modules
from data_cleaner import StockDataCleaner, quick_clean
from file_processor import FileProcessor, interactive_file_selection

# Import configuration
try:
    from config import TICKER, PERIOD
except ImportError:
    TICKER = 'TATACAPITAL.NS'
    PERIOD = '6mo'

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# ============================================================================
# ALL ORIGINAL FUNCTIONS (fetch_stock_data, engineer_features, etc.)
# ============================================================================

def fetch_stock_data(ticker, period='6mo'):
    """Fetch historical stock data from Yahoo Finance"""
    print(f"\n📊 Fetching data for {ticker}...")
    
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            raise ValueError("No data retrieved")
        
        df.reset_index(inplace=True)
        
        print(f"✅ Successfully fetched {len(df)} days of data")
        print(f"📅 Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
        
        return df
    
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def engineer_features(df):
    """Create behavioral analysis features"""
    print("\n🔧 Engineering features...")
    
    df = df.copy()
    df['Price_Change_Pct'] = df['Close'].pct_change() * 100
    df['Volume_MA20'] = df['Volume'].rolling(window=20, min_periods=1).mean()
    df['Volume_Mean'] = df['Volume'].rolling(window=20, min_periods=1).mean()
    df['Volume_Std'] = df['Volume'].rolling(window=20, min_periods=1).std()
    df['Volume_Zscore'] = (df['Volume'] - df['Volume_Mean']) / df['Volume_Std']
    df['Volume_Zscore'].fillna(0, inplace=True)
    df['Volatility'] = df['Price_Change_Pct'].rolling(window=7, min_periods=1).std()
    df['Momentum_5d'] = df['Close'].pct_change(periods=5) * 100
    
    print(f"✅ Features engineered successfully")
    
    return df

def detect_investor_behavior(df):
    """Detect retail investor behavioral patterns"""
    print("\n🔍 Detecting investor behaviors...")
    
    df = df.copy()
    df['Behavior'] = 'Normal'
    
    # Detection thresholds
    panic_mask = (
        (df['Price_Change_Pct'] < -2.5) &
        (df['Volume_Zscore'] > 1.5) &
        (df['Volatility'] > 2.0)
    )
    df.loc[panic_mask, 'Behavior'] = 'Panic Selling'
    
    fomo_mask = (
        (df['Price_Change_Pct'] > 2.5) &
        (df['Volume_Zscore'] > 1.5) &
        (df['Volatility'] > 1.5)
    )
    df.loc[fomo_mask, 'Behavior'] = 'FOMO Buying'
    
    overtrade_mask = (
        (abs(df['Price_Change_Pct']) < 1.0) &
        (df['Volume_Zscore'] > 2.0) &
        (df['Volatility'] > 1.8)
    )
    df.loc[overtrade_mask, 'Behavior'] = 'Overconfidence'
    
    behavior_counts = df['Behavior'].value_counts()
    print("\n📊 Behavior Detection Summary:")
    print("=" * 50)
    for behavior, count in behavior_counts.items():
        percentage = (count / len(df)) * 100
        print(f"   {behavior:20s}: {count:3d} days ({percentage:5.1f}%)")
    print("=" * 50)
    
    return df

def create_visualizations(df, ticker):
    """Create comprehensive visualizations (same as before)"""
    # [Copy the full visualization function from main.py]
    print("\n📈 Creating visualizations...")
    print("✅ Visualizations created (function simplified for demo)")
    pass

def generate_insights(df, ticker):
    """Generate actionable insights (same as before)"""
    # [Copy the full insights function from main.py]
    print("\n🎯 Generating insights...")
    print("✅ Insights generated (function simplified for demo)")
    pass

# ============================================================================
# NEW: ENHANCED MAIN WITH DATA CLEANING
# ============================================================================

def main_with_cleaning():
    """
    Enhanced main function with data cleaning options
    """
    print("=" * 70)
    print(" " * 10 + "ENHANCED STOCK BEHAVIOR ANALYSIS SYSTEM")
    print(" " * 15 + "With Data Cleaning & Processing")
    print("=" * 70)
    
    # Ask user for data source
    print("\n📊 Select data source:")
    print("   1. Download from Yahoo Finance (online)")
    print("   2. Load from local file (CSV/Excel)")
    print("   3. Interactive file selection")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    df = None
    ticker_name = TICKER
    
    # ========== OPTION 1: Download from Yahoo Finance ==========
    if choice == '1':
        ticker = input(f"\n🎯 Enter ticker symbol (default: {TICKER}): ").strip().upper()
        ticker = ticker if ticker else TICKER
        
        period = input(f"📅 Enter period (default: {PERIOD}): ").strip()
        period = period if period else PERIOD
        
        ticker_name = ticker
        
        df = fetch_stock_data(ticker, period)
        
        if df is not None:
            # Clean the downloaded data
            print("\n🧹 Cleaning downloaded data...")
            cleaner = StockDataCleaner(verbose=True)
            df = cleaner.clean_pipeline(df, remove_outliers_flag=False)
            cleaner.generate_cleaning_report()
    
    # ========== OPTION 2: Load from File ==========
    elif choice == '2':
        filepath = input("\n📁 Enter file path (e.g., data/stock_data.csv): ").strip()
        
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            return
        
        # Use data cleaner
        print("\n🧹 Loading and cleaning data from file...")
        df = quick_clean(filepath, remove_outliers=True)
        
        # Extract ticker from filename
        ticker_name = os.path.basename(filepath).split('_')[0].split('.')[0].upper()
    
    # ========== OPTION 3: Interactive Selection ==========
    elif choice == '3':
        selected_file = interactive_file_selection()
        
        if selected_file:
            df = quick_clean(str(selected_file), remove_outliers=True)
            ticker_name = selected_file.stem.upper()
    
    else:
        print("❌ Invalid choice")
        return
    
    # ========== Proceed with Analysis ==========
    if df is None or df.empty:
        print("❌ No data to analyze. Exiting...")
        return
    
    print("\n" + "=" * 70)
    print(" " * 20 + "🚀 STARTING ANALYSIS")
    print("=" * 70)
    
    # Engineer features
    df = engineer_features(df)
    
    # Detect behaviors
    df = detect_investor_behavior(df)
    
    # Create visualizations
    create_visualizations(df, ticker_name)
    
    # Generate insights
    generate_insights(df, ticker_name)
    
    # Save results
    output_file = f'{ticker_name}_behavior_analysis.csv'
    df.to_csv(output_file, index=False)
    print(f"\n💾 Analysis saved to '{output_file}'")
    
    print("\n✅ Analysis complete!")
    print("=" * 70)


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def show_menu():
    """Show main menu"""
    print("\n" + "=" * 70)
    print(" " * 15 + "STOCK BEHAVIOR ANALYSIS SYSTEM")
    print("=" * 70)
    print("\n📋 Main Menu:")
    print("   1. Analyze single stock (Yahoo Finance)")
    print("   2. Analyze from file (with cleaning)")
    print("   3. Batch process multiple files")
    print("   4. Data cleaning only")
    print("   5. Exit")
    print("=" * 70)
    
    return input("\nEnter choice (1-5): ").strip()

def main():
    """Main menu-driven interface"""
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            # Single stock analysis
            main_with_cleaning()
        
        elif choice == '2':
            # File analysis with cleaning
            filepath = input("\n📁 Enter file path: ").strip()
            if os.path.exists(filepath):
                df = quick_clean(filepath, remove_outliers=True)
                if df is not None:
                    ticker = input("Enter ticker name for this data: ").strip().upper()
                    df = engineer_features(df)
                    df = detect_investor_behavior(df)
                    df.to_csv(f'{ticker}_analyzed.csv', index=False)
                    print(f"✅ Saved to {ticker}_analyzed.csv")
        
        elif choice == '3':
            # Batch processing
            processor = FileProcessor()
            cleaner = StockDataCleaner(verbose=True)
            processor.batch_process(cleaner)
        
        elif choice == '4':
            # Data cleaning only
            filepath = input("\n📁 Enter file to clean: ").strip()
            output = input("📁 Enter output path (optional): ").strip()
            output = output if output else None
            
            quick_clean(filepath, output_path=output, remove_outliers=True)
        
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()