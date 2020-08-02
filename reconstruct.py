import discord
import asyncio
import requests
import shutil
from PIL import Image
from webhook import send_webhook


async def clear_server(server):
    for c in server.channels:
        await c.delete()
    for role in server.roles:
        try:
            await role.delete()
        except discord.errors.Forbidden:
            pass #This should only happen when we get to the @everyone role
        except discord.errors.HTTPException:
            pass

async def reconstruct_server(server_json, client, message, *, messages=False):
    server = message.channel.guild
    roles = {}
    timeout = 20
    embed=discord.Embed()
    embed.add_field(name=':warning: Are you sure?', value='Re-creating {} here will completely erase the current state of this server'.format(server_json['name']), inline=False)
    embed.add_field(name='Type "I understand" to continue', value=f'(timout in {timeout}s)', inline=False)
    warning = await message.channel.send(embed=embed)

    def check(author):
        def inner_check(message):
            return message.author == author and message.content.lower() == "i understand"
        return inner_check
    try:
        msg = await client.wait_for('message', check=check(message.author), timeout=timeout)
    except asyncio.TimeoutError:
        await warning.delete()
        await message.channel.send(':timer: **Timeout! Server re-creation canceled**')
        return

    print('Reconstructing ' + server_json['name'])

    #Deletes all channels, categories and roles
    await clear_server(server)

    #A mess to konvert the server .webp icon to a .jpg
    #(since discord stores icons as .webp, but doesen't accept it as input :/)
    if server_json['icon_url'] != '':
        r = requests.get(server_json['icon_url'], stream=True)
        with open('files/icon.webp', 'w+b') as out_file:
            shutil.copyfileobj(r.raw, out_file)
        im = Image.open('files/icon.webp').convert('RGB')
        im.save('files/icon.jpg','jpeg')
        with open('files/icon.jpg', 'rb') as in_file:
            icon = in_file.read()
        await server.edit(icon=icon)


    '''Creates all the roles
    The dictionary "roles" links the id of the role on the last
    server, to the object of the role on the current one, since
    the roles id:s is stored with their old one in the .json'''
    for role_id, role in server_json['roles'].items():
        if role['name'] != '@everyone':
            perm = discord.Permissions()._from_value(role['permissions'])
            #Convert the hex string to a RGB tuple
            color = tuple(int(role['color'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            color = discord.Colour(0).from_rgb(color[0], color[1], color[2])

            role = await server.create_role(name=role['name'], color=color, permissions=perm)
            roles[role_id] = role
        else:
            #Can not create the @everyone, but need it as an object,
            #so we just call server.default_role
            roles[role_id] = server.default_role

    #Don't have to reformat anything
    #since it's already good in the file
    users = server_json['user_info']

    #Create all the channels and cetegories with the correct permissions
    for cn, channels in server_json['categories'].items():
        category = await server.create_category(cn)

        for channel in channels:
            #Create a PermissionOverwrite object for every channel
            overwrites = {}
            for role_id, perms in channel['overwrites'].items():
                role = roles[role_id]
                perm = {x: perms[x] for x in perms if x != 'type'}
                overwrites[role] = discord.PermissionOverwrite(**perm)

            #If it has a description it means it's a text channel, else a voice
            if 'description' in channel:
                channel_object = await server.create_text_channel(channel['name'], category=category,
                topic=channel['description'], overwrites=overwrites)

                #Recreate all the messages if requested
                #(very slow, took over 3 hours for ~5200 messages)
                if messages:
                    web = await channel_object.create_webhook(name='Archiver Webhook')
                    url = web.url
                    for msg in channel['messages']:
                        user = users[msg['author']]
                        if msg['content'] != '':
                            send_webhook(url, user['avatar_url'], user['name'], msg['content'], msg['attachments'])
            else:
                channel = await server.create_voice_channel(channel['name'], category=category, overwrites=overwrites)
        if category.name == 'no-category':
            await category.delete()
                
            print(' Reconstructed #' + channel['name'])