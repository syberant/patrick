import asyncio
from discord import Embed, Colour
from discord.ext import commands


async def ask_confirmation(ctx, msg: str) -> bool:
    """Asks the user for confirmation."""

    embed = Embed(title="Confirmation", description=msg)
    message = await ctx.send(embed=embed)
    await asyncio.gather(message.add_reaction("👍"), message.add_reaction("👎"))

    def check(reaction, user):
        return user == ctx.author and message == reaction.message and reaction.emoji in ["👍", "👎"]

    try:
        reaction, user = await ctx.bot.wait_for("reaction_add", timeout=30, check=check)
    except asyncio.TimeoutError:
        embed.title = "Timed out"
        embed.colour = Colour.red()
        await asyncio.gather(message.edit(embed=embed), message.clear_reactions())
        return False
    else:
        if reaction.emoji == "👎":
            embed.title = "Denied"
            embed.colour = Colour.red()
            await asyncio.gather(message.edit(embed=embed), message.clear_reactions())
            return False
        elif reaction.emoji == "👍":
            embed.title = "Confirmed"
            embed.colour = Colour.green()
            await asyncio.gather(message.edit(embed=embed), message.clear_reactions())
            return True


def main():
    bot = commands.Bot(command_prefix='>')

    @bot.command()
    async def ping(ctx):
        await ctx.send('pong')

    bot.run('ODM0NzU0MjM2NjIwMzQxMjY4.YIFfdg.cAu7OaLqawMf0S3KI_b_kcFPqlY')
