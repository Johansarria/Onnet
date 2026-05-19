import pandas as pd
import sys

file_path = 'Prueba Consultor contratos e Inventario de red (1).xlsx'

try:
    xl = pd.ExcelFile(file_path)
    print(f"Sheets: {xl.sheet_names}")
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet, nrows=5)
        print(f"\n--- Sheet: {sheet} ---")
        print(f"Columns: {df.columns.tolist()}")
        print("Sample data:")
        print(df.head())
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
