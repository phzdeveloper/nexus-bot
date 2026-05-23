import discord
async def scan_content(interaction: discord.Interaction, conteudo: str):

    suspeito = [
        "grabify",
        "token",
        "nitro free",
        "malware",
        "phishing"
    ]

    resultado = "✅ Nenhuma ameaça detectada."

    for item in suspeito:
        if item in conteudo.lower():
            resultado = "🚨 Conteúdo suspeito detectado."
            break

    embed = discord.Embed(
        title="🔍 Nexus Scanner",
        description=resultado,
        color=0x5865F2
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="quarantine", description="Coloca usuário em quarentena")
@app_commands.describe(usuario="Usuário")
async def quarantine(interaction: discord.Interaction, usuario: discord.Member):

    role = discord.utils.get(interaction.guild.roles, name="Quarantine")

    if not role:
        role = await interaction.guild.create_role(name="Quarantine")

    await usuario.add_roles(role)

    embed = discord.Embed(
        title="🚨 Usuário em Quarentena",
        description=f"{usuario.mention} foi isolado pela staff.",
        color=0xff0000
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="analyze-pattern", description="Analisa padrão de mensagens")
@app_commands.describe(usuario="Usuário")
async def analyze_pattern(interaction: discord.Interaction, usuario: discord.Member):

    total = mensagens.get(usuario.id, 0)

    status = "🟢 Comportamento normal"

    if total > 500:
        status = "🟡 Alto volume detectado"

    if total > 1500:
        status = "🔴 Comportamento suspeito"

    embed = discord.Embed(
        title="🧠 Nexus Pattern Analyzer",
        description=(
            f"Usuário: {usuario.mention}
"
            f"Mensagens registradas: {total}
"
            f"Resultado: {status}"
        ),
        color=0x5865F2
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="check-reputation", description="Verifica reputação")
@app_commands.describe(alvo="Usuário, IP ou link")
async def check_reputation(interaction: discord.Interaction, alvo: str):

    embed = discord.Embed(
        title="🌐 Reputation Check",
        description=(
            f"Alvo analisado: {alvo}

"
            "✅ Nenhum histórico suspeito encontrado."
        ),
        color=0x5865F2
    )

    embed.set_footer(
        text="Simulação local • APIs externas não configuradas"
    )

    await interaction.response.send_message(embed=embed)

# =========================
# START
# =========================

bot.run(TOKEN)
