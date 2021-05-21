from discord.ext.commands import Context
from discord import Role, Guild
from typing import Optional


# TODO: Make this return a `Role` and add an exception?
# Should never fail.
def get_ta_role(guild: Guild) -> Optional[Role]:
    for role in guild.roles:
        if role.name == "TA":
            return role
    return None


async def get_ta_role_messaging(ctx: Context) -> Optional[Role]:
    role = None

    if ctx.guild:
        role = get_ta_role(ctx.guild)

    if role:
        return role
    else:
        await ctx.send("WARNING: There is currently no TA role on the server.")
        return None
