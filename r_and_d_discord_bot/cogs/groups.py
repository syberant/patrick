import asyncio
import logging
import random
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
    PartialEmoji,
)
from typing import Tuple, List, Dict
from r_and_d_discord_bot.bot_wrapper import BotWrapper
from r_and_d_discord_bot.helper_functions import (
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


class SelfPlacementMessageData:
    emoji_ta_mapping: Dict[PartialEmoji, Role]
    ta_emoji_mapping: Dict[Role, PartialEmoji]
    message_id: int

    async def _send_message(self, embed: Embed, target_channel: TextChannel):
        message = await target_channel.send(embed=embed)
        try:
            futures = [message.add_reaction(e) for e in self.emoji_ta_mapping.keys()]
            # Execute concurrently
            await asyncio.gather(*futures)
        except discord.HTTPException:
            logger.warning("Error trying to use emoji", exc_info=True)
        self.message_id = message.id

    def _choose_emoji(self, guild: Guild, bot: BotWrapper):
        ta_role = bot.get_ta_role(guild)

        shuffled = random.sample(EMOJIS, len(ta_role.members))
        chosen_emoji = [PartialEmoji(name=e) for e in shuffled]  # type: ignore

        ta_emoji = {}
        emoji_ta = {}
        for (ta, emoji) in zip(ta_role.members, chosen_emoji):
            role = bot.get_student_role(guild, ta)
            emoji_ta[emoji] = role
            ta_emoji[role] = emoji
        self.ta_emoji_mapping = ta_emoji
        self.emoji_ta_mapping = emoji_ta

    def __init__(self, guild: Guild, target_channel: TextChannel, bot: BotWrapper):
        self._choose_emoji(guild, bot)

        embed = self.placement_embed(guild.id, bot)
        asyncio.run(self._send_message(embed, target_channel))

    def placement_embed(self, guild_id: int, bot: BotWrapper) -> Embed:
        embed = Embed(
            title="Student roles",
            description="Use the emojis below to place yourself with a TA. \
                         Please spread evenly over the TAs.",
        )

        guild = bot.get_guild(guild_id)
        assert guild
        ta_role = bot.get_ta_role(guild)
        for ta in ta_role.members:
            name = ta.nick or ta.name
            role = bot.get_student_role(guild, ta)
            embed.add_field(
                name=name,
                value=f"{self.ta_emoji_mapping[role]} Currently {len(role.members)} \
                        student(s).",
            )

        return embed

    async def update_placement_message(
        self,
        channel,
        message_id: int,
        guild_id: int,
        bot: BotWrapper,
    ):
        embed = self.placement_embed(guild_id, bot)
        # TODO: Get channel myself
        message = await channel.fetch_message(message_id)
        await message.edit(embed=embed)


# Some of these are broken: ❄️🐨☘️🍀☄️💥☀️🌤⛅️🌥☁️🌦🌧⛈🌩🌨❄️☃️🌬💨💧💦☂️🌊⛳️🪁✈️🛫
EMOJIS = "🐶🐱🐭🐹🐰🦊🐻🐼🐻🐯🦁🐮🐷🐽🐸🐵🙈🙉🙊🐒🐔🐧🐦🐤🐣🐥🦆🦅🦉🦇🐺🐗🐴🦄🐝🪱🐛🦋🐌🐞🐜🪰🪲🪳🦟🦗🕷🕸🦂🐢🐍🦎🦖🦕🐙🦑🦐🦞🦀🐡🐠🐟🐬🐳🐋🦈🐊🐅🐆🦓🦍🦧🦣🐘🦛🦏🐪🐫🦒🦘🦬🐃🐂🐄🐎🐖🐏🐑🦙🐐🦌🐕🐩🦮🐕🦺🐈🪶🐓🦃🦤🦚🦜🦢🦩🕊🐇🦝🦨🦡🦫🦦🦥🐁🐀🐿🦔🐾🐉🐲🌵🎄🌲🌳🌴🪵🌱🌿🎍🪴🎋🍃🍂🍁🍄🐚🪨🌾💐🌷🌹🥀🌺🌸🌼🌻🌞🌝🌛🌜🌚🌕🌖🌗🌘🌑🌒🌓🌔🌙🌎🌍🌏🪐💫🌟✨🔥🌪🌈🌫🍏🍎🍐🍊🍋🍌🍉🍇🍓🫐🍈🍒🍑🥭🍍🥥🥝🍅🍆🥑🥦🥬🥒🌶🫑🌽🥕🫒🧄🧅🥔🍠🥐🥯🍞🥖🥨🧀🥚🍳🧈🥞🧇🥓🥩🍗🍖🦴🌭🍔🍟🍕🫓🥪🥙🧆🌮🌯🫔🥗🥘🫕🥫🍝🍜🍲🍛🍣🍱🥟🦪🍤🍙🍚🍘🍥🥠🥮🍢🍡🍧🍨🍦🥧🧁🍰🎂🍮🍭🍬🍫🍿🍩🍪🌰🥜🍯🥛🍼🫖🍵🧃🥤🧋🍶🍺🍻🥂🍷🥃🍸🍹🧉🍾🧊🥄🍴🍽🥣🥡🥢🧂🏀🏈🥎🎾🏐🏉🥏🎱🪀🏓🏸🏒🏑🥍🏏🪃🥅🏹🎣🤿🥊🥋🎽🛹🛼🛷⛸🥌🎿⛷🏂🪂🏆🥇🥈🥉🏅🎖🏵🎗🎫🎟🎪🎭🩰🎨🎬🎤🎧🎼🎹🥁🪘🎷🎺🪗🎸🪕🎻🎲♟🎯🎳🎮🎰🧩🚗🚕🚙🚌🚎🏎🚓🚑🚒🚐🛻🚚🚛🚜🦯🦽🦼🛴🚲🛵🏍🛺🚨🚔🚍🚘🚖🚡🚠🚟🚃🚋🚞🚝🚄🚅🚈🚂🚆🚇🚊🚉🛬🛩💺🛰🚀🛸🚁🛶🚤🛥🛳⛴🚢🪝🚧🚦🚥🚏🗺🗿🗽🗼🏰🏯🏟🎡🎢🎠⛱🏖🏝🏜🌋⛰🏔🗻🏕🛖🏠🏡🏘🏚🏗🏭🏢🏬🏣🏤🏥🏦🏨🏪🏫🏩💒🏛🕌🕍🛕🕋⛩🛤🛣🗾🎑🏞🌅🌄🌠🎇🎆🌇🌆🏙🌃🌌🌉🌁"  # noqa: E501


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
            description="This would be the distribution \
                    of new students over the TAs:",
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

        guild_data = self.bot.guild_data[guild.id]
        guild_data.placement_message = SelfPlacementMessageData(guild, target_channel, self.bot)

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
        if payload.message_id != data.message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        assert guild
        ta_role = self.bot.get_ta_role(guild)
        # Don't assign to bots (protection against our own reactions)
        # Disallow enrolling with multiple TAs
        if not is_unplaced_student(payload.member, ta_role):
            return

        channel = await self.bot.fetch_channel(payload.channel_id)
        assert isinstance(channel, TextChannel)

        role = data.emoji_ta_mapping.get(payload.emoji)

        if role:
            await payload.member.add_roles(role)

            guild = self.bot.get_guild(payload.guild_id)
            assert guild
            await payload.member.send(
                f"Reaction received in server '{guild.name}', placing you in '{role.name}'"
            )

            # Update placement embed
            await data.update_placement_message(
                channel,
                payload.message_id,
                payload.guild_id,
                self.bot
            )
        else:
            # Emoji does not correspond to a TA, removing to avoid confusion
            message = await channel.fetch_message(payload.message_id)
            await message.clear_reaction(payload.emoji)

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
        if payload.message_id != data.message_id:
            return

        channel = await self.bot.fetch_channel(payload.channel_id)

        role = data.emoji_ta_mapping.get(payload.emoji)

        if role:
            await member.remove_roles(role)
            await member.send(
                f"Reaction removed in server '{guild.name}', \
                  removing you from '{role.name}'"
            )

            # Update placement embed
            await data.update_placement_message(
                channel,
                payload.message_id,
                payload.guild_id,
                self.bot
            )
