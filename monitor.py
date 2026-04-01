import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# URL to monitor
URL = "https://www.canada.ca/en/immigration-refugees-citizenship/corporate/mandate/policies-operational-instructions-agreements/ministerial-instructions/express-entry-rounds.html"

# File to store data
DATA_FILE = "express_entry_data.json"

def scrape_express_entry():
      """Scrape the Express Entry page and extract the latest round data"""
      try:
                headers = {
                              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(URL, headers=headers, timeout=10)
                response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table
        table = soup.find('table')
        if not table:
                      print("Could not find table on page")
                      return None

        # Extract first row (latest round)
        rows = table.find_all('tr')[1:]  # Skip header
        if not rows:
                      print("No data rows found")
                      return None

        # Get the first row (most recent)
        first_row = rows[0]
        cells = first_row.find_all('td')

        if len(cells) < 5:
                      print("Not enough cells in row")
                      return None

        # Extract data
        data = {
                      'timestamp': datetime.now().isoformat(),
                      'round': cells[0].get_text().strip(),
                      'date': cells[1].get_text().strip(),
                      'program': cells[2].get_text().strip(),
                      'invitations': cells[3].get_text().strip(),
                      'crs_score': cells[4].get_text().strip()
        }

        return data

except Exception as e:
        print(f"Error scraping: {e}")
        return None

def save_data(data):
      """Save or update the data file"""
    history = []

    # Load existing data if file exists
    if os.path.exists(DATA_FILE):
              try:
                            with open(DATA_FILE, 'r') as f:
                                              history = json.load(f)
                                      except:
                            history = []

    # Add new data
    history.insert(0, data)

    # Keep only last 100 entries
    history = history[:100]

    # Write back
    with open(DATA_FILE, 'w') as f:
              json.dump(history, f, indent=2)

    return history

def check_for_new_round(current_data, history):
      """Check if this is a new round"""
    if len(history) < 2:
              return True, None

    previous_data = history[1]  # Second element is the previous record

    if current_data['round'] != previous_data['round']:
              return True, previous_data

    return False, None

def main():
      print(f"[{datetime.now()}] Checking Express Entry page...")

    current_data = scrape_express_entry()

    if not current_data:
              print("Failed to scrape data")
        return

    print(f"Latest round: {current_data['round']} - {current_data['date']}")

    history = save_data(current_data)
    is_new, previous = check_for_new_round(current_data, history)

    if is_new and previous:
              print(f"\n🎉 NEW ROUND DETECTED!")
        print(f"Previous: Round {previous['round']} on {previous['date']}")
        print(f"Current:  Round {current_data['round']} on {current_data['date']}")
        print(f"Program: {current_data['program']}")
        print(f"Invitations: {current_data['invitations']}")
        print(f"CRS Score: {current_data['crs_score']}")
else:
        print("No new round detected")

if __name__ == "__main__":
      main()
