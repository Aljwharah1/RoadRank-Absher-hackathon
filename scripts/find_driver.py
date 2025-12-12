import pandas as pd
import json
fn='data/Trip Summary.xlsx'
df=pd.read_excel(fn)
print('Columns:', df.columns.tolist())
val='1234567890'
mask = df.astype(str).apply(lambda col: col.str.contains(val)).any(axis=1)
print('Matches count:', int(mask.sum()))
if mask.any():
    print(json.dumps(df[mask].head().to_dict(orient='records'), ensure_ascii=False))
else:
    print('--- First 5 rows --')
    print(json.dumps(df.head().to_dict(orient='records'), ensure_ascii=False))
