import pandas as pd
from core.models import Material

# Read CSV file into a DataFrame
csv_file_path = 'core/data/materials.csv'
df = pd.read_csv(csv_file_path)

# Iterate through the DataFrame and create model instances
for index, row in df.iterrows():
    # Create the Material instance
    material = Material(
        item=row['Item'],
        description=row['Description'],
        price=row['Price']
    )
    # Save the material instance
    material.save()

print("CSV data has been loaded into the materials database.")
