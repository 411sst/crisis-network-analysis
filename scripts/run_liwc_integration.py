#!/usr/bin/env python3
"""
Corrected LIWC Integration Runner Script
Works with your existing project structure
"""

import pandas as pd
import sys
from pathlib import Path
import os

# Add the project root and src to Python path
project_root = Path(__file__).parent.parent  # Go up one level from scripts/
src_path = project_root / 'src'
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

print(f"Project root: {project_root}")
print(f"Src path: {src_path}")
print(f"Current directory: {Path.cwd()}")

# Now try to import (will work once we create the file)
try:
    from src.liwc_integration import LIWCCrisisAnalyzer, integrate_liwc_with_existing_analysis
    print("✅ Successfully imported LIWC integration")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n🔧 Quick Fix:")
    print("1. Save the LIWC framework code as: ../src/liwc_integration.py")
    print("2. Make sure you have the enhanced dataset available")

    # Let's check what files exist
    data_dir = project_root / 'data'
    results_dir = project_root / 'results'

    print(f"\n📁 Data directory contents:")
    if data_dir.exists():
        for item in data_dir.rglob('*.csv'):
            print(f"  Found CSV: {item}")
    else:
        print("  Data directory not found")

    print(f"\n📁 Results directory contents:")
    if results_dir.exists():
        for item in results_dir.rglob('*.csv'):
            print(f"  Found CSV: {item}")
        for item in results_dir.rglob('*.json'):
            print(f"  Found JSON: {item}")
    else:
        print("  Results directory not found")

    sys.exit(1)

def find_master_dataset():
    """Find the master dataset with all your collected data"""

    # Look for CSV files in common locations
    search_paths = [
        project_root / 'data' / 'collected',
        project_root / 'data' / 'processed',
        project_root / 'data',
        project_root / 'results',
        project_root
    ]

    for search_path in search_paths:
        if search_path.exists():
            csv_files = list(search_path.rglob('*.csv'))
            for csv_file in csv_files:
                # Look for files that might contain your full dataset
                if any(keyword in csv_file.name.lower() for keyword in
                      ['combined', 'master', 'all_crises', 'collected', 'enhanced']):
                    print(f"📊 Found potential dataset: {csv_file}")
                    return csv_file

    # If no combined file found, look for any CSV with substantial data
    for search_path in search_paths:
        if search_path.exists():
            csv_files = list(search_path.rglob('*.csv'))
            for csv_file in csv_files:
                try:
                    # Check file size - if it's substantial, it might be our data
                    if csv_file.stat().st_size > 100000:  # 100KB+
                        return csv_file
                except:
                    continue

    return None

def main():
    print("🧠 Starting LIWC Integration for Crisis Network Analysis")

    # Find the master dataset
    data_file = find_master_dataset()
    if not data_file:
        print("❌ Could not find master dataset CSV file")
        print("Please ensure you have your collected data in CSV format")
        print("Expected locations:")
        print("  - data/collected/")
        print("  - data/processed/")
        print("  - results/")
        return

    print(f"📊 Using dataset: {data_file}")

    # Network results directory
    network_results_dir = project_root / "results" / "networks"

    try:
        # Run the integration
        df_enhanced, padm_results, statistical_results = integrate_liwc_with_existing_analysis(
            str(data_file), str(network_results_dir)
        )

        print(f"✅ Enhanced dataset shape: {df_enhanced.shape}")
        print(f"✅ PADM analysis completed")
        print(f"✅ Statistical analysis completed")

        # Quick preview of results
        print("\n📊 Quick Results Preview:")

        # Show available columns
        print(f"Available columns: {len(df_enhanced.columns)}")

        # Show LIWC categories with highest scores
        liwc_columns = [col for col in df_enhanced.columns
                       if col in ['cogproc', 'affect', 'risk', 'social', 'time', 'space', 'motion']]

        if liwc_columns:
            print(f"\n🔍 Found LIWC categories: {liwc_columns}")

            if 'crisis_id' in df_enhanced.columns:
                print("\n📈 Top LIWC Categories by Crisis:")
                for crisis in df_enhanced['crisis_id'].unique():
                    crisis_data = df_enhanced[df_enhanced['crisis_id'] == crisis]
                    print(f"\n{crisis} ({len(crisis_data)} posts):")
                    for col in liwc_columns:
                        if col in crisis_data.columns:
                            mean_score = crisis_data[col].mean()
                            print(f"  {col}: {mean_score:.3f}")
            else:
                print("\n📈 Overall LIWC Scores:")
                for col in liwc_columns:
                    mean_score = df_enhanced[col].mean()
                    print(f"  {col}: {mean_score:.3f}")
        else:
            print("⚠️ No LIWC scores found - check the analysis")

        # Show where results were saved
        results_dir = project_root / 'results' / 'liwc'
        if results_dir.exists():
            print(f"\n💾 Results saved in: {results_dir}")
            for file in results_dir.iterdir():
                if file.is_file():
                    print(f"  - {file.name}")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return

    return df_enhanced, padm_results, statistical_results

if __name__ == "__main__":
    result = main()
    if result:
        print("\n🎉 LIWC Analysis completed successfully!")
    else:
        print("\n❌ LIWC Analysis failed")
