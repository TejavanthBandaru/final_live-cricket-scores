

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
