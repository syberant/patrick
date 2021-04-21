import discord
from discord.ext import commands

def main():
    bot = commands.Bot(command_prefix='>')

    @bot.command()
    async def ping(ctx):
        await ctx.send('pong')

    bot.run('token')

