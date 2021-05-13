from discord.ext.commands import Cog, command, has_permissions
from discord import Embed, Guild, Member, PermissionOverwrite, CategoryChannel
from typing import Optional
from r_and_d_discord_bot.helper_functions import (
    get_ta_role_messaging,
    create_text_channel,
    create_voice_channel,
)


async def getTAstudentsrole(guild: Guild, ta: Member):
    name = "Students " + ta.name
    for r in guild.roles:
        if r.name == name:
            return r
    return await guild.create_role(name=name)


async def get_or_create_category(guild: Guild, name: str, overwrites) \
        -> Optional[CategoryChannel]:
    for c in guild.categories:
        if c.name == name:
            return c
    return await guild.create_category(name, overwrites=overwrites)


class Groups(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command()
    @has_permissions(manage_channels=True)
    async def createTACategories(self, ctx):
        role = await get_ta_role_messaging(ctx)
        if not role:
            return

        added = {}

        for ta in role.members:
            category_name = "TA " + ta.name
            students = await getTAstudentsrole(ctx.guild, ta)
            overwrites = {
                ctx.guild.default_role:
                    PermissionOverwrite(view_channel=False),
                ta: PermissionOverwrite(view_channel=True),
                students: PermissionOverwrite(view_channel=True),
            }

            # Don't create duplicate categories
            category = await get_or_create_category(ctx.guild, category_name,
                                                    overwrites)
            added[category] = []
            res = await create_text_channel(ctx, "tekst", category=category)
            if res:
                added[category].append(res)
            res = await create_voice_channel(ctx, "spraak", category=category)
            if res:
                added[category].append(res)

        embed = Embed(
            title="Created TA categories",
            description="These are the channels that were added per TA:")
        for category, channels in added.items():
            embed.add_field(name=category.name, value='\n'.join(
                [c.mention for c in channels]) or "None")
        await ctx.send(embed=embed)
