import pandas as pd
import os
from datetime import datetime

def run_transformation(input_json, output_csv):
    df = pd.read_json(input_json)

    # Convert Price: "£51.77" -> 51.77 (float)
    df['price'] = df['price'].str.replace(r'[^\d.]', '', regex=True).astype(float)

    # Convert Rating: "Three" -> 3
    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    df['rating'] = df['rating'].map(rating_map)

    # Convert Availability: "In stock" -> 1
    df['availability'] = df['availability'].apply(lambda x: 1 if "In stock" in x else 0)

    # Extract book_id from URL
    df['book_id'] = df['link'].str.extract(r'_(\d+)/')

    # Convert to full URL
    base_url = "http://books.toscrape.com/catalogue/"
    df['link'] = base_url + df['link']

    # Add timestamp
    df['ingestion_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False) # Output as CSV
    print(f"Transformed data saved to {output_csv}.")