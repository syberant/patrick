from discord.ext.commands import Cog, command, has_permissions
from discord import (Embed, Guild, Member, Role, PermissionOverwrite,
                     CategoryChannel)
from typing import Optional, Tuple, List
from r_and_d_discord_bot.helper_functions import (
    get_ta_role_messaging,
    create_text_channel,
    create_voice_channel,
    ask_confirmation_embed,
)


# NOTE: will create a new role if TAs change their nickname
async def get_ta_studentsrole(guild: Guild, ta: Member):
    name = "Students " + (ta.nick or ta.name)
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
    async def create_ta_categories(self, ctx):
        role = await get_ta_role_messaging(ctx)
        if not role:
            return

        added = {}

        for ta in role.members:
            category_name = "TA " + (ta.nick or ta.name)
            students = await get_ta_studentsrole(ctx.guild, ta)
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

    def place_student(self, roles: List[Tuple[int, Role]]) -> Role:
        # Find the ta with the fewest members
        (i, (a, r)) = min(enumerate(roles), key=lambda x: x[1])

        # Update member count
        roles[i] = (a + 1, r)
        # NOTE: doesn't add role yet

        return r

    @command()
    @has_permissions(manage_roles=True)
    async def place_students(self, ctx):
        ta = await get_ta_role_messaging(ctx)

        def to_be_placed(m: Member, ta: Role):
            if m.bot:
                return False

            for r in m.roles:
                if r == ta or r.name.startswith("Students"):
                    return False

            return True

        students = [s for s in ctx.guild.members if to_be_placed(s, ta)]
        tmp = [await get_ta_studentsrole(ctx.guild, t)
               for t in ctx.guild.members if ta in t.roles]
        roles = [(len(r.members), r) for r in tmp]

        distribution = {r: [] for r in tmp}

        for s in students:
            r = self.place_student(roles)
            distribution[r].append(s)

        embed = Embed(
            title="Confirm placement?",
            description="This would be the distribution \
                    of new students over the TAs:")
        for r, stud in distribution.items():
            embed.add_field(name=r.name, value='\n'.join(
                [s.mention for s in stud]) or "Nobody")

        if await ask_confirmation_embed(ctx, embed):
            for r, stud in distribution.items():
                for s in stud:
                    await s.add_roles(r)

    @command()
    async def groups_overview(self, ctx):
        ta = await get_ta_role_messaging(ctx)
        assert ta

        student_roles = [await get_ta_studentsrole(ctx.guild, t)
                         for t in ctx.guild.members if ta in t.roles]
        distribution = {r: r.members for r in student_roles}

        embed = Embed(
            title="Overview of TA groups",
            description="This is the distribution of students over the TAs:")
        for r, stud in distribution.items():
            embed.add_field(name=r.name, value='\n'.join(
                [s.mention for s in stud]) or "Nobody")
        await ctx.send(embed=embed)
