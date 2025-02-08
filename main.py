import os
import discord
from discord.ext import commands
from keep_alive import keep_alive  # Para mantener el bot en línea

intents = discord.Intents.default()
intents.members = True  # Necesitamos permisos para manejar miembros

bot = commands.Bot(command_prefix='!', intents=intents)

GUILD_ID = 1337387112403697694 int(os.getenv('GUILD_ID'))
ROLE_ID = 1337394657860128788 int(os.getenv('ROLE_ID'))
ADMIN_CHANNEL_ID = 1337678870316453898 int(os.getenv('ADMIN_CHANNEL_ID'))

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está listo y en línea.')

@bot.event
async def on_member_join(member):
    try:
        await member.send("¡Bienvenido! Para participar, responde con tu usuario de Fortnite y especifica si es de Epic Games (PC), PlayStation o Xbox:")
    except discord.errors.Forbidden:
        print(f"No se pudo enviar un DM a {member.name}")

@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
        guild = bot.get_guild(GUILD_ID)
        member = guild.get_member(message.author.id)
        role = guild.get_role(ROLE_ID)
        admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)
        if guild and role and admin_channel:
            await admin_channel.send(f'{message.author.name} se ha unido y su nombre es {message.content}')
            await member.add_roles(role)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
