import os

import discord
from discord.ext import commands
from discord import app_commands
import discord_config
import aiosqlite
import DatabaseService

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

    setattr(bot, "PARTICIPANTS", [
        "pkgoss",
        "tot tuba",
        # "derrpshot",
        "kyekaii",
        # "naptimez"
    ])
    setattr(bot, "db", await aiosqlite.connect("data.db"))
    bot.db.row_factory = aiosqlite.Row

    async with bot.db.cursor() as cursor:
        await cursor.execute(
            "CREATE TABLE IF NOT EXISTS data(poll_id TEXT, time_polled TEXT, user INTEGER, wins INTEGER, total_games INTEGER, kills INTEGER, deaths INTEGER)")

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

    synced = await bot.tree.sync()
    print(f'Synced {synced} commands')


@app_commands.describe(
    username='Enter your username'
)
@bot.tree.command(name='kd')
async def add(interaction: discord.Interaction, username: str):
    # await interaction.response.send_message(content="Fetching Stats...", ephemeral=True)

    row = await DatabaseService.get_stats(bot.db, username)

    embed = discord.Embed(title=f"Stats for {row['user']}", colour=discord.Colour.from_str('0x0f8509'), type="rich")
    icon_file = discord.File("./icon.png", filename="icon.png")
    embed.set_thumbnail(url="attachment://icon.png")

    embed.description = f"Last updated at {row['time_polled']}"

    kd = round((row['kills'] / row['deaths']), 2)
    win_percentage = round((row['wins'] / row['total_games']), 2)

    embed.add_field(name='win%', value=win_percentage, inline=True)
    embed.add_field(name='k/d', value=kd, inline=True)

    await interaction.response.send_message(embed=embed, file=icon_file)


bot.run(discord_config.TOKEN)
