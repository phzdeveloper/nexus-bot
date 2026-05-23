import discord

@bot.command(name="nexusdashboard")
@commands.has_permissions(administrator=True)
async def nexus_dashboard(ctx):

    embed = discord.Embed(
        title="NEXUS SECURITY DASHBOARD",
        description=(
            "Painel central de segurança e moderação.

"
            "━━━━━━━━━━━━━━━━━━
"
            "⚔️ COMANDOS DISPONÍVEIS
"
            "━━━━━━━━━━━━━━━━━━

"
            "🔒 /lock
"
            "Bloqueia o canal atual.

"
            "🔓 /unlock
"
            "Desbloqueia o canal atual.

"
            "🚨 /ban @usuario motivo
"
            "Bane um membro.

"
            "👢 /kick @usuario motivo
"
            "Expulsa um membro.

"
            "🧹 /clear quantidade
"
            "Limpa mensagens.

"
            "🛡️ /nexusdashboard
"
            "Abre o painel de segurança.

"
            "━━━━━━━━━━━━━━━━━━
"
            "⚡ SISTEMAS ATIVOS
"
            "━━━━━━━━━━━━━━━━━━

"
            "• Anti-Link
"
            "• Logs automáticos
"
            "• Lockdown global
"
            "• Painel interativo
"
            "• Proteção administrativa"
        ),
        color=0x0f111a
    )

    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)

    embed.set_footer(
        text="Nexus Security • Advanced Protection System"
    )

    await ctx.send(
        embed=embed,
        view=NexusPanel()
    )

# =========================
# ERROS
# =========================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Você não tem permissão para isso.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Argumentos inválidos.")


bot.run(TOKEN)
