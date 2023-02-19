import os
import discord
from discord.ext import commands
from discord import app_commands
import discord_config
import Stats
import aiosqlite
import asyncio


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
        "derrpshot",
        "kyekaii",
        "naptimez"
    ])
    setattr(bot, "db", await aiosqlite.connect("data.db"))

    async with bot.db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS data(poll_id TEXT, time_polled TEXT, user INTEGER, wins INTEGER, losses INTEGER, kills INTEGER, deaths INTEGER)")

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
    await interaction.response.send_message(content="Fetching Stats...", ephemeral=True)
    await Stats.fetch_stats(interaction.channel_id, username)


bot.run(discord_config.TOKEN)
