"""
Create sample data files with various issues for testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def create_sample_data_with_issues():
    """
    Create sample stock data with common data quality issues
    """
    
    # Create directory
    os.makedirs('data/raw', exist_ok=True)
    
    print("🔧 Creating sample data files with various issues...")
    
    # ========== File 1: CSV with missing values ==========
    dates = pd.date_range('2024-01-01', periods=100)
    
    data1 = {
        'Date': dates,
        'Open': np.random.uniform(140, 160, 100),
        'High': np.random.uniform(145, 165, 100),
        'Low': np.random.uniform(135, 155, 100),
        'Close': np.random.uniform(140, 160, 100),
        'Volume': np.random.randint(1000000, 5000000, 100)
    }
    
    df1 = pd.DataFrame(data1)
    
    # Introduce missing values
    df1.loc[5, 'Open'] = np.nan
    df1.loc[12, 'Close'] = np.nan
    df1.loc[20, 'Volume'] = np.nan
    df1.loc[35:38, 'High'] = np.nan
    
    df1.to_csv('data/raw/sample_with_missing.csv', index=False)
    print("✅ Created: data/raw/sample_with_missing.csv (has missing values)")
    
    # ========== File 2: Excel with outliers ==========
    data2 = {
        'Date': dates,
        'Open': np.random.uniform(140, 160, 100),
        'High': np.random.uniform(145, 165, 100),
        'Low': np.random.uniform(135, 155, 100),
        'Close': np.random.uniform(140, 160, 100),
        'Volume': np.random.randint(1000000, 5000000, 100)
    }
    
    df2 = pd.DataFrame(data2)
    
    # Introduce outliers
    df2.loc[10, 'High'] = 500  # Extreme outlier
    df2.loc[25, 'Volume'] = 50000000  # Volume spike
    df2.loc[50, 'Low'] = 10  # Unrealistic low
    
    df2.to_excel('data/raw/sample_with_outliers.xlsx', index=False)
    print("✅ Created: data/raw/sample_with_outliers.xlsx (has outliers)")
    
    # ========== File 3: CSV with duplicates ==========
    data3 = {
        'Date': dates,
        'Open': np.random.uniform(140, 160, 100),
        'High': np.random.uniform(145, 165, 100),
        'Low': np.random.uniform(135, 155, 100),
        'Close': np.random.uniform(140, 160, 100),
        'Volume': np.random.randint(1000000, 5000000, 100)
    }
    
    df3 = pd.DataFrame(data3)
    
    # Add duplicate rows
    df3 = pd.concat([df3, df3.iloc[10:15], df3.iloc[30:33]], ignore_index=True)
    df3 = df3.sort_values('Date').reset_index(drop=True)
    
    df3.to_csv('data/raw/sample_with_duplicates.csv', index=False)
    print("✅ Created: data/raw/sample_with_duplicates.csv (has duplicates)")
    
    # ========== File 4: CSV with wrong column names ==========
    data4 = {
        'date': dates,
        'o': np.random.uniform(140, 160, 100),
        'h': np.random.uniform(145, 165, 100),
        'l': np.random.uniform(135, 155, 100),
        'c': np.random.uniform(140, 160, 100),
        'vol': np.random.randint(1000000, 5000000, 100)
    }
    
    df4 = pd.DataFrame(data4)
    df4.to_csv('data/raw/sample_wrong_columns.csv', index=False)
    print("✅ Created: data/raw/sample_wrong_columns.csv (wrong column names)")
    
    # ========== File 5: Perfect clean data (for comparison) ==========
    data5 = {
        'Date': dates,
        'Open': np.random.uniform(140, 160, 100),
        'High': np.random.uniform(145, 165, 100),
        'Low': np.random.uniform(135, 155, 100),
        'Close': np.random.uniform(140, 160, 100),
        'Volume': np.random.randint(1000000, 5000000, 100)
    }
    
    df5 = pd.DataFrame(data5)
    df5.to_csv('data/raw/sample_clean_data.csv', index=False)
    print("✅ Created: data/raw/sample_clean_data.csv (clean data)")
    
    print("\n" + "=" * 70)
    print("✅ All sample files created in data/raw/")
    print("=" * 70)
    print("\n💡 You can now test the cleaning pipeline with these files!")

if __name__ == "__main__":
    create_sample_data_with_issues()