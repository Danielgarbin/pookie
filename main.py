import os
import discord
from discord.ext import commands
from flask import Flask
import threading
import psycopg2
import psycopg2.extras
import asyncio
import datetime
import re

print("Iniciando el bot...")

# Leer variables de entorno
try:
    GUILD_ID = int(os.getenv('GUILD_ID', 0))
    ROLE_ID = int(os.getenv('ROLE_ID', 0))  # Este rol puede seguir usándose para otros fines
    ADMIN_CHANNEL_ID = int(os.getenv('ADMIN_CHANNEL_ID', 0))
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', '').strip()
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    # Es importante definir OWNER_ID y PUBLIC_CHANNEL_ID ya que se usan en los comandos de administración
    OWNER_ID = int(os.getenv('OWNER_ID', 0))
    PUBLIC_CHANNEL_ID = int(os.getenv('PUBLIC_CHANNEL_ID', 0))
except ValueError:
    print("Error: Alguna variable de entorno contiene un valor no válido.")
    exit(1)

if not DISCORD_TOKEN or DISCORD_TOKEN == "TOKEN_NO_VALIDO":
    print("Error: DISCORD_TOKEN no encontrado o es inválido. Verifica las variables de entorno en Render.")
    exit(1)

# Conexión a la base de datos y creación de la tabla de registros
db_conn = psycopg2.connect(DATABASE_URL)
db_conn.autocommit = True

def init_db():
    with db_conn.cursor() as cur:
        cur.execute("""
             CREATE TABLE IF NOT EXISTS registrations (
                user_id TEXT PRIMARY KEY,
                discord_name TEXT,
                fortnite_username TEXT,
                platform TEXT,
                country TEXT
             )
         """)
init_db()

# Configuración del bot
intents = discord.Intents.default()
intents.members = True          # Para manejar miembros
intents.messages = True         # Para recibir mensajes
intents.message_content = True  # Para leer el contenido de los mensajes

bot = commands.Bot(command_prefix='!', intents=intents)

# Servidor Flask para Uptimerobot
app = Flask(__name__)
@app.route("/")
def home():
    return "Bot is running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Diccionario para guardar el proceso de registro
registration_data = {}  # clave: user_id, valor: dict con claves: step, fortnite_username, platform, country

# ----------------------------
# EVENTOS Y PROCESOS DE REGISTRO
# ----------------------------

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
        await member.send("¡Bienvenido! Vamos a inscribirte en el torneo, escribe solamente tu nombre de usuario de Fortnite")
        registration_data[member.id] = {"step": "username"}
    except discord.errors.Forbidden:
        print(f"No se pudo enviar un DM a {member.name}")

@bot.event
async def on_message(message):
    # Procesar mensajes directos (DM) para el registro
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
        if message.author.id in registration_data:
            data = registration_data[message.author.id]
            if data["step"] == "username":
                # Guardar el nombre de usuario de Fortnite y pedir plataforma
                data["fortnite_username"] = message.content.strip()
                data["step"] = "platform"
                view = PlatformSelectionView(message.author)
                await message.author.send("Escoge la plataforma en la que juegas:", view=view)
                return
    await bot.process_commands(message)

# ----------------------------
# VIEWS PARA SELECCIÓN DE PLATAFORMA Y PAÍS
# ----------------------------

class PlatformSelectionView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user

    @discord.ui.button(label="PC", style=discord.ButtonStyle.primary)
    async def pc_button(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("No puedes interactuar con este mensaje.")
            return
        registration_data[self.user.id]["platform"] = "PC"
        registration_data[self.user.id]["step"] = "country"
        view = CountrySelectionView(self.user)
        await interaction.response.send_message("Escoge tu país:", view=view)

    @discord.ui.button(label="PlayStation", style=discord.ButtonStyle.primary)
    async def ps_button(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("No puedes interactuar con este mensaje.")
            return
        registration_data[self.user.id]["platform"] = "PlayStation"
        registration_data[self.user.id]["step"] = "country"
        view = CountrySelectionView(self.user)
        await interaction.response.send_message("Escoge tu país:", view=view)

    @discord.ui.button(label="Xbox", style=discord.ButtonStyle.primary)
    async def xbox_button(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("No puedes interactuar con este mensaje.")
            return
        registration_data[self.user.id]["platform"] = "Xbox"
        registration_data[self.user.id]["step"] = "country"
        view = CountrySelectionView(self.user)
        await interaction.response.send_message("Escoge tu país:", view=view)

    @discord.ui.button(label="Nintendo", style=discord.ButtonStyle.primary)
    async def nintendo_button(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("No puedes interactuar con este mensaje.")
            return
        registration_data[self.user.id]["platform"] = "Nintendo"
        registration_data[self.user.id]["step"] = "country"
        view = CountrySelectionView(self.user)
        await interaction.response.send_message("Escoge tu país:", view=view)

class CountrySelectionView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user
        countries = ["Argentina", "Bolivia", "Chile", "Colombia", "Costa Rica", "Cuba", "Ecuador", 
                     "El Salvador", "Guatemala", "Honduras", "Nicaragua", "Panamá", "Perú", 
                     "República Dominicana", "Uruguay", "Venezuela"]
        for country in countries:
            self.add_item(CountryButton(country, self.user))

class CountryButton(discord.ui.Button):
    def __init__(self, country, user):
        super().__init__(label=country, style=discord.ButtonStyle.secondary)
        self.country = country
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("No puedes interactuar con este mensaje.")
            return
        registration_data[self.user.id]["country"] = self.country
        # Guardar la información en la base de datos
        data = registration_data[self.user.id]
        with db_conn.cursor() as cur:
            cur.execute("""
                 INSERT INTO registrations (user_id, discord_name, fortnite_username, platform, country)
                 VALUES (%s, %s, %s, %s, %s)
                 ON CONFLICT (user_id) DO UPDATE SET
                     discord_name = EXCLUDED.discord_name,
                     fortnite_username = EXCLUDED.fortnite_username,
                     platform = EXCLUDED.platform,
                     country = EXCLUDED.country
            """, (str(self.user.id), self.user.name, data.get("fortnite_username", ""), data.get("platform", ""), self.country))
        registration_data.pop(self.user.id, None)
        # Asignar rol automáticamente si el usuario no es OWNER_ID
        if self.user.id != OWNER_ID:
            guild = bot.get_guild(GUILD_ID)
            if guild:
                member = guild.get_member(self.user.id)
                if member is None:
                    try:
                        member = await guild.fetch_member(self.user.id)
                    except Exception as e:
                        print(f"Error al obtener miembro {self.user.id}: {e}")
                if member:
                    role = guild.get_role(1337394657860128788)
                    if role and role not in member.roles:
                        try:
                            await member.add_roles(role)
                            await asyncio.sleep(1)
                        except Exception as e:
                            print(f"Error al asignar rol a {self.user.name}: {e}")
        await interaction.response.send_message("Gracias, acabas de inscribirte en el torneo. Para saber en qué fecha se realizará, visita el canal fechas-del-torneo en el servidor.")

# ----------------------------
# COMANDOS DE ADMINISTRACIÓN PARA REGISTROS (solo para OWNER_ID)
# ----------------------------
def is_owner_and_allowed(ctx):
    return ctx.author.id == OWNER_ID and (ctx.guild is None or ctx.channel.id == PUBLIC_CHANNEL_ID)

@bot.command()
async def lista_registros(ctx):
    if not is_owner_and_allowed(ctx):
        try:
            await ctx.message.delete()
        except:
            pass
        return
    with db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM registrations ORDER BY discord_name ASC")
        rows = cur.fetchall()
    if not rows:
        await ctx.send("No hay registros.")
        try:
            await ctx.message.delete()
        except:
            pass
        return
    lines = ["**Lista de Registros:**"]
    for row in rows:
        line = f"Discord: {row['discord_name']} (ID: {row['user_id']}) | Fortnite: {row['fortnite_username']} | Plataforma: {row['platform']} | País: {row['country']}"
        lines.append(line)
    full_message = "\n".join(lines)
    await ctx.send(full_message)
    try:
        await ctx.message.delete()
    except:
        pass

@bot.command()
async def agregar_registro_manual(ctx, *, data_str: str):
    if not is_owner_and_allowed(ctx):
        try:
            await ctx.message.delete()
        except:
            pass
        return
    # Formato: discord_user_id | discord_name | fortnite_username | platform | country
    parts = [part.strip() for part in data_str.split("|")]
    if len(parts) < 5:
        await ctx.send("❌ Formato incorrecto. Usa: discord_user_id | discord_name | fortnite_username | platform | country")
        return
    user_id, discord_name, fortnite_username, platform, country = parts
    with db_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO registrations (user_id, discord_name, fortnite_username, platform, country)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                discord_name = EXCLUDED.discord_name,
                fortnite_username = EXCLUDED.fortnite_username,
                platform = EXCLUDED.platform,
                country = EXCLUDED.country
        """, (user_id, discord_name, fortnite_username, platform, country))
    await ctx.send("✅ Registro manual agregado.")
    try:
        await ctx.message.delete()
    except:
        pass

# ----------------------------
# INICIO DEL SERVIDOR FLASK Y DEL BOT
# ----------------------------
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    try:
        print("Iniciando el bot en Discord...")
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"Error al iniciar el bot: {e}")
