"""
===============================================================================
RETAIL INVESTOR BEHAVIOUR-AWARE STOCK ANALYSIS SYSTEM
===============================================================================
Author: Data Science Team
Purpose: Detect emotional trading patterns in retail investors
- Panic Selling Zones
- FOMO (Fear of Missing Out) Buying Zones  
- Overconfidence / Overtrading Zones
===============================================================================
"""

# ============================================================================
# SECTION 1: IMPORT LIBRARIES
# ============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# For data fetching
import yfinance as yf

# For sentiment analysis (optional)
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    SENTIMENT_AVAILABLE = True
except:
    SENTIMENT_AVAILABLE = False
    print("⚠️ vaderSentiment not installed. Sentiment analysis will be skipped.")
    print("Install with: pip install vaderSentiment")

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# ============================================================================
# SECTION 2: DATA ACQUISITION
# ============================================================================
def fetch_stock_data(ticker, period='6mo'):
    """
    Fetch historical stock data from Yahoo Finance
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol (e.g., 'AAPL', 'TSLA')
    period : str
        Time period ('1mo', '3mo', '6mo', '1y', etc.)
    
    Returns:
    --------
    pd.DataFrame : Historical stock data
    """
    print(f"\n📊 Fetching data for {ticker}...")
    
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            raise ValueError("No data retrieved")
        
        # Reset index to make Date a column
        df.reset_index(inplace=True)
        
        print(f"✅ Successfully fetched {len(df)} days of data")
        print(f"📅 Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
        
        return df
    
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

# ============================================================================
# SECTION 3: FEATURE ENGINEERING
# ============================================================================
def engineer_features(df):
    """
    Create behavioral analysis features from raw stock data
    
    Features created:
    -----------------
    1. Price Change Percentage (daily returns)
    2. Volume Spike Detection (Z-score based)
    3. Volatility Index (rolling standard deviation)
    4. Volume Moving Average
    """
    print("\n🔧 Engineering features...")
    
    # Make a copy to avoid modifying original
    df = df.copy()
    
    # 1. Daily Price Change Percentage
    df['Price_Change_Pct'] = df['Close'].pct_change() * 100
    
    # 2. Calculate rolling average volume (20-day window)
    df['Volume_MA20'] = df['Volume'].rolling(window=20, min_periods=1).mean()
    
    # 3. Volume Spike Detection using Z-score
    # Calculate rolling mean and std for volume
    df['Volume_Mean'] = df['Volume'].rolling(window=20, min_periods=1).mean()
    df['Volume_Std'] = df['Volume'].rolling(window=20, min_periods=1).std()
    
    # Calculate Z-score for volume
    df['Volume_Zscore'] = (df['Volume'] - df['Volume_Mean']) / df['Volume_Std']
    df['Volume_Zscore'].fillna(0, inplace=True)
    
    # 4. Volatility Index (7-day rolling standard deviation of returns)
    df['Volatility'] = df['Price_Change_Pct'].rolling(window=7, min_periods=1).std()
    
    # 5. Price momentum (5-day rate of change)
    df['Momentum_5d'] = df['Close'].pct_change(periods=5) * 100
    
    print(f"✅ Features engineered successfully")
    print(f"   - Price Change %, Volume Z-score, Volatility, Momentum")
    
    return df

# ============================================================================
# SECTION 4: SENTIMENT ANALYSIS (OPTIONAL)
# ============================================================================
def analyze_sentiment(headlines):
    """
    Analyze sentiment of news headlines using VADER
    
    Parameters:
    -----------
    headlines : list
        List of news headlines
    
    Returns:
    --------
    dict : Sentiment scores
    """
    if not SENTIMENT_AVAILABLE:
        return {'compound': 0, 'sentiment_label': 'Neutral'}
    
    analyzer = SentimentIntensityAnalyzer()
    
    scores = [analyzer.polarity_scores(headline)['compound'] 
              for headline in headlines]
    
    avg_score = np.mean(scores)
    
    # Classify sentiment
    if avg_score >= 0.05:
        label = 'Positive'
    elif avg_score <= -0.05:
        label = 'Negative'
    else:
        label = 'Neutral'
    
    return {
        'compound': avg_score,
        'sentiment_label': label
    }

# Sample news headlines for demonstration
SAMPLE_NEWS = {
    'positive': [
        "Company reports record quarterly earnings",
        "Stock reaches new all-time high on strong fundamentals",
        "Analyst upgrades rating citing growth potential"
    ],
    'negative': [
        "Market concerns grow over economic slowdown",
        "Company faces regulatory scrutiny",
        "Disappointing earnings trigger sell-off"
    ],
    'neutral': [
        "Trading volume remains steady",
        "Market closes mixed amid uncertainty",
        "Investors await policy announcement"
    ]
}

# ============================================================================
# SECTION 5: BEHAVIOR DETECTION LOGIC
# ============================================================================
def detect_investor_behavior(df, sentiment_data=None):
    """
    Detect retail investor behavioral patterns using rule-based logic
    
    Behavior Categories:
    --------------------
    1. Panic Selling: Sharp negative price change + high volume + high volatility
    2. FOMO Buying: Sharp positive price change + high volume spike + volatility
    3. Overconfidence: High volume without significant price movement
    4. Normal: Standard trading conditions
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with engineered features
    sentiment_data : dict (optional)
        Sentiment scores to enhance detection
    
    Returns:
    --------
    pd.DataFrame : DataFrame with behavior labels
    """
    print("\n🔍 Detecting investor behaviors...")
    
    df = df.copy()
    
    # Initialize behavior column
    df['Behavior'] = 'Normal'
    
    # Define thresholds (can be adjusted based on stock characteristics)
    PANIC_PRICE_THRESHOLD = -2.5      # Price drop > 2.5%
    PANIC_VOLUME_THRESHOLD = 1.5      # Volume Z-score > 1.5
    PANIC_VOLATILITY_THRESHOLD = 2.0  # Volatility > 2%
    
    FOMO_PRICE_THRESHOLD = 2.5        # Price gain > 2.5%
    FOMO_VOLUME_THRESHOLD = 1.5       # Volume Z-score > 1.5
    FOMO_VOLATILITY_THRESHOLD = 1.5   # Volatility > 1.5%
    
    OVERTRADE_PRICE_THRESHOLD = 1.0   # Price change < 1%
    OVERTRADE_VOLUME_THRESHOLD = 2.0  # Volume Z-score > 2.0
    OVERTRADE_VOLATILITY_THRESHOLD = 1.8  # Volatility > 1.8%
    
    # PANIC SELLING DETECTION
    panic_mask = (
        (df['Price_Change_Pct'] < -PANIC_PRICE_THRESHOLD) &
        (df['Volume_Zscore'] > PANIC_VOLUME_THRESHOLD) &
        (df['Volatility'] > PANIC_VOLATILITY_THRESHOLD)
    )
    df.loc[panic_mask, 'Behavior'] = 'Panic Selling'
    
    # FOMO BUYING DETECTION
    fomo_mask = (
        (df['Price_Change_Pct'] > FOMO_PRICE_THRESHOLD) &
        (df['Volume_Zscore'] > FOMO_VOLUME_THRESHOLD) &
        (df['Volatility'] > FOMO_VOLATILITY_THRESHOLD)
    )
    df.loc[fomo_mask, 'Behavior'] = 'FOMO Buying'
    
    # OVERCONFIDENCE / OVERTRADING DETECTION
    overtrade_mask = (
        (abs(df['Price_Change_Pct']) < OVERTRADE_PRICE_THRESHOLD) &
        (df['Volume_Zscore'] > OVERTRADE_VOLUME_THRESHOLD) &
        (df['Volatility'] > OVERTRADE_VOLATILITY_THRESHOLD)
    )
    df.loc[overtrade_mask, 'Behavior'] = 'Overconfidence'
    
    # Print detection summary
    behavior_counts = df['Behavior'].value_counts()
    print("\n📊 Behavior Detection Summary:")
    print("=" * 50)
    for behavior, count in behavior_counts.items():
        percentage = (count / len(df)) * 100
        print(f"   {behavior:20s}: {count:3d} days ({percentage:5.1f}%)")
    print("=" * 50)
    
    return df

# ============================================================================
# SECTION 6: VISUALIZATION
# ============================================================================
def create_visualizations(df, ticker):
    """
    Create comprehensive visualizations of the analysis
    
    Plots:
    ------
    1. Price chart with behavior zones highlighted
    2. Volume analysis with moving average
    3. Volatility trends over time
    4. Scatter plot: Price Change vs Volume (colored by behavior)
    """
    print("\n📈 Creating visualizations...")
    
    # Set up the plotting area
    fig = plt.figure(figsize=(16, 12))
    
    # Define colors for each behavior
    colors = {
        'Normal': '#95a5a6',
        'Panic Selling': '#e74c3c',
        'FOMO Buying': '#2ecc71',
        'Overconfidence': '#f39c12'
    }
    
    # ========== PLOT 1: Price Chart with Behavior Zones ==========
    ax1 = plt.subplot(3, 2, 1)
    ax1.plot(df['Date'], df['Close'], linewidth=2, color='#3498db', label='Close Price')
    
    # Highlight behavior zones
    for behavior in ['Panic Selling', 'FOMO Buying', 'Overconfidence']:
        behavior_days = df[df['Behavior'] == behavior]
        if not behavior_days.empty:
            ax1.scatter(behavior_days['Date'], behavior_days['Close'], 
                       color=colors[behavior], s=100, alpha=0.6, 
                       label=behavior, zorder=5)
    
    ax1.set_title(f'{ticker} - Stock Price with Behavior Zones', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price ($)')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # ========== PLOT 2: Volume Analysis ==========
    ax2 = plt.subplot(3, 2, 2)
    ax2.bar(df['Date'], df['Volume'], alpha=0.3, color='#9b59b6', label='Daily Volume')
    ax2.plot(df['Date'], df['Volume_MA20'], color='#e91e63', linewidth=2, 
            label='20-Day MA', linestyle='--')
    
    ax2.set_title('Trading Volume Analysis', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Volume')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    # ========== PLOT 3: Volatility Index ==========
    ax3 = plt.subplot(3, 2, 3)
    ax3.fill_between(df['Date'], df['Volatility'], alpha=0.3, color='#ff6b6b')
    ax3.plot(df['Date'], df['Volatility'], linewidth=2, color='#c92a2a', 
            label='7-Day Volatility')
    ax3.axhline(y=2, color='red', linestyle='--', alpha=0.5, label='High Volatility Threshold')
    
    ax3.set_title('Volatility Index (7-Day Rolling Std Dev)', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Volatility (%)')
    ax3.legend(loc='best')
    ax3.grid(True, alpha=0.3)
    
    # ========== PLOT 4: Price Change Distribution ==========
    ax4 = plt.subplot(3, 2, 4)
    for behavior in colors.keys():
        behavior_data = df[df['Behavior'] == behavior]['Price_Change_Pct'].dropna()
        if not behavior_data.empty:
            ax4.hist(behavior_data, bins=20, alpha=0.5, label=behavior, 
                    color=colors[behavior])
    
    ax4.set_title('Price Change Distribution by Behavior', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Price Change (%)')
    ax4.set_ylabel('Frequency')
    ax4.legend(loc='best')
    ax4.grid(True, alpha=0.3)
    
    # ========== PLOT 5: Scatter - Price Change vs Volume Z-score ==========
    ax5 = plt.subplot(3, 2, 5)
    for behavior in colors.keys():
        behavior_data = df[df['Behavior'] == behavior]
        if not behavior_data.empty:
            ax5.scatter(behavior_data['Price_Change_Pct'], 
                       behavior_data['Volume_Zscore'],
                       c=colors[behavior], label=behavior, alpha=0.6, s=50)
    
    ax5.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax5.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    ax5.set_title('Price Change vs Volume Spike (Behavior Classification)', 
                 fontsize=14, fontweight='bold')
    ax5.set_xlabel('Price Change (%)')
    ax5.set_ylabel('Volume Z-Score')
    ax5.legend(loc='best')
    ax5.grid(True, alpha=0.3)
    
    # ========== PLOT 6: Behavior Timeline ==========
    ax6 = plt.subplot(3, 2, 6)
    
    # Create numeric mapping for behaviors
    behavior_map = {'Normal': 0, 'Overconfidence': 1, 'FOMO Buying': 2, 'Panic Selling': 3}
    df['Behavior_Numeric'] = df['Behavior'].map(behavior_map)
    
    # Plot as a line with color segments
    for behavior, num in behavior_map.items():
        mask = df['Behavior_Numeric'] == num
        if mask.any():
            ax6.scatter(df.loc[mask, 'Date'], df.loc[mask, 'Behavior_Numeric'],
                       c=colors[behavior], s=20, alpha=0.7, label=behavior)
    
    ax6.set_yticks(list(behavior_map.values()))
    ax6.set_yticklabels(list(behavior_map.keys()))
    ax6.set_title('Behavior Timeline', fontsize=14, fontweight='bold')
    ax6.set_xlabel('Date')
    ax6.set_ylabel('Detected Behavior')
    ax6.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('investor_behavior_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Visualizations saved as 'investor_behavior_analysis.png'")
    plt.show()

# ============================================================================
# SECTION 7: INSIGHTS GENERATION
# ============================================================================
def generate_insights(df, ticker):
    """
    Generate actionable insights from the behavior analysis
    """
    print("\n" + "=" * 70)
    print(" " * 20 + "🎯 KEY INSIGHTS")
    print("=" * 70)
    
    # 1. Overall Statistics
    print(f"\n📊 Analysis Period: {df['Date'].min().date()} to {df['Date'].max().date()}")
    print(f"📊 Total Trading Days Analyzed: {len(df)}")
    
    # 2. Behavior Breakdown
    print("\n🔍 BEHAVIORAL PATTERN DETECTION:")
    print("-" * 70)
    behaviors = df['Behavior'].value_counts()
    for behavior, count in behaviors.items():
        pct = (count / len(df)) * 100
        print(f"   {behavior:20s}: {count:4d} days ({pct:5.1f}%)")
    
    # 3. High-Risk Days
    print("\n⚠️  HIGH-RISK BEHAVIOR DAYS:")
    print("-" * 70)
    
    # Panic Selling Days
    panic_days = df[df['Behavior'] == 'Panic Selling'].sort_values('Price_Change_Pct')
    if not panic_days.empty:
        print("\n🔴 PANIC SELLING DETECTED:")
        for idx, row in panic_days.head(3).iterrows():
            print(f"   📅 {row['Date'].date()}: "
                  f"Price: {row['Price_Change_Pct']:.2f}%, "
                  f"Volume Spike: {row['Volume_Zscore']:.1f}σ, "
                  f"Volatility: {row['Volatility']:.2f}%")
    
    # FOMO Buying Days
    fomo_days = df[df['Behavior'] == 'FOMO Buying'].sort_values('Price_Change_Pct', ascending=False)
    if not fomo_days.empty:
        print("\n🟢 FOMO BUYING DETECTED:")
        for idx, row in fomo_days.head(3).iterrows():
            print(f"   📅 {row['Date'].date()}: "
                  f"Price: +{row['Price_Change_Pct']:.2f}%, "
                  f"Volume Spike: {row['Volume_Zscore']:.1f}σ, "
                  f"Volatility: {row['Volatility']:.2f}%")
    
    # Overconfidence Days
    overtrade_days = df[df['Behavior'] == 'Overconfidence'].sort_values('Volume_Zscore', ascending=False)
    if not overtrade_days.empty:
        print("\n🟡 OVERCONFIDENCE/OVERTRADING DETECTED:")
        for idx, row in overtrade_days.head(3).iterrows():
            print(f"   📅 {row['Date'].date()}: "
                  f"Price: {row['Price_Change_Pct']:.2f}%, "
                  f"Volume Spike: {row['Volume_Zscore']:.1f}σ, "
                  f"Volatility: {row['Volatility']:.2f}%")
    
    # 4. Statistical Summary
    print("\n📈 STATISTICAL SUMMARY:")
    print("-" * 70)
    print(f"   Average Daily Return: {df['Price_Change_Pct'].mean():.2f}%")
    print(f"   Return Std Deviation: {df['Price_Change_Pct'].std():.2f}%")
    print(f"   Average Volatility: {df['Volatility'].mean():.2f}%")
    print(f"   Max Volatility: {df['Volatility'].max():.2f}%")
    print(f"   Average Volume: {df['Volume'].mean():,.0f}")
    print(f"   Max Volume Spike: {df['Volume_Zscore'].max():.1f}σ")
    
    # 5. Investment Recommendations
    print("\n💡 INVESTMENT INSIGHTS:")
    print("-" * 70)
    
    recent_behavior = df.tail(5)['Behavior'].value_counts()
    
    if 'Panic Selling' in recent_behavior.index:
        print("   ⚠️  Recent panic selling detected - potential buying opportunity")
        print("      but exercise caution and validate fundamentals")
    
    if 'FOMO Buying' in recent_behavior.index:
        print("   ⚠️  Recent FOMO buying detected - price may be overextended")
        print("      consider waiting for a pullback")
    
    if 'Overconfidence' in recent_behavior.index:
        print("   ⚠️  Overtrading detected - market indecision or consolidation")
        print("      await clear directional signal")
    
    if recent_behavior.get('Normal', 0) == 5:
        print("   ✅ Market showing normal behavior - stable trading conditions")
    
    print("\n" + "=" * 70)

# ============================================================================
# SECTION 8: MAIN EXECUTION
# ============================================================================
def main():
    """
    Main execution function - orchestrates the entire analysis pipeline
    """
    print("=" * 70)
    print(" " * 10 + "RETAIL INVESTOR BEHAVIOUR ANALYSIS SYSTEM")
    print("=" * 70)
    
    # Configuration
    TICKER = 'ABCAPITAL.NS'  # Change this to analyze different stocks
    PERIOD = '1mo'    # Analysis period
    
    # Step 1: Fetch Data
    df = fetch_stock_data(TICKER, PERIOD)
    
    if df is None:
        print("❌ Failed to fetch data. Exiting...")
        return
    
    # Step 2: Engineer Features
    df = engineer_features(df)
    
    # Step 3: Detect Behaviors
    df = detect_investor_behavior(df)
    
    # Step 4: Create Visualizations
    create_visualizations(df, TICKER)
    
    # Step 5: Generate Insights
    generate_insights(df, TICKER)
    
    # Step 6: Save Processed Data
    output_file = f'{TICKER}_behavior_analysis.csv'
    df.to_csv(output_file, index=False)
    print(f"\n💾 Analysis saved to '{output_file}'")
    
    # Optional: Display sample of processed data
    print("\n📋 Sample of Processed Data:")
    print(df[['Date', 'Close', 'Price_Change_Pct', 'Volume_Zscore', 
              'Volatility', 'Behavior']].tail(10).to_string(index=False))
    
    print("\n✅ Analysis complete!")
    print("=" * 70)

# ============================================================================
# RUN THE ANALYSIS
# ============================================================================
if __name__ == "__main__":
    main()

# ============================================================================
# FUTURE SCOPE & ENHANCEMENTS
# ============================================================================
"""
FUTURE ENHANCEMENTS:
--------------------
1. Machine Learning Integration:
   - Use supervised learning (Random Forest, XGBoost) for behavior classification
   - Train on labeled historical data
   - Improve accuracy of behavior detection

2. Real-time Analysis:
   - Integrate with live data streams
   - Real-time alerts for behavior detection
   - WebSocket integration for live updates

3. Sentiment Analysis:
   - Scrape news from multiple sources (Google News, Twitter, Reddit)
   - Use transformer models (BERT, FinBERT) for better sentiment
   - Correlate sentiment with behavior patterns

4. Multi-Stock Portfolio Analysis:
   - Analyze multiple stocks simultaneously
   - Detect sector-wide behavioral patterns
   - Portfolio risk assessment based on behavior

5. Advanced Metrics:
   - Implement RSI, MACD, Bollinger Bands
   - Options flow analysis
   - Institutional vs retail volume separation

6. User Interface:
   - Build interactive dashboard (Streamlit/Dash)
   - Allow custom threshold configuration
   - Export reports in PDF format

7. Backtesting Framework:
   - Test trading strategies based on behavior signals
   - Calculate Sharpe ratio, maximum drawdown
   - Compare against buy-and-hold strategy
"""