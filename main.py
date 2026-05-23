import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import View, Button
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime
import os

# =========================
# CONFIG
# =========================

load_dotenv()

TOKEN = os.getenv("TOKEN")

RANKING_CHANNEL_ID = 1499492871500337366

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# DATABASE
# =========================

mensagens = defaultdict(int)

ranking_message = None

log_channel_id = None

admin_logs = []

# =========================
# EVENTOS
# =========================

@bot.event
async def on_ready():

    print(f"[NEXUS SECURITY] Online como {bot.user}")

    try:

        synced = await bot.tree.sync()

        print(f"{len(synced)} slash commands sincronizados.")

    except Exception as e:
        print(e)

    atualizar_ranking.start()


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    mensagens[message.author.id] += 1

    await bot.process_commands(message)


@bot.event
async def on_member_ban(guild, user):

    global log_channel_id

    admin_logs.append(
        f"{user} foi banido."
    )

    if log_channel_id:

        canal = bot.get_channel(log_channel_id)

        if canal:

            embed = discord.Embed(
                title="🔨 Banimento Detectado",
                description=f"{user} foi banido.",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )

            await canal.send(embed=embed)


@bot.event
async def on_guild_channel_update(before, after):

    global log_channel_id

    admin_logs.append(
        f"Canal alterado: {before.name}"
    )

    if log_channel_id:

        canal = bot.get_channel(log_channel_id)

        if canal:

            embed = discord.Embed(
                title="🛠️ Canal Atualizado",
                description=f"{before.name} foi modificado.",
                color=0x5865F2,
                timestamp=datetime.utcnow()
            )

            await canal.send(embed=embed)

# =========================
# RANKING
# =========================

@tasks.loop(minutes=1)
async def atualizar_ranking():

    global ranking_message

    canal = bot.get_channel(RANKING_CHANNEL_ID)

    if not canal:
        return

    ranking = sorted(
        mensagens.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    descricao = ""

    medalhas = [
        "🥇",
        "🥈",
        "🥉",
        "🔹",
        "🔹",
        "🔹",
        "🔹",
        "🔹",
        "🔹",
        "🔹"
    ]

    for i, (user_id, total) in enumerate(ranking):

        membro = canal.guild.get_member(user_id)

        if membro:

            descricao += (
                f"{medalhas[i]} "
                f"{membro.mention} — "
                f"**{total} mensagens**\n"
            )

    embed = discord.Embed(
        title="🏆 Ranking de Mensagens",
        description=(
            "Top 10 membros mais ativos 💬\n\n"
            "📊 Classificação\n\n"
            f"{descricao}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "⏱️ Atualiza automaticamente a cada 1 minuto"
        ),
        color=0x5865F2
    )

    embed.set_footer(
        text=f"Hoje às {datetime.now().strftime('%H:%M')}"
    )

    view = RankingView()

    if ranking_message:

        try:

            await ranking_message.edit(
                embed=embed,
                view=view
            )

        except:

            ranking_message = await canal.send(
                embed=embed,
                view=view
            )

    else:

        ranking_message = await canal.send(
            embed=embed,
            view=view
        )

# =========================
# BOTÃO RANKING
# =========================

class RankingView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Resetar Ranking",
        style=discord.ButtonStyle.danger,
        emoji="🗑️"
    )
    async def reset_button(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "Sem permissão.",
                ephemeral=True
            )

        mensagens.clear()

        await interaction.response.send_message(
            "Ranking resetado.",
            ephemeral=True
        )

# =========================
# METAS
# =========================

class MetaView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Ver Meta",
        style=discord.ButtonStyle.primary,
        emoji="📊"
    )
    async def ver_meta(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        total = mensagens.get(
            interaction.user.id,
            0
        )

        await interaction.response.send_message(
            f"Você possui {total} mensagens registradas.",
            ephemeral=True
        )


@bot.tree.command(
    name="metas",
    description="Painel de metas"
)
async def metas(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📌 Painel de Metas",
        description=(
            "📊 Ver Meta → veja suas mensagens.\n"
            "📄 Sistema de relatórios integrado."
        ),
        color=0x5865F2
    )

    await interaction.response.send_message(
        embed=embed,
        view=MetaView()
    )

# =========================
# AUDIT
# =========================

@bot.tree.command(
    name="audit",
    description="Resumo das ações administrativas"
)
async def audit(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🛡️ Audit Log",
        color=0x5865F2
    )

    if admin_logs:

        for log in admin_logs[-10:]:

            embed.add_field(
                name="Ação",
                value=log,
                inline=False
            )

    else:

        embed.description = (
            "Nenhuma ação registrada."
        )

    await interaction.response.send_message(
        embed=embed
    )

# =========================
# WHOIS
# =========================

@bot.tree.command(
    name="whois",
    description="Informações detalhadas"
)
@app_commands.describe(
    usuario="Usuário"
)
async def whois(
    interaction: discord.Interaction,
    usuario: discord.Member
):

    cargos = ", ".join(
        [role.name for role in usuario.roles[1:]]
    )

    embed = discord.Embed(
        title=f"🔍 Whois • {usuario}",
        color=0x5865F2
    )

    embed.add_field(
        name="📅 Conta criada",
        value=usuario.created_at.strftime(
            "%d/%m/%Y %H:%M"
        ),
        inline=False
    )

    embed.add_field(
        name="📥 Entrou no servidor",
        value=usuario.joined_at.strftime(
            "%d/%m/%Y %H:%M"
        ),
        inline=False
    )

    embed.add_field(
        name="🎭 Cargos",
        value=cargos if cargos else "Nenhum",
        inline=False
    )

    embed.set_thumbnail(
        url=usuario.display_avatar.url
    )

    await interaction.response.send_message(
        embed=embed
    )

# =========================
# LOG CHANNEL
# =========================

@bot.tree.command(
    name="log-channel",
    description="Define canal de logs"
)
@app_commands.describe(
    canal="Canal"
)
async def log_channel(
    interaction: discord.Interaction,
    canal: discord.TextChannel
):

    global log_channel_id

    log_channel_id = canal.id

    await interaction.response.send_message(
        f"Canal de logs definido para {canal.mention}."
    )

# =========================
# SCAN CONTENT
# =========================

@bot.tree.command(
    name="scan-content",
    description="Analisa conteúdo suspeito"
)
@app_commands.describe(
    conteudo="Mensagem ou link"
)
async def scan_content(
    interaction: discord.Interaction,
    conteudo: str
):

    palavras_suspeitas = [
        "grabify",
        "phishing",
        "token",
        "free nitro",
        "malware"
    ]

    resultado = (
        "✅ Nenhuma ameaça detectada."
    )

    for palavra in palavras_suspeitas:

        if palavra in conteudo.lower():

            resultado = (
                "🚨 Conteúdo suspeito detectado."
            )

            break

    embed = discord.Embed(
        title="🔍 Nexus Scanner",
        description=resultado,
        color=0x5865F2
    )

    await interaction.response.send_message(
        embed=embed
    )

# =========================
# QUARANTINE
# =========================

@bot.tree.command(
    name="quarantine",
    description="Coloca usuário em quarentena"
)
@app_commands.describe(
    usuario="Usuário"
)
async def quarantine(
    interaction: discord.Interaction,
    usuario: discord.Member
):

    role = discord.utils.get(
        interaction.guild.roles,
        name="Quarantine"
    )

    if not role:

        role = await interaction.guild.create_role(
            name="Quarantine"
        )

    await usuario.add_roles(role)

    embed = discord.Embed(
        title="🚨 Usuário em Quarentena",
        description=(
            f"Usuário: {usuario.mention}\n"
            "O membro foi isolado."
        ),
        color=0xff0000
    )

    await interaction.response.send_message(
        embed=embed
    )

# =========================
# ANALYZE PATTERN
# =========================

@bot.tree.command(
    name="analyze-pattern",
    description="Analisa padrão de mensagens"
)
@app_commands.describe(
    usuario="Usuário"
)
async def analyze_pattern(
    interaction: discord.Interaction,
    usuario: discord.Member
):

    total = mensagens.get(
        usuario.id,
        0
    )

    status = (
        "🟢 Comportamento normal"
    )

    if total > 500:

        status = (
            "🟡 Alto volume detectado"
        )

    if total > 1500:

        status = (
            "🔴 Comportamento suspeito"
        )

    embed = discord.Embed(
        title="🧠 Nexus Pattern Analyzer",
        description=(
            f"Usuário: {usuario.mention}\n"
            f"Mensagens registradas: {total}\n"
            f"Resultado: {status}"
        ),
        color=0x5865F2
    )

    await interaction.response.send_message(
        embed=embed
    )

# =========================
# CHECK REPUTATION
# =========================

@bot.tree.command(
    name="check-reputation",
    description="Verifica reputação"
)
@app_commands.describe(
    alvo="Usuário, IP ou link"
)
async def check_reputation(
    interaction: discord.Interaction,
    alvo: str
):

    embed = discord.Embed(
        title="🌐 Reputation Check",
        description=(
            f"Alvo analisado: {alvo}\n\n"
            "✅ Nenhum histórico suspeito encontrado."
        ),
        color=0x5865F2
    )

    embed.set_footer(
        text="APIs externas não configuradas"
    )

    await interaction.response.send_message(
        embed=embed
    )

# =========================
# START
# =========================

bot.run(TOKEN)
