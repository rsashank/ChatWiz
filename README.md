# Discord Bot with Lavalink Integration, Advanced AI Model Chat (GPT-3 API) , Reminders & More!

Lavalink Integration: The bot can play music in voice channels using the Lavalink audio player for low-latency and high-quality audio playback.

Advanced AI Chat: With GPT-3 API integration, the bot can make conversations with users.

Reminders: Users can set reminders for themselves and others on the server, with customizable messages and time intervals.

## Prerequisites

- Java 11 or higher installed
- Discord account with a bot token
- Python3

## Installation

1. Clone this repository to your local machine.
2. Update a file called secrets.json, with your OpenAI API Keys, and Discord Bot Token.
3. Open the `application.yml` file and update the following fields:
    - server address
    - server port
    - server password
4. Run the following command to install required packages:
```shell
pip install -r requirements.txt
```

## Usage

1. Open a terminal window and navigate to the directory where you cloned the repository.
2. Run the following command to start the bot:
```shell
java -jar DiscordBot.jar
```

## Credits

The Lavalink integration is based on a <a href="https://github.com/freyacodes/Lavalink"> standalone audio sending node by freyacodes.
