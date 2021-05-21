import logging
import random
import discord
from discord.ext.commands import Bot, Cog, command, has_permissions
from discord import (Embed, Guild, Member, Role, PermissionOverwrite,
                     CategoryChannel)
from typing import Optional, Tuple, List, Dict
from r_and_d_discord_bot.helper_functions import (
    get_ta_role_messaging,
    get_ta_role,
    create_text_channel,
    create_voice_channel,
    ask_confirmation_embed,
)


async def get_ta_students_role(guild: Guild, ta: Member):
    """ NOTE: will create a new role if TAs change their nickname """

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


def is_unplaced_student(m: Member, ta: Role):
    if m.bot:
        return False

    for r in m.roles:
        if r == ta or r.name.startswith("Students"):
            return False

    return True


async def placement_embed(ta: Role, guild: Guild, ta_emoji_mapping: Dict[Role, discord.PartialEmoji]) -> Embed:
    embed = Embed(
        title="Student roles",
        description="Use the emojis below to place yourself with a TA. Please spread evenly over the TAs.")

    for t in ta.members:
        name = t.nick or t.name
        role = await get_ta_students_role(guild, t)
        embed.add_field(name=name, value=f"{ta_emoji_mapping[role]} Currently {len(role.members)} student(s).")

    return embed


async def update_placement_message(channel, message_id: int, guild: Guild, ta_emoji_mapping: Dict[Role, discord.PartialEmoji]):
    ta = get_ta_role(guild)
    assert ta
    embed = await placement_embed(ta, guild, ta_emoji_mapping)
    message = await channel.fetch_message(message_id)
    await message.edit(embed=embed)

# TODO: Fix emojis
# Seems to break with (gender) modifiers
# Removed the sports part (which has those modifiers)
# Removed some emoji discord didn't seem to have.
EMOJIS = "🐶🐱🐭🐹🐰🦊🐻🐼🐻❄️🐨🐯🦁🐮🐷🐽🐸🐵🙈🙉🙊🐒🐔🐧🐦🐤🐣🐥🦆🦅🦉🦇🐺🐗🐴🦄🐝🪱🐛🦋🐌🐞🐜🪰🪲🪳🦟🦗🕷🕸🦂🐢🐍🦎🦖🦕🐙🦑🦐🦞🦀🐡🐠🐟🐬🐳🐋🦈🐊🐅🐆🦓🦍🦧🦣🐘🦛🦏🐪🐫🦒🦘🦬🐃🐂🐄🐎🐖🐏🐑🦙🐐🦌🐕🐩🦮🐕🦺🐈🪶🐓🦃🦤🦚🦜🦢🦩🕊🐇🦝🦨🦡🦫🦦🦥🐁🐀🐿🦔🐾🐉🐲🌵🎄🌲🌳🌴🪵🌱🌿☘️🍀🎍🪴🎋🍃🍂🍁🍄🐚🪨🌾💐🌷🌹🥀🌺🌸🌼🌻🌞🌝🌛🌜🌚🌕🌖🌗🌘🌑🌒🌓🌔🌙🌎🌍🌏🪐💫🌟✨☄️💥🔥🌪🌈☀️🌤⛅️🌥☁️🌦🌧⛈🌩🌨❄️☃️🌬💨💧💦☂️🌊🌫🍏🍎🍐🍊🍋🍌🍉🍇🍓🫐🍈🍒🍑🥭🍍🥥🥝🍅🍆🥑🥦🥬🥒🌶🫑🌽🥕🫒🧄🧅🥔🍠🥐🥯🍞🥖🥨🧀🥚🍳🧈🥞🧇🥓🥩🍗🍖🦴🌭🍔🍟🍕🫓🥪🥙🧆🌮🌯🫔🥗🥘🫕🥫🍝🍜🍲🍛🍣🍱🥟🦪🍤🍙🍚🍘🍥🥠🥮🍢🍡🍧🍨🍦🥧🧁🍰🎂🍮🍭🍬🍫🍿🍩🍪🌰🥜🍯🥛🍼🫖🍵🧃🥤🧋🍶🍺🍻🥂🍷🥃🍸🍹🧉🍾🧊🥄🍴🍽🥣🥡🥢🧂🏀🏈🥎🎾🏐🏉🥏🎱🪀🏓🏸🏒🏑🥍🏏🪃🥅⛳️🪁🏹🎣🤿🥊🥋🎽🛹🛼🛷⛸🥌🎿⛷🏂🪂🏆🥇🥈🥉🏅🎖🏵🎗🎫🎟🎪🎭🩰🎨🎬🎤🎧🎼🎹🥁🪘🎷🎺🪗🎸🪕🎻🎲♟🎯🎳🎮🎰🧩🚗🚕🚙🚌🚎🏎🚓🚑🚒🚐🛻🚚🚛🚜🦯🦽🦼🛴🚲🛵🏍🛺🚨🚔🚍🚘🚖🚡🚠🚟🚃🚋🚞🚝🚄🚅🚈🚂🚆🚇🚊🚉✈️🛫🛬🛩💺🛰🚀🛸🚁🛶🚤🛥🛳⛴🚢🪝🚧🚦🚥🚏🗺🗿🗽🗼🏰🏯🏟🎡🎢🎠⛱🏖🏝🏜🌋⛰🏔🗻🏕🛖🏠🏡🏘🏚🏗🏭🏢🏬🏣🏤🏥🏦🏨🏪🏫🏩💒🏛🕌🕍🛕🕋⛩🛤🛣🗾🎑🏞🌅🌄🌠🎇🎆🌇🌆🏙🌃🌌🌉🌁"


class Groups(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.emoji_ta_mapping = None
        self.ta_emoji_mapping = None
        self.message_id = None

    @command()
    @has_permissions(manage_channels=True)
    async def create_ta_categories(self, ctx):
        role = await get_ta_role_messaging(ctx)
        if not role:
            return

        added = {}

        for ta in role.members:
            category_name = "TA " + (ta.nick or ta.name)
            students = await get_ta_students_role(ctx.guild, ta)
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

        students = [s for s in ctx.guild.members if is_unplaced_student(s, ta)]
        roles = [await get_ta_students_role(ctx.guild, t)
                 for t in ctx.guild.members if ta in t.roles]
        member_counted_roles = [(len(r.members), r) for r in roles]

        distribution = {r: [] for r in roles}

        for s in students:
            r = self.place_student(member_counted_roles)
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

        student_roles = [await get_ta_students_role(ctx.guild, t)
                         for t in ctx.guild.members if ta in t.roles]
        distribution = {r: r.members for r in student_roles}

        embed = Embed(
            title="Overview of TA groups",
            description="This is the distribution of students over the TAs:")
        for r, stud in distribution.items():
            embed.add_field(name=r.name, value='\n'.join(
                [s.mention for s in stud]) or "Nobody")
        await ctx.send(embed=embed)

    @command()
    async def post_self_placement_message(self, ctx):
        ta = await get_ta_role_messaging(ctx)
        assert ta

        shuffled = random.sample(EMOJIS, len(ta.members))
        chosen_emoji = [discord.PartialEmoji(name=e) for e in shuffled]

        ta_emoji = {}
        emoji_ta = {}
        for t in ta.members:
            emoji = chosen_emoji[-1]
            chosen_emoji.pop()
            # TODO: do something when there's not enough emojis? We have a lot.
            role = await get_ta_students_role(ctx.guild, t)
            emoji_ta[emoji] = role
            ta_emoji[role] = emoji

        embed = await placement_embed(ta, ctx.guild, ta_emoji)

        message = await ctx.send(embed=embed)
        for e in emoji_ta.keys():
            try:
                await message.add_reaction(e)
            except discord.HTTPException:
                logging.warning(f"Error trying to use emoji: {str(e)} with name {e.name}")
                pass

        # TODO: use database
        self.message_id = message.id
        self.emoji_ta_mapping = emoji_ta
        self.ta_emoji_mapping = ta_emoji

    # Docs: https://discordpy.readthedocs.io/en/latest/api.html#discord.on_raw_reaction_add
    @Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        assert payload.member

        # Check if the placement message was sent
        if not self.emoji_ta_mapping or not self.message_id:
            return

        # Only count reactions to the right message
        if payload.message_id != self.message_id:
            return

        assert payload.guild_id
        guild = self.bot.get_guild(payload.guild_id)
        assert guild

        ta = get_ta_role(guild)
        assert ta
        # Don't assign to bots (protection against our own reactions)
        # Disallow enrolling with multiple TAs
        if not is_unplaced_student(payload.member, ta):
            return

        channel = await self.bot.fetch_channel(payload.channel_id)

        role = self.emoji_ta_mapping.get(payload.emoji)

        if role:
            await payload.member.add_roles(role)
            await payload.member.send(f"Reaction received in server '{guild.name}', placing you in '{role.name}'")

            # Update placement embed
            await update_placement_message(channel, payload.message_id, guild, self.ta_emoji_mapping)
        else:
            # Emoji does not correspond to a TA, removing to avoid confusion
            message = await channel.fetch_message(payload.message_id)
            await message.clear_reaction(payload.emoji)

    # TODO: Is deze listener nodig/wensbaar?
    @Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        # Check if the placement message was sent
        if not self.emoji_ta_mapping or not self.message_id:
            return

        assert payload.guild_id
        guild = self.bot.get_guild(payload.guild_id)
        assert guild

        member = guild.get_member(payload.user_id)

        # Don't remove from bots (protection against our own reactions)
        if member.bot:
            return

        # Only count reactions to the right message
        if payload.message_id != self.message_id:
            return

        channel = await self.bot.fetch_channel(payload.channel_id)

        role = self.emoji_ta_mapping.get(payload.emoji)

        if role:
            await member.remove_roles(role)
            await member.send(f"Reaction removed in server '{guild.name}', removing you from '{role.name}'")

            # Update placement embed
            await update_placement_message(channel, payload.message_id, guild, self.ta_emoji_mapping)
