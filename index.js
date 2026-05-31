require("dotenv").config();

const fs = require("fs");
const path = require("path");

const {
    Client,
    GatewayIntentBits,
    Collection
} = require("discord.js");

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMembers
    ]
});

client.commands = new Collection();

const commandFolders = fs.readdirSync(
    path.join(__dirname, "commands")
);

for (const folder of commandFolders) {

    const commandFiles = fs
        .readdirSync(path.join(__dirname, "commands", folder))
        .filter(file => file.endsWith(".js"));

    for (const file of commandFiles) {

        const command = require(
            path.join(__dirname, "commands", folder, file)
        );

        client.commands.set(
            command.data.name,
            command
        );
    }
}

const eventFiles = fs
    .readdirSync(path.join(__dirname, "events"))
    .filter(file => file.endsWith(".js"));

for (const file of eventFiles) {

    const event = require(
        path.join(__dirname, "events", file)
    );

    if (event.once) {
        client.once(event.name, (...args) =>
            event.execute(...args, client)
        );
    } else {
        client.on(event.name, (...args) =>
            event.execute(...args, client)
        );
    }
}

client.login(process.env.TOKEN);
