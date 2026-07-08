import asyncio
import os
from datetime import datetime
import discord
from discord.ext import commands
from playwright.async_api import async_playwright

# ==================== CONFIGURATION ====================
# Open-Source Safe: Pulls credentials securely from environment variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", 0))
WHATSAPP_GROUP_NAME = os.getenv("WHATSAPP_GROUP_NAME", "TechBrosWhatsApp") 
# =======================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

whatsapp_page = None
last_seen_msg_id = None

@bot.event
async def on_ready():
    print(f"🤖 Discord Relay active as: {bot.user}")
    bot.loop.create_task(run_whatsapp_monitor())

# 🎯 PREFIX TRIGGER: Only forwards if you start the message with "!text "
@bot.event
async def on_message(message):
    global whatsapp_page
    if message.author == bot.user or message.channel.id != DISCORD_CHANNEL_ID:
        return

    if message.content.startswith("!text "):
        if whatsapp_page is not None:
            try:
                clean_message = message.content[6:]
                
                input_selector = 'footer div[contenteditable="true"]'
                await whatsapp_page.wait_for_selector(input_selector, timeout=5000)
                await whatsapp_page.click(input_selector)
                await whatsapp_page.type(input_selector, clean_message, delay=25)
                await whatsapp_page.press(input_selector, "Enter")
                print(f"📤 Sent from Discord to WhatsApp -> Host (Me): {clean_message}")
            except Exception as e:
                print(f"⚠️ Message send failure: {e}")

    await bot.process_commands(message)

async def run_whatsapp_monitor():
    global whatsapp_page, last_seen_msg_id
    
    async with async_playwright() as p:
        print("🚀 Launching clean, separate browser window...")
        
        context = await p.chromium.launch_persistent_context(
            user_data_dir="./whatsapp_clean_session",
            channel="chrome",  
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars"
            ]
        )
        
        whatsapp_page = await context.new_page()
        
        await whatsapp_page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
        """)
        
        await whatsapp_page.goto("https://web.whatsapp.com")
        print("📱 Please scan the QR code inside the separate window to link your account.")
        
        await whatsapp_page.wait_for_selector('div[contenteditable="true"]', timeout=90000)
        print("✅ Main chat dashboard fully loaded!")

        try:
            group_selector = f"span[title='{WHATSAPP_GROUP_NAME}']"
            await whatsapp_page.wait_for_selector(group_selector, timeout=20000)
            await whatsapp_page.click(group_selector)
            print(f"🎯 Opened group room panel: '{WHATSAPP_GROUP_NAME}'")
        except Exception:
            print(f"💡 Select '{WHATSAPP_GROUP_NAME}' manually in the browser view window to anchor tracker.")
            await asyncio.sleep(8)

        print("🎧 System fully listening for group chat events...")

        while True:
            try:
                messages = await whatsapp_page.query_selector_all('div[role="row"]')
                
                if messages:
                    last_msg_node = messages[-1]
                    raw_text_block = await last_msg_node.inner_text()
                    lines = [line.strip() for line in raw_text_block.split('\n') if line.strip()]
                    
                    if len(lines) >= 1:
                        unique_id = "_".join(lines)
                        
                        if unique_id != last_seen_msg_id:
                            last_seen_msg_id = unique_id
                            
                            if len(lines) == 1:
                                sender_name = "Group Member"
                                message_content = lines[0]
                            else:
                                sender_name = lines[0]
                                message_content = lines[1]
                                
                                if ":" in sender_name or len(sender_name) > 25 or "am" in sender_name.lower() or "pm" in sender_name.lower():
                                    sender_name = "Host (Me)"
                                    message_content = lines[0] if len(lines) == 1 else lines[0] if ":" not in lines[0] else lines[1]

                            print(f"👀 Live Chat Event -> {sender_name}: {message_content}")
                            
                            try:
                                channel = bot.get_channel(DISCORD_CHANNEL_ID)
                                if not channel:
                                    channel = await bot.fetch_channel(DISCORD_CHANNEL_ID)
                                
                                if channel:
                                    embed = discord.Embed(
                                        description=str(message_content),
                                        color=discord.Color.from_rgb(37, 211, 102),
                                        timestamp=datetime.utcnow()
                                    )
                                    embed.set_author(name=str(sender_name))
                                    await channel.send(embed=embed)
                                    print(f"🚀 Successfully relayed to Discord!")
                            except Exception:
                                pass
                                
            except Exception:
                pass
                
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    if DISCORD_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or DISCORD_CHANNEL_ID == 0:
        print("❌ Error: Missing configuration values. Set environment variables or edit configuration constants.")
    else:
        bot.run(DISCORD_BOT_TOKEN)
