import json
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

print("🚀 Starting PlatineThemAll Bot...")
print("📁 Loading teams data...")

AUTHORIZED_ROLE_ID = None

# Creation of Teams


class Teams:
    def __init__(self, nom, points):
        self.nom = nom
        self.points = points

    def add_points(self, nombre):
        self.points += nombre


teams = {}

# Fichier JSON

DATA_FILE = "teams.json"


def load_teams():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        for nom, info in data.items():
            teams[nom] = Teams(nom, info["points"])
    else:
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)


def save_teams():
    data = {nom: {"points": team.points} for nom, team in teams.items()}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


load_teams()
print("✅ Teams data loaded successfully")

# Setup du Bot
print("🔧 Setting up bot with intents...")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
print("✅ Bot instance created")

# Commandes et événements


@bot.event
async def on_ready():
    print("🎯 on_ready event triggered!")
    print(f"🤖 Bot connecté en tant que {bot.user}")
    print(f"🆔 Bot ID: {bot.user.id}")
    print(f"🌐 Connected to {len(bot.guilds)} guild(s)")

    try:
        print("🔄 Syncing slash commands...")
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} commandes slash synchronisées avec succès!")
        print("🎉 BOT HAS STARTED SUCCESSFULLY AND IS READY!")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")
        print("⚠️  Bot started but with command sync errors")


@bot.event
async def on_message(message: discord.message):
    if message.content.lower() == "$help":
        channel = message.channel
        await channel.send(
            "Ta besoin d'aide ? Voici les **commandes** dispo ! :\n"
            "- **/set-role** : Mettre à jour le role Modo d'event\n"
            "- **/new-team** : Ajouter une nouvelle équipe à l'event\n"
            "- **/remove-team** : Enlever une nouvelle équipe à l'event\n"
            "- **/add-points** : Ajouter des points à une équipe\n"
            "- **/remove-points** : Enlever des points à une équipe\n"
            "- **/classement** : Afficher le classement des meilleurs équipes\n"
        )


@bot.tree.command(name="set-role", description="Changer le rôle Modo d'event")
@app_commands.checks.has_permissions(administrator=True)
async def setrole(interaction: discord.Interaction, role: discord.Role):
    global AUTHORIZED_ROLE_ID
    AUTHORIZED_ROLE_ID = role.id
    await interaction.response.send_message(
        f"le role a bien étais modifer et est maintentant {role.name}", ephemeral=True
    )


def has_authorized_role(interaction: discord.Interaction) -> bool:
    if AUTHORIZED_ROLE_ID is None:
        return False
    return any(role.id == AUTHORIZED_ROLE_ID for role in interaction.user.roles)


@setrole.error
async def setrole_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "Tu n'as pas le droit d'effectuer cette commande !", ephemeral=True
        )


@bot.tree.command(name="new-team", description="Ajouter une nouvelle équipe a l'event")
async def newteam(
    interaction: discord.Interaction,
    nom: str,
):
    if not has_authorized_role(interaction):
        await interaction.response.send_message(
            "Tu n'as pas le droit d'effectuer cette commande !", ephemeral=True
        )
        return
    points = 0
    if nom in teams:
        await interaction.response.send_message("Nom déjà utiliser !!!", ephemeral=True)
        return
    teams[nom] = Teams(nom, points)
    save_teams()
    await interaction.response.send_message(f"L'équipe {nom} à été crée !")


@bot.tree.command(name="remove-team", description="Enlever une équipe a l'event")
async def remove_team(
    interaction: discord.Interaction,
    nom: str,
):
    if not has_authorized_role(interaction):
        await interaction.response.send_message(
            "Tu n'as pas le droit d'effectuer cette commande !", ephemeral=True
        )
        return
    if nom not in teams:
        await interaction.response.send_message("Nom déjà utiliser !!!", ephemeral=True)
        return
    del teams[nom]
    save_teams()
    await interaction.response.send_message(f"L'équipe {nom} à été supprimée !")


@bot.tree.command(name="add-points", description="Ajouter des points à une équipe !")
async def addpoints(
    interaction: discord.Interaction,
    nom_team: str,
    nom_jeu: str,
    difficulté: int,
    bronze: int,
    silver: int,
    gold: int,
    plat: int,
    temps: int,
):
    if not has_authorized_role(interaction):
        await interaction.response.send_message(
            "Tu n'as pas le droit d'effectuer cette commande !", ephemeral=True
        )
        return
    if nom_team not in teams:
        await interaction.response.send_message("L'équipe n'existe pas", ephemeral=True)
        return
    if temps < 5:
        coef_temps = 0.5
    elif temps < 15:
        coef_temps = 0.8
    elif temps < 25:
        coef_temps = 1.0
    elif temps < 35:
        coef_temps = 1.2
    elif temps < 45:
        coef_temps = 1.5
    else:
        coef_temps = 2.0
    coef_difficulter = difficulté / 5
    points = (
        ((bronze * 10) + (silver * 20) + (gold * 50) + (plat * 500)) * coef_difficulter
    ) * coef_temps
    teams[nom_team].add_points(points)
    save_teams()
    await interaction.response.send_message(
        f"L'équipe {nom_team} à ajouter {points} à son score avec le jeu {nom_jeu} !"
    )


@bot.tree.command(
    name="remove-points", description="Enlever un nombre de point definie"
)
async def team_classement(
    interaction: discord.Interaction, nom_team: str, nombre_points: int
):
    if not has_authorized_role(interaction):
        await interaction.response.send_message(
            "Tu n'as pas le droit d'effectuer cette commande !", ephemeral=True
        )
        return
    if nom_team not in teams:
        await interaction.response.send_message("L'équipe n'existe pas", ephemeral=True)
        return
    points = nombre_points - (nombre_points * 2)
    teams[nom_team].add_points(points)
    save_teams()
    await interaction.response.send_message(
        f"Vous avez enlevez {points} à l'équipe {nom_team}"
    )


@bot.tree.command(
    name="classement", description="Afficher le classement des meilleurs équipes"
)
async def team_classement(interaction: discord.Interaction):
    if not teams:
        await interaction.response.send_message("Il n'y a pas d'équipe actuellement")
        return
    classement = sorted(teams.values(), key=lambda team: team.points, reverse=True)

    # Discord limite les embeds à 25 champs par message.
    max_fields = 25

    for i in range(0, len(classement), max_fields):
        chunk = classement[i : i + max_fields]
        title = (
            "🏆 --- Classement des équipes --- 🏆"
            if i == 0
            else "🏆 --- Suite du classement --- 🏆"
        )
        embed = discord.Embed(title=title, color=discord.Color.blue())
        for index, team in enumerate(chunk, start=i + 1):
            embed.add_field(
                name=f"{index}. {team.nom}",
                value=f"{team.points} points",
                inline=False,
            )

        if i == 0:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.followup.send(embed=embed)


# Démarrage du Bot
print("🔑 Getting Discord token...")
token = os.getenv("DISCORD_TOKEN")
if token:
    print("✅ Discord token found")
    print("🚀 Starting bot connection to Discord...")
    bot.run(token)
else:
    print("❌ No Discord token found! Check DISCORD_TOKEN environment variable.")
