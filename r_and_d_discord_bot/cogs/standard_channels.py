from discord import ClientUser, PermissionOverwrite, Role
from typing import List, Dict, Union
from discord.ext.commands import Cog, command, Context
from r_and_d_discord_bot.bot_wrapper import BotWrapper
from r_and_d_discord_bot.helper_functions import create_text_channel
import logging

logger = logging.getLogger(__name__)
PermissionUser = Union[ClientUser, Role]


class StandardChannels(Cog):
    def __init__(self, bot: BotWrapper):
        self.bot = bot

    @command()
    async def standard_channels(self, ctx: Context) -> None:
        """
        Creates common Discord channels.

        Create the following standard channels: #students-for-students,
        #questions, #looking-for-a-partner, #announcements. In the
        #announcements channel, only members with the TA role and the bot can
        send messages.
        """
        if ctx.guild is None:
            # Early exit, since this function crucially depends on the
            # ctx.guild not being None.
            return

        announcements_overwrites: Dict[PermissionUser, PermissionOverwrite] = {
            ctx.guild.default_role: PermissionOverwrite(send_messages=False)
        }

        ta_role = self.bot.get_ta_role(ctx.guild)
        announcements_overwrites[ta_role] = PermissionOverwrite(
            send_messages=True)
        bot_user = self.bot.user
        assert bot_user
        announcements_overwrites[bot_user] = PermissionOverwrite(
            send_messages=True)

        channels: List[Dict[str, object]] = [
            {
                "name": "students-for-students",
                "topic": "Ask questions to other students here",
            },
            {"name": "questions", "topic": "Ask questions to TAs here"},
            {"name": "looking-for-a-partner", "topic": "Find a partner here"},
            {
                "name": "announcements",
                "topic": "Important announcements",
                "overwrites": announcements_overwrites,
            },
        ]

        mentions = []
        for channel in channels:
            chan = await create_text_channel(
                ctx,
                str(channel["name"]),
                topic=channel.get("topic"),  # type: ignore
                overwrites=channel.get("overwrites"),
            )
            if chan:
                mentions += [chan.mention]

        if len(mentions) == 0:
            await ctx.send("The standard channels already exist!")
        else:
            await ctx.send("Created channels:\n" + "\n".join(mentions))

        return None
