#
# import requests
# from bs4 import BeautifulSoup
# import json
# import re
#
#
# def extract_match_info(url):
#     """Extract match ID and slug from any Cricbuzz URL"""
#     parts = url.split('/')
#     match_id = None
#     slug = None
#
#     # Find the numeric part that looks like a match ID
#     for part in parts:
#         if part.isdigit() and len(part) > 5:  # Match IDs are typically 6+ digits
#             match_id = part
#             # Get the next part as the slug
#             try:
#                 slug_index = parts.index(part) + 1
#                 if slug_index < len(parts):
#                     slug = parts[slug_index]
#             except:
#                 pass
#             break
#
#     return match_id, slug
#
#
# def get_live_match_data(match_id, slug):
#     """Get live match data including scores, players, and run rates"""
#     url = f"https://www.cricbuzz.com/live-cricket-scores/{match_id}"
#     if slug:
#         url += f"/{slug}"
#
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, "lxml")
#
#     # Get First and Second Batting Team scores
#     try:
#         first_batting_team_score = (
#                 soup.find('div', class_="cb-text-gray cb-font-16") or
#                 soup.find('span', class_="cb-font-20 text-bold") or
#                 soup.find('div', class_="cb-col cb-col-100 cb-min-tm cb-text-gray")
#         ).text.strip()
#     except:
#         first_batting_team_score = 'Yet to bat'
#
#     try:
#         second_batting_team_score = (
#                 soup.find('div', class_="cb-col cb-col-100 cb-min-tm") or
#                 soup.find_all('span', class_="cb-font-20 text-bold")[1]
#         ).text.strip()
#     except:
#         second_batting_team_score = 'Yet to bat'
#
#     # Get Match Status
#     try:
#         match_status = soup.find('div', class_="cb-col cb-col-100 cb-min-stts cb-text-complete").text.strip()
#     except:
#         match_status = "Match in progress"
#
#     # Extract CRR and RRR
#     crr_label = soup.find('span', string=lambda x: x and 'CRR' in x)
#     crr_value = crr_label.find_next('span').text.strip() if crr_label else "N/A"
#
#     rrr_label = soup.find('span', string=lambda x: x and 'REQ:' in x)
#     rrr_value = rrr_label.find_next('span').text.strip() if rrr_label else "N/A"
#
#     # Extract player information
#     batters = []
#     bowlers = []
#     section = None
#
#     for tag in soup.find_all():
#         if tag.name == 'div' and tag.get_text(strip=True) == "Batter":
#             section = "batter"
#         elif tag.name == 'div' and tag.get_text(strip=True) == "Bowler":
#             section = "bowler"
#
#         if tag.name == 'div' and 'cb-min-itm-rw' in tag.get('class', []):
#             anchor = tag.find('a', class_='cb-text-link')
#             if not anchor:
#                 continue
#
#             name = anchor.text.strip()
#             profile_url = "https://www.cricbuzz.com/" + anchor['href'].strip()
#             stats = tag.find_all('div', class_='cb-col')
#             values = [s.text.strip() for s in stats if 'text-right' in s.get('class', [])]
#
#             if section == "batter" and len(values) == 5:
#                 batters.append({
#                     'name': name,
#                     'url': profile_url,
#                     'runs': values[0],
#                     'balls': values[1],
#                     'fours': values[2],
#                     'sixes': values[3],
#                     'strike_rate': values[4]
#                 })
#             elif section == "bowler" and len(values) == 5:
#                 bowlers.append({
#                     'name': name,
#                     'url': profile_url,
#                     'overs': values[0],
#                     'maidens': values[1],
#                     'runs_conceded': values[2],
#                     'wickets': values[3],
#                     'economy': values[4]
#                 })
#
#     # Extract Playing XI
#     playing_xi = []
#     team_containers = soup.find_all('div', class_='cb-min-tm')
#     if not team_containers:
#         team_containers = soup.find_all('div', class_='cb-col cb-col-100 cb-min-tm')
#
#     for container in team_containers:
#         team_name_div = container.find('div', class_='cb-min-tm-nm')
#         if team_name_div:
#             team_name = team_name_div.text.strip()
#             players = []
#             player_divs = container.find_all('div', class_='cb-min-tm-itm')
#             for player_div in player_divs:
#                 player_name = player_div.text.strip()
#                 players.append(player_name)
#             playing_xi.append({'team': team_name, 'players': players})
#
#     # Get squad URL from navigation
#     squad_url = None
#     highlight_url = None
#     nav_tabs = soup.find_all('a', class_="cb-nav-tab")
#     for tab in nav_tabs:
#         href = tab.get('href', '')
#         if 'cricket-scores' in href or 'cricket-match-squads' in href:
#             squad_url = "https://www.cricbuzz.com" + href
#         elif 'cricket-match-highlights' in href:
#             highlight_url = "https://www.cricbuzz.com" + href
#
#     return {
#         'first_batting_score': first_batting_team_score,
#         'second_batting_score': second_batting_team_score,
#         'match_status': match_status,
#         'crr': crr_value,
#         'rrr': rrr_value,
#         'batters': batters,
#         'bowlers': bowlers,
#         'squad_url': squad_url,
#         'highlight_url': highlight_url,
#         'playing_xi': playing_xi
#     }
#
#
# def get_squads_data(squad_url):
#     """Get team squad information"""
#     if not squad_url:
#         return None
#
#     response = requests.get(squad_url)
#     soup = BeautifulSoup(response.content, 'html.parser')
#
#     # Extract team names
#     team_headers = soup.find_all("h2", class_="cb-ltst-wgt-hdr")
#     if len(team_headers) >= 2:
#         team1_name = team_headers[0].text.strip()
#         team2_name = team_headers[1].text.strip()
#     else:
#         team_names = [div.text.strip() for div in soup.find_all("div", class_="pad5")]
#         team1_name = team_names[1] if len(team_names) > 1 else "Team 1"
#         team2_name = team_names[3] if len(team_names) > 3 else "Team 2"
#
#     base_url = "https://www.cricbuzz.com"
#     left_cards = soup.find_all('a', class_='cb-col cb-col-100 pad10 cb-player-card-left')
#     right_cards = soup.find_all('a', class_='cb-col cb-col-100 pad10 cb-player-card-right')
#
#     def process_squad(cards):
#         squad = []
#         for card in cards:
#             name_div = card.find('div', class_='cb-player-name-left') or card.find('div', class_='cb-player-name-right')
#             if name_div:
#                 name_and_role = name_div.get_text(separator='|', strip=True).split('|')
#                 name = name_and_role[0].strip()
#                 role = name_and_role[1].strip() if len(name_and_role) > 1 else "Player"
#                 profile_link = base_url + card['href']
#                 squad.append({
#                     'name': name,
#                     'role': role,
#                     'profile': profile_link
#                 })
#         return squad
#
#     return {
#         'team1': {'name': team1_name, 'squad': process_squad(left_cards)},
#         'team2': {'name': team2_name, 'squad': process_squad(right_cards)}
#     }
#
#
# def get_match_highlights(match_id):
#     """Get match highlights commentary"""
#     api_url = f'https://www.cricbuzz.com/api/cricket-match/commentary/{match_id}'
#     response = requests.get(api_url)
#     json_data = json.loads(response.text)
#     commentary = json_data.get("commentaryList", [])
#
#     highlights = []
#     for entry in commentary:
#         over = entry.get("overNumber", "")
#         bowler = entry.get("bowlerStriker", {}).get("bowlName", "")
#         batsman = entry.get("batsmanStriker", {}).get("batName", "")
#         text = entry.get("commText", "").strip()
#
#         # Replace formatting tags
#         if "commentaryFormats" in entry:
#             bold = entry["commentaryFormats"].get("bold", {})
#             ids = bold.get("formatId", [])
#             values = bold.get("formatValue", [])
#             for tag, val in zip(ids, values):
#                 text = text.replace(tag, val)
#
#         highlights.append({
#             'over': over,
#             'bowler': bowler,
#             'batsman': batsman,
#             'text': text,
#             'is_wicket': entry.get("event") == "WICKET"
#         })
#
#     return highlights
#
#
# def display_live_data(data):
#     """Display live match data in a formatted way"""
#     print("\n" + "=" * 50)
#     print("LIVE MATCH SCORES")
#     print("=" * 50)
#     print(f"First Batting Team: {data['first_batting_score']}")
#     print(f"Second Batting Team: {data['second_batting_score']}")
#     print(f"\nMatch Status: {data['match_status']}")
#     print(f"\nCurrent Run Rate (CRR): {data['crr']}")
#     print(f"Required Run Rate (RRR): {data['rrr']}")
#
#     # Batters
#     if data['batters']:
#         print("\n" + "=" * 50)
#         print("CURRENT BATTERS")
#         print("=" * 50)
#         roles = ['Striker', 'Non-Striker']
#         for i, batter in enumerate(data['batters']):
#             role = roles[i] if i < len(roles) else f"Batter {i + 1}"
#             print(f"\n{role}: {batter['name']}")
#             print(f"  Runs: {batter['runs']} | Balls: {batter['balls']}")
#             print(f"  4s/6s: {batter['fours']}/{batter['sixes']} | SR: {batter['strike_rate']}")
#             print(f"  Profile: {batter['url']}")
#
#     # Bowlers
#     if data['bowlers']:
#         print("\n" + "=" * 50)
#         print("CURRENT BOWLERS")
#         print("=" * 50)
#         roles = ['Bowler', 'Previous Bowler']
#         for i, bowler in enumerate(data['bowlers']):
#             role = roles[i] if i < len(roles) else f"Bowler {i + 1}"
#             print(f"\n{role}: {bowler['name']}")
#             print(f"  Overs: {bowler['overs']} | Maidens: {bowler['maidens']}")
#             print(f"  Wickets: {bowler['wickets']} | Runs: {bowler['runs_conceded']}")
#             print(f"  Economy: {bowler['economy']}")
#             print(f"  Profile: {bowler['url']}")
#
#
# def display_squads(squads_data):
#     """Display squad information in a formatted way"""
#     if not squads_data:
#         print("\nSquad information not available")
#         return
#
#     print("\n" + "=" * 50)
#     print("TEAM SQUADS")
#     print("=" * 50)
#
#     for team_key in ['team1', 'team2']:
#         team = squads_data[team_key]
#         print(f"\n{team['name'].upper()}")
#         print("-" * 50)
#         for i, player in enumerate(team['squad'], 1):
#             print(f"\n{i}. {player['name']} ({player['role']})")
#             print(f"   Profile: {player['profile']}")
#
#
# def display_starting_xi(live_data):
#     """Display starting XI players in a formatted way"""
#     if not live_data.get('playing_xi'):
#         print("\nStarting XI information not available")
#         return
#
#     print("\n" + "=" * 50)
#     print("STARTING XI PLAYERS")
#     print("=" * 50)
#
#     for xi_team in live_data['playing_xi']:
#         team_name = xi_team['team']
#         print(f"\n{team_name}:")
#         for player in xi_team['players']:
#             print(f"  - {player}")
#         print("-" * 50)
#
#
# def display_bench_strength(live_data, squads_data):
#     """Display bench strength in a formatted way"""
#     if not live_data.get('playing_xi') or not squads_data:
#         print("\nBench strength information not available")
#         return
#
#     print("\n" + "=" * 50)
#     print("BENCH STRENGTH")
#     print("=" * 50)
#
#     # Helper function to clean player names
#     def clean_name(name):
#         return re.sub(r'\([^)]*\)', '', name).strip().lower()
#
#     for xi_team in live_data['playing_xi']:
#         team_name = xi_team['team']
#         playing_xi_names = [clean_name(name) for name in xi_team['players']]
#
#         # Find matching squad data
#         squad_team = None
#         for key in ['team1', 'team2']:
#             if squads_data[key]['name'].lower() in team_name.lower():
#                 squad_team = squads_data[key]
#                 break
#
#         if not squad_team:
#             continue
#
#         # Find bench players
#         bench = []
#         for squad_player in squad_team['squad']:
#             squad_name = clean_name(squad_player['name'])
#             if squad_name not in playing_xi_names:
#                 bench.append(squad_player)
#
#         print(f"\n{team_name} Bench ({len(bench)} players):")
#         if bench:
#             for i, player in enumerate(bench, 1):
#                 print(f"  {i}. {player['name']} ({player['role']})")
#         else:
#             print("  No bench players available")
#         print("-" * 50)
#
#
# def display_highlights(highlights):
#     """Display match highlights in a formatted way"""
#     if not highlights:
#         print("\nNo highlights available")
#         return
#
#     print("\n" + "=" * 50)
#     print("MATCH HIGHLIGHTS")
#     print("=" * 50)
#
#     for entry in highlights:
#         if not entry['text']:
#             continue
#
#         if entry['is_wicket']:
#             print(f"\n{entry['over']} - WICKET!")
#             print(f"{entry['bowler']} to {entry['batsman']}: {entry['text']}")
#             print(f"{entry['bowler']} to {entry['batsman']}, THAT'S OUT!!")
#         else:
#             print(f"\n{entry['over']} - {entry['bowler']} to {entry['batsman']}: {entry['text']}")
#
#
# def main():
#     url = input("Enter Cricbuzz Match URL: ")
#     match_id, slug = extract_match_info(url)
#
#     if not match_id:
#         print("Could not extract match ID from URL. Please provide a valid Cricbuzz match URL.")
#         return
#
#     print("\nFetching match data...")
#
#     # Get and display live match data
#     try:
#         live_data = get_live_match_data(match_id, slug)
#         display_live_data(live_data)
#
#         # Display starting XI players
#         display_starting_xi(live_data)
#     except Exception as e:
#         print(f"Error fetching live data: {e}")
#
#     # Get and display squad data
#     try:
#         if live_data.get('squad_url'):
#             squads_data = get_squads_data(live_data['squad_url'])
#             display_squads(squads_data)
#
#             # Display bench strength
#             display_bench_strength(live_data, squads_data)
#         else:
#             print("\nSquad URL not found")
#     except Exception as e:
#         print(f"Error fetching squad data: {e}")
#
#     # Get and display highlights
#     try:
#         highlights = get_match_highlights(match_id)
#         display_highlights(highlights)
#     except Exception as e:
#         print(f"Error fetching highlights: {e}")
#
#
# if __name__ == "__main__":
#     main()

from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

# ----------------------------
# FUNCTION 1: Extract match ID and slug
# ----------------------------
def extract_match_info(url):
    parts = url.split('/')
    match_id = None
    slug = None
    for part in parts:
        if part.isdigit() and len(part) > 5:
            match_id = part
            try:
                slug_index = parts.index(part) + 1
                if slug_index < len(parts):
                    slug = parts[slug_index]
            except:
                pass
            break
    return match_id, slug

# ----------------------------
# FUNCTION 2: Live Score Info (Improved with Code 2 enhancements)
# ----------------------------
def get_live_match_data(match_id, slug):
    url = f"https://www.cricbuzz.com/live-cricket-scores/{match_id}"
    if slug:
        url += f"/{slug}"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")

    # IMPROVED SCORE EXTRACTION (From Code 2)
    try:
        first_batting_team_score = (
            soup.find('div', class_="cb-text-gray cb-font-16") or
            soup.find('span', class_="cb-font-20 text-bold") or
            soup.find('div', class_="cb-col cb-col-100 cb-min-tm cb-text-gray")
        ).text.strip()
    except:
        first_batting_team_score = 'Yet to bat'

    try:
        second_batting_team_score = (
            soup.find('div', class_="cb-col cb-col-100 cb-min-tm") or
            soup.find_all('span', class_="cb-font-20 text-bold")[1]
        ).text.strip()
    except:
        second_batting_team_score = 'Yet to bat'

    # IMPROVED MATCH STATUS (From Code 2)
    try:
        match_status = soup.find('div', class_="cb-col cb-col-100 cb-min-stts cb-text-complete").text.strip()
    except:
        match_status = "Match in progress"

    # Existing CRR/RRR extraction
    crr_label = soup.find('span', string=lambda x: x and 'CRR' in x)
    crr_value = crr_label.find_next('span').text.strip() if crr_label else "N/A"

    rrr_label = soup.find('span', string=lambda x: x and 'REQ:' in x)
    rrr_value = rrr_label.find_next('span').text.strip() if rrr_label else "N/A"

    # Player extraction (unchanged)
    batters = []
    bowlers = []
    section = None

    for tag in soup.find_all():
        if tag.name == 'div' and tag.get_text(strip=True) == "Batter":
            section = "batter"
        elif tag.name == 'div' and tag.get_text(strip=True) == "Bowler":
            section = "bowler"

        if tag.name == 'div' and 'cb-min-itm-rw' in tag.get('class', []):
            anchor = tag.find('a', class_='cb-text-link')
            if not anchor:
                continue

            name = anchor.text.strip()
            profile_url = "https://www.cricbuzz.com/" + anchor['href'].strip()
            stats = tag.find_all('div', class_='cb-col')
            values = [s.text.strip() for s in stats if 'text-right' in s.get('class', [])]

            if section == "batter" and len(values) == 5:
                batters.append({
                    'name': name,
                    'url': profile_url,
                    'runs': values[0],
                    'balls': values[1],
                    'fours': values[2],
                    'sixes': values[3],
                    'strike_rate': values[4]
                })
            elif section == "bowler" and len(values) == 5:
                bowlers.append({
                    'name': name,
                    'url': profile_url,
                    'overs': values[0],
                    'maidens': values[1],
                    'runs_conceded': values[2],
                    'wickets': values[3],
                    'economy': values[4]
                })

    # IMPROVED SQUAD URL DETECTION (From Code 2)
    squad_url = None
    highlight_url = None
    nav_tabs = soup.find_all('a', class_="cb-nav-tab")
    for tab in nav_tabs:
        href = tab.get('href', '')
        if 'cricket-scores' in href or 'cricket-match-squads' in href:
            squad_url = "https://www.cricbuzz.com" + href
        elif 'cricket-match-highlights' in href:
            highlight_url = "https://www.cricbuzz.com" + href

    return {
        'first_batting_score': first_batting_team_score,
        'second_batting_score': second_batting_team_score,
        'match_status': match_status,  # New field
        'crr': crr_value,
        'rrr': rrr_value,
        'batters': batters,
        'bowlers': bowlers,
        'squad_url': squad_url,
        'highlight_url': highlight_url
    }

# ----------------------------
# FUNCTION 3: Squad Info
# ----------------------------
def get_squads_data(squad_url):
    if not squad_url:
        return None

    response = requests.get(squad_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # IMPROVED TEAM NAME EXTRACTION (From Code 2)
    team_headers = soup.find_all("h2", class_="cb-ltst-wgt-hdr")
    if len(team_headers) >= 2:
        team1_name = team_headers[0].text.strip()
        team2_name = team_headers[1].text.strip()
    else:
        team_names = [div.text.strip() for div in soup.find_all("div", class_="pad5")]
        team1_name = team_names[1] if len(team_names) > 1 else "Team 1"
        team2_name = team_names[3] if len(team_names) > 3 else "Team 2"

    base_url = "https://www.cricbuzz.com"
    left_cards = soup.find_all('a', class_='cb-col cb-col-100 pad10 cb-player-card-left')
    right_cards = soup.find_all('a', class_='cb-col cb-col-100 pad10 cb-player-card-right')

    def process_squad(cards):
        squad = []
        for card in cards:
            name_div = card.find('div', class_='cb-player-name-left') or card.find('div', class_='cb-player-name-right')
            if name_div:
                name_and_role = name_div.get_text(separator='|', strip=True).split('|')
                name = name_and_role[0].strip()
                role = name_and_role[1].strip() if len(name_and_role) > 1 else "Player"
                profile_link = base_url + card['href']
                squad.append({
                    'name': name,
                    'role': role,
                    'profile': profile_link
                })
        return squad

    return {
        'team1': {'name': team1_name, 'squad': process_squad(left_cards)},
        'team2': {'name': team2_name, 'squad': process_squad(right_cards)}
    }

# ----------------------------
# FUNCTION 4: Match Highlights
# ----------------------------
def get_match_highlights(match_id):
    api_url = f'https://www.cricbuzz.com/api/cricket-match/commentary/{match_id}'
    response = requests.get(api_url)
    json_data = json.loads(response.text)
    commentary = json_data.get("commentaryList", [])

    highlights = []
    for entry in commentary:
        over = entry.get("overNumber", "")
        bowler = entry.get("bowlerStriker", {}).get("bowlName", "")
        batsman = entry.get("batsmanStriker", {}).get("batName", "")
        text = entry.get("commText", "").strip()

        if "commentaryFormats" in entry:
            bold = entry["commentaryFormats"].get("bold", {})
            ids = bold.get("formatId", [])
            values = bold.get("formatValue", [])
            for tag, val in zip(ids, values):
                text = text.replace(tag, val)

        highlights.append({
            'over': over,
            'bowler': bowler,
            'batsman': batsman,
            'text': text,
            'is_wicket': entry.get("event") == "WICKET"
        })

    return highlights

# ----------------------------
# ROUTES
# ----------------------------

@app.route('/')
def home():
    return '✅ Cricbuzz Live Score API is running! Use /api/cricbuzz/live-scores?url='

@app.route('/api/cricbuzz/live-scores', methods=['GET'])
def cricbuzz_api():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing "url" query parameter'}), 400

    match_id, slug = extract_match_info(url)
    if not match_id:
        return jsonify({'error': 'Invalid Cricbuzz URL. Match ID not found.'}), 400

    try:
        live_data = get_live_match_data(match_id, slug)
        squads_data = get_squads_data(live_data.get('squad_url'))
        highlights = get_match_highlights(match_id)

        return jsonify({
            'match_id': match_id,
            'slug': slug,
            'live_data': live_data,
            'squads': squads_data,
            'highlights': highlights
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------------------
# Start the Flask app
# ----------------------------
if __name__ == '__main__':
    app.run(debug=True)