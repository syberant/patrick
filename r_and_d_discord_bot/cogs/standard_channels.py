from discord import PermissionOverwrite
from typing import List, Dict
from discord.ext.commands import Cog, command, Context
from r_and_d_discord_bot.bot_wrapper import BotWrapper
from r_and_d_discord_bot.helper_functions import create_text_channel
import logging


class StandardChannels(Cog):
    def __init__(self, bot: BotWrapper):
        self.bot = bot

    @command()
    async def standard_channels(self, ctx: Context) -> None:
        if ctx.guild is None:
            # Early exit, since this function crucially depends on the
            # ctx.guild not being None.
            return

        announcements_overwrites = {
            ctx.guild.default_role: PermissionOverwrite(send_messages=False)
        }

        ta_role = self.bot.guild_data[ctx.guild.id].ta
        if ta_role:
            announcements_overwrites[ta_role] = PermissionOverwrite(
                send_messages=True)
            bot_user = self.bot.user
            assert bot_user
            announcements_overwrites[bot_user] = PermissionOverwrite(
                send_messages=True)
        else:
            logging.warning("Could not find TA role.")

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
