from datetime import datetime

import discord
import pandas
from discord import app_commands
from discord.ext import commands, tasks

import DataService
from DatabaseService import store_data


async def prepare_leaderboard(data) -> pandas.DataFrame:
    lb = pandas.DataFrame(columns=['gamertag', 'win%', 'k/d'])

    for ind in data.index:
        kd = data['kills'][ind] / data['deaths'][ind]
        win_percentage = data['wins'][ind] / data['total_games'][ind]

        row = pandas.Series({'gamertag': data['gamertag'][ind],
                             'win%': win_percentage,
                             'k/d': kd})
        lb = pandas.concat([lb, row.to_frame().T], ignore_index=True)
    lb = lb.sort_values('k/d', ascending=False, ignore_index=True)
    lb.index = lb.index + 1
    return lb


class Leaderboard(commands.Cog):
    UPDATE_INTERVAL = 300  # in seconds

    def __init__(self, bot):
        self.last_message = None
        self.bot = bot
        self.channel = None
        self.started = None

    async def cog_load(self) -> None:
        print('cog loaded')

    @tasks.loop(seconds=1.0)
    async def loop(self):
        now = datetime.now()
        delta = now - self.started
        if delta.total_seconds() > self.UPDATE_INTERVAL:
            self.started = now
            await self.channel.send(f"it’s been {self.UPDATE_INTERVAL} seconds")
            stats = await DataService.fetch_stats(usernames=self.bot.PARTICIPANTS)
            await store_data(self.bot.db, stats)
            leaderboard_results = await prepare_leaderboard(stats)
            await self.send_leaderboard(leaderboard_results)

    @app_commands.command(name='start-leaderboard')
    async def start_leaderboard(self, interaction: discord.Interaction):
        self.channel = await self.bot.fetch_channel(interaction.channel_id)
        self.started = datetime.now()
        await interaction.response.send_message(content="Fetching Stats for Leaderboard...", ephemeral=True)
        self.loop.start()
        stats = await DataService.fetch_stats(self.bot.PARTICIPANTS)

        await store_data(self.bot.db, stats)

        leaderboard_results = await prepare_leaderboard(stats)
        await self.send_leaderboard(leaderboard_results)

    async def send_leaderboard(self, leaderboard_results):
        embed = discord.Embed(title='Leaderboard', colour=discord.Colour.from_str('0x0f8509'), type="rich")
        icon_file = discord.File("./icon.png", filename="icon.png")
        embed.set_thumbnail(url="attachment://icon.png")
        embed.description = f'Last updated at {datetime.now()}'
        table_data = f'```{leaderboard_results.to_markdown(tablefmt="heavy_grid")}```'
        embed.add_field(name='Results', value=table_data)

        await self.channel.send(file=icon_file, embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
