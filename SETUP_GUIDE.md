# Express Entry Monitor - Complete Setup Guide

## Overview
This automated bot monitors the official IRCC Express Entry page and when a new draw is detected, it:
1. Sends a webhook notification to Zapier
2. Generates a Canva poster with draw information
3. Sends you an email with all the details

## Prerequisites
- GitHub account (with this repository)
- Gmail account (or another SMTP-compatible email service)
- Canva account with API access
- Zapier account (optional, for advanced workflows)

---

## Step 1: Configure GitHub Secrets

Your bot needs API keys and credentials stored securely. Go to:
**Settings → Secrets and variables → Actions → New repository secret**

Add these secrets one by one:

### 1.1 Email Configuration
**SENDER_EMAIL**
- Value: Your Gmail address (e.g., `your-email@gmail.com`)

**SENDER_PASSWORD**
- Value: Gmail App Password (NOT your regular password)
- How to get Gmail App Password:
  1. Go to myaccount.google.com
    2. Click "Security" in the left menu
      3. Enable "2-Step Verification" if not already done
        4. Scroll to "App passwords"
          5. Select "Mail" and "Windows Computer"
            6. Copy the 16-character password and paste it here

            **RECIPIENT_EMAIL**
            - Value: Email address where you want to receive notifications (can be same as SENDER_EMAIL)

            ### 1.2 Zapier Configuration (Optional)
            **ZAPIER_WEBHOOK_URL**
            - Value: Your Zapier webhook URL (from Step 3 below)
            - Example: `https://hooks.zapier.com/hooks/catch/27050143/ungnl5h/`

            ### 1.3 Canva Configuration
            **CANVA_API_KEY**
            - Value: Your Canva API key
            - How to get it:
              1. Go to canva.com/developers
                2. Click "Your apps"
                  3. Create a new app if needed
                    4. Go to "Security" tab
                      5. Copy the "App ID" (this is your API key)

                      **CANVA_DESIGN_ID**
                      - Value: Your design template ID
                      - How to get it:
                        1. Open your Express Entry poster in Canva
                          2. Look at the URL: `canva.com/design/DAHEVLKR-9E/...`
                            3. The part after `/design/` is your Design ID (e.g., `DAHEVLKR-9E`)

                            ---

                            ## Step 2: Update GitHub Actions Workflow

                            The bot runs on a schedule using GitHub Actions. Check that your workflow file (`.github/workflows/monitor.yml`) includes the required environment variables.

                            Example workflow configuration:
                            ```yaml
                            name: Monitor Express Entry
                            on:
                              schedule:
                                  - cron: '*/10 * * * *'  # Runs every 10 minutes
                                    workflow_dispatch:

                                    jobs:
                                      monitor:
                                          runs-on: ubuntu-latest
                                              steps:
                                                    - uses: actions/checkout@v2
                                                          - name: Set up Python
                                                                  uses: actions/setup-python@v2
                                                                          with:
                                                                                    python-version: '3.9'
                                                                                          - name: Install dependencies
                                                                                                  run: |
                                                                                                            pip install requests beautifulsoup4
                                                                                                                  - name: Run monitor
                                                                                                                          env:
                                                                                                                                    ZAPIER_WEBHOOK_URL: ${{ secrets.ZAPIER_WEBHOOK_URL }}
                                                                                                                                              SENDER_EMAIL: ${{ secrets.SENDER_EMAIL }}
                                                                                                                                                        SENDER_PASSWORD: ${{ secrets.SENDER_PASSWORD }}
                                                                                                                                                                  RECIPIENT_EMAIL: ${{ secrets.RECIPIENT_EMAIL }}
                                                                                                                                                                            CANVA_API_KEY: ${{ secrets.CANVA_API_KEY }}
                                                                                                                                                                                      CANVA_DESIGN_ID: ${{ secrets.CANVA_DESIGN_ID }}
                                                                                                                                                                                              run: python monitor.py
                                                                                                                                                                                              ```
                                                                                                                                                                                              
                                                                                                                                                                                              ---
                                                                                                                                                                                              
                                                                                                                                                                                              ## Step 3: Set Up Zapier (Optional but Recommended)
                                                                                                                                                                                              
                                                                                                                                                                                              If you want to use Zapier for advanced workflows (e.g., storing data, sending to multiple channels):
                                                                                                                                                                                              
                                                                                                                                                                                              1. Go to zapier.com and create a new Zap
                                                                                                                                                                                              2. Set trigger: **Webhooks by Zapier → Catch Hook**
                                                                                                                                                                                              3. Copy the webhook URL it generates
                                                                                                                                                                                              4. Add this URL as the `ZAPIER_WEBHOOK_URL` secret (Step 1.2)
                                                                                                                                                                                              5. Add actions as needed:
                                                                                                                                                                                                 - Email via Gmail
                                                                                                                                                                                                    - Save to Google Sheets
                                                                                                                                                                                                       - Post to Slack
                                                                                                                                                                                                          - etc.
                                                                                                                                                                                                          
                                                                                                                                                                                                          ---
                                                                                                                                                                                                          
                                                                                                                                                                                                          ## Step 4: Test Your Setup
                                                                                                                                                                                                          
                                                                                                                                                                                                          1. Go to your repository
                                                                                                                                                                                                          2. Click **Actions** tab
                                                                                                                                                                                                          3. Select **Monitor Express Entry** workflow
                                                                                                                                                                                                          4. Click **Run workflow**
                                                                                                                                                                                                          5. Check the logs to see if it runs successfully
                                                                                                                                                                                                          
                                                                                                                                                                                                          Expected output:
                                                                                                                                                                                                          ```
                                                                                                                                                                                                          [2026-03-31 ...] Checking Express Entry page...
                                                                                                                                                                                                          Latest round: 407 - March 31, 2026
                                                                                                                                                                                                          No new round detected  (or)
                                                                                                                                                                                                          🎉 NEW ROUND DETECTED!
                                                                                                                                                                                                          Round 408 on April 1, 2026
                                                                                                                                                                                                          ...
                                                                                                                                                                                                          ✅ Sent to Zapier webhook: 200
                                                                                                                                                                                                          ✅ Email sent to your-email@gmail.com
                                                                                                                                                                                                          ```
                                                                                                                                                                                                          
                                                                                                                                                                                                          ---
                                                                                                                                                                                                          
                                                                                                                                                                                                          ## What Happens When a New Draw is Detected
                                                                                                                                                                                                          
                                                                                                                                                                                                          1. **Bot Detection**: Compares current draw with previous one
                                                                                                                                                                                                          2. **Webhook Sent**: Posts data to Zapier (if configured)
                                                                                                                                                                                                          3. **Email Sent**: You receive an HTML email with:
                                                                                                                                                                                                             - Draw number
                                                                                                                                                                                                                - Draw date
                                                                                                                                                                                                                   - Program type (FSW, CEC, PNP, etc.)
                                                                                                                                                                                                                      - Number of invitations
                                                                                                                                                                                                                         - CRS cutoff score
                                                                                                                                                                                                                         4. **Canva Poster**: Attempted generation (API integration)
                                                                                                                                                                                                                         
                                                                                                                                                                                                                         ---
                                                                                                                                                                                                                         
                                                                                                                                                                                                                         ## Troubleshooting
                                                                                                                                                                                                                         
                                                                                                                                                                                                                         ### Email Not Sending
                                                                                                                                                                                                                         - Check SENDER_EMAIL is correct and 2FA is enabled
                                                                                                                                                                                                                         - Verify SENDER_PASSWORD is a Gmail App Password (not your regular password)
                                                                                                                                                                                                                         - Check RECIPIENT_EMAIL is valid
                                                                                                                                                                                                                         
                                                                                                                                                                                                                         ### Webhook Not Reaching Zapier
                                                                                                                                                                                                                         - Verify ZAPIER_WEBHOOK_URL is correct (full URL including https://)
                                                                                                                                                                                                                         - Check Zapier Zap is active/published
                                                                                                                                                                                                                         - Check Zapier logs in the dashboard
                                                                                                                                                                                                                         
                                                                                                                                                                                                                         ### No Canva Poster Generated
                                                                                                                                                                                                                         - Verify CANVA_API_KEY is correct
                                                                                                                                                                                                                         - Verify CANVA_DESIGN_ID matches your Canva template
                                                                                                                                                                                                                         - Note: Canva API requires setting up "app exports" properly
                                                                                                                                                                                                                         
                                                                                                                                                                                                                         ### Workflow Not Running
                                                                                                                                                                                                                         - Go to Actions tab → Monitor Express Entry workflow
                                                                                                                                                                                                                         - Check "Run workflow" history
                                                                                                                                                                                                                         - Click on failed run to see error logs
                                                                                                                                                                                                                         - Verify all secrets are set correctly (Settings → Secrets)
                                                                                                                                                                                                                         
                                                                                                                                                                                                                         ---
                                                                                                                                                                                                                         
                                                                                                                                                                                                                         ## Customization
                                                                                                                                                                                                                         
                                                                                                                                                                                                                         ### Change Check Frequency
                                                                                                                                                                                                                         Edit `.github/workflows/monitor.yml`:
                                                                                                                                                                                                                         - `'*/10 * * * *'` = Every 10 minutes
                                                                                                                                                                                                                         - `'*/5 * * * *'` = Every 5 minutes
                                                                                                                                                                                                                         - `'0 * * * *'` = Every hour
                                                                                                                                                                                                                         - `'0 8 * * *'` = Daily at 8 AM UTC
                                                                                                                                                                                                                         
                                                                                                                                                                                                                         ### Modify Email Template
                                                                                                                                                                                                                         Edit `monitor.py`, find the `send_email()` function and modify the HTML body to customize the email appearance.
                                                                                                                                                                                                                         
                                                                                                                                                                                                                         ### Add More Actions
                                                                                                                                                                                                                         In the `main()` function, add new function calls to:
                                                                                                                                                                                                                         - Send Slack messages
                                                                                                                                                                                                                         - Post to Twitter
                                                                                                                                                                                                                         - Log to a database
                                                                                                                                                                                                                         - etc.
                                                                                                                                                                                                                         
                                                                                                                                                                                                                         ---
                                                                                                                                                                                                                         
                                                                                                                                                                                                                         ## Support
                                                                                                                                                                                                                         
                                                                                                                                                                                                                         For issues or questions:
                                                                                                                                                                                                                         1. Check the GitHub Actions logs
                                                                                                                                                                                                                         2. Review the error messages
                                                                                                                                                                                                                         3. Verify all secrets are configured correctly
                                                                                                                                                                                                                         4. Test the bot manually using "Run workflow"
                                                                                                                                                                                                                         
                                                                                                                                                                                                                         Good luck! 🍀
