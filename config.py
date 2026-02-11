"""
Configuration file for Stock Behavior Analysis
Edit these parameters to customize your analysis
"""

# ============================================================================
# STOCK SELECTION
# ============================================================================
TICKER = 'AAPL'  # Stock ticker symbol
PERIOD = '6mo'   # Options: '1mo', '3mo', '6mo', '1y', '2y', '5y'

# ============================================================================
# BEHAVIOR DETECTION THRESHOLDS
# ============================================================================

# Panic Selling Detection
PANIC_PRICE_THRESHOLD = -2.5      # Price drop percentage
PANIC_VOLUME_THRESHOLD = 1.5      # Volume Z-score
PANIC_VOLATILITY_THRESHOLD = 2.0  # Volatility percentage

# FOMO Buying Detection
FOMO_PRICE_THRESHOLD = 2.5        # Price gain percentage
FOMO_VOLUME_THRESHOLD = 1.5       # Volume Z-score
FOMO_VOLATILITY_THRESHOLD = 1.5   # Volatility percentage

# Overconfidence/Overtrading Detection
OVERTRADE_PRICE_THRESHOLD = 1.0   # Maximum price change
OVERTRADE_VOLUME_THRESHOLD = 2.0  # Volume Z-score
OVERTRADE_VOLATILITY_THRESHOLD = 1.8  # Volatility percentage

# ============================================================================
# TECHNICAL INDICATORS SETTINGS
# ============================================================================
VOLATILITY_WINDOW = 7   # Days for volatility calculation
VOLUME_MA_WINDOW = 20   # Days for volume moving average
MOMENTUM_WINDOW = 5     # Days for momentum calculation

# ============================================================================
# VISUALIZATION SETTINGS
# ============================================================================
FIGURE_SIZE = (16, 12)  # Figure size for plots
DPI = 300               # Resolution for saved images
PLOT_STYLE = 'whitegrid'  # Seaborn style: whitegrid, darkgrid, white, dark

# ============================================================================
# OUTPUT SETTINGS
# ============================================================================
SAVE_CSV = True         # Save processed data to CSV
SAVE_PLOTS = True       # Save visualization plots
OUTPUT_DIR = 'output'   # Directory for outputs

# ============================================================================
# COLOR SCHEME
# ============================================================================
COLORS = {
    'Normal': '#95a5a6',
    'Panic Selling': '#e74c3c',
    'FOMO Buying': '#2ecc71',
    'Overconfidence': '#f39c12',
    'Price Line': '#3498db',
    'Volume': '#9b59b6'
}