# WWE Fantasy League Discord Bot

A Discord bot for managing a fantasy WWE 2K25 league with Google Sheets integration.

## Features

### View Commands (Everyone)
- `!champions` - Display all current championship holders by brand (RAW/SmackDown/NXT)
- `!roster [team]` - Show a specific team's roster (austin/devin/pacelli)
- `!stats [wrestler]` - View a wrestler's championship history
- `!freeagents` - List all available NXT free agents
- `!ping` - Test if bot is online

### Management Commands (Requires "WWE League" Role)
- `!newchamp [title] [winner] [team]` - Update championship holder (automatically adds old reign to history)
- `!adddays [number]` - Add days to all current championships
- `!addwrestler [name] [team] [show] [gender]` - Add wrestler to team roster
- `!removewrestler [name] [team]` - Remove wrestler from roster (returns to free agents)
- `!addfreeagent [name] [gender]` - Add new wrestler to NXT free agents
- `!removefreeagent [name]` - Remove wrestler from free agents

## Tech Stack

- **Python 3.x**
- **discord.py** - Discord bot framework
- **gspread** - Google Sheets API integration
- **oauth2client** - Google authentication

## Setup

### Prerequisites
- Python 3.8+
- Discord Bot Token
- Google Sheets API credentials
- Google Sheet with proper structure

### Environment Variables
```
DISCORD_TOKEN=your_discord_bot_token
SHEET_URL=your_google_sheets_url
GOOGLE_CREDENTIALS=your_service_account_json
```

### Google Sheets Structure

The bot expects the following worksheets:
- **Championship Tracker** - Current champions (columns: Title, Champion, Team, blank, Days, blank, Show)
- **Championship History** - Historical reigns (columns: Championship, Champion, Team, Reign #, Status, Days Held)
- **Austin Roster, Devin Roster, Pacelli Roster** - Team rosters (columns: Name, Show, Gender)
- **NXT Free Agents** - Available wrestlers (columns: Name, Show, Gender)

### Installation

1. Clone this repository
2. Install dependencies: `pip install discord.py gspread oauth2client`
3. Set up environment variables
4. Run: `python main.py`

## Usage Examples

**Update a championship:**
```
!newchamp "RAW World Championship" "Roman Reigns" austin
```

**Add a wrestler to a roster:**
```
!addwrestler "Rhea Ripley" devin raw F
```

**View championship history:**
```
!stats "John Cena"
```

**Note:** Multi-word names require quotes.

## Features in Action

- Automatic championship history tracking when titles change hands
- Automatic reign number calculation
- Free agent management with draft functionality
- Role-based permissions for management commands

## Future Improvements

- Convert to slash commands for better UX
- Add more detailed statistics tracking
- Automated weekly reports
- Match result logging

## Author

Built for managing a fantasy WWE 2K25 league with friends.

## License

MIT License - Feel free to use and modify for your own fantasy leagues!
```

**Scroll down and click "Commit changes"**

---

## **STEP 6: ADD A .gitignore FILE (if not already there)**

**Click "Add file" → "Create new file"**

**Name:** `.gitignore`

**Content:**
```
# Environment variables
.env
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Credentials
credentials.json
service-account.json
*.json

# Replit
.replit
replit.nix
```

**Commit it**

---

## **STEP 7: OPTIONAL - ADD REQUIREMENTS.TXT**

**Create new file:** `requirements.txt`

**Content:**
```
discord.py>=2.0.0<img width="583" height="843" alt="Screenshot 2026-02-15 085739" src="https://github.com/user-attachments/assets/2e42fcb2-d085-489e-87ac-284b8a3eeb6c" />
<img width="698" height="1063" alt="Screenshot 2026-02-15 085730" src="https://github.com/user-attachments/assets/504585e2-4820-40e8-bde4-fd2f6f5e89c9" />
<img width="625" height="742" alt="Screenshot 2026-02-15 085845" src="https://github.com/user-attachments/assets/fef27ffb-2ed5-439b-819a-5ace757ca625" />

gspread>=5.0.0
oauth2client>=4.1.3
```

**Commit it**

---

## **YOU'RE DONE!**

**Your GitHub repo now has:**
- ✅ `main.py` - Your bot code
- ✅ `README.md` - Documentation
- ✅ `.gitignore` - Protects secrets
- ✅ `requirements.txt` - Dependencies

---

## **SHARE YOUR PORTFOLIO:**

**Your GitHub profile URL is:**
```
github.com/[your-username]/wwe-fantasy-league-bot
