import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# URL to monitor
URL = "https://www.canada.ca/en/immigration-refugees-citizenship/corporate/mandate/policies-operational-instructions-agreements/ministerial-instructions/express-entry-rounds.html"

# File to store data
DATA_FILE = "express_entry_data.json"

# Get environment variables
ZAPIER_WEBHOOK = os.getenv('ZAPIER_WEBHOOK_URL', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', '')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', '')
CANVA_API_KEY = os.getenv('CANVA_API_KEY', '')
CANVA_DESIGN_ID = os.getenv('CANVA_DESIGN_ID', '')

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

def send_to_zapier(draw_data):
          """Send draw data to Zapier webhook"""
    if not ZAPIER_WEBHOOK:
                  print("Zapier webhook URL not configured")
                  return False

    try:
                  payload = {
                                    'round': draw_data['round'],
                                    'date': draw_data['date'],
                                    'program': draw_data['program'],
                                    'invitations': draw_data['invitations'],
                                    'crs_score': draw_data['crs_score'],
                                    'timestamp': draw_data['timestamp']
                  }

        response = requests.post(ZAPIER_WEBHOOK, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✅ Sent to Zapier webhook: {response.status_code}")
        return True
except Exception as e:
        print(f"Error sending to Zapier: {e}")
        return False

def generate_canva_poster(draw_data):
          """Generate a Canva poster with draw data"""
    if not CANVA_API_KEY or not CANVA_DESIGN_ID:
                  print("Canva API key or Design ID not configured")
                  return None

    try:
                  # Canva API endpoint for creating exports
                  url = "https://api.canva.com/v1/exports"

        headers = {
                          "Authorization": f"Bearer {CANVA_API_KEY}",
                          "Content-Type": "application/json"
        }

        # Request parameters
        payload = {
                          "design_id": CANVA_DESIGN_ID,
                          "file_type": "pdf",
                          "export_type": "standard"
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        export_data = response.json()
        export_id = export_data.get('id')

        if export_id:
                          print(f"✅ Canva poster export initiated: {export_id}")
                          # In production, you'd poll for the download URL
                          return export_id

        return None
except Exception as e:
        print(f"Error generating Canva poster: {e}")
        return None

def send_email(draw_data, poster_path=None):
          """Send email with draw information and optional poster"""
    if not SENDER_EMAIL or not SENDER_PASSWORD or not RECIPIENT_EMAIL:
                  print("Email configuration not set")
                  return False

    try:
                  # Create message
                  message = MIMEMultipart()
                  message['From'] = SENDER_EMAIL
                  message['To'] = RECIPIENT_EMAIL
                  message['Subject'] = f"🎉 NEW EXPRESS ENTRY DRAW #{draw_data['round']}"

        # Email body
                  body = f"""
                          <html>
                                      <body>
                                                      <h2>Express Entry Draw Detected! 🎯</h2>

                                                                                      <p><strong>Draw Number:</strong> #{draw_data['round']}</p>
                                                                                                      <p><strong>Date:</strong> {draw_data['date']}</p>
                                                                                                                      <p><strong>Program:</strong> {draw_data['program']}</p>
                                                                                                                                      <p><strong>Invitations Issued:</strong> {draw_data['invitations']}</p>
                                                                                                                                                      <p><strong>CRS Cutoff Score:</strong> {draw_data['crs_score']}</p>
                                                                                                                                                                      
                                                                                                                                                                                      <p>Check the official IRCC website for more details:</p>
                                                                                                                                                                                                      <p><a href="https://www.canada.ca/en/immigration-refugees-citizenship/corporate/mandate/policies-operational-instructions-agreements/ministerial-instructions/express-entry-rounds.html">Express Entry Draws</a></p>
                                                                                                                                                                                                                  </body>
                                                                                                                                                                                                                          </html>
                                                                                                                                                                                                                                  """

        message.attach(MIMEText(body, 'html'))

        # If poster is available, attach it
        if poster_path and os.path.exists(poster_path):
                          try:
                                                with open(poster_path, 'rb') as attachment:
                                                                          part = MIMEBase('application', 'octet-stream')
                                                                          part.set_payload(attachment.read())
                                                                      encoders.encode_base64(part)
                                                part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(poster_path)}')
                                                message.attach(part)
                                                print(f"✅ Poster attached to email")
except Exception as e:
                print(f"Warning: Could not attach poster: {e}")

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                          server.starttls()
                          server.login(SENDER_EMAIL, SENDER_PASSWORD)
                          server.send_message(message)

        print(f"✅ Email sent to {RECIPIENT_EMAIL}")
        return True

except Exception as e:
        print(f"Error sending email: {e}")
        return False

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
                  print(f"Current: Round {current_data['round']} on {current_data['date']}")
                  print(f"Program: {current_data['program']}")
                  print(f"Invitations: {current_data['invitations']}")
                  print(f"CRS Score: {current_data['crs_score']}")

        # Send to Zapier webhook
                  send_to_zapier(current_data)

        # Try to generate Canva poster
        poster_id = generate_canva_poster(current_data)

        # Send email with draw information
        send_email(current_data, poster_path=None)
else:
        print("No new round detected")

if __name__ == "__main__":
          main()
