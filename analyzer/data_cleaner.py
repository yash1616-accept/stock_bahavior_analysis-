"""
===============================================================================
DATA CLEANING & PREPROCESSING MODULE
===============================================================================
Handles missing data, outliers, validation, and data quality reporting
===============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class StockDataCleaner:
    """
    Comprehensive data cleaning for stock market data
    """
    
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.cleaning_report = {
            'total_rows_original': 0,
            'total_rows_cleaned': 0,
            'missing_values_found': 0,
            'missing_values_handled': 0,
            'outliers_detected': 0,
            'outliers_removed': 0,
            'duplicates_found': 0,
            'duplicates_removed': 0,
            'data_quality_score': 0
        }
    
    def load_data(self, filepath):
        """
        Load data from various file formats
        
        Supported formats: CSV, Excel (.xlsx, .xls), JSON
        """
        if self.verbose:
            print(f"\n📂 Loading data from: {filepath}")
        
        filepath = str(filepath)
        
        try:
            # Determine file type and load
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
            elif filepath.endswith('.json'):
                df = pd.read_json(filepath)
            else:
                raise ValueError("Unsupported file format. Use CSV, Excel, or JSON")
            
            self.cleaning_report['total_rows_original'] = len(df)
            
            if self.verbose:
                print(f"✅ Loaded {len(df)} rows and {len(df.columns)} columns")
                print(f"📊 Columns: {', '.join(df.columns.tolist())}")
            
            return df
        
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return None
    
    def validate_stock_data(self, df):
        """
        Validate that DataFrame has required stock data columns
        
        Required columns: Date, Open, High, Low, Close, Volume
        """
        if self.verbose:
            print("\n🔍 Validating stock data structure...")
        
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            # Try case-insensitive matching
            df.columns = [col.capitalize() for col in df.columns]
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"❌ Missing required columns: {missing_cols}")
                print(f"   Available columns: {df.columns.tolist()}")
                return False
        
        if self.verbose:
            print("✅ All required columns present")
        
        return True
    
    def handle_missing_values(self, df, strategy='forward_fill'):
        """
        Handle missing values in stock data
        
        Strategies:
        - 'forward_fill': Fill with previous value (default)
        - 'interpolate': Linear interpolation
        - 'drop': Drop rows with missing values
        - 'mean': Fill with column mean (for Volume)
        """
        if self.verbose:
            print("\n🧹 Handling missing values...")
        
        # Count missing values
        missing_before = df.isnull().sum()
        total_missing = missing_before.sum()
        
        if total_missing == 0:
            if self.verbose:
                print("✅ No missing values found")
            return df
        
        self.cleaning_report['missing_values_found'] = total_missing
        
        if self.verbose:
            print(f"⚠️  Found {total_missing} missing values:")
            for col, count in missing_before[missing_before > 0].items():
                print(f"   {col}: {count} missing ({count/len(df)*100:.1f}%)")
        
        df_cleaned = df.copy()
        
        if strategy == 'forward_fill':
            # Forward fill for price data (carry last known price)
            price_cols = ['Open', 'High', 'Low', 'Close']
            for col in price_cols:
                if col in df_cleaned.columns:
                    df_cleaned[col] = df_cleaned[col].ffill()
            
            # Fill Volume with 0 or forward fill
            if 'Volume' in df_cleaned.columns:
                df_cleaned['Volume'] = df_cleaned['Volume'].fillna(0)
        
        elif strategy == 'interpolate':
            # Linear interpolation for all numeric columns
            numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
            df_cleaned[numeric_cols] = df_cleaned[numeric_cols].interpolate(method='linear')
        
        elif strategy == 'drop':
            # Drop rows with any missing values
            df_cleaned = df_cleaned.dropna()
        
        elif strategy == 'mean':
            # Fill with column mean (not recommended for time series)
            numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mean())
        
        # Final check - drop any remaining NaN rows
        df_cleaned = df_cleaned.dropna()
        
        missing_after = df_cleaned.isnull().sum().sum()
        self.cleaning_report['missing_values_handled'] = total_missing - missing_after
        
        if self.verbose:
            print(f"✅ Handled {total_missing - missing_after} missing values")
            print(f"   Strategy used: {strategy}")
        
        return df_cleaned
    
    def detect_outliers(self, df, method='iqr', threshold=3):
        """
        Detect outliers in stock price and volume data
        
        Methods:
        - 'iqr': Interquartile Range (default)
        - 'zscore': Z-score method
        - 'isolation_forest': Machine learning based
        """
        if self.verbose:
            print(f"\n🔍 Detecting outliers using {method} method...")
        
        outlier_indices = set()
        
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        numeric_cols = [col for col in numeric_cols if col in df.columns]
        
        for col in numeric_cols:
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index
                
            elif method == 'zscore':
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outliers = df[z_scores > threshold].index
            
            outlier_indices.update(outliers)
            
            if self.verbose and len(outliers) > 0:
                print(f"   {col}: {len(outliers)} outliers detected")
        
        self.cleaning_report['outliers_detected'] = len(outlier_indices)
        
        if self.verbose:
            print(f"✅ Total outliers detected: {len(outlier_indices)}")
        
        return list(outlier_indices)
    
    def remove_outliers(self, df, outlier_indices):
        """Remove detected outliers from DataFrame"""
        if len(outlier_indices) == 0:
            return df
        
        df_cleaned = df.drop(outlier_indices)
        self.cleaning_report['outliers_removed'] = len(outlier_indices)
        
        if self.verbose:
            print(f"🗑️  Removed {len(outlier_indices)} outlier rows")
        
        return df_cleaned
    
    def handle_duplicates(self, df, subset=['Date']):
        """
        Remove duplicate rows based on Date column
        """
        if self.verbose:
            print("\n🔍 Checking for duplicate dates...")
        
        duplicates = df.duplicated(subset=subset)
        num_duplicates = duplicates.sum()
        
        self.cleaning_report['duplicates_found'] = num_duplicates
        
        if num_duplicates == 0:
            if self.verbose:
                print("✅ No duplicates found")
            return df
        
        if self.verbose:
            print(f"⚠️  Found {num_duplicates} duplicate dates")
        
        # Keep the first occurrence
        df_cleaned = df.drop_duplicates(subset=subset, keep='first')
        self.cleaning_report['duplicates_removed'] = num_duplicates
        
        if self.verbose:
            print(f"🗑️  Removed {num_duplicates} duplicate rows")
        
        return df_cleaned
    
    def validate_price_logic(self, df):
        """
        Validate stock price logic (High >= Low, Close within range, etc.)
        """
        if self.verbose:
            print("\n🔍 Validating price logic...")
        
        issues = []
        
        # Check: High >= Low
        if 'High' in df.columns and 'Low' in df.columns:
            invalid_hl = df[df['High'] < df['Low']]
            if len(invalid_hl) > 0:
                issues.append(f"High < Low in {len(invalid_hl)} rows")
        
        # Check: Close within High-Low range
        if all(col in df.columns for col in ['Close', 'High', 'Low']):
            invalid_close = df[(df['Close'] > df['High']) | (df['Close'] < df['Low'])]
            if len(invalid_close) > 0:
                issues.append(f"Close outside High-Low range in {len(invalid_close)} rows")
        
        # Check: Open within High-Low range
        if all(col in df.columns for col in ['Open', 'High', 'Low']):
            invalid_open = df[(df['Open'] > df['High']) | (df['Open'] < df['Low'])]
            if len(invalid_open) > 0:
                issues.append(f"Open outside High-Low range in {len(invalid_open)} rows")
        
        # Check: Volume >= 0
        if 'Volume' in df.columns:
            negative_volume = df[df['Volume'] < 0]
            if len(negative_volume) > 0:
                issues.append(f"Negative volume in {len(negative_volume)} rows")
        
        if len(issues) > 0:
            if self.verbose:
                print("⚠️  Price logic issues found:")
                for issue in issues:
                    print(f"   - {issue}")
            return False, issues
        
        if self.verbose:
            print("✅ All price logic checks passed")
        
        return True, []
    
    def fix_data_types(self, df):
        """
        Ensure correct data types for all columns
        """
        if self.verbose:
            print("\n🔧 Fixing data types...")
        
        # Convert Date to datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce', utc=True)
        
        # Convert numeric columns
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if self.verbose:
            print("✅ Data types corrected")
        
        return df
    
    def sort_by_date(self, df):
        """Sort DataFrame by date in ascending order"""
        if 'Date' in df.columns:
            df = df.sort_values('Date').reset_index(drop=True)
            if self.verbose:
                print("✅ Data sorted by date")
        return df
    
    def calculate_quality_score(self, df):
        """
        Calculate overall data quality score (0-100)
        """
        score = 100
        
        # Deduct for missing values
        missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
        score -= missing_ratio * 30
        
        # Deduct for duplicates
        duplicate_ratio = self.cleaning_report['duplicates_removed'] / max(self.cleaning_report['total_rows_original'], 1)
        score -= duplicate_ratio * 20
        
        # Deduct for outliers
        outlier_ratio = self.cleaning_report['outliers_removed'] / max(self.cleaning_report['total_rows_original'], 1)
        score -= outlier_ratio * 15
        
        self.cleaning_report['data_quality_score'] = max(0, min(100, score))
        
        return self.cleaning_report['data_quality_score']
    
    def generate_cleaning_report(self, output_path='output/cleaning_reports/'):
        """
        Generate a comprehensive data cleaning report
        """
        print("\n" + "=" * 70)
        print(" " * 20 + "📋 DATA CLEANING REPORT")
        print("=" * 70)
        
        print(f"\n📊 ORIGINAL DATA:")
        print(f"   Total rows: {self.cleaning_report['total_rows_original']}")
        
        print(f"\n🧹 CLEANING ACTIONS:")
        print(f"   Missing values found: {self.cleaning_report['missing_values_found']}")
        print(f"   Missing values handled: {self.cleaning_report['missing_values_handled']}")
        print(f"   Duplicates removed: {self.cleaning_report['duplicates_removed']}")
        print(f"   Outliers detected: {self.cleaning_report['outliers_detected']}")
        print(f"   Outliers removed: {self.cleaning_report['outliers_removed']}")
        
        print(f"\n✅ CLEANED DATA:")
        print(f"   Total rows: {self.cleaning_report['total_rows_cleaned']}")
        print(f"   Rows removed: {self.cleaning_report['total_rows_original'] - self.cleaning_report['total_rows_cleaned']}")
        
        print(f"\n🎯 DATA QUALITY SCORE: {self.cleaning_report['data_quality_score']:.1f}/100")
        
        # Quality rating
        score = self.cleaning_report['data_quality_score']
        if score >= 90:
            rating = "Excellent ⭐⭐⭐⭐⭐"
        elif score >= 75:
            rating = "Good ⭐⭐⭐⭐"
        elif score >= 60:
            rating = "Fair ⭐⭐⭐"
        else:
            rating = "Needs Improvement ⭐⭐"
        
        print(f"   Rating: {rating}")
        print("=" * 70)
    
    def clean_pipeline(self, df, remove_outliers_flag=True, outlier_method='iqr'):
        """
        Complete cleaning pipeline
        
        Steps:
        1. Validate structure
        2. Fix data types
        3. Handle missing values
        4. Remove duplicates
        5. Detect and optionally remove outliers
        6. Validate price logic
        7. Sort by date
        """
        print("\n" + "=" * 70)
        print(" " * 15 + "🚀 STARTING DATA CLEANING PIPELINE")
        print("=" * 70)
        
        # Step 1: Validate
        if not self.validate_stock_data(df):
            print("❌ Data validation failed. Cannot proceed.")
            return None
        
        # Step 2: Fix data types
        df = self.fix_data_types(df)
        
        # Step 3: Handle missing values
        df = self.handle_missing_values(df, strategy='forward_fill')
        
        # Step 4: Remove duplicates
        df = self.handle_duplicates(df)
        
        # Step 5: Detect outliers
        outlier_indices = self.detect_outliers(df, method=outlier_method)
        
        if remove_outliers_flag and len(outlier_indices) > 0:
            df = self.remove_outliers(df, outlier_indices)
        
        # Step 6: Validate price logic
        valid, issues = self.validate_price_logic(df)
        if not valid:
            print("⚠️  Warning: Some price logic issues detected but continuing...")
        
        # Step 7: Sort by date
        df = self.sort_by_date(df)
        
        # Update final row count
        self.cleaning_report['total_rows_cleaned'] = len(df)
        
        # Calculate quality score
        quality_score = self.calculate_quality_score(df)
        
        print("\n✅ Data cleaning pipeline completed!")
        print(f"   Quality Score: {quality_score:.1f}/100")
        
        return df
    
    def visualize_missing_data(self, df, save_path=None):
        """
        Create visualization of missing data patterns
        """
        try:
            import missingno as msno
            
            fig, ax = plt.subplots(figsize=(12, 6))
            msno.matrix(df, ax=ax)
            plt.title('Missing Data Pattern', fontsize=14, fontweight='bold')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"💾 Missing data visualization saved: {save_path}")
            
            plt.show()
        except ImportError:
            print("⚠️  missingno not installed. Skipping visualization.")
            print("   Install with: pip install missingno")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def quick_clean(filepath, output_path=None, remove_outliers=True):
    """
    Quick cleaning function for easy use
    
    Usage:
        cleaned_df = quick_clean('data/stock_data.csv')
    """
    cleaner = StockDataCleaner(verbose=True)
    
    # Load data
    df = cleaner.load_data(filepath)
    if df is None:
        return None
    
    # Clean data
    df_cleaned = cleaner.clean_pipeline(df, remove_outliers_flag=remove_outliers)
    
    # Generate report
    cleaner.generate_cleaning_report()
    
    # Save cleaned data
    if output_path:
        df_cleaned.to_csv(output_path, index=False)
        print(f"\n💾 Cleaned data saved: {output_path}")
    
    return df_cleaned


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Clean a CSV file
    print("Example: Data Cleaning Demo")
    print("=" * 70)
    
    # Create sample data with issues
    sample_data = {
        'Date': pd.date_range('2024-01-01', periods=10),
        'Open': [100, 102, None, 105, 103, 107, 110, 108, 112, 115],
        'High': [102, 104, 106, 107, 105, 109, 112, 110, 114, 117],
        'Low': [99, 101, 103, 104, 102, 106, 109, 107, 111, 114],
        'Close': [101, 103, 105, 106, 104, 108, 111, 109, 113, 116],
        'Volume': [1000000, 1200000, 1100000, None, 1300000, 1500000, 1400000, 1600000, 1700000, 1800000]
    }
    
    df = pd.DataFrame(sample_data)
    
    # Clean the data
    cleaner = StockDataCleaner(verbose=True)
    df_cleaned = cleaner.clean_pipeline(df)
    
    # Generate report
    cleaner.generate_cleaning_report()
    
    print("\n✅ Demo complete!")