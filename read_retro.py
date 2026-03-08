import pandas as pd
import numpy as np

template_path = "Sprint Retrospective.xlsx"
try:
    xl = pd.ExcelFile(template_path)
    for sheet in xl.sheet_names:
        df = pd.read_excel(template_path, sheet_name=sheet, header=None)
        print(f"\n--- Sheet: {sheet} ---")
        for index, row in df.iterrows():
            row_vals = [str(x) for x in row.values if not pd.isna(x)]
            if row_vals:
                print(f"Row {index}: {row_vals}")
except Exception as e:
    print(f"Error reading Excel template: {e}")
