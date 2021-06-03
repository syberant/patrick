# Protect against cyclic import for type annotations
# https://adamj.eu/tech/2021/05/13/python-type-hints-how-to-fix-circular-imports/
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from patrick.bot_wrapper import BotWrapper

import logging
import discord
from discord.ext.commands import Cog, Context, command, has_permissions
from discord import (
    Embed,
    Guild,
    Member,
    Role,
    PermissionOverwrite,
    CategoryChannel,
    TextChannel,
)
from typing import Tuple, List, Dict
from .self_placement import SelfPlacementMessageData, SelfPlacementMessageDataBinary
from patrick.helper_functions import (
    create_text_channel,
    create_voice_channel,
    ask_confirmation_embed,
)

logger = logging.getLogger(__name__)


async def get_or_create_category(
    guild: Guild, name: str, overwrites
) -> CategoryChannel:
    for c in guild.categories:
        if c.name == name:
            return c
    return await guild.create_category(name, overwrites=overwrites)


def is_unplaced_student(m: Member, ta_role: Role):
    if m.bot:
        return False

    for r in m.roles:
        if r == ta_role or r.name.startswith("Students"):
            return False

    return True


class Groups(Cog):
    bot: BotWrapper

    def __init__(self, bot: BotWrapper):
        self.bot = bot

    # TODO: Ask for confirmation before creating
    @command()
    @has_permissions(manage_channels=True)
    async def create_ta_categories(self, ctx: Context):
        """
        Creates categories for TAs and their students.

        For every TA a category, a text channel and a voice channel will be
        created. These will be private i.e. only visible to the TA and his/her
        students.
        """
        if not ctx.guild:
            return

        ta_role = self.bot.get_ta_role(ctx.guild)

        added: Dict[CategoryChannel, List[discord.abc.GuildChannel]] = {}

        for ta in ta_role.members:
            category_name = "TA " + (ta.nick or ta.name)
            students = self.bot.get_student_role(ctx.guild, ta)
            overwrites = {
                ctx.guild.default_role: PermissionOverwrite(
                    view_channel=False
                ),
                ta: PermissionOverwrite(view_channel=True),
                students: PermissionOverwrite(view_channel=True),
            }

            # Don't create duplicate categories
            category = await get_or_create_category(
                ctx.guild, category_name, overwrites
            )
            added[category] = []
            text = await create_text_channel(ctx, "tekst", category=category)
            if text:
                added[category].append(text)
            voice = await create_voice_channel(
                ctx, "spraak", category=category
            )
            if voice:
                added[category].append(voice)

        embed = Embed(
            title="Created TA categories",
            description="These are the channels that were added per TA:",
        )
        for category, channels in added.items():
            embed.add_field(
                name=category.name,
                value="\n".join([c.mention for c in channels]) or "None",
            )
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
    async def place_students(self, ctx: Context):
        """
        Randomly distribute students over TAs.

        This command will automatically and randomly distribute new students
        over the TAs. The placement will balance students among TAs and as
        such TAs with the fewest existing students will be the first to receive
        new students.

        New students are defined as accounts that satisfy all of the following
        conditions:
            - They are not a bot
            - They do not have the `TA` role
            - They do not have any `Students {ta}` role
        """
        if not ctx.guild:
            return

        ta_role = self.bot.get_ta_role(ctx.guild)

        students = [s for s in ctx.guild.members if is_unplaced_student(s, ta_role)]
        roles = [self.bot.get_student_role(ctx.guild, ta) for ta in ta_role.members]
        member_counted_roles = [(len(r.members), r) for r in roles]

        distribution: Dict[Role, List[Member]] = {r: [] for r in roles}

        for s in students:
            r = self.place_student(member_counted_roles)
            distribution[r].append(s)

        embed = Embed(
            title="Confirm placement?",
            description="This would be the distribution of new students over the TAs:",
        )
        for r, stud in distribution.items():
            embed.add_field(
                name=r.name,
                value="\n".join([s.mention for s in stud]) or "Nobody",
            )

        if await ask_confirmation_embed(ctx, embed):
            for r, stud in distribution.items():
                for s in stud:
                    await s.add_roles(r)

    @command()
    async def groups_overview(self, ctx: Context):
        """
        Overview of TAs and their students.

        For each TA it will print the names of their students, i.e. those with
        the `Students {ta}` role.
        """
        if not ctx.guild:
            return

        ta_role = self.bot.get_ta_role(ctx.guild)

        student_roles = [self.bot.get_student_role(ctx.guild, ta) for ta in ta_role.members]
        distribution = {r: r.members for r in student_roles}

        embed = Embed(
            title="Overview of TA groups",
            description="This is the distribution of students over the TAs:",
        )
        for r, stud in distribution.items():
            embed.add_field(
                name=r.name,
                value="\n".join([s.mention for s in stud]) or "Nobody",
            )
        await ctx.send(embed=embed)

    @command()
    async def post_self_placement_message(
        self, ctx: Context, target_channel: TextChannel
    ):
        """
        Allow students to choose their TA.

        Posts a message which lists all TAs, the amount of students they have
        and their associated emoji. These emoji will be posted as reactions
        and if a student clicks on them they would be assigned to that TA. If
        they then remove their reaction their `Students {ta}` role will be
        removed as well.

        Requires `target_channel` argument which is the channel where the
        message will be posted. The emoji are randomly sampled from a (large)
        preselected list.
        """
        guild = ctx.guild
        if not guild:
            return

        self.bot.guild_data[guild.id].placement_message = await SelfPlacementMessageData.create(
            guild, self.bot, target_channel
        )

    @Cog.listener()
    async def on_raw_reaction_add(
        self, payload: discord.RawReactionActionEvent
    ):
        assert payload.member
        assert payload.guild_id

        data = self.bot.guild_data[payload.guild_id].placement_message
        # Check if the placement message was sent
        if not data:
            return

        # Only count reactions to the right message
        if payload.message_id != data.message.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        assert guild
        ta_role = self.bot.get_ta_role(guild)
        # Don't assign to bots (protection against our own reactions)
        # Disallow enrolling with multiple TAs
        if not is_unplaced_student(payload.member, ta_role):
            return

        role = data.emoji_ta_mapping.get(payload.emoji)

        if role:
            await payload.member.add_roles(role)

            guild = self.bot.get_guild(payload.guild_id)
            assert guild
            await payload.member.send(
                f"Reaction received in server '{guild.name}', placing you in '{role.name}'"
            )

            # Update placement embed
            await data.update_placement_message()
        else:
            # Emoji does not correspond to a TA, removing to avoid confusion
            await data.message.clear_reaction(payload.emoji)

    @Cog.listener()
    async def on_raw_reaction_remove(
        self, payload: discord.RawReactionActionEvent
    ):
        assert payload.guild_id

        data = self.bot.guild_data[payload.guild_id].placement_message
        # Check if the placement message was sent
        if not data:
            return

        guild = self.bot.get_guild(payload.guild_id)
        assert guild

        member = guild.get_member(payload.user_id)
        assert member

        # Don't remove from bots (protection against our own reactions)
        if member.bot:
            return

        # Don't message TAs, they probably clicked on accident.
        ta_role = self.bot.get_ta_role(guild)
        if ta_role in member.roles:
            return

        # Only count reactions to the right message
        if payload.message_id != data.message.id:
            return

        role = data.emoji_ta_mapping.get(payload.emoji)

        if role:
            await member.remove_roles(role)
            await member.send(
                f"Reaction removed in server '{guild.name}', removing you from '{role.name}'"
            )

            # Update placement embed
            await data.update_placement_message()
