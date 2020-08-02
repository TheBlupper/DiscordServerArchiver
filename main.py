import discord
import json
import requests
from archive import archive_server
from reconstruct import reconstruct_server

with open('access_token', 'r') as f:
    TOKEN = f.read()

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    for guild in client.guilds:
        await check_perms(guild)

async def check_perms(guild):
    if not guild.me.top_role.permissions.administrator:
        for channel in guild.channels:
            if channel and channel.permissions_for(guild.me).send_messages and channel.type == discord.ChannelType(0):
                await channel.send(':no_entry_sign: **I need to have administrator priviliges to funktion! Re-add me with the** `permissions` **tag in the url set to** `8`')
                break
        await guild.leave()

@client.event
async def on_guild_join(guild):
    await check_perms(guild)

@client.event
async def on_guild_role_update(before, after):
    if after.guild.me.top_role.id == after.id:
        await check_perms(after.guild)

@client.event
async def on_message(message):
    if message.author.bot:
        return
    member = message.channel.guild.get_member(message.author.id)
    admin = member.guild_permissions.administrator

    for channel in message.channel.guild.channels:
        if not channel.permissions_for(member).read_message_history:
            read_history = False
            break
    else:
        read_history = True

    if message.content.startswith('!archive'):
        if not read_history:
            await message.channel.send(':no_entry_sign: **You need to have permission to read all channels history to archive a server!**')
            return
        await message.channel.send(f'**Started archiving {message.channel.guild.name}! Check your PM\'s, {message.author.mention}**')
        result = await archive_server(message)
        file_name = f'{message.channel.guild}.json'
        with open(file_name, 'w', encoding='UTF-8') as f:
            f.write(json.dumps(result, ensure_ascii=False))
        await message.author.send(file=discord.File(file_name))

    elif message.content.startswith('!reconstruct'):
        if not admin:
            await message.channel.send(':no_entry_sign: **You need to be a administrator to reconstruct a server!**')
            return
        warning_attach = ':warning: **Attach a .json file to your message to begin a server re-creation.**'
        if len(message.attachments) != 1:
            await message.channel.send(warning_attach)
            return
        a = message.attachments[0]
        if a.filename.split('.')[-1] != 'json':
            await message.channel.send(warning_attach)
            return
        r = requests.get(str(a.url), stream=True)

        messages = 'preserve_messages' in message.content.split()
        await reconstruct_server(r.json(), client, message, messages=messages)

    elif message.content.startswith('!help'):
        embed=discord.Embed()
        embed.add_field(name='Information about Archiver :books:', value='A summary of archivers functions', inline=False)
        embed.add_field(name='!archive :closed_book:', value='Saves the whole server it is run on to a .json file and sends it in a private message to the user who called the command.', inline=False)
        embed.add_field(name='!reconstruct :construction_site:', value='In order to be run, the message calling this command needs to have a .json file containing a server attached to it. The server this command is run on will then be overwritten by the server in the .json file. \n\nIf "preserve_messages" is passed directly after the command, all messages from the last server will also be recreated with authentic webhooks (note that this process is very slow, and may will take several hours for big server)', inline=False)
        embed.add_field(name='!help :newspaper:', value='Shows this message', inline=False)
        await message.channel.send(embed=embed)

        
client.run(TOKEN)