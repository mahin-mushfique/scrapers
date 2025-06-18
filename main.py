try:
    from trustpilot_scraper.scraper import scrape_trustpilot_reviews
except ImportError as e:
    print(f"ImportError: {e}")
    print("Ensure the trustpilot_scraper package is installed with 'pip install .' in the virtual environment.")
    exit(1)

import json
import csv
import os
import re
import pandas as pd

def extract_site_name(url):
    match = re.search(r'review/([^\.\/]+)', url)
    return match.group(1) if match else 'reviews'

def main():
    base_dir = os.path.dirname(__file__)
    input_file = os.path.join(base_dir, 'input_data.csv')
    result_dir = os.path.join(base_dir, 'Result')

    # Create Result folder if it doesn't exist
    os.makedirs(result_dir, exist_ok=True)

    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return

    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Failed to read CSV file: {e}")
        return

    if 'url' not in df.columns:
        print("The CSV file must have a column named 'url'")
        return

    for index, row in df.iterrows():
        base_url = row['url']
        if not isinstance(base_url, str) or not base_url.startswith("http"):
            print(f"Skipping invalid URL at row {index + 2}: {base_url}")
            continue

        print(f"\nProcessing URL: {base_url}")
        site_name = extract_site_name(base_url)
        reviews = scrape_trustpilot_reviews(base_url)

        if not reviews:
            print(f"No reviews found for {base_url}")
            continue

        # Export to JSON
        json_file = os.path.join(result_dir, f'{site_name}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, indent=4, ensure_ascii=False)
        print(f"Exported JSON to {json_file}")

        # Export to CSV
        csv_file = os.path.join(result_dir, f'{site_name}.csv')
        headers = ['Date', 'Author', 'Location', 'Rating', 'Heading', 'Body']
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(reviews)
        print(f"Exported CSV to {csv_file}")

if __name__ == "__main__":
    main()
