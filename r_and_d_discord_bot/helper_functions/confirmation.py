from discord import Embed, Colour
import asyncio


async def ask_confirmation(ctx, msg: str) -> bool:
    """Asks the user for confirmation."""

    embed = Embed(title="Confirmation", description=msg)
    message = await ctx.send(embed=embed)
    await message.add_reaction("👍")
    await message.add_reaction("👎")

    def check(reaction, user):
        return user == ctx.author and message == reaction.message and \
                reaction.emoji in ["👍", "👎"]

    try:
        reaction, user = await \
                ctx.bot.wait_for("reaction_add", timeout=30, check=check)
    except asyncio.TimeoutError:
        embed.title = "Timed out"
        embed.colour = Colour.red()
        await message.edit(embed=embed)
        await message.clear_reactions()
        return False
    else:
        if reaction.emoji == "👎":
            embed.title = "Denied"
            embed.colour = Colour.red()
            await message.edit(embed=embed)
            await message.clear_reactions()
            return False
        elif reaction.emoji == "👍":
            embed.title = "Confirmed"
            embed.colour = Colour.green()
            await message.edit(embed=embed)
            await message.clear_reactions()
            return True
