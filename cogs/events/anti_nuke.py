import discord
from discord.ext import commands
import time
from collections import defaultdict

class AntiNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Sistema de memória tática: Regista {id_do_utilizador: [tempos_das_acoes]}
        self.action_logs = defaultdict(list)
        
        # ━━━━━━━━━━━━━━━━━━
        # CONFIGURAÇÕES DO ANTI-NUKE
        # ━━━━━━━━━━━━━━━━━━
        self.LIMIT = 3          # Número de ações perigosas permitidas...
        self.TIME_WINDOW = 10   # ...dentro deste intervalo de tempo (em segundos)

    def check_nuke(self, user_id):
        """Verifica se o utilizador excedeu o limite de ações no tempo definido."""
        now = time.time()
        # Limpa os registos antigos que já passaram da janela de tempo
        self.action_logs[user_id] = [t for t in self.action_logs[user_id] if now - t < self.TIME_WINDOW]
        self.action_logs[user_id].append(now)
        
        # Se as ações ultrapassarem o limite, aciona o alerta crítico
        if len(self.action_logs[user_id]) >= self.LIMIT:
            return True
        return False

    async def punish_nuker(self, guild, user_id, reason):
        """Executa a punição máxima (Ban) no agressor."""
        try:
            member = guild.get_member(user_id)
            if member:
                await member.ban(reason=f"NEXUS ANTI-NUKE: {reason}")
                print(f"[ALERTA CRÍTICO] {member} foi neutralizado. Motivo: {reason}.")
                
                # Opcional: Tentar enviar um aviso para o canal principal do servidor
                if guild.system_channel:
                    embed = discord.Embed(
                        title="🛡️ DEFESA ANTI-NUKE ATIVADA",
                        description=f"O utilizador **{member.name}** foi banido preventivamente.\n**Ameaça detetada:** {reason}.",
                        color=0xFF0000
                    )
                    await guild.system_channel.send(embed=embed)
        except discord.Forbidden:
            print(f"[FALHA] O Nexus não tem permissão para banir o utilizador {user_id}.")

    # ━━━━━━━━━━━━━━━━━━
    # MONITORES DE EVENTOS
    # ━━━━━━━━━━━━━━━━━━

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Dispara quando um canal é apagado."""
        guild = channel.guild
        # Inspeciona os registos de auditoria (Audit Logs) para descobrir quem apagou o canal
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            user = entry.user
            if user.bot: return # Ignora outros bots

            if self.check_nuke(user.id):
                await self.punish_nuker(guild, user.id, "Deleção em massa de canais")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Dispara quando alguém é banido do servidor."""
        # Inspeciona os registos de auditoria para descobrir quem deu o ban
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            admin = entry.user
            if admin.bot: return

            if self.check_nuke(admin.id):
                await self.punish_nuker(guild, admin.id, "Banimentos em massa (Raid)")

async def setup(bot):
    await bot.add_cog(AntiNuke(bot))
