import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

GUILD_ID = int(os.getenv('GUILD_ID', 0))
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', 'TOKEN_NO_VALIDO')

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está listo y en línea.')
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f'Conectado al servidor: {guild.name}')
    else:
        print(f'No se pudo encontrar el servidor con ID: {GUILD_ID}')

try:
    print("Iniciando el bot en Discord...")
    bot.run(DISCORD_TOKEN)
    print("Bot en Discord iniciado")
except Exception as e:
    print(f"Error al iniciar el bot: {e}")
