import os
import pandas as pd

def validate():
    data_dir = os.path.dirname(os.path.abspath(__file__))
    
    files = {
        "bus_loads.csv": 33,
        "line_params.csv": 32,
        "ev_renter_behavior.csv": 140,
    }
    
    print("=" * 60)
    print("AI-POWERED SMART EV RENTAL MANAGEMENT SYSTEM - DATA VALIDATION")
    print("=" * 60)
    
    dfs = {}
    all_passed = True
    
    # 1. Load and check shape & null values
    for filename, expected_rows in files.items():
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            print(f"[ERROR] File not found: {filename}")
            all_passed = False
            continue
            
        df = pd.read_csv(filepath)
        dfs[filename] = df
        
        rows, cols = df.shape
        null_count = df.isnull().sum().sum()
        
        print(f"\n--- {filename} ---")
        print(f"  Shape: {rows} rows x {cols} columns (Columns: {list(df.columns)})")
        print(f"  Row count match: {'PASS' if rows == expected_rows else 'FAIL'} (Expected: {expected_rows}, Actual: {rows})")
        print(f"  Missing / Null values: {null_count} ({'PASS' if null_count == 0 else 'FAIL'})")
        
        if rows != expected_rows or null_count != 0:
            all_passed = False

    # 2. EV Renter Behavior Summary Statistics
    if "ev_renter_behavior.csv" in dfs:
        ev_df = dfs["ev_renter_behavior.csv"]
        print("\n" + "=" * 60)
        print("EV RENTER BEHAVIOR - SUMMARY STATISTICS")
        print("=" * 60)
        
        target_cols = ["charging_energy_kwh", "dropoff_time_hr", "pickup_time_hr"]
        for col in target_cols:
            if col in ev_df.columns:
                mean_val = ev_df[col].mean()
                min_val = ev_df[col].min()
                max_val = ev_df[col].max()
                std_val = ev_df[col].std()
                print(f"{col:22s} -> Mean: {mean_val:6.2f} | Min: {min_val:5.1f} | Max: {max_val:5.1f} | Std: {std_val:5.2f}")
            else:
                print(f"[ERROR] Column {col} missing from ev_renter_behavior.csv")
                all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] All 3 datasets passed validation successfully!")
    else:
        print("[FAILED] One or more datasets failed validation.")
    print("=" * 60)

if __name__ == "__main__":
    validate()
