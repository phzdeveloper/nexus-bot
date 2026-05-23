import discord


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, motivo="Sem motivo"):
    await member.ban(reason=motivo)

    embed = discord.Embed(
        title="Membro banido",
        description=f"{member.mention} foi banido.",
        color=0xff0000
    )

    embed.add_field(name="Motivo", value=motivo)

    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, quantidade: int):
    await ctx.channel.purge(limit=quantidade + 1)

    msg = await ctx.send(f"{quantidade} mensagens apagadas.")
    await asyncio.sleep(3)
    await msg.delete()


# =========================
# PAINEL NEXUS DEFENSE
# =========================

class NexusPanel(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Lock", style=discord.ButtonStyle.danger)
    async def lock_button(self, interaction: discord.Interaction, button: Button):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False

        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            overwrite=overwrite
        )

        await interaction.response.send_message(
            "Canal bloqueado.",
            ephemeral=True
        )


    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.success)
    async def unlock_button(self, interaction: discord.Interaction, button: Button):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = True

        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            overwrite=overwrite
        )

        await interaction.response.send_message(
            "Canal desbloqueado.",
            ephemeral=True
        )


@bot.command(name="nexusdefense")
@commands.has_permissions(administrator=True)
async def nexus_defense(ctx):
    embed = discord.Embed(
        title="Nexus Defense Dashboard",
        description=(
            "Sistema de segurança do servidor.\n\n"
            "Funções:\n"
            "• Lock de canais\n"
            "• Unlock de canais\n"
            "• Anti-Link\n"
            "• Logs automáticos\n"
            "• Moderação avançada"
        ),
        color=0x2b2d31
    )

    embed.set_footer(text="Nexus Security System")

    await ctx.send(embed=embed, view=NexusPanel())


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
