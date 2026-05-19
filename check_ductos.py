import pandas as pd
import sys

file_path = 'Prueba Consultor contratos e Inventario de red (1).xlsx'

try:
    df_inv = pd.read_excel(file_path, sheet_name='Inventario OTs')
    print("Q Ductos values:")
    print(df_inv['Q Ductos'].dropna().value_counts())
    
    print("\nQ Total Postes values (first 10):")
    print(df_inv['Q Total Postes'].head(10))

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
