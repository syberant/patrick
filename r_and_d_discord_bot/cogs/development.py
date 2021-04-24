from discord.ext.commands import Cog, command
from r_and_d_discord_bot.helper_functions import ask_confirmation


# Aid in development and testing. Should be either removed, disabled or polished and require an Admin role in final product
class Development(Cog):

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        print("Bot is online.")

    @command()
    async def ping(self, ctx):
        await ctx.send('pong')

    @command()
    async def create_channel(self, ctx, name):
        channel = await ctx.guild.create_text_channel(name)
        await ctx.send("Created channel " + channel.mention)

    @command()
    async def clear_channel(self, ctx, name):
        for c in ctx.guild.channels:
            if (c.name == name):
                await c.delete()

    @command()
    async def clear_all_channels(self, ctx):
        candidates = [c for c in ctx.guild.channels if c.name not in ["Text Channels", "Voice Channels", "General", "general"]]
        descr = "Delete following channels?\n" + '\n'.join(map(lambda c: c.mention, candidates))
        confirmed = await ask_confirmation(ctx, descr)
        if (confirmed):
            for c in candidates:
                await c.delete()
