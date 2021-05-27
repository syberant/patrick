from discord.ext.commands import Bot, Cog
from discord import Guild, Member, Role
from typing import Optional, Dict, Any
import logging


def get_ta_role(guild: Guild) -> Optional[Role]:
    for role in guild.roles:
        if role.name == "TA":
            return role
    return None


async def get_ta_students_role(guild: Guild, ta: Member):
    """ NOTE: will create a new role if TAs change their nickname """

    name = "Students " + (ta.nick or ta.name)
    for r in guild.roles:
        if r.name == name:
            return r
    return await guild.create_role(name=name)


class GuildData:
    pass


class BotWrapper(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @Cog.listener()
    async def on_ready(self):
        self.guild_data: Dict[int, Any] = {}

        for g in self.guilds:
            await self.init_guild(g)

    async def init_guild(self, guild: Guild):
        ta = get_ta_role(guild)
        if not ta:
            logging.error(f"Could not find TA role for server {guild.name}.")

            owner = guild.owner
            if owner:
                await owner.send(
                    f"Hello, sorry to bother you but your server '{guild.name}' does not appear to have a 'TA' role. This is required for most operations."
                )
            else:
                logging.critical(
                    "Could not find owner of server without TA role."
                )
            return

        self.guild_data[guild.id] = GuildData()
        gd = self.guild_data[guild.id]
        gd.ta = ta
        gd.student_roles = {
            t: await get_ta_students_role(guild, t) for t in ta.members
        }

    @Cog.listener()
    async def on_member_update(self, before, after):
        guild = after.guild
        guild_data = self.guild_data[guild.id]
        ta = guild_data.ta

        # Became TA
        if ta not in before.roles and ta in after.roles:
            guild_data.student_roles[after] = await get_ta_students_role(
                guild, after
            )

        # Exit if no TA
        if ta not in after.roles:
            return

        # Changed nickname
        if before.nick != after.nick:
            name = after.nick or after.name
            # Change role name
            await guild_data.student_roles[after].edit(name=f"Students {name}")
            # TODO: Also change category name?
