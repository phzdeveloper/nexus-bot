require("dotenv").config();

const fs = require("fs");
const path = require("path");

const {
    REST,
    Routes
} = require("discord.js");

const commands = [];

const commandFolders = fs.readdirSync("./src/commands");

for (const folder of commandFolders) {

    const files = fs
        .readdirSync(`./src/commands/${folder}`)
        .filter(file => file.endsWith(".js"));

    for (const file of files) {

        const command =
            require(`./src/commands/${folder}/${file}`);

        commands.push(
            command.data.toJSON()
        );
    }
}

const rest = new REST({
    version: "10"
}).setToken(process.env.TOKEN);

(async () => {

    await rest.put(
        Routes.applicationGuildCommands(
            process.env.CLIENT_ID,
            process.env.GUILD_ID
        ),
        {
            body: commands
        }
    );

    console.log("✅ Slash Commands registrados.");

})();
