import discord
from discord import TextChannel
from discord.ext.commands import Bot, Context, CheckFailure
from r_and_d_discord_bot.cogs import Development, Groups, StandardChannels


class OnlyAdminCommands(CheckFailure):
    pass


def main():
    intents = discord.Intents.default()
    intents.members = True
    bot = Bot(command_prefix='>', intents=intents)

    bot.add_cog(Development(bot))
    bot.add_cog(Groups(bot))
    bot.add_cog(StandardChannels(bot))

    @bot.check
    async def admin_channel(ctx: Context) -> bool:
        if isinstance(ctx.channel, TextChannel):
            if ctx.channel.name == "admin":
                return True
            await ctx.send("This channel can not be used for commands," +
                           " please use #admin.")
            raise OnlyAdminCommands("Command sent in non-admin channel")
        await ctx.send("This channel cannot be used for commands, as it is" +
                       " not part of a server.")
        raise OnlyAdminCommands("Command not sent in text channel of server," +
                                " so not in admin channel")

    bot.run('ODM0NzU0MjM2NjIwMzQxMjY4.YIFfdg.cAu7OaLqawMf0S3KI_b_kcFPqlY')
