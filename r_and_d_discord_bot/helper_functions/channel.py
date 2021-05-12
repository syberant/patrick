from discord import TextChannel, VoiceChannel, CategoryChannel
from discord.ext.commands import Context
from typing import Optional


async def create_text_channel(
        ctx: Context,
        name: str,
        topic: Optional[str] = None,
        overwrites=None,
        category: CategoryChannel = None,
) -> Optional[TextChannel]:
    """
    Create a text channel with the given parameters if no text channel with
    the given name exists within the guild if category is None, within the
    category if a category is supplied.
    """

    if ctx.guild:
        if category:
            channels = category.text_channels
        else:
            # If category is not supplied, only check channels without
            # a category.
            channels = [
                c for c in ctx.guild.text_channels if c.category is None]
        for channel in channels:
            if channel.name == name:
                return None

        if topic:
            return await ctx.guild.create_text_channel(
                name,
                topic=topic,
                overwrites=overwrites,
                category=category,
            )
        else:
            return await ctx.guild.create_text_channel(
                name,
                overwrites=overwrites,
                category=category,
            )

    return None


async def create_voice_channel(
        ctx: Context,
        name: str,
        overwrites=None,
        category: CategoryChannel = None,
) -> Optional[VoiceChannel]:
    """
    Create a voice channel with the given parameters if no voice channel with
    the given name exists within the guild if category is None, within the
    category if a category is supplied.
    """

    if ctx.guild:
        if category:
            channels = category.voice_channels
        else:
            # If category is not supplied, only check channels without
            # a category.
            channels = [
                c for c in ctx.guild.voice_channels if c.category is None]
        for channel in channels:
            if channel.name == name:
                return None

        return await ctx.guild.create_voice_channel(
            name,
            overwrites=overwrites,
            category=category,
        )

    return None
