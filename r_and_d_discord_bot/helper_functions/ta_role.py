from discord.ext.commands import Context
from discord import Role
from typing import Optional


def get_ta_role(ctx: Context) -> Optional[Role]:
    if ctx.guild:
        for role in ctx.guild.roles:
            if role.name == "TA":
                return role
    return None


async def get_ta_role_messaging(ctx: Context) -> Optional[Role]:
    role = get_ta_role(ctx)

    if role:
        return role
    else:
        await ctx.send("WARNING: There is currently no TA role on the server.")
        return None
