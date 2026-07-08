` and powered by automated browser interactions using `Playwright`.

## ✨ Features
* **Live Inbound Mirroring**: Forwards group text data directly into Discord via structured embeds instantly.
* **Smart Sender Detection**: Parses and tags group members accurately while filtering system timestamp blocks.
* **Controlled Intercept Response**: Type `!text <message>` into your Discord channel to send a message back to WhatsApp.
* **Anti-Detection Engine**: Runs on a separate Google Chrome engine to completely bypass automation browser blocks.

## 🛠️ Prerequisites
* **Python 3.8+** installed on your system.
* A standard desktop installation of **Google Chrome**.

## 🚀 Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com
   cd YOUR_REPO_NAME
   ```

2. **Install Required Libraries**
   ```bash
   pip install discord.py playwright
   playwright install chromium
   ```

3. **Configure Your Credentials**
   Set up your system environment configuration variables (or edit the configuration lines at the top of `bot.py` directly for quick testing):
   * `DISCORD_BOT_TOKEN` : Your secret bot gateway app token string.
   * `DISCORD_CHANNEL_ID` : The target room ID where texts should stream.
   * `WHATSAPP_GROUP_NAME` : The case-sensitive target group name.

4. **Run the Script**
   ```bash
   python bot.py
   ```
5. **Authenticate**
   When the persistent automation window opens, scan the displayed QR code with your phone just once. The session cookies will save locally inside `./whatsapp_clean_session` so you remain permanently logged in!

## 🧪 How To Use
* **Reading**: Let the script run in the background. Incoming text items stream cleanly into Discord.
* **Replying**: Inside your designated Discord text channel, write:
  `!text Hello Everyone!`
  The bot will strip the command prefix and type only the words into your active WhatsApp group!

## 📄 License
This repository is open-sourced under the MIT License. Use it responsibly for experimental purposes.
