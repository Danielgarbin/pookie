import os
import discord
import requests
from discord.ext import commands, tasks
from keep_alive import keep_alive  # Para mantener el bot en línea

print("Iniciando el bot...")

intents = discord.Intents.default()
intents.members = True  # Necesitamos permisos para manejar miembros

bot = commands.Bot(command_prefix='!', intents=intents)

# Agregar registros para verificar las variables de entorno
GUILD_ID = int(os.getenv('GUILD_ID', '0'))
ROLE_ID = int(os.getenv('ROLE_ID', '0'))
ADMIN_CHANNEL_ID = int(os.getenv('ADMIN_CHANNEL_ID', '0'))
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', 'TOKEN_NO_VALIDO')

print(f"GUILD_ID: {GUILD_ID}")
print(f"ROLE_ID: {ROLE_ID}")
print(f"ADMIN_CHANNEL_ID: {ADMIN_CHANNEL_ID}")
print(f"DISCORD_TOKEN: {'TOKEN_PROPORCIONADO' if DISCORD_TOKEN != 'TOKEN_NO_VALIDO' else 'TOKEN_NO_VALIDO'}")

keep_alive_url = "https://pookie-k3sy.onrender.com"  # Reemplaza con la URL de tu bot

@tasks.loop(minutes=5)
async def keep_alive_task():
    try:
        requests.get(keep_alive_url)
        print("Solicitud keep-alive enviada")
    except Exception as e:
        print(f"Error en keep-alive: {e}")

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está listo y en línea.')
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f'Conectado al servidor: {guild.name}')
    else:
        print(f'No se pudo encontrar el servidor con ID: {GUILD_ID}')
    keep_alive_task.start()

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
        if guild:
            member = guild.get_member(message.author.id)
            role = guild.get_role(ROLE_ID)
            admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)
            if role and admin_channel:
                await admin_channel.send(f'{message.author.name} se ha unido y su nombre es {message.content}')
                await member.add_roles(role)
                await message.author.send("Gracias, acabas de inscribirte en el torneo. Para saber en qué fecha se realizará, visita el canal fases-del-torneo en el servidor.")
            else:
                print(f'No se pudo encontrar el rol o el canal con ID: {ROLE_ID} o {ADMIN_CHANNEL_ID}')
        else:
            print(f'No se pudo encontrar el servidor con ID: {GUILD_ID}')

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Error en mensaje: {args[0]}\n')
        else:
            raise

# Captura y maneja excepciones para asegurar que los errores se registren
try:
    keep_alive()
    print("Iniciando el bot en Discord...")
    bot.run(DISCORD_TOKEN)
    print("Bot en Discord iniciado")
except Exception as e:
    print(f"Error al iniciar el bot: {e}")
