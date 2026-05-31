const {
    SlashCommandBuilder,
    EmbedBuilder
} = require("discord.js");

module.exports = {

    data: new SlashCommandBuilder()
        .setName("userinfo")
        .setDescription("Informações do usuário")
        .addUserOption(option =>
            option
                .setName("usuario")
                .setDescription("Usuário")
                .setRequired(false)
        ),

    async execute(interaction) {

        const user =
            interaction.options.getUser("usuario")
            || interaction.user;

        const member =
            await interaction.guild.members.fetch(user.id);

        const embed = new EmbedBuilder()
            .setTitle("User Info")
            .setThumbnail(user.displayAvatarURL())
            .addFields(
                {
                    name: "Usuário",
                    value: user.tag
                },
                {
                    name: "ID",
                    value: user.id
                },
                {
                    name: "Entrou",
                    value: `<t:${Math.floor(member.joinedTimestamp / 1000)}:R>`
                }
            );

        await interaction.reply({
            embeds: [embed]
        });
    }
};
