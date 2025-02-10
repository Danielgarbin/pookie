import os
import discord
import requests
from discord.ext import commands, tasks
from flask import Flask
import threading

print("Iniciando el bot...")

# Leer variables de entorno de forma segura
try:
    GUILD_ID = int(os.getenv('GUILD_ID', 0))
    ROLE_ID = int(os.getenv('ROLE_ID', 0))
    ADMIN_CHANNEL_ID = int(os.getenv('ADMIN_CHANNEL_ID', 0))
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', '').strip()
except ValueError:
    print("Error: Alguna variable de entorno contiene un valor no válido.")
    exit(1)

# Verificar si el token es válido
if not DISCORD_TOKEN or DISCORD_TOKEN == "TOKEN_NO_VALIDO":
    print("Error: DISCORD_TOKEN no encontrado o es inválido. Verifica las variables de entorno en Render.")
    exit(1)

# Configuración del bot
intents = discord.Intents.default()
intents.members = True          # Permite manejar miembros
intents.messages = True         # Permite recibir mensajes
intents.message_content = True  # Necesario para leer el contenido de mensajes

bot = commands.Bot(command_prefix='!', intents=intents)

# --- SERVIDOR FLASK PARA UPTIMEROBOT ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# --- EVENTOS Y FUNCIONALIDAD DEL BOT ---
@bot.event
async def on_ready():
    print(f'Bot {bot.user} está listo y en línea.')
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f'Conectado al servidor: {guild.name}')
    else:
        print(f'No se pudo encontrar el servidor con ID: {GUILD_ID}')

@bot.event
async def on_member_join(member):
    try:
        await member.send("¡Bienvenido! Para participar, responde con tu usuario de Fortnite y especifica si es de Epic Games (PC), PlayStation o Xbox:")
    except discord.errors.Forbidden:
        print(f"No se pudo enviar un DM a {member.name}")

@bot.event
async def on_message(message):
    # Procesa mensajes directos (DM) de usuarios (ignora bots)
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            # Intenta obtener el miembro desde la caché; si no, lo intenta con fetch
            member = guild.get_member(message.author.id)
            if member is None:
                try:
                    member = await guild.fetch_member(message.author.id)
                except discord.NotFound:
                    print(f"Miembro {message.author.id} no encontrado en el servidor {GUILD_ID}.")
                    return

            role = guild.get_role(ROLE_ID)
            admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)

            if role and admin_channel:
                # Verificar si el usuario ya tiene el rol para evitar solicitudes repetitivas
                if role not in member.roles:
                    try:
                        await admin_channel.send(f'{message.author.name} se ha unido y su nombre es {message.content}')
                        await member.add_roles(role)
                        await message.author.send("Gracias, acabas de inscribirte en el torneo. Para saber en qué fecha se realizará, visita el canal fases-del-torneo en el servidor.")
                    except discord.DiscordException as e:
                        print(f"Error al asignar rol o enviar mensajes para {message.author.name}: {e}")
                else:
                    print(f"{message.author.name} ya tiene el rol y no se le enviará el mensaje nuevamente.")
            else:
                print(f'No se pudo encontrar el rol o el canal con ID: {ROLE_ID} o {ADMIN_CHANNEL_ID}')
        else:
            print(f'No se pudo encontrar el servidor con ID: {GUILD_ID}')

    # Si deseas que el bot procese comandos (además de esta lógica en DM), descomenta la siguiente línea:
    # await bot.process_commands(message)

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Error en mensaje: {args[0]}\n')
        else:
            raise

# --- INICIO DEL BOT Y DEL SERVIDOR FLASK ---
if __name__ == "__main__":
    # Inicia el servidor Flask en un hilo separado para que Uptimerobot pueda hacer ping
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    try:
        print("Iniciando el bot en Discord...")
        bot.run(DISCORD_TOKEN)
        print("Bot en Discord iniciado")
    except Exception as e:
        print(f"Error al iniciar el bot: {e}")
