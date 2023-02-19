from io import StringIO
import aiohttp
import time
import pandas as pd


async def fetch_stats(usernames: []) -> pd.DataFrame:
    results = pd.DataFrame(columns=['gamertag', 'win%', 'kd'])
    for username in usernames:
        url = f"https://leafapp.co/player/{username}/matches/csv/matches"
        print(f'retrieving stats for {username}')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"error: file NOT retrieved for {username}!")
                    continue
                print(f"file retrieved for {username}!")
                csv_string = await resp.text()
        # convert to dataframe
        csv_string_io = StringIO(csv_string)
        # print(csv_string)
        csv_string_io.seek(0)
        data = pd.read_csv(csv_string_io, sep=',')
        data = data.query("Playlist == 'Tactical Slayer'")
        # print(data)
        # calculate kd
        kills = data['Kills'].astype(float).sum()
        print(f'kills: {kills}')
        deaths = data['Deaths'].astype(float).sum()
        print(f'deaths: {deaths}')
        kd = 0
        if deaths == 0:
            kd = "---"
        else:
            kd = kills / deaths

        # calc win%
        total_outcomes = len(data)
        wins = len(data.query("Outcome == 'Win'"))
        if total_outcomes == 0:
            win_percentage = "---"
        else:
            win_percentage = round((wins / total_outcomes), 2)

        # add row to dataframe
        # row = {'gamertag': username, 'kd': kd, 'win%': win_percentage}
        # results = results.append(row, ignore_index=True)
        row = pd.Series({'gamertag': username, 'win%': win_percentage, 'kd': kd})
        results = pd.concat([results, row.to_frame().T], ignore_index=True)
        results.sort_values('kd')
        # print(results)

        # stop 1 second before each request
        time.sleep(1)
    return results