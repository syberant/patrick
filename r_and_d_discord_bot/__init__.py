import discord
from discord import TextChannel
from discord.ext.commands import Bot, Context, CheckFailure, CommandError
from r_and_d_discord_bot.bot_wrapper import BotWrapper
from r_and_d_discord_bot.cogs import Development, Groups, StandardChannels
import os
import logging

logger = logging.getLogger(__name__)


class OnlyAdminCommands(CheckFailure):
    pass


def main():
    intents = discord.Intents.default()
    intents.members = True
    bot = BotWrapper("guilddata.pickle", command_prefix='>', intents=intents)

    bot.add_cog(Development(bot))
    bot.add_cog(Groups(bot))
    bot.add_cog(StandardChannels(bot))

    @bot.check
    async def admin_channel(ctx: Context) -> bool:
        if isinstance(ctx.channel, TextChannel):
            if ctx.channel.name == "admin":
                return True
            raise OnlyAdminCommands("Command sent in non-admin channel")
        raise OnlyAdminCommands("Command not sent in text channel of server," +
                                " so not in admin channel")

    @bot.event
    async def on_command_error(ctx: Context, error: CommandError):
        from discord.ext.commands import CommandNotFound, CommandInvokeError, UserInputError, CheckFailure

        if isinstance(error, UserInputError):
            await ctx.send(f"400 Bad Request: Some part of your input was incorrect, either too few arguments, \
                           too many arguments or invalid arguments. Have a look at `>help {ctx.invoked_with}`")
            return

        if isinstance(error, CommandNotFound):
            await ctx.send("404 Command Not Found: As far as this bot knows, that command does not exist.")
            return

        if isinstance(error, CheckFailure):
            if isinstance(error, OnlyAdminCommands):
                if ctx.guild:
                    await ctx.send("This channel can not be used for commands, please use #admin.")
                else:
                    await ctx.send("This channel cannot be used for commands, as it is not part of a server.")
            else:
                await ctx.send("403 Forbidden: You are for some reason (probably a good one) not permitted \
                               to execute this command.")
            return

        # Getting to more serious errors, log them.
        logger.error(f"Some error occured while executing command `{ctx.message.content}`", exc_info=error)

        if isinstance(error, CommandInvokeError):
            await ctx.send("500 Internal Server Error: Uh oh, something went wrong on our side \
                           while processing that command.")
        else:
            await ctx.send("An unknown error occured. Ask the server admin to have a look at the logs.")

    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        logging.critical(
            "No token provided, please set the environment " +
            "variable DISCORD_BOT_TOKEN to the Discord bot's token"
        )
        return

    bot.run(token)
