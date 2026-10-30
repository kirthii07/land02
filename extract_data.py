from docx import Document
import pandas as pd

file_path = "data/raw/landslide_events.docx"

doc = Document(file_path)

rows = []

for table in doc.tables:
    for row in table.rows:
        values = [cell.text.strip() for cell in row.cells]
        if values:
            rows.append(values)

df = pd.DataFrame(rows)

print("Rows:", len(df))
print("Columns:", len(df.columns))
print("\nFirst 10 rows:")
print(df.head(10).to_string(index=False))

df.to_csv("data/raw/landslide_events.csv", index=False)

print("\nSaved: data/raw/landslide_events.csv")