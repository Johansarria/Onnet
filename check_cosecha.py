import pandas as pd
import sys

file_path = 'Prueba Consultor contratos e Inventario de red (1).xlsx'

try:
    df_inv = pd.read_excel(file_path, sheet_name='Inventario OTs')
    print("Cosecha values in Inventory OTs:")
    print(df_inv['Cosecha'].value_counts())
    
    df_liq = pd.read_excel(file_path, sheet_name='Ots para liquidación', header=1)
    print("\nCosecha values in Ots para liquidación:")
    print(df_liq['Cosecha'].value_counts())

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
