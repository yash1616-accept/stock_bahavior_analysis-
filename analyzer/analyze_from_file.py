"""
===============================================================================
COMPLETE PIPELINE: CLEAN → ANALYZE → VISUALIZE
===============================================================================
Seamlessly process files from raw data to behavioral insights
===============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

from data_cleaner import StockDataCleaner
from file_processor import FileProcessor

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)

# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

def engineer_features(df, verbose=True):
    """Create behavioral analysis features"""
    if verbose:
        print("\n🔧 Engineering behavioral features...")
    
    df = df.copy()
    
    # 1. Daily Price Change Percentage
    df['Price_Change_Pct'] = df['Close'].pct_change() * 100
    
    # 2. Volume Statistics
    df['Volume_MA20'] = df['Volume'].rolling(window=20, min_periods=1).mean()
    df['Volume_Mean'] = df['Volume'].rolling(window=20, min_periods=1).mean()
    df['Volume_Std'] = df['Volume'].rolling(window=20, min_periods=1).std()
    
    # 3. Volume Z-Score (for spike detection)
    df['Volume_Zscore'] = (df['Volume'] - df['Volume_Mean']) / df['Volume_Std']
    df['Volume_Zscore'].fillna(0, inplace=True)
    
    # 4. Volatility Index (7-day rolling std dev)
    df['Volatility'] = df['Price_Change_Pct'].rolling(window=7, min_periods=1).std()
    
    # 5. Price Momentum
    df['Momentum_5d'] = df['Close'].pct_change(periods=5) * 100
    
    # 6. Trading Range (High - Low)
    df['Daily_Range'] = ((df['High'] - df['Low']) / df['Low']) * 100
    
    # 7. Price Position (where Close is within High-Low range)
    df['Price_Position'] = ((df['Close'] - df['Low']) / (df['High'] - df['Low'])) * 100
    df['Price_Position'].fillna(50, inplace=True)
    
    if verbose:
        print("✅ Features engineered:")
        print("   - Price Change %, Volume Z-score, Volatility")
        print("   - Momentum, Daily Range, Price Position")
    
    return df

# ============================================================================
# BEHAVIOR DETECTION
# ============================================================================

def detect_investor_behavior(df, verbose=True):
    """
    Detect retail investor behavioral patterns
    
    Detection Rules:
    ----------------
    1. Panic Selling: Sharp drop + high volume + high volatility
    2. FOMO Buying: Sharp gain + high volume + volatility
    3. Overconfidence: High volume with minimal price movement
    4. Normal: Standard trading conditions
    """
    if verbose:
        print("\n🔍 Detecting investor behaviors...")
    
    df = df.copy()
    df['Behavior'] = 'Normal'
    df['Confidence_Score'] = 0.0
    
    # Panic Selling Detection
    panic_mask = (
        (df['Price_Change_Pct'] < -2.5) &
        (df['Volume_Zscore'] > 1.5) &
        (df['Volatility'] > 2.0)
    )
    df.loc[panic_mask, 'Behavior'] = 'Panic Selling'
    df.loc[panic_mask, 'Confidence_Score'] = (
        abs(df.loc[panic_mask, 'Price_Change_Pct']) / 10 +
        df.loc[panic_mask, 'Volume_Zscore'] / 5 +
        df.loc[panic_mask, 'Volatility'] / 10
    )
    
    # FOMO Buying Detection
    fomo_mask = (
        (df['Price_Change_Pct'] > 2.5) &
        (df['Volume_Zscore'] > 1.5) &
        (df['Volatility'] > 1.5)
    )
    df.loc[fomo_mask, 'Behavior'] = 'FOMO Buying'
    df.loc[fomo_mask, 'Confidence_Score'] = (
        df.loc[fomo_mask, 'Price_Change_Pct'] / 10 +
        df.loc[fomo_mask, 'Volume_Zscore'] / 5 +
        df.loc[fomo_mask, 'Volatility'] / 10
    )
    
    # Overconfidence Detection
    overtrade_mask = (
        (abs(df['Price_Change_Pct']) < 1.0) &
        (df['Volume_Zscore'] > 2.0) &
        (df['Volatility'] > 1.8)
    )
    df.loc[overtrade_mask, 'Behavior'] = 'Overconfidence'
    df.loc[overtrade_mask, 'Confidence_Score'] = (
        df.loc[overtrade_mask, 'Volume_Zscore'] / 5 +
        df.loc[overtrade_mask, 'Volatility'] / 10
    )
    
    # Normalize confidence scores
    if df['Confidence_Score'].max() > 0:
        df['Confidence_Score'] = (df['Confidence_Score'] / df['Confidence_Score'].max()) * 100
    
    behavior_counts = df['Behavior'].value_counts()
    
    if verbose:
        print("\n📊 Behavior Detection Summary:")
        print("=" * 70)
        for behavior, count in behavior_counts.items():
            percentage = (count / len(df)) * 100
            print(f"   {behavior:20s}: {count:4d} days ({percentage:5.1f}%)")
        print("=" * 70)
    
    return df

# ============================================================================
# COMPREHENSIVE VISUALIZATIONS
# ============================================================================

def create_comprehensive_visualizations(df, ticker, save_path=None):
    """Create comprehensive analysis visualizations"""
    print("\n📈 Creating comprehensive visualizations...")
    
    fig = plt.figure(figsize=(18, 14))
    
    colors = {
        'Normal': '#95a5a6',
        'Panic Selling': '#e74c3c',
        'FOMO Buying': '#2ecc71',
        'Overconfidence': '#f39c12'
    }
    
    # ========== PLOT 1: Price Chart with Behavior Zones ==========
    ax1 = plt.subplot(3, 3, 1)
    ax1.plot(df['Date'], df['Close'], linewidth=2, color='#3498db', 
            label='Close Price', alpha=0.7)
    
    for behavior in ['Panic Selling', 'FOMO Buying', 'Overconfidence']:
        behavior_days = df[df['Behavior'] == behavior]
        if not behavior_days.empty:
            ax1.scatter(behavior_days['Date'], behavior_days['Close'], 
                       color=colors[behavior], s=100, alpha=0.7, 
                       label=behavior, zorder=5, edgecolors='white', linewidth=1)
    
    ax1.set_title(f'{ticker} - Stock Price with Behavior Zones', 
                 fontsize=12, fontweight='bold', pad=10)
    ax1.set_xlabel('Date', fontsize=10)
    ax1.set_ylabel('Price ($)', fontsize=10)
    ax1.legend(loc='best', fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # ========== PLOT 2: Volume Analysis ==========
    ax2 = plt.subplot(3, 3, 2)
    ax2.bar(df['Date'], df['Volume'], alpha=0.3, color='#9b59b6', 
           label='Daily Volume')
    ax2.plot(df['Date'], df['Volume_MA20'], color='#e91e63', linewidth=2.5, 
            label='20-Day MA', linestyle='--')
    
    ax2.set_title('Trading Volume Analysis', fontsize=12, fontweight='bold', pad=10)
    ax2.set_xlabel('Date', fontsize=10)
    ax2.set_ylabel('Volume', fontsize=10)
    ax2.legend(loc='best', fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # ========== PLOT 3: Volatility Index ==========
    ax3 = plt.subplot(3, 3, 3)
    ax3.fill_between(df['Date'], df['Volatility'], alpha=0.4, color='#ff6b6b')
    ax3.plot(df['Date'], df['Volatility'], linewidth=2, color='#c92a2a', 
            label='7-Day Volatility')
    ax3.axhline(y=2, color='red', linestyle='--', alpha=0.5, 
               label='Panic Threshold')
    ax3.axhline(y=1.5, color='orange', linestyle='--', alpha=0.5, 
               label='FOMO Threshold')
    
    ax3.set_title('Volatility Index (7-Day Rolling Std Dev)', 
                 fontsize=12, fontweight='bold', pad=10)
    ax3.set_xlabel('Date', fontsize=10)
    ax3.set_ylabel('Volatility (%)', fontsize=10)
    ax3.legend(loc='best', fontsize=8)
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # ========== PLOT 4: Price Change Distribution ==========
    ax4 = plt.subplot(3, 3, 4)
    for behavior in colors.keys():
        behavior_data = df[df['Behavior'] == behavior]['Price_Change_Pct'].dropna()
        if not behavior_data.empty:
            ax4.hist(behavior_data, bins=25, alpha=0.6, label=behavior, 
                    color=colors[behavior], edgecolor='white', linewidth=0.5)
    
    ax4.axvline(x=0, color='black', linestyle='-', alpha=0.3, linewidth=1)
    ax4.set_title('Price Change Distribution by Behavior', 
                 fontsize=12, fontweight='bold', pad=10)
    ax4.set_xlabel('Price Change (%)', fontsize=10)
    ax4.set_ylabel('Frequency', fontsize=10)
    ax4.legend(loc='best', fontsize=8)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # ========== PLOT 5: Scatter - Price Change vs Volume ==========
    ax5 = plt.subplot(3, 3, 5)
    for behavior in colors.keys():
        behavior_data = df[df['Behavior'] == behavior]
        if not behavior_data.empty:
            ax5.scatter(behavior_data['Price_Change_Pct'], 
                       behavior_data['Volume_Zscore'],
                       c=colors[behavior], label=behavior, alpha=0.6, s=40,
                       edgecolors='white', linewidth=0.5)
    
    ax5.axhline(y=0, color='black', linestyle='-', alpha=0.2)
    ax5.axvline(x=0, color='black', linestyle='-', alpha=0.2)
    ax5.axhline(y=1.5, color='orange', linestyle='--', alpha=0.3)
    ax5.axvline(x=-2.5, color='red', linestyle='--', alpha=0.3)
    ax5.axvline(x=2.5, color='green', linestyle='--', alpha=0.3)
    
    ax5.set_title('Price Change vs Volume Spike', fontsize=12, fontweight='bold', pad=10)
    ax5.set_xlabel('Price Change (%)', fontsize=10)
    ax5.set_ylabel('Volume Z-Score', fontsize=10)
    ax5.legend(loc='best', fontsize=8)
    ax5.grid(True, alpha=0.3)
    
    # ========== PLOT 6: Behavior Timeline ==========
    ax6 = plt.subplot(3, 3, 6)
    behavior_map = {'Normal': 0, 'Overconfidence': 1, 'FOMO Buying': 2, 'Panic Selling': 3}
    df['Behavior_Numeric'] = df['Behavior'].map(behavior_map)
    
    for behavior, num in behavior_map.items():
        mask = df['Behavior_Numeric'] == num
        if mask.any():
            ax6.scatter(df.loc[mask, 'Date'], df.loc[mask, 'Behavior_Numeric'],
                       c=colors[behavior], s=30, alpha=0.7, label=behavior,
                       edgecolors='white', linewidth=0.5)
    
    ax6.set_yticks(list(behavior_map.values()))
    ax6.set_yticklabels(list(behavior_map.keys()), fontsize=9)
    ax6.set_title('Behavior Timeline', fontsize=12, fontweight='bold', pad=10)
    ax6.set_xlabel('Date', fontsize=10)
    ax6.set_ylabel('Detected Behavior', fontsize=10)
    ax6.grid(True, alpha=0.3, axis='x')
    ax6.tick_params(axis='x', rotation=45)
    
    # ========== PLOT 7: Momentum Indicator ==========
    ax7 = plt.subplot(3, 3, 7)
    ax7.fill_between(df['Date'], df['Momentum_5d'], alpha=0.3, 
                     color=np.where(df['Momentum_5d'] > 0, 'green', 'red'))
    ax7.plot(df['Date'], df['Momentum_5d'], linewidth=1.5, color='#34495e')
    ax7.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
    
    ax7.set_title('5-Day Price Momentum', fontsize=12, fontweight='bold', pad=10)
    ax7.set_xlabel('Date', fontsize=10)
    ax7.set_ylabel('Momentum (%)', fontsize=10)
    ax7.grid(True, alpha=0.3)
    ax7.tick_params(axis='x', rotation=45)
    
    # ========== PLOT 8: Daily Trading Range ==========
    ax8 = plt.subplot(3, 3, 8)
    ax8.fill_between(df['Date'], df['Daily_Range'], alpha=0.4, color='#3498db')
    ax8.plot(df['Date'], df['Daily_Range'], linewidth=1.5, color='#2980b9', 
            label='Daily Range %')
    
    range_ma = df['Daily_Range'].rolling(window=20).mean()
    ax8.plot(df['Date'], range_ma, linewidth=2, color='#e74c3c', 
            linestyle='--', label='20-Day MA')
    
    ax8.set_title('Daily Trading Range (High-Low %)', fontsize=12, fontweight='bold', pad=10)
    ax8.set_xlabel('Date', fontsize=10)
    ax8.set_ylabel('Range (%)', fontsize=10)
    ax8.legend(loc='best', fontsize=8)
    ax8.grid(True, alpha=0.3)
    ax8.tick_params(axis='x', rotation=45)
    
    # ========== PLOT 9: Behavior Confidence Heatmap ==========
    ax9 = plt.subplot(3, 3, 9)
    
    # Group by week and behavior
    df['Week'] = pd.to_datetime(df['Date']).dt.to_period('W')
    weekly_behavior = df.groupby(['Week', 'Behavior']).size().unstack(fill_value=0)
    
    if not weekly_behavior.empty:
        sns.heatmap(weekly_behavior.T, annot=True, fmt='d', cmap='YlOrRd', 
                   cbar_kws={'label': 'Count'}, ax=ax9, linewidths=0.5)
        ax9.set_title('Weekly Behavior Heatmap', fontsize=12, fontweight='bold', pad=10)
        ax9.set_xlabel('Week', fontsize=10)
        ax9.set_ylabel('Behavior', fontsize=10)
        ax9.tick_params(axis='x', rotation=45)
    
    plt.suptitle(f'{ticker} - Comprehensive Behavioral Analysis Dashboard', 
                fontsize=16, fontweight='bold', y=0.995)
    
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"💾 Visualizations saved: {save_path}")
    
    # plt.show()
    print("✅ Visualizations created successfully")

# ============================================================================
# DETAILED INSIGHTS GENERATION
# ============================================================================

def generate_detailed_insights(df, ticker):
    """Generate comprehensive insights and recommendations"""
    print("\n" + "=" * 70)
    print(" " * 20 + "🎯 DETAILED INSIGHTS & ANALYSIS")
    print("=" * 70)
    
    # Basic Statistics
    print(f"\n📊 ANALYSIS PERIOD:")
    print(f"   Stock: {ticker}")
    print(f"   Period: {df['Date'].min().date()} to {df['Date'].max().date()}")
    print(f"   Total Trading Days: {len(df)}")
    
    # Price Statistics
    print(f"\n💰 PRICE STATISTICS:")
    print(f"   Opening Price: ${df['Open'].iloc[0]:.2f}")
    print(f"   Closing Price: ${df['Close'].iloc[-1]:.2f}")
    print(f"   Overall Change: {((df['Close'].iloc[-1] - df['Open'].iloc[0]) / df['Open'].iloc[0] * 100):.2f}%")
    print(f"   Highest Price: ${df['High'].max():.2f}")
    print(f"   Lowest Price: ${df['Low'].min():.2f}")
    print(f"   Average Close: ${df['Close'].mean():.2f}")
    
    # Volatility Analysis
    print(f"\n📉 VOLATILITY ANALYSIS:")
    print(f"   Average Volatility: {df['Volatility'].mean():.2f}%")
    print(f"   Maximum Volatility: {df['Volatility'].max():.2f}%")
    print(f"   High Volatility Days: {len(df[df['Volatility'] > 2])} ({len(df[df['Volatility'] > 2])/len(df)*100:.1f}%)")
    
    # Volume Analysis
    print(f"\n📊 VOLUME ANALYSIS:")
    print(f"   Average Daily Volume: {df['Volume'].mean():,.0f}")
    print(f"   Highest Volume Day: {df.loc[df['Volume'].idxmax(), 'Date'].date()}")
    print(f"   Volume on that day: {df['Volume'].max():,.0f}")
    
    # Behavior Analysis
    print(f"\n🔍 BEHAVIORAL PATTERN ANALYSIS:")
    print("-" * 70)
    behaviors = df['Behavior'].value_counts()
    for behavior, count in behaviors.items():
        pct = (count / len(df)) * 100
        avg_confidence = df[df['Behavior'] == behavior]['Confidence_Score'].mean()
        print(f"   {behavior:20s}: {count:4d} days ({pct:5.1f}%) | Avg Confidence: {avg_confidence:.1f}%")
    
    # High-Risk Days Analysis
    print(f"\n⚠️  HIGH-RISK BEHAVIOR DAYS:")
    print("-" * 70)
    
    # Top 3 Panic Selling Days
    panic_days = df[df['Behavior'] == 'Panic Selling'].sort_values('Confidence_Score', ascending=False)
    if not panic_days.empty:
        print("\n🔴 TOP PANIC SELLING INCIDENTS:")
        for idx, row in panic_days.head(3).iterrows():
            print(f"   📅 {row['Date'].date()}:")
            print(f"      Price Drop: {row['Price_Change_Pct']:.2f}%")
            print(f"      Volume Spike: {row['Volume_Zscore']:.1f}σ above average")
            print(f"      Volatility: {row['Volatility']:.2f}%")
            print(f"      Confidence: {row['Confidence_Score']:.1f}%")
    
    # Top 3 FOMO Buying Days
    fomo_days = df[df['Behavior'] == 'FOMO Buying'].sort_values('Confidence_Score', ascending=False)
    if not fomo_days.empty:
        print("\n🟢 TOP FOMO BUYING INCIDENTS:")
        for idx, row in fomo_days.head(3).iterrows():
            print(f"   📅 {row['Date'].date()}:")
            print(f"      Price Gain: +{row['Price_Change_Pct']:.2f}%")
            print(f"      Volume Spike: {row['Volume_Zscore']:.1f}σ above average")
            print(f"      Volatility: {row['Volatility']:.2f}%")
            print(f"      Confidence: {row['Confidence_Score']:.1f}%")
    
    # Top 3 Overconfidence Days
    overtrade_days = df[df['Behavior'] == 'Overconfidence'].sort_values('Volume_Zscore', ascending=False)
    if not overtrade_days.empty:
        print("\n🟡 TOP OVERCONFIDENCE/OVERTRADING INCIDENTS:")
        for idx, row in overtrade_days.head(3).iterrows():
            print(f"   📅 {row['Date'].date()}:")
            print(f"      Price Change: {row['Price_Change_Pct']:.2f}%")
            print(f"      Volume Spike: {row['Volume_Zscore']:.1f}σ above average")
            print(f"      Volatility: {row['Volatility']:.2f}%")
            print(f"      Confidence: {row['Confidence_Score']:.1f}%")
    
    # Recent Trend Analysis
    print(f"\n📈 RECENT TREND ANALYSIS (Last 10 Days):")
    print("-" * 70)
    recent = df.tail(10)
    recent_behaviors = recent['Behavior'].value_counts()
    recent_avg_change = recent['Price_Change_Pct'].mean()
    recent_avg_vol = recent['Volatility'].mean()
    
    print(f"   Average Price Change: {recent_avg_change:+.2f}%")
    print(f"   Average Volatility: {recent_avg_vol:.2f}%")
    print(f"   Dominant Behavior: {recent_behaviors.index[0]} ({recent_behaviors.iloc[0]} days)")
    
    # Investment Recommendations
    print(f"\n💡 INVESTMENT INSIGHTS & RECOMMENDATIONS:")
    print("-" * 70)
    
    if 'Panic Selling' in recent_behaviors.index and recent_behaviors['Panic Selling'] >= 2:
        print("   ⚠️  RECENT PANIC SELLING DETECTED")
        print("      → Potential buying opportunity if fundamentals are strong")
        print("      → Exercise caution and validate company fundamentals")
        print("      → Consider dollar-cost averaging")
    
    if 'FOMO Buying' in recent_behaviors.index and recent_behaviors['FOMO Buying'] >= 2:
        print("   ⚠️  RECENT FOMO BUYING DETECTED")
        print("      → Stock may be overbought - prices could be overextended")
        print("      → Consider waiting for a pullback before entry")
        print("      → If holding, consider taking partial profits")
    
    if 'Overconfidence' in recent_behaviors.index and recent_behaviors['Overconfidence'] >= 2:
        print("   ⚠️  OVERTRADING DETECTED")
        print("      → Market showing indecision - consolidation phase")
        print("      → Await clear directional signal before major positions")
        print("      → Good time for research and preparation")
    
    if recent_behaviors.get('Normal', 0) >= 7:
        print("   ✅ STABLE MARKET CONDITIONS")
        print("      → Normal trading behavior observed")
        print("      → Good environment for strategic positioning")
        print("      → Monitor for emerging patterns")
    
    # Risk Assessment
    high_risk_days = len(df[df['Behavior'] != 'Normal'])
    risk_ratio = (high_risk_days / len(df)) * 100
    
    print(f"\n🎲 RISK ASSESSMENT:")
    print("-" * 70)
    print(f"   High-Risk Days: {high_risk_days} ({risk_ratio:.1f}%)")
    
    if risk_ratio > 30:
        risk_level = "HIGH RISK ⚠️⚠️⚠️"
        recommendation = "Extreme caution advised"
    elif risk_ratio > 20:
        risk_level = "MODERATE RISK ⚠️⚠️"
        recommendation = "Careful monitoring required"
    elif risk_ratio > 10:
        risk_level = "LOW-MODERATE RISK ⚠️"
        recommendation = "Normal vigilance recommended"
    else:
        risk_level = "LOW RISK ✅"
        recommendation = "Stable conditions"
    
    print(f"   Risk Level: {risk_level}")
    print(f"   Recommendation: {recommendation}")
    
    print("\n" + "=" * 70)

# ============================================================================
# COMPLETE ANALYSIS PIPELINE
# ============================================================================

def analyze_from_file(filepath, ticker_name=None, save_outputs=True):
    """
    Complete pipeline: Load → Clean → Analyze → Visualize
    
    Parameters:
    -----------
    filepath : str
        Path to data file (CSV, Excel, JSON)
    ticker_name : str (optional)
        Stock ticker name for labeling
    save_outputs : bool
        Whether to save CSV and visualizations
    
    Returns:
    --------
    pd.DataFrame : Analyzed dataframe with all features
    """
    
    print("=" * 70)
    print(" " * 10 + "🚀 COMPLETE STOCK ANALYSIS PIPELINE")
    print(" " * 15 + "Clean → Analyze → Visualize")
    print("=" * 70)
    
    # Extract ticker name from filename if not provided
    if ticker_name is None:
        ticker_name = os.path.basename(filepath).split('_')[0].split('.')[0].upper()
    
    print(f"\n📊 Analyzing: {ticker_name}")
    print(f"📁 Source: {filepath}")
    
    # STEP 1: LOAD AND CLEAN DATA
    print("\n" + "=" * 70)
    print("STEP 1: DATA LOADING & CLEANING")
    print("=" * 70)
    
    cleaner = StockDataCleaner(verbose=True)
    df = cleaner.load_data(filepath)
    
    if df is None:
        return None
    
    # Clean the data
    df = cleaner.clean_pipeline(df, remove_outliers_flag=True, outlier_method='iqr')
    cleaner.generate_cleaning_report()
    
    if df is None or df.empty:
        print("❌ Data cleaning failed")
        return None
    
    # STEP 2: FEATURE ENGINEERING
    print("\n" + "=" * 70)
    print("STEP 2: FEATURE ENGINEERING")
    print("=" * 70)
    
    df = engineer_features(df, verbose=True)
    
    # STEP 3: BEHAVIOR DETECTION
    print("\n" + "=" * 70)
    print("STEP 3: BEHAVIORAL PATTERN DETECTION")
    print("=" * 70)
    
    df = detect_investor_behavior(df, verbose=True)
    
    # STEP 4: VISUALIZATIONS
    print("\n" + "=" * 70)
    print("STEP 4: GENERATING VISUALIZATIONS")
    print("=" * 70)
    
    viz_path = None
    if save_outputs:
        os.makedirs('output', exist_ok=True)
        viz_path = f'output/{ticker_name}_comprehensive_analysis.png'
    
    create_comprehensive_visualizations(df, ticker_name, save_path=viz_path)
    
    # STEP 5: INSIGHTS GENERATION
    print("\n" + "=" * 70)
    print("STEP 5: GENERATING INSIGHTS")
    print("=" * 70)
    
    generate_detailed_insights(df, ticker_name)
    
    # STEP 6: SAVE RESULTS
    if save_outputs:
        os.makedirs('output', exist_ok=True)
        output_csv = f'output/{ticker_name}_complete_analysis.csv'
        
        # Save with all features
        df.to_csv(output_csv, index=False)
        print(f"\n💾 Complete analysis saved:")
        print(f"   📊 Data: {output_csv}")
        print(f"   📈 Visualizations: {viz_path}")
    
    print("\n" + "=" * 70)
    print("✅ ANALYSIS PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    
    return df


# ============================================================================
# INTERACTIVE CLI
# ============================================================================

def interactive_analysis():
    """Interactive command-line interface for analysis"""
    
    print("\n" + "=" * 70)
    print(" " * 15 + "📊 INTERACTIVE STOCK ANALYSIS")
    print("=" * 70)
    
    processor = FileProcessor()
    files = processor.list_available_files()
    
    if not files:
        print("\n❌ No files found in data/raw/")
        print("💡 Add CSV/Excel files to data/raw/ folder first")
        print("   Or use create_sample_data.py to generate test files")
        return
    
    print("\n" + "=" * 70)
    choice = input("Enter file number to analyze (or 'q' to quit): ").strip()

    # ... (Continuing from: choice = input("Enter file number to analyze (or 'b' for back): ").strip())

    if choice.lower() == 'b':
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(files):
            selected_file = files[idx]
            file_path = str(selected_file)
            
            # Auto-suggest ticker name from filename
            default_ticker = selected_file.stem.upper()
            ticker = input(f"📊 Enter ticker name [Default: {default_ticker}]: ").strip().upper()
            if not ticker:
                ticker = default_ticker
            
            # Execute the full pipeline
            analyze_from_file(file_path, ticker_name=ticker, save_outputs=True)
            
            input("\nPress Enter to return to main menu...")
        else:
            print("❌ Invalid selection. Please choose a number from the list.")
    except ValueError:
        print("❌ Invalid input. Please enter a numeric choice.")

# ============================================================================
# BATCH PROCESSING
# ============================================================================

def batch_analyze_all_files():
    """Process every valid file in the raw data directory"""
    processor = FileProcessor()
    files = processor.list_available_files()
    
    if not files:
        print("\n❌ No files found in data/raw/ to batch process.")
        return
        
    print(f"\n🚀 Starting batch analysis of {len(files)} files...")
    
    results_summary = []
    
    for file in files:
        file_path = str(file)
        ticker = file.stem.upper()
        
        try:
            # Run pipeline without blocking (verbose=False recommended for large batches)
            df = analyze_from_file(file_path, ticker_name=ticker, save_outputs=True)
            if df is not None:
                results_summary.append({
                    'Ticker': ticker,
                    'Days': len(df),
                    'Panic_Days': len(df[df['Behavior'] == 'Panic Selling']),
                    'FOMO_Days': len(df[df['Behavior'] == 'FOMO Buying']),
                    'Risk_Score': (len(df[df['Behavior'] != 'Normal']) / len(df)) * 100
                })
        except Exception as e:
            print(f"❌ Failed to process {ticker}: {e}")

    # Print a summary table of the batch
    if results_summary:
        print("\n" + "=" * 70)
        print(" " * 20 + "📋 BATCH PROCESS SUMMARY")
        print("=" * 70)
        summary_df = pd.DataFrame(results_summary)
        print(summary_df.to_string(index=False))
        print("=" * 70)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Ensure directory structure exists
    for folder in ['data/raw', 'output']:
        os.makedirs(folder, exist_ok=True)
        
    # Main Application Loop
    while True:
        print("\n" + "=" * 70)
        print(" " * 10 + "STOCK BEHAVIOR ANALYSIS SYSTEM - v1.0")
        print("=" * 70)
        print("   1. Interactive File Analysis")
        print("   2. Batch Analyze All Files")
        print("   3. Analyze Specific Path")
        print("   4. Exit")
        print("=" * 70)
        
        main_choice = input("\nEnter choice (1-4): ").strip()
        
        if main_choice == '1':
            interactive_analysis()
        elif main_choice == '2':
            batch_analyze_all_files()
        elif main_choice == '3':
            path = input("\n📁 Enter full file path: ").strip()
            tick = input("📊 Enter ticker name: ").strip().upper()
            if os.path.exists(path):
                analyze_from_file(path, ticker_name=tick)
            else:
                print("❌ Path does not exist.")
        elif main_choice == '4':
            print("\n👋 Happy Trading! Goodbye.")
            break
        else:
            print("❌ Invalid choice. Try again.")