import discord
from collections import defaultdict

async def archive_server(message):
    server = message.channel.guild
    channel = message.author

    #ChannelType(4) means that the server is a category, which we don't want
    channels = [c for c in server.channels if c.type != discord.ChannelType(4)]

    print('Archiving ' + server.name + '...')
    start_msg = f'**Archiving** ***{server.name}*** *[{{}} / {len(channels)}]*... :hourglass:'
    msg = await channel.send(start_msg.format(1))

    user_info = {}
    categories = defaultdict(list)
    for index, channel in enumerate(channels, 1):
        await msg.edit(content=start_msg.format(index))

        '''It creates issues when trying to
        recontruct individual users permissions,
        so we only save pmerissions for roles'''
        overwrites = {obj.id: perm._values for obj, perm in channel.overwrites.items() if obj.__class__.__name__ == 'Role'}

        channel_info = {
            'name': channel.name,
            'overwrites': overwrites
            }
        #ChannelType(0) is a text channel
        if channel.type == discord.ChannelType(0):
            messages, user_info_channel = await archive_channel(channel)
            user_info.update(user_info_channel)
            channel_info['description'] = channel.topic
            channel_info['messages'] = messages
        if channel.category is None:
            category = 'no-category'
        else:
            category = channel.category.name
        categories[category].append(channel_info)

        print(' Archived channel #' + channel.name)


    role_info = {}
    for role in server.roles:
        role_info[role.id] = {
            'name': role.name,
            'color': str(role.color),
            'permissions': role.permissions.value
        }
    await msg.edit(content=f'**Archived** ***{server.name}***  :closed_book:')
    return {
        'icon_url': str(server.icon_url),
        'name': server.name,
        'categories': dict(categories),
        'user_info': user_info,
        'roles': role_info}

async def archive_channel(channel):
    messages = []
    '''I'm saving all the user info here,
    when looping trough messages since if we
    were to only include the members on the server,
    it would cause problems if a user had sent a message
    and then left the server.'''
    user_info = {}
    messages_raw = await channel.history(limit=100000).flatten()
    for msg in messages_raw[::-1]:
        message = {
            'content' : msg.content,
            'author' : f'{msg.author.id}',
            'created_at' : str(msg.created_at),
            'created_at_timestamp' : msg.created_at.timestamp(),
            'edited' : msg.edited_at != None,
            'attachments' : [a.url for a in msg.attachments],
            }
        user_info[msg.author.id] = {
            'name': msg.author.name,
            'avatar_url': str(msg.author.avatar_url)
            }
            
        #Checks if the user is still a member of the server
        member = channel.guild.get_member(msg.author.id)
        if member is not None:
            user_info['roles'] = [role.id for role in member.roles]
        messages.append(message)
    return messages, user_info