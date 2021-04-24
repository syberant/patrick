from discord.ext import commands
from r_and_d_discord_bot.cogs import Development


def main():
    bot = commands.Bot(command_prefix='>')

    bot.add_cog(Development(bot))

    bot.run('ODM0NzU0MjM2NjIwMzQxMjY4.YIFfdg.cAu7OaLqawMf0S3KI_b_kcFPqlY')
