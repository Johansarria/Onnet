import pandas as pd
import sys

file_path = 'Prueba Consultor contratos e Inventario de red (1).xlsx'

try:
    df_inv = pd.read_excel(file_path, sheet_name='Inventario OTs')
    df_liq = pd.read_excel(file_path, sheet_name='Ots para liquidación', header=1)
    
    inv_ots = set(df_inv['OT_ORIGINAL'].dropna().unique())
    liq_ots = set(df_liq['OT'].dropna().unique())
    
    print(f"Total OTs in Inventory: {len(inv_ots)}")
    print(f"Total OTs in Liquidation list: {len(liq_ots)}")
    
    intersect = inv_ots.intersection(liq_ots)
    print(f"OTs in both: {len(intersect)}")
    
    missing = liq_ots - inv_ots
    print(f"OTs in Liquidation but missing from Inventory: {len(missing)}")
    if missing:
        print(f"First 5 missing: {list(missing)[:5]}")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
