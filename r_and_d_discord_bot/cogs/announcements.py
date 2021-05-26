from discord import Embed, Guild, TextChannel
from discord.ext import tasks
from discord.ext.commands import Cog, Context, command
from r_and_d_discord_bot.bot_wrapper import AnnouncementsData
import logging
from r_and_d_discord_bot.helper_functions import (
    get_brightspace_announcements
)

logger = logging.getLogger(__name__)


class Announcements(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.brightspace_announcements.start()

    @command()
    async def configure_announcements(
            self,
            ctx: Context,
            url: str,
            d2l_session_val: str,
            d2l_secure_session_val: str,
            channel: TextChannel,
    ) -> None:
        """
        Configure Brightspace announcements. This command requires four
        parameters: the URL of the announcements page, which can be reached by
        clicking the ‘Announcements’ link on the ‘Course Home’ page of a
        course; the `d2lSessionVal` and `d2lSecureSessionVal`, which can be
        found in the ‘Cookie’ request header of the request your browsers sends
        to the announcements page; the channel to send the announcements to.
        """
        if ctx.guild is None:
            return

        self.bot.guild_data[ctx.guild.id].announcements_data = AnnouncementsData(
            url,
            d2l_session_val,
            d2l_secure_session_val,
            None,
            channel
        )

    @tasks.loop(seconds=60)
    async def brightspace_announcements(self):
        logger.info("Sending announcements")
        for guild in self.bot.guilds:
            data = self.bot.guild_data[guild.id].announcements_data
            if data:
                await self.send_announcements(guild, data)

    async def send_announcements(self, guild: Guild, data: AnnouncementsData) -> None:
        announcements = get_brightspace_announcements(
            data.url, data.d2l_session_val, data.d2l_secure_session_val, since=data.last_updated)

        if announcements is None:
            logging.error("Could not retrieve announcements")
            return

        for title, date, message in announcements:
            embed = Embed(title=title, timestamp=date, description=message)
            if data.last_updated is None or date > data.last_updated:
                data.last_updated = date
            await data.channel.send(embed=embed)

    @brightspace_announcements.before_loop  # type:ignore
    async def before_announcements(self):
        logger.info("Waiting for bot to log in...")
        await self.bot.wait_until_ready()
