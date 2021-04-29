from discord.ext.commands import Cog, command, has_permissions
from discord import Guild, Role, Member, PermissionOverwrite, CategoryChannel
from typing import Optional


def getTArole(guild: Guild) -> Role:
    for r in guild.roles:
        if r.name == "TA":
            return r


async def getTAstudentsrole(guild: Guild, ta: Member):
    name = "Students " + ta.name
    for r in guild.roles:
        if r.name == name:
            return r
    return await guild.create_role(name=name)


def get_category(guild: Guild, name: str) -> Optional[CategoryChannel]:
    for c in guild.categories:
        if c.name == name:
            return c
    return None


class Groups(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command()
    @has_permissions(manage_channels=True)
    async def createTACategories(self, ctx):
        role = getTArole(ctx.guild)
        created = []
        preexisting = []

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
            if get_category(ctx.guild, category_name) is None:
                category = await ctx.guild.create_category(
                    category_name,
                    overwrites=overwrites)
                await ctx.guild.create_text_channel("tekst", category=category)
                await ctx.guild.create_voice_channel("spraak",
                                                     category=category)
                created.append(ta)
            else:
                preexisting.append(ta)

        await ctx.send("Created categories for these TAs: "
                       + ' '.join([ta.mention for ta in created]))
        await ctx.send("These TAs already had categories: "
                       + ' '.join([ta.mention for ta in preexisting]))
