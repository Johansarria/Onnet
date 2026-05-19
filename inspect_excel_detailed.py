import pandas as pd
import sys

file_path = 'Prueba Consultor contratos e Inventario de red (1).xlsx'

try:
    # Inventario OTs
    df_inv = pd.read_excel(file_path, sheet_name='Inventario OTs')
    print("\n--- Sheet: Inventario OTs ---")
    print(f"Shape: {df_inv.shape}")
    print(df_inv.info())

    # Ots para liquidación - Header seems to be in row 0
    df_liq = pd.read_excel(file_path, sheet_name='Ots para liquidación', header=1)
    print("\n--- Sheet: Ots para liquidación ---")
    print(f"Shape: {df_liq.shape}")
    print(f"Columns: {df_liq.columns.tolist()}")
    print(df_liq.head())

    # Precios - Header is complex
    df_precios = pd.read_excel(file_path, sheet_name='Precios')
    print("\n--- Sheet: Precios ---")
    print(df_precios)

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
