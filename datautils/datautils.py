import random
import re

import discord
import matplotlib.colors as colors
import tabulate
from discord.ext import commands

from cogs.utils import chat_formatting as chat
from cogs.utils import checks


def rgb_to_hex(rgb_tuple):
    return colors.rgb2hex([1.0 * x / 255 for x in rgb_tuple])


def get_rgb_from_int(rgb_int):
    blue = rgb_int & 255
    green = (rgb_int >> 8) & 255
    red = (rgb_int >> 16) & 255
    return red, green, blue


class DataUtils:
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True, aliases=['memberinfo', 'membinfo',
                                                              'member', 'user'])
    async def uinfo(self, ctx, member: discord.Member = None):
        """Information on a user"""
        if member is None:
            member = ctx.message.author
        roles = [x.name for x in member.roles if x.name != "@everyone"]  # from Red-DiscordBot by TwentySix
        if roles:
            roles = sorted(roles, key=[x.name for x in ctx.message.server.role_hierarchy
                                       if x.name != "@everyone"].index)
            roles = "\n".join(roles)
        else:
            roles = "`None`"
        em = discord.Embed(title=member.nick, colour=member.colour)
        em.add_field(name="Name", value=member.name)
        em.add_field(name="Joined server", value=member.joined_at.strftime('%d.%m.%Y %H:%M:%S %Z'))
        em.add_field(name="ID", value=member.id)
        em.add_field(name="Has existed since", value=member.created_at.strftime('%d.%m.%Y %H:%M:%S %Z'))
        em.add_field(name="Color", value=member.colour)
        em.add_field(name="Bot?", value=str(member.bot).replace("True", "✔").replace("False", "❌"))
        em.add_field(name="Server perms", value="[" + str(
            member.server_permissions.value) + "](https://discordapi.com/permissions.html#" + str(
            member.server_permissions.value) + ")")
        em.add_field(name="Roles", value=roles, inline=False)
        em.set_image(url=member.avatar_url)
        em.set_thumbnail(url="https://xenforo.com/community/rgba.php?r=" + str(member.colour.r) + "&g=" + str(
            member.colour.g) + "&b=" + str(member.colour.b) + "&a=255")
        if ctx.message.channel.permissions_for(ctx.message.author).embed_links:
            await self.bot.say(embed=em)
        else:
            await self.bot.say("```\n" +
                               "Name: " + member.name +
                               "\nJoined server: " + member.joined_at.strftime('%d.%m.%Y %H:%M:%S %Z') +
                               "\nID: " + member.id +
                               "\nHas existed since: " + member.created_at.strftime('%d.%m.%Y %H:%M:%S %Z') +
                               "\nColor: " + str(member.color) +
                               "\nBot?: " + str(member.bot).replace("True", "✔").replace("False", "❌") +
                               "\nServer perms: " + str(member.server_permissions.value) +
                               "\nRoles: " + roles +
                               "```\n" +
                               member.avatar_url)

    @commands.command(pass_context=True, no_pm=True, aliases=['server', 'servinfo', 'serv', 'sv'])
    @checks.is_owner()
    async def sinfo(self, ctx, server: str = None):
        """Shows server information"""
        if server is None:
            server = ctx.message.server
        else:
            server = self.bot.get_server(server)
        if server is None:
            await self.bot.say("Failed to get server with provided ID")
            return
        afk = server.afk_timeout / 60
        vip_regs = str("VIP_REGIONS" in server.features).replace("True", "✔").replace("False", "❌")
        van_url = str("VANITY_URL" in server.features).replace("True", "✔").replace("False", "❌")
        inv_splash = "INVITE_SPLASH" in server.features
        em = discord.Embed(title="Server info", colour=server.owner.colour)
        em.add_field(name="Name", value=server.name)
        em.add_field(name="Server ID", value=server.id)
        em.add_field(name="Region", value=server.region)
        em.add_field(name="Existed since", value=server.created_at.strftime('%d.%m.%Y %H:%M:%S %Z'))
        em.add_field(name="Owner", value=server.owner)
        em.add_field(name="AFK Timeout and Channel", value=str(afk) + " min in " + str(server.afk_channel))
        em.add_field(name="Verification level",
                     value=str(server.verification_level)
                     .replace("none", "None")
                     .replace("low", "Low")
                     .replace("medium", "Medium")
                     .replace("high", "(╯°□°）╯︵ ┻━┻"))
        em.add_field(name="2FA admins", value=str(server.mfa_level).replace("0", "❌").replace("1", "✔"))
        em.add_field(name="Member Count", value=server.member_count)
        em.add_field(name="Role Count", value=str(len(server.roles)))
        em.add_field(name="Channel Count", value=str(len(server.channels)))
        em.add_field(name="VIP Voice Regions", value=vip_regs)
        em.add_field(name="Vanity URL", value=van_url)
        if not inv_splash:
            em.add_field(name="Invite Splash", value="❌")
        elif server.splash_url == "":
            em.add_field(name="Invite Splash", value="✔")
        else:
            em.add_field(name="Invite Splash", value="✔ [🔗](" + server.splash_url + ")")
        em.set_image(url=server.icon_url)
        if ctx.message.channel.permissions_for(ctx.message.author).embed_links:
            await self.bot.say(embed=em)
        else:
            await self.bot.say("```\n" +
                               "Name: " + server.name +
                               "\nServer ID: " + server.id +
                               "\nRegion: " + str(server.region) +
                               "\nExisted since: " + server.created_at.strftime('%d.%m.%Y %H:%M:%S %Z') +
                               "\nOwner: " + str(server.owner) +
                               "\nAFK timeout and Channel: " + str(afk) + " min in " + str(server.afk_channel) +
                               "\nVerification level: " +
                               str(server.verification_level).replace("none", "None").replace("low", "Low")
                               .replace("medium", "Medium").replace("high", "(╯°□°）╯︵ ┻━┻") +
                               "\n2FA admins: " + str(server.mfa_level).replace("0", "❌").replace("1", "✔") +
                               "\nMember Count: " + str(server.member_count) +
                               "\nRole Count: " + str(len(server.roles)) +
                               "\nChannel Count: " + str(len(server.channels)) +
                               "\nVIP Voice Regions: " + vip_regs +
                               "\nVanity URL: " + van_url +
                               "\nInvite Splash: " + str(inv_splash).replace("True", "✔").replace("False", "❌") +
                               "\nInvite Splash URL: " + server.splash_url +
                               "```\n" +
                               server.icon_url)

    @commands.command(pass_context=True, no_pm=True, aliases=['channel', 'chaninfo', 'chan', 'channelinfo'])
    async def cinfo(self, ctx, *, channel: discord.Channel):
        """Get info about channel"""
        changed_roles = sorted(channel.changed_roles,
                               key=lambda chan: chan.position,
                               reverse=True)
        em = discord.Embed(title=channel.name, description=channel.topic, colour=random.randint(0, 16777215))
        em.add_field(name="ID", value=channel.id)
        em.add_field(name="Type", value=str(channel.type).replace("voice", "🔈").replace("text", "📰"))
        em.add_field(name="Has existed since", value=channel.created_at.strftime('%d.%m.%Y %H:%M:%S %Z'))
        em.add_field(name="Position", value=channel.position)
        em.add_field(name="Changed roles permissions",
                     value="\n".join([str(x) for x in changed_roles])
                           or "`Not set`")
        em.add_field(name="Mention", value=channel.mention + "\n`" + channel.mention + "`")
        if ctx.message.channel.permissions_for(ctx.message.author).embed_links:
            await self.bot.say(embed=em)
        else:
            await self.bot.say("```\n" +
                               "Name: " + channel.name +
                               "\nTopic: " + channel.topic +
                               "\nID: " + channel.id +
                               "\nType: " + channel.type.name +
                               "\nHas existed since: " + channel.created_at.strftime('%d.%m.%Y %H:%M:%S %Z') +
                               "\nPosition: " + str(channel.position) +
                               "\nChanged roles permissions: " + "\n".join([str(x) for x in changed_roles]) +
                               "\nMention: " + str(channel.mention) +
                               "```")

    @commands.command(pass_context=True, no_pm=True, aliases=['channellist', 'listchannels'])
    async def channels(self, ctx, server: str = None):
        """Get all channels on server"""
        if server is None:
            server = ctx.message.server
        else:
            server = discord.utils.get(self.bot.servers, id=server)
        if server is None:
            await self.bot.say("Failed to get server with provided ID")
            return
        channels = []
        acc, cc, vcc, tcc = 0, 0, 0, 0
        # ↑ ACC = All channels count
        # CC = Category Count
        # VCC = Voice Chat Count
        # TCC = Text Chat Count
        acc = len(server.channels)
        for elem in server.channels:
            channels.append(elem)
        channels = sorted(channels, key=lambda chan: chan.position)
        channels_str = []
        for elem in server.channels:
            if elem.type == discord.ChannelType.category:
                channels_str.append(chat.bold(chat.escape(elem.name)))
                cc += 1
            elif elem.type == discord.ChannelType.text:
                channels_str.append(chat.escape(elem.mention))
                vcc += 1
            elif elem.type == discord.ChannelType.voice:
                channels_str.append(chat.escape(elem.name))
                tcc += 1
        em = discord.Embed(title="Channels list", colour=random.randint(0, 16777215))
        em.add_field(name="Channels:",
                     value="\n".join([x for x in channels]) or "No channels",
                     inline=False)
        em.set_footer(text="Total count of channels: {} | "
                           "Categories: {} | "
                           "Text Channels: {} | "
                           "Voice Channels: {}".format(acc, cc, tcc, vcc))
        if ctx.message.channel.permissions_for(ctx.message.author).embed_links:
            await self.bot.say(embed=em)
        else:
            await self.bot.say("\n".join([x for x in channels]) +
                               chat.box("""🔢 Total count: {}
📂 Categories: {}
📄 Text Channels: {}
🔊 Voice Channels: {}""".format(acc, cc, tcc, vcc)))

    @commands.command(pass_context=True, no_pm=True, aliases=['role', 'roleinfo'])
    async def rinfo(self, ctx, *, role: discord.Role):
        """Get info about role"""
        em = discord.Embed(title=role.name, colour=role.colour)
        em.add_field(name="ID", value=role.id)
        em.add_field(name="Perms",
                     value="[" + str(role.permissions.value) + "](https://discordapi.com/permissions.html#" + str(
                         role.permissions.value) + ")")
        em.add_field(name="Has existed since", value=role.created_at.strftime('%d.%m.%Y %H:%M:%S %Z'))
        em.add_field(name="Hoist", value=str(role.hoist)
                     .replace("True", "✔")
                     .replace("False", "❌"))
        em.add_field(name="Position", value=role.position)
        em.add_field(name="Color", value=role.colour)
        em.add_field(name="Managed", value=str(role.managed).replace("True", "✔").replace("False", "❌"))
        em.add_field(name="Mentionable", value=str(role.mentionable).replace("True", "✔").replace("False", "❌"))
        em.add_field(name="Mention", value=role.mention + "\n`" + role.mention + "`")
        em.set_thumbnail(url="https://xenforo.com/community/rgba.php?r=" + str(role.colour.r) + "&g=" + str(
            role.colour.g) + "&b=" + str(role.colour.b) + "&a=255")
        if ctx.message.channel.permissions_for(ctx.message.author).embed_links:
            await self.bot.say(embed=em)
        else:
            await self.bot.say("```\n" +
                               "ID: " + role.id +
                               "\nPerms: " + str(role.permissions.value) +
                               "\nHas existed since: " + role.created_at.strftime('%d.%m.%Y %H:%M:%S %Z') +
                               "\nHoist: " + str(role.hoist).replace("True", "✔").replace("False", "❌") +
                               "\nPosition: " + str(role.position) +
                               "\nColor: " + str(rgb_to_hex(get_rgb_from_int(role.colour.value))) +
                               "\nManaged: " + str(role.managed).replace("True", "✔").replace("False", "❌") +
                               "\nMentionable: " + str(role.mentionable).replace("True", "✔").replace("False", "❌") +
                               "\nMention: " + str(role.mention) +
                               "```")

    @commands.command(pass_context=True, no_pm=True, aliases=['listroles', 'rolelist'])
    async def roles(self, ctx, server: str = None):
        """Get all roles on server"""
        if server is None:
            server = ctx.message.server
        else:
            server = discord.utils.get(self.bot.servers, id=server)
        if server is None:
            await self.bot.say("Failed to get server with provided ID")
            return
        roles = []
        for role in server.role_hierarchy:
            dic = {
                "Name": role.name,
                "ID": role.id
            }
            roles.append(dic)
        embeds = []
        randcolor = random.randint(0, 16777215)
        for page in chat.pagify(tabulate.tabulate(roles, tablefmt="orgtbl"), page_length=1900):
            em = discord.Embed(  # description="\n".join([str(x) for x in roles]),
                description=chat.box(page),
                colour=randcolor)
            embeds.append(em)
        embeds[0].title = "Table of roles"
        embeds[-1].set_footer(text="Total count of roles: " + str(len(server.roles)))
        if ctx.message.channel.permissions_for(ctx.message.author).embed_links:
            for em in embeds:
                await self.bot.say(embed=em)
        else:
            for page in chat.pagify(tabulate.tabulate(roles, tablefmt="orgtbl")):
                await self.bot.say("**List of roles:**\n{}".format(chat.box(page)))

    @commands.command(pass_context=True, no_pm=True, aliases=["cperms", "permissions"])
    async def chan_perms(self, ctx, member: discord.Member, channel: discord.Channel = None):
        """Check user's permission for current or provided channel"""
        # From Dusty-Cogs for Red-DiscordBot: https://github.com/Lunar-Dust/Dusty-Cogs
        perms_names = {
            "add_reactions": "Add Reactions",
            "attach_files": "Attach Files",
            "change_nickname": "Change Nickname",
            "create_instant_invite": "Create Instant Invite",
            "embed_links": "Embed Links",
            "external_emojis": "Use External Emojis",
            "read_message_history": "Read Message History",
            "read_messages": "Read Messages",
            "send_messages": "Send Messages",
            "administrator": "Administrator",
            "ban_members": "Ban Members",
            "connect": "Connect",
            "deafen_members": "Deafen Members",
            "kick_members": "Kick Members",
            "manage_channels": "Manage Channels",
            "manage_emojis": "Manage Emojis",
            "manage_messages": "Manage Messages",
            "manage_nicknames": "Manage Nicknames",
            "manage_roles": "Manage Roles",
            "manage_server": "Manage Server",
            "manage_webhooks": "Manage Webhooks",
            "mention_everyone": "Mention Everyone",
            "move_members": "Move Members",
            "mute_members": "Mute Mebmers",
            "send_tts_messages": "Send TTS Messages",
            "speak": "Speak",
            "use_voice_activation": "Use Voice Activity",
            "view_audit_logs": "View Audit Log"
        }
        if channel is None:
            channel = ctx.message.channel
        perms = iter(channel.permissions_for(member))
        has_perms = " ```diff\n"
        no_perms = ""
        for x in perms:
            if "True" in str(x):
                pattern = re.compile('|'.join(perms_names.keys()))
                result = pattern.sub(lambda y: perms_names[y.group()], "+\t{0}\n".format(str(x).split('\'')[1]))
                has_perms += result
            else:
                pattern = re.compile('|'.join(perms_names.keys()))
                result = pattern.sub(lambda y: perms_names[y.group()], ("-\t{0}\n".format(str(x).split('\'')[1])))
                no_perms += result
        await self.bot.say(chat.inline(str(member.server_permissions.value)) + "{0}{1}```".format(has_perms, no_perms))


def setup(bot):
    bot.add_cog(DataUtils(bot))
