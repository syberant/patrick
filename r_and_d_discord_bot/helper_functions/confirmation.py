from discord import Embed, Colour
import asyncio


async def ask_confirmation_embed(ctx, embed: Embed, timeout: int = 30) -> bool:
    """Asks the user for confirmation, requires embed."""

    message = await ctx.send(embed=embed)
    await message.add_reaction("👍")
    await message.add_reaction("👎")

    def check(reaction, user):
        return user == ctx.author and message == reaction.message and \
            reaction.emoji in ["👍", "👎"]

    try:
        reaction, user = await \
            ctx.bot.wait_for("reaction_add", timeout=timeout, check=check)
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

    raise Exception("This code should be unreachable")


async def ask_confirmation(ctx, msg: str, timeout: int = 30) -> bool:
    """Asks the user for confirmation, requires description."""

    embed = Embed(title="Confirmation", description=msg)
    await ask_confirmation(ctx, embed, timeout)
