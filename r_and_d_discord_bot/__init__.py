import discord
from discord.ext import commands


def main():
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix='>', intents=intents)

    @bot.command()
    async def ping(ctx):
        await ctx.send('pong')

    bot.run('ODM0NzU0MjM2NjIwMzQxMjY4.YIFfdg.cAu7OaLqawMf0S3KI_b_kcFPqlY')
