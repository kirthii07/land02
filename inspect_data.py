import geopandas as gpd

file_path = "data/raw/Kerela landslide.shp"

print("Loading dataset...")

gdf = gpd.read_file(file_path)

print("\n========== DATASET INFO ==========")
print("Rows:", len(gdf))
print("Columns:", len(gdf.columns))

print("\n========== COLUMNS ==========")
for column in gdf.columns:
    print("-", column)

print("\n========== FIRST 5 RECORDS ==========")
print(gdf.head())

print("\n========== DATA TYPES ==========")
print(gdf.dtypes)

print("\n========== MISSING VALUES ==========")
print(gdf.isnull().sum())