from discord.ext.commands import Bot, Cog
from discord import Guild, Member, Role
from typing import Optional, Dict, Any
import logging
import asyncio


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

    # TODO: automatically forward all args
    def __init__(self, command_prefix: str, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    # TODO: cleaner option to wait for guilds to become available
    @Cog.listener()
    async def on_ready(self):
        # TODO: Use guild_id instead.
        self.guild_data: Dict[Guild, Any] = {}
        # TODO: Do multiple guilds in parallel
        for g in self.guilds:
            #  asyncio.run(self.init_guild(g))
            await self.init_guild(g)

    async def init_guild(self, guild: Guild):
        ta = get_ta_role(guild)
        if not ta:
            logging.error(f"Could not find TA role for server {guild.name}.")

            owner = guild.owner
            if owner:
                await owner.send(f"Hello, sorry to bother you but your server '{guild.name}' does not appear to have a 'TA' role. This is required for most operations.")
            else:
                logging.critical("Could not find owner of server without TA role.")
            return

        self.guild_data[guild] = GuildData()
        gd = self.guild_data[guild]
        gd.ta = ta
        gd.student_roles = {t: await get_ta_students_role(guild, t) for t in ta.members}

    # TODO
    #  @Cog.listener()
    #  def on_member_update(self, before, after):
