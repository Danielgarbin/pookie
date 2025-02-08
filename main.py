import os
from keep_alive import keep_alive  # Importa la función keep_alive

# Definir intents
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

# Configura el bot con el prefijo '!' y los intents
bot = commands.Bot(command_prefix='!', intents=intents)


# Mantén el bot vivo llamando a la función keep_alive()
keep_alive()

# Variables del entorno
GUILD_ID = 1337387112403697694  # ID del servidor
ROLE_ID = 1337394657860128788  # ID del rol que se asignará
ADMIN_CHANNEL_ID = 1337678870316453898  # ID del canal donde recibirás los nombres

# Ejecuta el bot usando la variable de entorno para el token
bot.run(os.getenv('DISCORD_TOKEN'))


intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Diccionario para rastrear usuarios que aún no han respondido
awaiting_response = {}

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.event
async def on_member_join(member):
    try:
        await member.send("¡Bienvenido! Para asignarte un rol y registrarte, responde con tu usuario de Fortnite y especifica si es de Epic Games (PC), PlayStation o Xbox:")
        awaiting_response[member.id] = True  # Marcamos que este usuario debe responder
    except discord.Forbidden:
        print(f"No pude enviar un mensaje a {member.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild = bot.get_guild(GUILD_ID)
    member = guild.get_member(message.author.id)
    role = guild.get_role(ROLE_ID)
    admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)

    # Verifica si el usuario está en la lista de espera o no tiene rol
    if member.id in awaiting_response or role not in member.roles:
        await member.add_roles(role)
        await admin_channel.send(f"{member.mention} se ha registrado con el nombre: {message.content}")
        try:
            await member.send("Gracias, se te ha asignado un rol.")
        except discord.Forbidden:
            pass

        # Eliminamos al usuario de la lista de espera
        if member.id in awaiting_response:
            del awaiting_response[member.id]

    await bot.process_commands(message)

bot.run(TOKEN)
