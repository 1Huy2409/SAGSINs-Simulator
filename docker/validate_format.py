#!/usr/bin/env python3
"""
Script để validate format của traffic_ingest.csv
"""
import pandas as pd
import sys

def validate_csv(filepath):
    """Validate CSV format matches requirements"""
    print(f"Validating {filepath}...")
    print("=" * 60)
    
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False
    
    # Expected columns theo format yêu cầu
    expected_columns = [
        "timestamp",
        "bytes_sent",
        "bitrate_bps",
        "rtt_milliseconds",
        "loss_rate",
        "jitter_milliseconds",
        "link_latency_milliseconds",
        "capacity_bps",
        "source_layer",
        "destination_layer",
        "link_id",
        "hour",
        "day_of_week",
        "is_weekend",
        "hour_sin",
        "hour_cos",
        "day_sin",
        "day_cos",
        "utilization",
        "throughput_mbps",
        "quality_score",
        "efficiency",
    ]
    
    # Check columns
    print("\n✓ Column Check:")
    actual_columns = df.columns.tolist()
    
    if actual_columns == expected_columns:
        print(f"  ✅ All {len(expected_columns)} columns present and in correct order")
    else:
        print("  ❌ Column mismatch!")
        print(f"  Expected: {expected_columns}")
        print(f"  Actual:   {actual_columns}")
        
        missing = set(expected_columns) - set(actual_columns)
        extra = set(actual_columns) - set(expected_columns)
        if missing:
            print(f"  Missing columns: {missing}")
        if extra:
            print(f"  Extra columns: {extra}")
        return False
    
    # Check data types and ranges
    print("\n✓ Data Validation:")
    
    checks = {
        "bytes_sent": (df["bytes_sent"] >= 0).all(),
        "bitrate_bps": (df["bitrate_bps"] >= 0).all(),
        "rtt_milliseconds": (df["rtt_milliseconds"] >= 0).all(),
        "loss_rate": ((df["loss_rate"] >= 0) & (df["loss_rate"] <= 1)).all(),
        "jitter_milliseconds": (df["jitter_milliseconds"] >= 0).all(),
        "link_latency_milliseconds": (df["link_latency_milliseconds"] >= 0).all(),
        "capacity_bps": (df["capacity_bps"] > 0).all(),
        "hour": ((df["hour"] >= 0) & (df["hour"] <= 23)).all(),
        "day_of_week": ((df["day_of_week"] >= 0) & (df["day_of_week"] <= 6)).all(),
        "is_weekend": ((df["is_weekend"] == 0) | (df["is_weekend"] == 1)).all(),
        "hour_sin": ((df["hour_sin"] >= -1) & (df["hour_sin"] <= 1)).all(),
        "hour_cos": ((df["hour_cos"] >= -1) & (df["hour_cos"] <= 1)).all(),
        "day_sin": ((df["day_sin"] >= -1) & (df["day_sin"] <= 1)).all(),
        "day_cos": ((df["day_cos"] >= -1) & (df["day_cos"] <= 1)).all(),
        "utilization": ((df["utilization"] >= 0) & (df["utilization"] <= 1)).all(),
        "throughput_mbps": (df["throughput_mbps"] >= 0).all(),
        "quality_score": ((df["quality_score"] >= 0) & (df["quality_score"] <= 1)).all(),
        "efficiency": ((df["efficiency"] >= 0) & (df["efficiency"] <= 1)).all(),
    }
    
    all_passed = True
    for field, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {field}")
        if not passed:
            all_passed = False
            print(f"      Invalid values: {df[field].describe()}")
    
    # Check for missing values
    print("\n✓ Missing Values:")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("  ✅ No missing values")
    else:
        print("  ❌ Found missing values:")
        for col, count in missing[missing > 0].items():
            print(f"      {col}: {count} missing")
        all_passed = False
    
    # Statistics
    print("\n✓ Data Statistics:")
    print(f"  Total records: {len(df)}")
    print(f"  Unique links: {df['link_id'].nunique()}")
    print(f"  Unique layers: {df['source_layer'].nunique()} source, {df['destination_layer'].nunique()} destination")
    print(f"\n  Utilization stats:")
    print(f"    Min:  {df['utilization'].min():.4f}")
    print(f"    Mean: {df['utilization'].mean():.4f}")
    print(f"    Max:  {df['utilization'].max():.4f}")
    print(f"\n  Loss rate stats:")
    print(f"    Min:  {df['loss_rate'].min():.6f}")
    print(f"    Mean: {df['loss_rate'].mean():.6f}")
    print(f"    Max:  {df['loss_rate'].max():.6f}")
    
    # Sample data
    print("\n✓ Sample Records (first 3 rows):")
    print(df.head(3).to_string())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ VALIDATION PASSED - Format is correct!")
        return True
    else:
        print("❌ VALIDATION FAILED - Please fix the issues above")
        return False

if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "data/traffic_ingest.csv"
    success = validate_csv(filepath)
    sys.exit(0 if success else 1)
