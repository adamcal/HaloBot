from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks

import Stats


class leaderboard(commands.Cog):
    UPDATE_INTERVAL = 180  # in seconds
    # PARTICIPANTS = [
    #     "pkgoss",
    #     "tot tuba",
    #     "derrpshot",
    #     "kyekaii",
    #     "naptimez"
    # ]

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
            stats = await Stats.fetch_stats(usernames=self.bot.PARTICIPANTS)

    @app_commands.command(name='startleaderboard')
    async def startleaderboard(self, interaction: discord.Interaction):
        self.channel = await self.bot.fetch_channel(interaction.channel_id)
        self.started = datetime.now()
        await interaction.response.send_message(content="Fetching Stats for Leaderboard...", ephemeral=True)
        # self.loop.start()
        leaderboard_results = await Stats.fetch_stats(self.bot.PARTICIPANTS)

        async with self.bot.db.cursor() as cursor:


        leaderboard_results = leaderboard_results.sort_values('kd', ascending=False, ignore_index=True)
        leaderboard_results.index = leaderboard_results.index + 1
        print(leaderboard_results)
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
    await bot.add_cog(leaderboard(bot))
