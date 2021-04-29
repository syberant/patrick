import discord
from discord.ext import commands
from r_and_d_discord_bot.cogs import Development, StandardChannels


def main():
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix='>', intents=intents)

    bot.add_cog(Development(bot))
    bot.add_cog(StandardChannels(bot))

    bot.run('ODM0NzU0MjM2NjIwMzQxMjY4.YIFfdg.cAu7OaLqawMf0S3KI_b_kcFPqlY')
