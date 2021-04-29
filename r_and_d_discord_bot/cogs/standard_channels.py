from discord import PermissionOverwrite, Role, TextChannel
from typing import Optional
from discord.ext.commands import Cog, command, Context
import logging


class StandardChannels(Cog):

    def __init__(self, bot):
        self.bot = bot

    # TODO: maak kanaal niet dubbel aan.
    # TODO: misschien bericht sturen om kanaal uit te leggen?
    @command()
    async def standard_channels(self, ctx: Context) -> None:
        channels = [
            {"name": "students-for-students",
                "topic": "Ask questions to other students here"},
            {"name": "questions", "topic": "Ask questions to TAs here"},
            {"name": "looking-for-a-partner", "topic": "Find a partner here"},
        ]

        mentions = []
        for channel in channels:
            chan = await ctx.guild.create_text_channel(
                channel["name"],
                topic=channel["topic"]
            )
            mentions += [chan.mention]

        announcements = await self.make_announcements(ctx)
        mentions += [announcements.mention]

        await ctx.send("Created channels:\n" + "\n".join(mentions))

    async def make_announcements(self, ctx: Context) -> TextChannel:
        overwrites = {
            ctx.guild.default_role: PermissionOverwrite(send_messages=False)}

        ta_role = self.get_ta_role(ctx)
        if ta_role:
            overwrites[ta_role] = PermissionOverwrite(send_messages=True)
        else:
            logging.warning("Could not find TA role.")

        return await ctx.guild.create_text_channel(
            "announcements",
            overwrites=overwrites,
            topic="Important announcements",
        )

    # TODO: op een of andere manier standaardiseren.
    def get_ta_role(self, ctx: Context) -> Optional[Role]:
        for role in ctx.guild.roles:
            if role.name == "TA":
                return role

        return None
