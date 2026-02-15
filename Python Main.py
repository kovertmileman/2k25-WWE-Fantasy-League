import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
from datetime import datetime, timedelta

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Google Sheets setup
SCOPES = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# Load environment variables
token = os.getenv("DISCORD_TOKEN")
sheet_url = os.getenv("SHEET_URL")
creds_env = os.getenv("GOOGLE_CREDENTIALS")

if not token:
    raise RuntimeError("DISCORD_TOKEN is not set")
if not sheet_url:
    raise RuntimeError("SHEET_URL is not set")
if not creds_env:
    raise RuntimeError("GOOGLE_CREDENTIALS is not set")

try:
    creds_dict = json.loads(creds_env)
except json.JSONDecodeError:
    raise RuntimeError(
        "GOOGLE_CREDENTIALS must be a JSON service account object (starting with '{'). "
        "Re-check the Secret value and paste the full JSON.")


def get_sheet():
    """Connect to Google Sheets"""
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        creds_dict, SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url)
    return sheet


# Helper function to check if user has mod role
def is_mod():

    async def predicate(ctx):
        role = discord.utils.get(ctx.author.roles, name="WWE League")
        return role is not None

    return commands.check(predicate)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} server(s)')


# ============ VIEW COMMANDS (Everyone can use) ============


@bot.command(name='champions', help='Shows all current champions')
async def champions(ctx):
    """Display all current championship holders"""
    try:
        sheet = get_sheet()
        tracker = sheet.worksheet('Championship Tracker')

        # Get all champion data (rows 4-15)
        data = tracker.get('A4:G15')

        embed = discord.Embed(title="Current Champions",
                              color=discord.Color.gold(),
                              timestamp=datetime.utcnow())

        raw_champs = []
        sd_champs = []
        nxt_champs = []

        for row in data:
            if len(row) >= 7:
                title = row[0]
                champion = row[1]
                team = row[2]
                days = row[4] if len(row) > 4 and row[4] else "0"
                show = row[6] if len(row) > 6 else ""

                if champion and champion.strip():
                    champ_text = f"**{title}**\n{champion} ({team}) - {days} days\n"

                    if 'RAW' in show:
                        raw_champs.append(champ_text)
                    elif 'Smackdown' in show:
                        sd_champs.append(champ_text)
                    elif 'NXT' in show:
                        nxt_champs.append(champ_text)

        if raw_champs:
            embed.add_field(name="RAW",
                            value="\n".join(raw_champs),
                            inline=False)
        if sd_champs:
            embed.add_field(name="SMACKDOWN",
                            value="\n".join(sd_champs),
                            inline=False)
        if nxt_champs:
            embed.add_field(name="NXT",
                            value="\n".join(nxt_champs),
                            inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        import traceback
        error_msg = f"Error retrieving champions: {type(e).__name__}: {str(e)}"
        await ctx.send(error_msg)
        print(f"\n========== CHAMPIONS ERROR ==========")
        print(error_msg)
        traceback.print_exc()
        print(f"====================================\n")


@bot.command(name='roster',
             help='Shows a team\'s roster. Usage: !roster austin')
async def roster(ctx, team: str):
    """Display a team's roster"""
    try:
        team = team.lower().capitalize()
        sheet = get_sheet()

        if team not in ['Austin', 'Devin', 'Pacelli']:
            await ctx.send("Invalid team! Use: austin, devin, or pacelli")
            return

        roster_sheet = sheet.worksheet(f'{team} Roster')
        data = roster_sheet.get('A1:C40')

        embed = discord.Embed(title=f"{team.upper()}'S ROSTER",
                              color=discord.Color.blue(),
                              timestamp=datetime.utcnow())

        # Skip header row
        wrestlers = []
        for row in data[1:]:  # Skip first row (header)
            if len(row) >= 1 and row[0]:  # If there's a name
                name = row[0]
                show = row[1] if len(row) > 1 else "Unknown"
                gender = row[2] if len(row) > 2 else ""

                wrestlers.append(f"{name} ({show})")

        if wrestlers:
            # Split into chunks if too long
            chunk_size = 20
            for i in range(0, len(wrestlers), chunk_size):
                chunk = wrestlers[i:i + chunk_size]
                field_name = f"Wrestlers ({i+1}-{min(i+chunk_size, len(wrestlers))})"
                embed.add_field(name=field_name,
                                value="\n".join(chunk),
                                inline=False)
        else:
            embed.description = "No wrestlers found on this roster."

        await ctx.send(embed=embed)

    except Exception as e:
        import traceback
        error_msg = f"Error retrieving roster: {type(e).__name__}: {str(e)}"
        await ctx.send(error_msg)
        print(f"\n========== ROSTER ERROR ==========")
        print(error_msg)
        traceback.print_exc()
        print(f"====================================\n")


@bot.command(name='freeagents', help='Shows available NXT free agents')
async def freeagents(ctx):
    """Display available NXT free agents"""
    try:
        sheet = get_sheet()
        agents = sheet.worksheet('NXT Free Agents')

        data = agents.get('A2:C50')  # Skip header

        embed = discord.Embed(title="NXT FREE AGENTS",
                              color=discord.Color.green(),
                              timestamp=datetime.utcnow())

        male_agents = []
        female_agents = []

        for row in data:
            if len(row) >= 1 and row[0]:
                name = row[0]
                show = row[1] if len(row) > 1 else "NXT"
                gender = row[2] if len(row) > 2 else ""

                agent_text = f"{name} ({show})"

                if 'F' in gender.upper():
                    female_agents.append(agent_text)
                else:
                    male_agents.append(agent_text)

        # Split into chunks to avoid 1024 char limit
        def chunk_list(lst, max_chars=900):
            chunks = []
            current_chunk = []
            current_length = 0

            for item in lst:
                item_length = len(item) + 1  # +1 for newline
                if current_length + item_length > max_chars:
                    chunks.append(current_chunk)
                    current_chunk = [item]
                    current_length = item_length
                else:
                    current_chunk.append(item)
                    current_length += item_length

            if current_chunk:
                chunks.append(current_chunk)

            return chunks

        if male_agents:
            male_chunks = chunk_list(male_agents)
            for i, chunk in enumerate(male_chunks):
                field_name = f"Male Superstars" if i == 0 else f"Male Superstars (cont.)"
                embed.add_field(name=field_name,
                                value="\n".join(chunk),
                                inline=False)

        if female_agents:
            female_chunks = chunk_list(female_agents)
            for i, chunk in enumerate(female_chunks):
                field_name = f"Female Superstars" if i == 0 else f"Female Superstars (cont.)"
                embed.add_field(name=field_name,
                                value="\n".join(chunk),
                                inline=False)

        if not male_agents and not female_agents:
            embed.description = "No free agents available"

        await ctx.send(embed=embed)

    except Exception as e:
        import traceback
        error_msg = f"Error retrieving free agents: {type(e).__name__}: {str(e)}"
        await ctx.send(error_msg)
        print(f"\n========== FREE AGENTS ERROR ==========")
        print(error_msg)
        traceback.print_exc()
        print(f"====================================\n")


@bot.command(
    name='stats',
    help='Shows a wrestler\'s championship history. Usage: !stats wrestler_name'
)
async def stats(ctx, *, wrestler_name: str):
    """Display a wrestler's championship history"""
    try:
        sheet = get_sheet()
        history = sheet.worksheet('Championship History')

        # Get all data starting from row 4 (actual data starts here)
        all_data = history.get('A4:F100')

        wrestler_reigns = []

        # Search through data
        for row in all_data:
            if len(row) >= 2:
                championship = row[0] if len(row) > 0 else ""
                wrestler_in_row = row[1] if len(row) > 1 else ""
                team = row[2] if len(row) > 2 else ""
                reign_num = row[3] if len(row) > 3 else "1"
                date_lost = row[4] if len(row) > 4 else "Current"
                days = row[5] if len(row) > 5 else "0"

                # Case-insensitive partial match
                if wrestler_name.lower() in wrestler_in_row.lower():
                    reign_text = f"**{championship}** (Reign #{reign_num})\n"
                    reign_text += f"Team: {team}\n"
                    reign_text += f"Status: {date_lost}\n"
                    reign_text += f"Days Held: {days}"

                    wrestler_reigns.append(reign_text)

        if wrestler_reigns:
            embed = discord.Embed(
                title=f"{wrestler_name.upper()} - Championship History",
                description=f"Total Reigns: {len(wrestler_reigns)}",
                color=discord.Color.purple(),
                timestamp=datetime.utcnow())

            for i, reign in enumerate(wrestler_reigns, 1):
                embed.add_field(name=f"Championship #{i}",
                                value=reign,
                                inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send(
                f"No championship history found for '{wrestler_name}'")

    except Exception as e:
        import traceback
        error_msg = f"Error retrieving stats: {type(e).__name__}: {str(e)}"
        await ctx.send(error_msg)
        print(f"\n========== STATS ERROR ==========")
        print(error_msg)
        traceback.print_exc()
        print(f"====================================\n")


# ============ MOD COMMANDS (WWE League role required) ============


@bot.command(
    name='newchamp',
    help=
    'Updates championship holder. Usage: !newchamp "RAW World Championship" "ROMAN REIGNS" austin'
)
@is_mod()
async def newchamp(ctx, title: str, winner: str, team: str):
    """Update championship holder and add old reign to history"""
    try:
        team = team.lower().capitalize()

        if team not in ['Austin', 'Devin', 'Pacelli']:
            await ctx.send("❌ Invalid team! Use: austin, devin, or pacelli")
            return

        sheet = get_sheet()
        tracker = sheet.worksheet('Championship Tracker')
        history = sheet.worksheet('Championship History')

        # Get all championship data
        champ_data = tracker.get('A4:G15')

        # Find the championship
        row_index = None
        old_champ_info = None

        for i, row in enumerate(champ_data, start=4):  # Start at row 4
            if len(row) >= 1 and title.upper() in row[0].upper():
                row_index = i
                old_champ_info = {
                    'title': row[0],
                    'champion': row[1] if len(row) > 1 else "",
                    'team': row[2] if len(row) > 2 else "",
                    'days': row[4] if len(row) > 4 else "0"
                }
                break

        if not row_index:
            await ctx.send(f"❌ Championship '{title}' not found in tracker")
            return

        # Add old champion to history (if there was one)
        if old_champ_info['champion']:
            # Calculate reign number
            history_data = history.get('A4:F100')
            reign_count = 0

            for row in history_data:
                if (len(row) >= 2
                        and old_champ_info['title'].upper() in row[0].upper()
                        and old_champ_info['champion'].upper()
                        in row[1].upper()):
                    reign_count += 1

            new_reign_num = reign_count + 1

            # Add to history (find first empty row)
            history_rows = len(history_data) + 4  # +4 for header rows
            new_history_row = [
                old_champ_info['title'], old_champ_info['champion'],
                old_champ_info['team'],
                str(new_reign_num), 'Lost', old_champ_info['days']
            ]

            history.append_row(new_history_row)

        # Update championship tracker with new champion
        tracker.update(f'B{row_index}', winner.upper())  # Champion name
        tracker.update(f'C{row_index}', team)  # Team
        tracker.update(f'E{row_index}', '0')  # Reset days to 0

        await ctx.send(
            f"✅ **{title}** championship updated!\n**New Champion:** {winner.upper()} ({team})\n**Previous Champion:** {old_champ_info['champion']} - {old_champ_info['days']} days"
        )

    except Exception as e:
        import traceback
        error_msg = f"❌ Error updating championship: {type(e).__name__}: {str(e)}"
        await ctx.send(error_msg)
        print(f"\n========== NEWCHAMP ERROR ==========")
        print(error_msg)
        traceback.print_exc()
        print(f"====================================\n")


@bot.command(name='adddays',
             help='Adds days to all championships. Usage: !adddays 5')
@is_mod()
async def adddays(ctx, days: int):
    """Add days to all current championships"""
    try:
        sheet = get_sheet()
        tracker = sheet.worksheet('Championship Tracker')

        # Get all championship data
        champ_data = tracker.get('A4:G15')

        updates_made = 0

        for i, row in enumerate(champ_data, start=4):
            if len(row) >= 5 and row[1]:  # If there's a champion
                current_days = int(
                    row[4]) if row[4] and row[4].isdigit() else 0
                new_days = current_days + days

                # Update the days column (E)
                tracker.update(f'E{i}', str(new_days))
                updates_made += 1

        await ctx.send(f"✅ Added {days} days to {updates_made} championships")

    except Exception as e:
        import traceback
        error_msg = f"❌ Error adding days: {type(e).__name__}: {str(e)}"
        await ctx.send(error_msg)
        print(f"\n========== ADDDAYS ERROR ==========")
        print(error_msg)
        traceback.print_exc()
        print(f"====================================\n")


@bot.command(
    name='addwrestler',
    help=
    'Adds wrestler to team roster. Usage: !addwrestler "RHEA RIPLEY" austin raw F'
)
@is_mod()
async def addwrestler(ctx, name: str, team: str, show: str, gender: str):
    """Add wrestler to a team's roster"""
    try:
        team = team.lower().capitalize()
        show = show.upper()
        gender = gender.upper()

        if team not in ['Austin', 'Devin', 'Pacelli']:
            await ctx.send("❌ Invalid team! Use: austin, devin, or pacelli")
            return

        if show not in ['RAW', 'SMACKDOWN']:
            await ctx.send("❌ Invalid show! Use: raw or smackdown")
            return

        if gender not in ['M', 'F']:
            await ctx.send("❌ Invalid gender! Use: M or F")
            return

        sheet = get_sheet()
        roster_sheet = sheet.worksheet(f'{team} Roster')

        # Check if wrestler already on roster
        existing_data = roster_sheet.get('A2:A100')
        for row in existing_data:
            if row and name.upper() in row[0].upper():
                await ctx.send(f"❌ {name} is already on {team}'s roster")
                return

        # Add to roster
        new_row = [name.upper(), show, gender]
        roster_sheet.append_row(new_row)

        # Try to remove from free agents if they're there
        try:
            free_agents = sheet.worksheet('NXT Free Agents')
            fa_data = free_agents.get('A2:C100')

            for i, row in enumerate(fa_data, start=2):
                if row and name.upper() in row[0].upper():
                    free_agents.delete_rows(i)
                    await ctx.send(
                        f"✅ Added {name.upper()} to {team}'s roster ({show}) and removed from free agents"
                    )
                    return
        except:
            pass

        await ctx.send(f"✅ Added {name.upper()} to {team}'s roster ({show})")

    except Exception as e:
        import traceback
        error_msg = f"❌ Error adding wrestler: {type(e).__name__}: {str(e)}"
        await ctx.send(error_msg)
        print(f"\n========== ADDWRESTLER ERROR ==========")
        print(error_msg)
        traceback.print_exc()
        print(f"====================================\n")


@bot.command(
    name='removewrestler',
    help=
    'Removes wrestler from team roster. Usage: !removewrestler "RHEA RIPLEY" austin'
)
@is_mod()
async def removewrestler(ctx, name: str, team: str):
    """Remove wrestler from a team's roster and add back to free agents"""
    try:
        team = team.lower().capitalize()

        if team not in ['Austin', 'Devin', 'Pacelli']:
            await ctx.send("❌ Invalid team! Use: austin, devin, or pacelli")
            return

        sheet = get_sheet()
        roster_sheet = sheet.worksheet(f'{team} Roster')

        # Find and remove wrestler
        roster_data = roster_sheet.get('A2:C100')

        for i, row in enumerate(roster_data, start=2):
            if row and name.upper() in row[0].upper():
                wrestler_name = row[0]
                show = row[1] if len(row) > 1 else "NXT"
                gender = row[2] if len(row) > 2 else "M"

                # Remove from roster
                roster_sheet.delete_rows(i)

                # Add back to free agents
                free_agents = sheet.worksheet('NXT Free Agents')
                free_agents.append_row([wrestler_name, "NXT", gender])

                await ctx.send(
                    f"✅ Removed {wrestler_name} from {team}'s roster and added back to NXT free agents"
                )
                return

        await ctx.send(f"❌ {name} not found on {team}'s roster")

    except Exception as e:
        import traceback
        error_msg = f"❌ Error removing wrestler: {type(e).__name__}: {str(e)}"
        await ctx.send(error_msg)
        print(f"\n========== REMOVEWRESTLER ERROR ==========")
        print(error_msg)
        traceback.print_exc()
        print(f"====================================\n")


@bot.command(
    name='addfreeagent',
    help='Adds wrestler to NXT free agents. Usage: !addfreeagent "SOLO SIKOA" M'
)
@is_mod()
async def addfreeagent(ctx, name: str, gender: str):
    """Add new wrestler to NXT free agents"""
    try:
        gender = gender.upper()

        if gender not in ['M', 'F']:
            await ctx.send("❌ Invalid gender! Use: M or F")
            return

        sheet = get_sheet()
        free_agents = sheet.worksheet('NXT Free Agents')

        # Check if already exists
        fa_data = free_agents.get('A2:A100')
        for row in fa_data:
            if row and name.upper() in row[0].upper():
                await ctx.send(f"❌ {name} is already in free agents")
                return

        # Add to free agents
        new_row = [name.upper(), "NXT", gender]
        free_agents.append_row(new_row)

        await ctx.send(f"✅ Added {name.upper()} to NXT free agents ({gender})")

    except Exception as e:
        import traceback
        error_msg = f"❌ Error adding free agent: {type(e).__name__}: {str(e)}"
        await ctx.send(error_msg)
        print(f"\n========== ADDFREEAGENT ERROR ==========")
        print(error_msg)
        traceback.print_exc()
        print(f"====================================\n")


@bot.command(
    name='removefreeagent',
    help=
    'Removes wrestler from NXT free agents. Usage: !removefreeagent "SOLO SIKOA"'
)
@is_mod()
async def removefreeagent(ctx, name: str):
    """Remove wrestler from NXT free agents"""
    try:
        sheet = get_sheet()
        free_agents = sheet.worksheet('NXT Free Agents')

        # Find and remove
        fa_data = free_agents.get('A2:C100')

        for i, row in enumerate(fa_data, start=2):
            if row and name.upper() in row[0].upper():
                wrestler_name = row[0]
                free_agents.delete_rows(i)
                await ctx.send(
                    f"✅ Removed {wrestler_name} from NXT free agents")
                return

        await ctx.send(f"❌ {name} not found in free agents")

    except Exception as e:
        import traceback
        error_msg = f"❌ Error removing free agent: {type(e).__name__}: {str(e)}"
        await ctx.send(error_msg)
        print(f"\n========== REMOVEFREEAGENT ERROR ==========")
        print(error_msg)
        traceback.print_exc()
        print(f"====================================\n")


# ============ TEST COMMANDS ============


@bot.command(name='testsheet')
async def testsheet(ctx):
    """Test Google Sheets connection"""
    try:
        await ctx.send("Attempting to connect to Google Sheets...")

        sheet = get_sheet()
        await ctx.send(f"Connected to sheet: {sheet.title}")

        worksheets = sheet.worksheets()
        worksheet_names = [ws.title for ws in worksheets]
        await ctx.send(
            f"Found {len(worksheets)} worksheets: {', '.join(worksheet_names)}"
        )

    except Exception as e:
        await ctx.send(f"Connection failed: {type(e).__name__}: {str(e)}")


@bot.command(name='ping')
async def ping(ctx):
    """Simple test command"""
    await ctx.send("Pong! Bot is working!")


# Run the bot
bot.run(token)
