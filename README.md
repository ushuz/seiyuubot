# Seiyuu Bot

Give what you said on Discord a voice. Powered by [Azure Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/text-to-speech/).


### Prerequisites

- [Discord Bot](https://discord.com/developers/applications)
    + Generate bot token
    + Grant bot permissions to:
        * Read messages
        * Connect to and speak in voice channels
- [Azure Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/text-to-speech/)
    + Add a Speech service
    + Use credentials from "Keys and Endpoint" portal:
        * `KEY 1` or `KEY 2` as the key
        * `Location/Region` as the region

### Install

Ensure dependencies are installed

```bash
# libraries
brew install ffmpeg libopus

# packages
pip install -r requirements.txt
```

### Usage

```bash
# setup credentials
export DISCORD_TOKEN=<token>
export AZURE_SPEECH_KEY=<key>
export AZURE_SPEECH_REGION=<region>

# configure VOICES in bot.py
vi bot.py

# launch the bot
python bot.py
```
