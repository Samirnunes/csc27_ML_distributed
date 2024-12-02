import pandas as pd
import json
import numpy as np

# Load the CSV file with the header row
data = pd.read_csv('house_pricing_test.csv')[:1]

# Replace NaN values with None
data = data.replace({np.nan: None})

# Convert the DataFrame to a dictionary with feature names as keys
json_data = data.to_dict(orient='list')

# Save the JSON data to a file
with open('one_prediction_house_pricing_test.json', 'w') as json_file:
    json.dump(json_data, json_file, indent=4)

print("JSON file created successfully.")