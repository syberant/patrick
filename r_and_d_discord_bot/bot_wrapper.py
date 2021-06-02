from datetime import datetime
from discord import Guild, Member, Role, TextChannel
from discord.ext.commands import Bot, Cog
from typing import cast, Optional, Dict
from r_and_d_discord_bot.cogs.groups import SelfPlacementMessageData
import logging
import pickle

logger = logging.getLogger(__name__)


def get_ta_role(guild: Guild) -> Optional[Role]:
    for role in guild.roles:
        if role.name == "TA":
            return role
    return None


async def get_ta_students_role(guild: Guild, ta: Member) -> Role:
    """NOTE: will create a new role if TAs change their nickname."""

    name = "Students " + (ta.nick or ta.name)
    for r in guild.roles:
        if r.name == name:
            return r
    return await guild.create_role(name=name)


class AnnouncementsDataBinary:
    url: str
    d2l_session_val: str
    d2l_secure_session_val: str
    last_updated: Optional[datetime]
    channel: int  # TextChannel.id

    def __init__(self, announcements_data):  # announcements_data: AnnouncementsData
        self.url = announcements_data.url
        self.d2l_session_val = announcements_data.d2l_session_val
        self.d2l_secure_session_val = announcements_data.d2l_secure_session_val
        self.last_updated = announcements_data.last_updated
        self.channel = announcements_data.channel.id


class AnnouncementsData:
    # URL of Announcements page
    url: str
    d2l_session_val: str
    d2l_secure_session_val: str
    # Last time announcements were fetched
    last_updated: Optional[datetime]
    # Announcements channel
    channel: TextChannel

    def __init__(
            self,
            url: str,
            d2l_session_val: str,
            d2l_secure_session_val: str,
            last_updated: Optional[datetime],
            channel: TextChannel
    ):
        self.url = url
        self.d2l_session_val = d2l_session_val
        self.d2l_secure_session_val = d2l_secure_session_val
        self.last_updated = last_updated
        self.channel = channel

    @staticmethod
    def from_bin(announcements_data_bin: AnnouncementsDataBinary, guild: Guild):
        url = announcements_data_bin.url
        d2l_session_val = announcements_data_bin.d2l_session_val
        d2l_secure_session_val = announcements_data_bin.d2l_secure_session_val
        last_updated = announcements_data_bin.last_updated
        channel = guild.get_channel(announcements_data_bin.channel)
        assert channel
        channel = cast(TextChannel, channel)
        return AnnouncementsData(url, d2l_session_val, d2l_secure_session_val, last_updated, channel)


class GuildDataBinary:
    """
    A class that stores a serialisable copy of GuildData.
    """

    ta_role: int  # Role.id
    student_roles: Dict[int, int]  # Dict[Member.id, Role.id]
    announcements_data: Optional[AnnouncementsDataBinary]

    def __init__(self, guild_data):
        self.ta_role = guild_data.ta_role.id
        self.student_roles = {
            ta.id: student_role.id
            for ta, student_role in guild_data.student_roles.items()
        }
        self.announcements_data = None
        if guild_data.announcements_data:
            self.announcements_data = AnnouncementsDataBinary(guild_data.announcements_data)


class GuildData:
    guild: Guild
    ta_role: Optional[Role]
    student_roles: Dict[Member, Role]
    announcements_data: Optional[AnnouncementsData]
    placement_message: Optional[SelfPlacementMessageData]

    def __init__(self, guild_data_bin: Optional[GuildDataBinary], guild: Guild):
        self.guild = guild
        self.ta_role = None
        self.student_roles = {}
        self.announcements_data = None
        self.self_placement_message = None

        if guild_data_bin:
            ta_role = guild.get_role(guild_data_bin.ta_role)
            if ta_role:
                self.ta_role = ta_role

            student_roles = {}
            if guild_data_bin:
                for member_id, role_id in guild_data_bin.student_roles.items():
                    member = guild.get_member(member_id)
                    role = guild.get_role(role_id)
                    if member and role:
                        student_roles[member] = role

            self.student_roles = student_roles

            if guild_data_bin.announcements_data:
                self.announcements_data = AnnouncementsData.from_bin(guild_data_bin.announcements_data, guild)

    def get_ta_role(self, guild: Guild) -> Optional[Role]:
        return self.ta_role

    def get_student_role(self, guild: Guild, ta: Member) -> Optional[Role]:
        return self.student_roles.get(ta)


class BotWrapper(Bot):
    # The file from which the guild data is read and to which it is written.
    guild_data_filename: str
    guild_data: Dict[int, GuildData]  # Dict[Guild.id, GuildData]

    def __init__(self, guild_data_filename: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guild_data = {}
        self.guild_data_filename = guild_data_filename

    def __del__(self):
        logging.info(f"Writing guild data to {self.guild_data_filename}")
        with open(self.guild_data_filename, "wb") as f:
            pickle.dump({guild_id: GuildDataBinary(data)
                         for guild_id, data in self.guild_data.items()}, f)

    @Cog.listener()
    async def on_ready(self):
        logger.info(f"Reading guild data from {self.guild_data_filename}")
        try:
            with open(self.guild_data_filename, "rb") as f:
                guild_data_bin = pickle.load(f)
                self.guild_data = {
                    guild.id: GuildData(guild_data_bin.get(guild.id), guild)
                    for guild in self.guilds
                }
        except FileNotFoundError:
            logging.info(
                f"Guild data file {self.guild_data_filename} does not exist;" +
                " creating it when saving the guild data instead.")
            self.guild_data = {
                guild.id: GuildData(None, guild) for guild in self.guilds
            }

        # Update guild data if necessary.
        for guild in self.guilds:
            gd = self.guild_data[guild.id]
            if not gd.ta_role:
                gd.ta_role = get_ta_role(guild)
                if not gd.ta_role:
                    logger.error(
                        f"Could not find TA role for server {guild.name}.")

                    owner = guild.owner
                    if owner:
                        await owner.send(
                            f"Hello, sorry to bother you but your server \
                              '{guild.name}' does not appear to have a 'TA' \
                              role. This is required for most operations."
                        )
                    else:
                        logger.error(
                            "Could not find owner of server without TA role."
                        )
                    return

            gd.student_roles.update({
                ta: await get_ta_students_role(guild, ta)
                for ta in gd.ta_role.members
                if ta not in gd.student_roles.keys()
            })

    @Cog.listener()
    async def on_member_update(self, before, after):
        guild = after.guild
        guild_data = self.guild_data[guild.id]
        ta_role = guild_data.get_ta_role(guild)

        # Became TA
        if ta_role not in before.roles and ta_role in after.roles:
            role = await get_ta_students_role(guild, after)
            guild_data.student_roles[after.id] = role.id

        # Exit if no TA
        if ta_role not in after.roles:
            return

        # Changed nickname
        if before.nick != after.nick:
            name = after.nick or after.name
            # Change role name
            await guild_data.student_roles[after.id].edit(
                name=f"Students {name}"
            )
            # TODO: Also change category name?

    def get_ta_role(self, guild: Guild) -> Role:
        """
        NOTE: This method should be used after the on_ready event has
        happened.
        """
        ta_role = self.guild_data[guild.id].get_ta_role(guild)
        assert ta_role
        return ta_role

    def get_student_role(self, guild: Guild, ta: Member) -> Role:
        """
        Get the student role for a TA in a guild.

        NOTE: This method should be used after the on_ready event has
        happened.
        """
        return self.guild_data[guild.id].student_roles[ta]
