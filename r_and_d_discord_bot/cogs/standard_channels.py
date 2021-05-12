from discord import PermissionOverwrite, Role, TextChannel
from typing import Optional
from discord.ext.commands import Cog, command, Context
import logging


class StandardChannels(Cog):

    def __init__(self, bot):
        self.bot = bot

    # TODO: misschien bericht sturen om kanaal uit te leggen?
    @command()
    async def standard_channels(self, ctx: Context) -> None:
        announcements_overwrites = {
            ctx.guild.default_role: PermissionOverwrite(send_messages=False)}

        ta_role = self.get_ta_role(ctx)
        if ta_role:
            announcements_overwrites[ta_role] = PermissionOverwrite(
                send_messages=True)
        else:
            logging.warning("Could not find TA role.")

        channels = [
            {"name": "students-for-students",
                "topic": "Ask questions to other students here"},
            {"name": "questions", "topic": "Ask questions to TAs here"},
            {"name": "looking-for-a-partner", "topic": "Find a partner here"},
            {"name": "announcements", "topic": "Important announcements",
                "overwrites": announcements_overwrites}
        ]

        mentions = []
        for channel in channels:
            chan = await self.create_text_channel(
                ctx,
                channel["name"],
                topic=channel.get("topic"),
                overwrites=channel.get("overwrites"),
            )
            if chan:
                mentions += [chan.mention]

        if len(mentions) == 0:
            await ctx.send("The standard channels already exist!")
        else:
            await ctx.send("Created channels:\n" + "\n".join(mentions))

    async def create_text_channel(
            self,
            ctx: Context,
            name: str,
            topic: str = None,
            overwrites=None) -> Optional[TextChannel]:
        """
        Create a text channel with the given parameters if no text channel with
        the given name exists.
        """

        if ctx.guild:
            for channel in ctx.guild.channels:
                if channel.name == name:
                    return None

            return await ctx.guild.create_text_channel(
                name,
                topic=topic,
                overwrites=overwrites,
            )

    # TODO: op een of andere manier standaardiseren.
    def get_ta_role(self, ctx: Context) -> Optional[Role]:
        for role in ctx.guild.roles:
            if role.name == "TA":
                return role

        return None
