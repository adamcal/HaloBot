from io import StringIO
import aiohttp
import time
import pandas as pd
import uuid
from datetime import datetime


async def fetch_stats(usernames: []) -> pd.DataFrame:
    results = pd.DataFrame(columns=['poll_id', 'time_polled', 'gamertag', 'kills', 'deaths', 'wins', 'total_games'])

    poll_id = str(uuid.uuid4())

    for username in usernames:
        url = f"https://leafapp.co/player/{username}/matches/csv/matches"
        print(f'retrieving stats for {username}')
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"error: file NOT retrieved for {username}!")
                    continue
                print(f"file retrieved for {username}!")
                csv_string = await resp.text()
        # convert to dataframe
        csv_string_io = StringIO(csv_string)

        csv_string_io.seek(0)
        data = pd.read_csv(csv_string_io, sep=',')
        data = data.query("Playlist == 'Tactical Slayer'")

        total_games = len(data)
        if total_games == 0:
            print(f"error: {username} has 0 games!")
            continue

        kills = data['Kills'].astype(float).sum()
        deaths = data['Deaths'].astype(float).sum()
        wins = len(data.query("Outcome == 'Win'"))

        row = pd.Series({'poll_id': poll_id,
                         'time_polled': datetime.now(),
                         'gamertag': username,
                         'kills': kills,
                         'deaths': deaths,
                         'wins': wins,
                         'total_games': total_games})
        results = pd.concat([results, row.to_frame().T], ignore_index=True)

        # stop 1 second before each request
        time.sleep(1)

    return results
