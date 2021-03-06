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


# Some of these are broken: โ๏ธ๐จโ๏ธ๐โ๏ธ๐ฅโ๏ธ๐คโ๏ธ๐ฅโ๏ธ๐ฆ๐งโ๐ฉ๐จโ๏ธโ๏ธ๐ฌ๐จ๐ง๐ฆโ๏ธ๐โณ๏ธ๐ชโ๏ธ๐ซ
EMOJIS = "๐ถ๐ฑ๐ญ๐น๐ฐ๐ฆ๐ป๐ผ๐ป๐ฏ๐ฆ๐ฎ๐ท๐ฝ๐ธ๐ต๐๐๐๐๐๐ง๐ฆ๐ค๐ฃ๐ฅ๐ฆ๐ฆ๐ฆ๐ฆ๐บ๐๐ด๐ฆ๐๐ชฑ๐๐ฆ๐๐๐๐ชฐ๐ชฒ๐ชณ๐ฆ๐ฆ๐ท๐ธ๐ฆ๐ข๐๐ฆ๐ฆ๐ฆ๐๐ฆ๐ฆ๐ฆ๐ฆ๐ก๐ ๐๐ฌ๐ณ๐๐ฆ๐๐๐๐ฆ๐ฆ๐ฆง๐ฆฃ๐๐ฆ๐ฆ๐ช๐ซ๐ฆ๐ฆ๐ฆฌ๐๐๐๐๐๐๐๐ฆ๐๐ฆ๐๐ฉ๐ฆฎ๐๐ฆบ๐๐ชถ๐๐ฆ๐ฆค๐ฆ๐ฆ๐ฆข๐ฆฉ๐๐๐ฆ๐ฆจ๐ฆก๐ฆซ๐ฆฆ๐ฆฅ๐๐๐ฟ๐ฆ๐พ๐๐ฒ๐ต๐๐ฒ๐ณ๐ด๐ชต๐ฑ๐ฟ๐๐ชด๐๐๐๐๐๐๐ชจ๐พ๐๐ท๐น๐ฅ๐บ๐ธ๐ผ๐ป๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐ช๐ซ๐โจ๐ฅ๐ช๐๐ซ๐๐๐๐๐๐๐๐๐๐ซ๐๐๐๐ฅญ๐๐ฅฅ๐ฅ๐๐๐ฅ๐ฅฆ๐ฅฌ๐ฅ๐ถ๐ซ๐ฝ๐ฅ๐ซ๐ง๐ง๐ฅ๐ ๐ฅ๐ฅฏ๐๐ฅ๐ฅจ๐ง๐ฅ๐ณ๐ง๐ฅ๐ง๐ฅ๐ฅฉ๐๐๐ฆด๐ญ๐๐๐๐ซ๐ฅช๐ฅ๐ง๐ฎ๐ฏ๐ซ๐ฅ๐ฅ๐ซ๐ฅซ๐๐๐ฒ๐๐ฃ๐ฑ๐ฅ๐ฆช๐ค๐๐๐๐ฅ๐ฅ ๐ฅฎ๐ข๐ก๐ง๐จ๐ฆ๐ฅง๐ง๐ฐ๐๐ฎ๐ญ๐ฌ๐ซ๐ฟ๐ฉ๐ช๐ฐ๐ฅ๐ฏ๐ฅ๐ผ๐ซ๐ต๐ง๐ฅค๐ง๐ถ๐บ๐ป๐ฅ๐ท๐ฅ๐ธ๐น๐ง๐พ๐ง๐ฅ๐ด๐ฝ๐ฅฃ๐ฅก๐ฅข๐ง๐๐๐ฅ๐พ๐๐๐ฅ๐ฑ๐ช๐๐ธ๐๐๐ฅ๐๐ช๐ฅ๐น๐ฃ๐คฟ๐ฅ๐ฅ๐ฝ๐น๐ผ๐ทโธ๐ฅ๐ฟโท๐๐ช๐๐ฅ๐ฅ๐ฅ๐๐๐ต๐๐ซ๐๐ช๐ญ๐ฉฐ๐จ๐ฌ๐ค๐ง๐ผ๐น๐ฅ๐ช๐ท๐บ๐ช๐ธ๐ช๐ป๐ฒโ๐ฏ๐ณ๐ฎ๐ฐ๐งฉ๐๐๐๐๐๐๐๐๐๐๐ป๐๐๐๐ฆฏ๐ฆฝ๐ฆผ๐ด๐ฒ๐ต๐๐บ๐จ๐๐๐๐๐ก๐ ๐๐๐๐๐๐๐๐๐๐๐๐๐๐ฌ๐ฉ๐บ๐ฐ๐๐ธ๐๐ถ๐ค๐ฅ๐ณโด๐ข๐ช๐ง๐ฆ๐ฅ๐๐บ๐ฟ๐ฝ๐ผ๐ฐ๐ฏ๐๐ก๐ข๐ โฑ๐๐๐๐โฐ๐๐ป๐๐๐ ๐ก๐๐๐๐ญ๐ข๐ฌ๐ฃ๐ค๐ฅ๐ฆ๐จ๐ช๐ซ๐ฉ๐๐๐๐๐๐โฉ๐ค๐ฃ๐พ๐๐๐๐๐ ๐๐๐๐๐๐๐๐๐"  # noqa: E501


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
