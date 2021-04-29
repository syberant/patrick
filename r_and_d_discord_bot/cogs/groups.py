from discord.ext.commands import Cog, command, has_permissions
from r_and_d_discord_bot.helper_functions import ask_confirmation
from discord import Guild, Role, Member, PermissionOverwrite


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

class Groups(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command()
    @has_permissions(manage_channels=True)
    async def createTACategories(self, ctx):
        role = getTArole(ctx.guild)
        for ta in role.members:
            students = await getTAstudentsrole(ctx.guild, ta)
            overwrites = {
                ctx.guild.default_role: PermissionOverwrite(view_channel=False),
                ta: PermissionOverwrite(view_channel=True),
                students: PermissionOverwrite(view_channel=True),
            }

            category = await ctx.guild.create_category("TA " + ta.name, overwrites=overwrites)
            await ctx.guild.create_text_channel("tekst", category=category)
            await ctx.guild.create_voice_channel("spraak", category=category)
