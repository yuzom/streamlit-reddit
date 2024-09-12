import toml
import os
import json

# Define the input JSON file and output TOML file paths
input_file = "firestore-key.json"
output_file = ".streamlit/secrets.toml"

# Ensure the .streamlit directory exists
os.makedirs(".streamlit", exist_ok=True)

# Open and read the JSON file
with open(input_file, "r") as json_file:
    json_text = json_file.read()

# Parse the JSON text to a Python dictionary
json_data = json.loads(json_text)

# Create a dictionary with the key that will go into the TOML file
config = {"firestore": json_data}

# Convert the dictionary to TOML format
toml_config = toml.dumps(config)

# Write the TOML configuration to the output file
with open(output_file, "w") as target:
    target.write(toml_config)

print(f"Secrets successfully written to {output_file}")
