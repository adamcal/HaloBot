from aiosqlite import Row


async def store_data(db, data):
    for ind in data.index:
        row = {'poll_id': data['poll_id'][ind],
               'time_polled': str(data['time_polled'][ind]),
               'user': data['gamertag'][ind],
               'wins': data['wins'][ind],
               'total_games': data['total_games'][ind],
               'kills': data['kills'][ind],
               'deaths': data['deaths'][ind]}
        async with db.cursor() as cursor:
            await cursor.execute(
                """INSERT INTO data (poll_id, time_polled, user, wins, total_games, kills, deaths) 
                VALUES(:poll_id, :time_polled, :user, :wins, :total_games, :kills, :deaths);""",
                row)
            await db.commit()


async def get_stats(db, user) -> Row:

    async with db.cursor() as cursor:
        await cursor.execute("""SELECT * FROM data WHERE user=? ORDER BY ROWID DESC LIMIT 1""", (user,))
        row = await cursor.fetchone()

    return row
