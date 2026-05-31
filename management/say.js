const {
    SlashCommandBuilder,
    PermissionFlagsBits
} = require("discord.js");

const roles = require("../../config/permissions");

module.exports = {

    data: new SlashCommandBuilder()
        .setName("say")
        .setDescription("Enviar mensagem")
        .addChannelOption(option =>
            option
                .setName("canal")
                .setDescription("Canal")
                .setRequired(true)
        )
        .addStringOption(option =>
            option
                .setName("mensagem")
                .setDescription("Mensagem")
                .setRequired(true)
        ),

    async execute(interaction) {

        const allowed = [

            roles.CEO,
            roles.MANAGER,
            roles.ADMINISTRATOR,
            roles.MODERATOR,
            roles.STAFF

        ];

        const hasRole =
            interaction.member.roles.cache
                .some(role => allowed.includes(role.id));

        if (!hasRole) {

            return interaction.reply({
                content: "❌ Sem permissão.",
                ephemeral: true
            });
        }

        const channel =
            interaction.options.getChannel("canal");

        const message =
            interaction.options.getString("mensagem");

        await channel.send(message);

        await interaction.reply({
            content: `✅ Mensagem enviada em ${channel}`
        });
    }
};
