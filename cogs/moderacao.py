import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timezone

INFRACTIONS_FILE = "infractions.json"


def load_infractions():
    if not os.path.exists(INFRACTIONS_FILE):
        return {}
    with open(INFRACTIONS_FILE, "r") as f:
        return json.load(f)


def save_infractions(data):
    with open(INFRACTIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_infraction(guild_id: int, user_id: int, tipo: str, motivo: str, mod: str):
    data = load_infractions()
    key = f"{guild_id}"
    if key not in data:
        data[key] = {}
    uid = str(user_id)
    if uid not in data[key]:
        data[key][uid] = []
    data[key][uid].append({
        "tipo": tipo,
        "motivo": motivo,
        "mod": mod,
        "data": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"),
    })
    save_infractions(data)


async def log_action(interaction: discord.Interaction, acao: str, alvo: discord.Member, motivo: str, cor: discord.Color):
    data = load_infractions()
    config = data.get("config", {}).get(str(interaction.guild_id), {})
    log_channel_id = config.get("log_channel")
    if not log_channel_id:
        return
    channel = interaction.guild.get_channel(int(log_channel_id))
    if not channel:
        return
    embed = discord.Embed(
        title=f"🔨 {acao}",
        color=cor,
        timestamp=datetime.now(timezone.utc),
    )
    embed.add_field(name="Membro", value=f"{alvo.mention} (`{alvo.id}`)", inline=True)
    embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
    embed.add_field(name="Motivo", value=motivo, inline=False)
    embed.set_footer(text="Nexus Ascension Moderation")
    await channel.send(embed=embed)


def is_mod():
    async def predicate(interaction: discord.Interaction):
        data = load_infractions()
        config = data.get("config", {}).get(str(interaction.guild_id), {})
        mod_role_id = config.get("mod_role")
        if interaction.user.guild_permissions.administrator:
            return True
        if mod_role_id:
            role = interaction.guild.get_role(int(mod_role_id))
            if role and role in interaction.user.roles:
                return True
        await interaction.response.send_message("❌ Você não tem permissão para usar este comando.", ephemeral=True)
        return False
    return app_commands.check(predicate)


class Moderacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Bane um membro permanentemente do servidor")
    @app_commands.describe(membro="Membro a ser banido", motivo="Motivo do ban")
    @is_mod()
    async def ban(self, interaction: discord.Interaction, membro: discord.Member, motivo: str = "Sem motivo informado"):
        if membro.top_role >= interaction.user.top_role and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Você não pode banir alguém com cargo igual ou superior ao seu.", ephemeral=True)
        await membro.ban(reason=f"{motivo} | Mod: {interaction.user}")
        add_infraction(interaction.guild_id, membro.id, "BAN", motivo, str(interaction.user))
        await interaction.response.send_message(f"🔨 **{membro}** foi banido.\n📝 Motivo: {motivo}")
        await log_action(interaction, "Ban", membro, motivo, discord.Color.red())

    @app_commands.command(name="warn", description="Emite um aviso formal ao membro")
    @app_commands.describe(membro="Membro a ser avisado", motivo="Motivo do aviso")
    @is_mod()
    async def warn(self, interaction: discord.Interaction, membro: discord.Member, motivo: str = "Sem motivo informado"):
        add_infraction(interaction.guild_id, membro.id, "WARN", motivo, str(interaction.user))
        data = load_infractions()
        total = len(data.get(str(interaction.guild_id), {}).get(str(membro.id), []))
        await interaction.response.send_message(f"⚠️ **{membro}** recebeu um aviso.\n📝 Motivo: {motivo}\n🗂️ Total de infrações: **{total}**")
        await log_action(interaction, "Warn", membro, motivo, discord.Color.yellow())
        try:
            await membro.send(f"⚠️ Você recebeu um aviso no servidor **{interaction.guild.name}**.\n📝 Motivo: {motivo}")
        except discord.Forbidden:
            pass

    @app_commands.command(name="mute", description="Silencia um membro por tempo determinado")
    @app_commands.describe(membro="Membro a ser silenciado", minutos="Duração em minutos", motivo="Motivo do mute")
    @is_mod()
    async def mute(self, interaction: discord.Interaction, membro: discord.Member, minutos: int = 10, motivo: str = "Sem motivo informado"):
        from datetime import timedelta
        if minutos < 1 or minutos > 40320:
            return await interaction.response.send_message("❌ Duração deve ser entre 1 minuto e 28 dias.", ephemeral=True)
        duracao = timedelta(minutes=minutos)
        await membro.timeout(duracao, reason=f"{motivo} | Mod: {interaction.user}")
        add_infraction(interaction.guild_id, membro.id, "MUTE", f"{motivo} ({minutos}min)", str(interaction.user))
        await interaction.response.send_message(f"🔇 **{membro}** foi silenciado por **{minutos} minuto(s)**.\n📝 Motivo: {motivo}")
        await log_action(interaction, f"Mute ({minutos}min)", membro, motivo, discord.Color.orange())

    @app_commands.command(name="purge", description="Deleta mensagens em massa de um canal")
    @app_commands.describe(quantidade="Número de mensagens a deletar (máx. 100)")
    @is_mod()
    async def purge(self, interaction: discord.Interaction, quantidade: int = 10):
        if quantidade < 1 or quantidade > 100:
            return await interaction.response.send_message("❌ A quantidade deve ser entre 1 e 100.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        deletadas = await interaction.channel.purge(limit=quantidade)
        await interaction.followup.send(f"🗑️ **{len(deletadas)}** mensagens deletadas.", ephemeral=True)

    @app_commands.command(name="infrações", description="Lista as infrações de um membro")
    @app_commands.describe(membro="Membro a consultar")
    @is_mod()
    async def infracoes(self, interaction: discord.Interaction, membro: discord.Member):
        data = load_infractions()
        registros = data.get(str(interaction.guild_id), {}).get(str(membro.id), [])
        if not registros:
            return await interaction.response.send_message(f"✅ **{membro}** não possui infrações registradas.", ephemeral=True)
        embed = discord.Embed(title=f"📋 Infrações de {membro}", color=discord.Color.orange())
        for i, r in enumerate(registros[-10:], 1):
            embed.add_field(
                name=f"#{i} — {r['tipo']}",
                value=f"📝 {r['motivo']}\n👮 {r['mod']} · 🗓️ {r['data']}",
                inline=False,
            )
        embed.set_footer(text=f"Total: {len(registros)} infração(ões)")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="modlog", description="Exibe o log das últimas ações de moderação")
    @is_mod()
    async def modlog(self, interaction: discord.Interaction):
        data = load_infractions()
        guild_data = data.get(str(interaction.guild_id), {})
        todas = []
        for uid, registros in guild_data.items():
            for r in registros:
                todas.append((uid, r))
        todas = sorted(todas, key=lambda x: x[1]["data"], reverse=True)[:15]
        if not todas:
            return await interaction.response.send_message("📭 Nenhuma ação registrada ainda.", ephemeral=True)
        embed = discord.Embed(title="📔 Modlog — Nexus Ascension", color=discord.Color.blurple())
        for uid, r in todas:
            membro = interaction.guild.get_member(int(uid))
            nome = str(membro) if membro else f"ID {uid}"
            embed.add_field(
                name=f"{r['tipo']} → {nome}",
                value=f"📝 {r['motivo']}\n👮 {r['mod']} · 🗓️ {r['data']}",
                inline=False,
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="userinfo", description="Exibe informações detalhadas de um membro")
    @app_commands.describe(membro="Membro a consultar")
    @is_mod()
    async def userinfo(self, interaction: discord.Interaction, membro: discord.Member = None):
        membro = membro or interaction.user
        data = load_infractions()
        infracoes = len(data.get(str(interaction.guild_id), {}).get(str(membro.id), []))
        cargos = [r.mention for r in reversed(membro.roles) if r.name != "@everyone"]
        embed = discord.Embed(title=f"👤 {membro}", color=membro.color)
        embed.set_thumbnail(url=membro.display_avatar.url)
        embed.add_field(name="ID", value=membro.id, inline=True)
        embed.add_field(name="Apelido", value=membro.nick or "—", inline=True)
        embed.add_field(name="Conta criada em", value=membro.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Entrou no servidor", value=membro.joined_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Infrações", value=str(infracoes), inline=True)
        embed.add_field(name="Bot", value="Sim" if membro.bot else "Não", inline=True)
        embed.add_field(name=f"Cargos ({len(cargos)})", value=" ".join(cargos[:10]) or "—", inline=False)
        embed.set_footer(text="Nexus Ascension Moderation")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="antiraid", description="Ativa ou desativa proteção contra raids")
    @app_commands.describe(ativo="Ativar ou desativar o antiraid")
    @is_mod()
    async def antiraid(self, interaction: discord.Interaction, ativo: bool):
        data = load_infractions()
        if "config" not in data:
            data["config"] = {}
        gid = str(interaction.guild_id)
        if gid not in data["config"]:
            data["config"][gid] = {}
        data["config"][gid]["antiraid"] = ativo
        save_infractions(data)
        status = "✅ ativado" if ativo else "❌ desativado"
        await interaction.response.send_message(f"🛡️ Antiraid **{status}** para este servidor.")


join_cache = {}


async def on_member_join(member: discord.Member):
    data = load_infractions()
    config = data.get("config", {}).get(str(member.guild.id), {})
    if not config.get("antiraid"):
        return
    gid = member.guild.id
    now = datetime.now(timezone.utc).timestamp()
    if gid not in join_cache:
        join_cache[gid] = []
    join_cache[gid] = [t for t in join_cache[gid] if now - t < 10]
    join_cache[gid].append(now)
    if len(join_cache[gid]) >= 5:
        try:
            await member.kick(reason="[Antiraid] Entrada suspeita em massa detectada")
        except discord.Forbidden:
            pass


async def setup(bot):
    cog = Moderacao(bot)
    await bot.add_cog(cog)
    bot.add_listener(on_member_join, "on_member_join")
