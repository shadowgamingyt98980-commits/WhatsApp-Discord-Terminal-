# 📱 WhatsApp ⇄ Discord Two-Way Bridge (V2.5)

An asynchronous Python tool that creates a real-time, bidirectional connection between a specific WhatsApp Group Chat and a Discord channel. Powered by `discord.py` and automated browser streaming via `Playwright`.

This project is built explicitly for hobby experimental setups where hosting can live locally on a dual-monitor machine.

---

## 🔥 Features (V2.5 Updates)
* **Live Inbound Mirroring**: Instantly parses incoming raw text rows and pushes cleanly formatted Discord rich embeds.
* **Contextual Reply Extraction**: Dynamically parses modern multi-line HTML structures from WhatsApp when users `@` or reply to someone, attaching the original quoted conversation text within the Discord embed layout.
* **Controlled Intercept Prefix**: Type `!text <message>` in Discord to transmit outgoing messages seamlessly back to WhatsApp via automated, human-like typing delays (25ms).
* **System Lock Overrides**: Administrators can execute `!lock` or `!unlock` to immediately pause or resume both inbound parsing and outbound transmission streams.
* **Multi-Admin Permission Control**: Restricts administrative capabilities (`!lock`, `!unlock`, and `!text`) strictly to pre-authorized Discord User ID snowflakes.
* **Evasion & Session Stability**: Uses standalone Google Chrome persistent application footprints to eliminate browser-support block walls and remember QR authorization states locally.

---

## 🛠️ System Requirements
* **Python 3.8+**
* An official local installation of the **Google Chrome Browser** (Windows/macOS/Linux).

---

## 🚀 Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com
   cd YOUR_REPOSITORY
   ```

2. **Install Required Python Dependencies**
   ```bash
   pip install discord.py playwright
   playwright install chromium
   ```

3. **Configure Settings**
   Open `bot.py` and modify the configuration constants block at the top, or provide them as environment variables:
   * `DISCORD_BOT_TOKEN`: Your secret Discord Application Bot Token.
   * `DISCORD_CHANNEL_ID`: The exact Text Channel Snowflake ID where messages should stream.
   * `WHATSAPP_GROUP_NAME`: The case-sensitive target name of your WhatsApp group chat.
   * `ADMIN_IDS`: The collection of authorized Discord User IDs.

4. **Launch the Controller**
   ```bash
   python bot.py
   ```
5. **Scan & Sync**
   Upon initialization, a standalone Chrome window will launch. Scan the QR code using WhatsApp's **Linked Devices** utility. The layout profile will cache securely into `./whatsapp_clean_session`, bypassing future login gates.

---

## 🎮 Command Usage Matrix

| Command | Permission Tier | Action Context |
| :--- | :--- | :--- |
| `!text <message>` | Administrator | Strips prefix and types your sentence cleanly into WhatsApp as you. |
| `!lock` | Administrator | Fully locks the application, stopping mirror streaming and outbound triggers. |
| `!unlock` | Administrator | Restores standard bidirectional tracking states immediately. |

---

## 🛡️ License & Safety Disclaimer
This repository is released under the **MIT License**. This project is completely independent, unendorsed by Meta Platforms Inc. or Discord Inc., and was built solely for local sandbox testing. Use responsibly.
