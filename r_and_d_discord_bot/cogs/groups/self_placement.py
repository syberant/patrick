# Protect against cyclic import for type annotations
# https://adamj.eu/tech/2021/05/13/python-type-hints-how-to-fix-circular-imports/
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from r_and_d_discord_bot.bot_wrapper import BotWrapper

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
)
from typing import Dict

logger = logging.getLogger(__name__)


# Some of these are broken: ❄️🐨☘️🍀☄️💥☀️🌤⛅️🌥☁️🌦🌧⛈🌩🌨❄️☃️🌬💨💧💦☂️🌊⛳️🪁✈️🛫
EMOJIS = "🐶🐱🐭🐹🐰🦊🐻🐼🐻🐯🦁🐮🐷🐽🐸🐵🙈🙉🙊🐒🐔🐧🐦🐤🐣🐥🦆🦅🦉🦇🐺🐗🐴🦄🐝🪱🐛🦋🐌🐞🐜🪰🪲🪳🦟🦗🕷🕸🦂🐢🐍🦎🦖🦕🐙🦑🦐🦞🦀🐡🐠🐟🐬🐳🐋🦈🐊🐅🐆🦓🦍🦧🦣🐘🦛🦏🐪🐫🦒🦘🦬🐃🐂🐄🐎🐖🐏🐑🦙🐐🦌🐕🐩🦮🐕🦺🐈🪶🐓🦃🦤🦚🦜🦢🦩🕊🐇🦝🦨🦡🦫🦦🦥🐁🐀🐿🦔🐾🐉🐲🌵🎄🌲🌳🌴🪵🌱🌿🎍🪴🎋🍃🍂🍁🍄🐚🪨🌾💐🌷🌹🥀🌺🌸🌼🌻🌞🌝🌛🌜🌚🌕🌖🌗🌘🌑🌒🌓🌔🌙🌎🌍🌏🪐💫🌟✨🔥🌪🌈🌫🍏🍎🍐🍊🍋🍌🍉🍇🍓🫐🍈🍒🍑🥭🍍🥥🥝🍅🍆🥑🥦🥬🥒🌶🫑🌽🥕🫒🧄🧅🥔🍠🥐🥯🍞🥖🥨🧀🥚🍳🧈🥞🧇🥓🥩🍗🍖🦴🌭🍔🍟🍕🫓🥪🥙🧆🌮🌯🫔🥗🥘🫕🥫🍝🍜🍲🍛🍣🍱🥟🦪🍤🍙🍚🍘🍥🥠🥮🍢🍡🍧🍨🍦🥧🧁🍰🎂🍮🍭🍬🍫🍿🍩🍪🌰🥜🍯🥛🍼🫖🍵🧃🥤🧋🍶🍺🍻🥂🍷🥃🍸🍹🧉🍾🧊🥄🍴🍽🥣🥡🥢🧂🏀🏈🥎🎾🏐🏉🥏🎱🪀🏓🏸🏒🏑🥍🏏🪃🥅🏹🎣🤿🥊🥋🎽🛹🛼🛷⛸🥌🎿⛷🏂🪂🏆🥇🥈🥉🏅🎖🏵🎗🎫🎟🎪🎭🩰🎨🎬🎤🎧🎼🎹🥁🪘🎷🎺🪗🎸🪕🎻🎲♟🎯🎳🎮🎰🧩🚗🚕🚙🚌🚎🏎🚓🚑🚒🚐🛻🚚🚛🚜🦯🦽🦼🛴🚲🛵🏍🛺🚨🚔🚍🚘🚖🚡🚠🚟🚃🚋🚞🚝🚄🚅🚈🚂🚆🚇🚊🚉🛬🛩💺🛰🚀🛸🚁🛶🚤🛥🛳⛴🚢🪝🚧🚦🚥🚏🗺🗿🗽🗼🏰🏯🏟🎡🎢🎠⛱🏖🏝🏜🌋⛰🏔🗻🏕🛖🏠🏡🏘🏚🏗🏭🏢🏬🏣🏤🏥🏦🏨🏪🏫🏩💒🏛🕌🕍🛕🕋⛩🛤🛣🗾🎑🏞🌅🌄🌠🎇🎆🌇🌆🏙🌃🌌🌉🌁"  # noqa: E501


class SelfPlacementMessageData:
    emoji_ta_mapping: Dict[PartialEmoji, Role]
    ta_emoji_mapping: Dict[Role, PartialEmoji]
    message_id: int

    async def send_message(self, guild: Guild, bot: BotWrapper, target_channel: TextChannel):
        embed = self._placement_embed(guild, bot)

        message = await target_channel.send(embed=embed)
        self.message_id = message.id
        try:
            futures = [message.add_reaction(e) for e in self.emoji_ta_mapping.keys()]
            # Execute concurrently
            await asyncio.gather(*futures)
        except discord.HTTPException:
            logger.warning("Error trying to use emoji", exc_info=True)

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

    def __init__(self, guild: Guild, bot: BotWrapper):
        self._choose_emoji(guild, bot)
        # NOTE: Message still needs to be sent but that's async so caller is
        # responsible for that

    def _placement_embed(self, guild: Guild, bot: BotWrapper) -> Embed:
        embed = Embed(
            title="Student roles",
            description="Use the emojis below to place yourself with a TA. \
                         Please spread evenly over the TAs.",
        )

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
        guild: Guild,
        bot: BotWrapper,
    ):
        embed = self._placement_embed(guild, bot)
        # TODO: Get channel myself
        message = await channel.fetch_message(message_id)
        await message.edit(embed=embed)
