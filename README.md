# Discord Archiver


This is a discord bot that can turn whole servers into a .json file and back. Be sure to put your bots token in the "access_token" file before running.

**NOTE**: This bot requires admin priviliges to function. If the bot gets added without it, it will automatically leave the server.

# Features

  - Turn a whole discord server into a .json file for safe keeping
  - Reconstruct all the channels from a .json containing a server, as well as the messages using webhooks if specified

# Usage

- ```!archive``` - Turns a whole server into a .json (if the user calling it has permission to view all channels) and sends it to the user who called the command in a private message.

- ```!reconstruct``` - Reconstructs a servers channels, roles and permissions. The .json containing the server needs to be attachted to the message calling it. This operation can only be performed by server operators, as it overwrites the server it is called on. Use with caution.

- ```!reconstruct preserve_messages``` . The same as ```!reconstruct```, except it also reconstructs all the messages and users sending them using webhooks. This will take a very long time. From testing, a channel containing a mixture of messages and images, with ~5200 messages in it, took over 3 hours to reconstruct.
