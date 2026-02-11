"""
===============================================================================
FILE PROCESSING MODULE
===============================================================================
Handle multiple file formats and data sources
===============================================================================
"""

import pandas as pd
import os
from pathlib import Path
import json

class FileProcessor:
    """
    Process stock data from various file formats
    """
    
    def __init__(self, data_dir=None):
        # If no data_dir provided, assume it's in the project root (parent of this script's dir)
        if data_dir is None:
            # Get the directory where this script is located (analyzer/)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to project root and then to data/
            self.data_dir = os.path.join(os.path.dirname(current_dir), 'data')
        else:
            self.data_dir = data_dir
            
        self.raw_dir = os.path.join(self.data_dir, 'raw')
        self.cleaned_dir = os.path.join(self.data_dir, 'cleaned')
        
        # Create directories if they don't exist
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.cleaned_dir, exist_ok=True)
    
    def list_available_files(self):
        """List all available data files"""
        print("\n📁 Available data files:")
        print("=" * 70)
        
        files = []
        for ext in ['*.csv', '*.xlsx', '*.xls', '*.json']:
            files.extend(Path(self.raw_dir).glob(ext))
        
        if not files:
            print("   No files found in data/raw/")
            print("   Please add CSV, Excel, or JSON files to analyze")
            return []
        
        for i, file in enumerate(files, 1):
            file_size = os.path.getsize(file) / 1024  # KB
            print(f"   {i}. {file.name} ({file_size:.1f} KB)")
        
        return files
    
    def read_csv(self, filepath, **kwargs):
        """
        Read CSV with various delimiters and encodings
        """
        print(f"\n📄 Reading CSV: {filepath}")
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(filepath, encoding=encoding, **kwargs)
                print(f"✅ Successfully read with {encoding} encoding")
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"⚠️  Error with {encoding}: {e}")
                continue
        
        print("❌ Failed to read CSV with all encodings")
        return None
    
    def read_excel(self, filepath, sheet_name=0):
        """
        Read Excel file (supports .xlsx and .xls)
        """
        print(f"\n📊 Reading Excel: {filepath}")
        
        try:
            # List all sheets
            xls = pd.ExcelFile(filepath)
            print(f"   Available sheets: {xls.sheet_names}")
            
            # Read specified sheet
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            print(f"✅ Successfully read sheet: {sheet_name if isinstance(sheet_name, str) else xls.sheet_names[sheet_name]}")
            return df
        
        except Exception as e:
            print(f"❌ Error reading Excel: {e}")
            return None
    
    def read_json(self, filepath):
        """Read JSON file"""
        print(f"\n📋 Reading JSON: {filepath}")
        
        try:
            df = pd.read_json(filepath)
            print("✅ Successfully read JSON")
            return df
        except Exception as e:
            print(f"❌ Error reading JSON: {e}")
            return None
    
    def auto_detect_format(self, filepath):
        """
        Automatically detect file format and read
        """
        filepath = str(filepath)
        
        if filepath.endswith('.csv'):
            return self.read_csv(filepath)
        elif filepath.endswith(('.xlsx', '.xls')):
            return self.read_excel(filepath)
        elif filepath.endswith('.json'):
            return self.read_json(filepath)
        else:
            print(f"❌ Unsupported file format: {filepath}")
            return None
    
    def convert_to_standard_format(self, df, date_column='Date'):
        """
        Convert various data formats to standard stock data format
        
        Expected columns: Date, Open, High, Low, Close, Volume
        """
        print("\n🔄 Converting to standard format...")
        
        # Column mapping (common variations)
        column_mapping = {
            'date': 'Date',
            'datetime': 'Date',
            'timestamp': 'Date',
            'time': 'Date',
            'open': 'Open',
            'o': 'Open',
            'high': 'High',
            'h': 'High',
            'low': 'Low',
            'l': 'Low',
            'close': 'Close',
            'c': 'Close',
            'adj close': 'Close',
            'adjusted close': 'Close',
            'volume': 'Volume',
            'vol': 'Volume',
            'v': 'Volume'
        }
        
        # Rename columns
        df.columns = df.columns.str.lower().str.strip()
        df = df.rename(columns=column_mapping)
        
        # Check if we have all required columns
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        missing = [col for col in required_cols if col not in df.columns]
        
        if missing:
            print(f"⚠️  Missing columns after conversion: {missing}")
            print(f"   Available columns: {df.columns.tolist()}")
        else:
            print("✅ Successfully converted to standard format")
        
        return df
    
    def batch_process(self, cleaner):
        """
        Process all files in raw directory
        """
        files = self.list_available_files()
        
        if not files:
            return
        
        print("\n🚀 Starting batch processing...")
        
        processed_count = 0
        
        for file in files:
            print("\n" + "=" * 70)
            print(f"Processing: {file.name}")
            print("=" * 70)
            
            # Read file
            df = self.auto_detect_format(file)
            
            if df is None:
                continue
            
            # Convert to standard format
            df = self.convert_to_standard_format(df)
            
            # Clean data
            df_cleaned = cleaner.clean_pipeline(df)
            
            if df_cleaned is not None:
                # Save cleaned file
                output_file = os.path.join(
                    self.cleaned_dir,
                    f"cleaned_{file.stem}.csv"
                )
                df_cleaned.to_csv(output_file, index=False)
                print(f"\n💾 Saved cleaned data: {output_file}")
                processed_count += 1
        
        print("\n" + "=" * 70)
        print(f"✅ Batch processing complete!")
        print(f"   Files processed: {processed_count}/{len(files)}")
        print("=" * 70)


# ============================================================================
# INTERACTIVE FILE SELECTOR
# ============================================================================

def interactive_file_selection():
    """
    Interactive CLI for file selection and processing
    """
    processor = FileProcessor()
    
    files = processor.list_available_files()
    
    if not files:
        print("\n💡 Tip: Add data files to 'data/raw/' folder")
        return None
    
    print("\n" + "=" * 70)
    selection = input("Enter file number to process (or 'all' for batch): ").strip()
    
    if selection.lower() == 'all':
        from data_cleaner import StockDataCleaner
        cleaner = StockDataCleaner(verbose=True)
        processor.batch_process(cleaner)
        return None
    
    try:
        idx = int(selection) - 1
        selected_file = files[idx]
        return selected_file
    except (ValueError, IndexError):
        print("❌ Invalid selection")
        return None


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "FILE PROCESSOR DEMO")
    print("=" * 70)
    
    processor = FileProcessor()
    
    # List files
    files = processor.list_available_files()
    
    if files:
        # Process first file as example
        df = processor.auto_detect_format(files[0])
        
        if df is not None:
            print("\n📊 Data preview:")
            print(df.head())
            
            # Convert to standard format
            df_standard = processor.convert_to_standard_format(df)
            print("\n📊 Standardized data:")
            print(df_standard.head())