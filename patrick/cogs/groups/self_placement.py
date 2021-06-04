# Protect against cyclic import for type annotations
# https://adamj.eu/tech/2021/05/13/python-type-hints-how-to-fix-circular-imports/
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from patrick.bot_wrapper import BotWrapper

import asyncio
import logging
import random
import discord
from discord import (
    Embed,
    Guild,
    Role,
    TextChannel,
    PartialEmoji,
    Message,
    PartialMessage,
)
from typing import Dict, List, Tuple, Union

logger = logging.getLogger(__name__)


# Some of these are broken: ❄️🐨☘️🍀☄️💥☀️🌤⛅️🌥☁️🌦🌧⛈🌩🌨❄️☃️🌬💨💧💦☂️🌊⛳️🪁✈️🛫
EMOJIS = "🐶🐱🐭🐹🐰🦊🐻🐼🐻🐯🦁🐮🐷🐽🐸🐵🙈🙉🙊🐒🐔🐧🐦🐤🐣🐥🦆🦅🦉🦇🐺🐗🐴🦄🐝🪱🐛🦋🐌🐞🐜🪰🪲🪳🦟🦗🕷🕸🦂🐢🐍🦎🦖🦕🐙🦑🦐🦞🦀🐡🐠🐟🐬🐳🐋🦈🐊🐅🐆🦓🦍🦧🦣🐘🦛🦏🐪🐫🦒🦘🦬🐃🐂🐄🐎🐖🐏🐑🦙🐐🦌🐕🐩🦮🐕🦺🐈🪶🐓🦃🦤🦚🦜🦢🦩🕊🐇🦝🦨🦡🦫🦦🦥🐁🐀🐿🦔🐾🐉🐲🌵🎄🌲🌳🌴🪵🌱🌿🎍🪴🎋🍃🍂🍁🍄🐚🪨🌾💐🌷🌹🥀🌺🌸🌼🌻🌞🌝🌛🌜🌚🌕🌖🌗🌘🌑🌒🌓🌔🌙🌎🌍🌏🪐💫🌟✨🔥🌪🌈🌫🍏🍎🍐🍊🍋🍌🍉🍇🍓🫐🍈🍒🍑🥭🍍🥥🥝🍅🍆🥑🥦🥬🥒🌶🫑🌽🥕🫒🧄🧅🥔🍠🥐🥯🍞🥖🥨🧀🥚🍳🧈🥞🧇🥓🥩🍗🍖🦴🌭🍔🍟🍕🫓🥪🥙🧆🌮🌯🫔🥗🥘🫕🥫🍝🍜🍲🍛🍣🍱🥟🦪🍤🍙🍚🍘🍥🥠🥮🍢🍡🍧🍨🍦🥧🧁🍰🎂🍮🍭🍬🍫🍿🍩🍪🌰🥜🍯🥛🍼🫖🍵🧃🥤🧋🍶🍺🍻🥂🍷🥃🍸🍹🧉🍾🧊🥄🍴🍽🥣🥡🥢🧂🏀🏈🥎🎾🏐🏉🥏🎱🪀🏓🏸🏒🏑🥍🏏🪃🥅🏹🎣🤿🥊🥋🎽🛹🛼🛷⛸🥌🎿⛷🏂🪂🏆🥇🥈🥉🏅🎖🏵🎗🎫🎟🎪🎭🩰🎨🎬🎤🎧🎼🎹🥁🪘🎷🎺🪗🎸🪕🎻🎲♟🎯🎳🎮🎰🧩🚗🚕🚙🚌🚎🏎🚓🚑🚒🚐🛻🚚🚛🚜🦯🦽🦼🛴🚲🛵🏍🛺🚨🚔🚍🚘🚖🚡🚠🚟🚃🚋🚞🚝🚄🚅🚈🚂🚆🚇🚊🚉🛬🛩💺🛰🚀🛸🚁🛶🚤🛥🛳⛴🚢🪝🚧🚦🚥🚏🗺🗿🗽🗼🏰🏯🏟🎡🎢🎠⛱🏖🏝🏜🌋⛰🏔🗻🏕🛖🏠🏡🏘🏚🏗🏭🏢🏬🏣🏤🏥🏦🏨🏪🏫🏩💒🏛🕌🕍🛕🕋⛩🛤🛣🗾🎑🏞🌅🌄🌠🎇🎆🌇🌆🏙🌃🌌🌉🌁"  # noqa: E501


class SelfPlacementMessageDataBinary:
    mapping: List[Tuple[PartialEmoji, int]]
    channel_id: int
    message_id: int

    def __init__(self, data):  # data: SelfPlacementMessageData
        channel = data.message.channel
        self.channel_id = channel.id
        self.message_id = data.message.id

        self.mapping = [(e, role.id) for e, role in data.emoji_ta_mapping.items()]

    def to_data(self, guild: Guild, bot: BotWrapper) -> SelfPlacementMessageData:
        channel = guild.get_channel(self.channel_id)
        assert isinstance(channel, TextChannel)
        message = channel.get_partial_message(self.message_id)

        def unpack_mapping(e, r):
            role = guild.get_role(r)
            assert role
            return (e, role)

        unpacked_mapping = [unpack_mapping(e, r) for (e, r) in self.mapping]
        emoji_ta_mapping = {e: r for (e, r) in unpacked_mapping}
        ta_emoji_mapping = {r: e for (e, r) in unpacked_mapping}

        return SelfPlacementMessageData(emoji_ta_mapping, ta_emoji_mapping, message, guild, bot)


class SelfPlacementMessageData:
    emoji_ta_mapping: Dict[PartialEmoji, Role]
    ta_emoji_mapping: Dict[Role, PartialEmoji]
    message: Union[Message, PartialMessage]
    guild: Guild
    bot: BotWrapper

    def __init__(
            self,
            emoji_ta_mapping: Dict[PartialEmoji, Role],
            ta_emoji_mapping: Dict[Role, PartialEmoji],
            message: Union[Message, PartialMessage],
            guild: Guild,
            bot: BotWrapper,
            ):
        self.emoji_ta_mapping = emoji_ta_mapping
        self.ta_emoji_mapping = ta_emoji_mapping
        self.message = message
        self.guild = guild
        self.bot = bot

    async def _send_message(self, target_channel: TextChannel):
        embed = self._placement_embed()

        self.message = await target_channel.send(embed=embed)
        try:
            futures = [self.message.add_reaction(e) for e in self.emoji_ta_mapping.keys()]
            # Execute concurrently
            await asyncio.gather(*futures)
        except discord.HTTPException:
            logger.warning("Error trying to use emoji", exc_info=True)

    def _choose_emoji(self):
        ta_role = self.bot.get_ta_role(self.guild)

        shuffled = random.sample(EMOJIS, len(ta_role.members))
        chosen_emoji = [PartialEmoji(name=e) for e in shuffled]  # type: ignore

        ta_emoji = {}
        emoji_ta = {}
        for (ta, emoji) in zip(ta_role.members, chosen_emoji):
            role = self.bot.get_student_role(self.guild, ta)
            emoji_ta[emoji] = role
            ta_emoji[role] = emoji
        self.ta_emoji_mapping = ta_emoji
        self.emoji_ta_mapping = emoji_ta

    @staticmethod
    async def create(guild: Guild, bot: BotWrapper, target_channel: TextChannel) -> SelfPlacementMessageData:
        cls = SelfPlacementMessageData(None, None, None, guild, bot)  # type: ignore

        # Initialises emoji_ta_mapping and ta_emoji_mapping
        cls._choose_emoji()

        # Initialises message
        await cls._send_message(target_channel)

        return cls

    def _placement_embed(self) -> Embed:
        embed = Embed(
            title="Student roles",
            description="Use the emojis below to place yourself with a TA. Please spread evenly over the TAs.",
        )

        ta_role = self.bot.get_ta_role(self.guild)
        for ta in ta_role.members:
            name = ta.nick or ta.name
            role = self.bot.get_student_role(self.guild, ta)
            embed.add_field(
                name=name,
                value=f"{self.ta_emoji_mapping[role]} Currently {len(role.members)} student(s).",
            )

        return embed

    async def update_placement_message(self):
        embed = self._placement_embed()
        await self.message.edit(embed=embed)
