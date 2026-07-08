import asyncio
import os
from datetime import datetime
import discord
from discord.ext import commands
from playwright.async_api import async_playwright

# ==================== CONFIGURATION (V2.5 GitHub Safe) ====================
# Pulls credentials securely from environment variables OR falls back to defaults
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "YOUR_DISCORD_BOT_TOKEN_HERE")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", 1524198003064176861))
WHATSAPP_GROUP_NAME = os.getenv("WHATSAPP_GROUP_NAME", "the W table")

# Admin IDs allowed to bypass lock state and control system parameters
# Defaults to your ID, but developers can expand this array via comma-separated string env
env_admins = os.getenv("ADMIN_IDS")
if env_admins:
    ADMIN_IDS = [int(x.strip()) for x in env_admins.split(",")]
else:
    ADMIN_IDS = [1167246675828551791, 908016908606005278]
# ==========================================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

whatsapp_page = None
last_seen_msg_id = None
is_locked = False

@bot.event
async def on_ready():
    print(f"🤖 Discord Relay active as: {bot.user}")
    bot.loop.create_task(run_whatsapp_monitor())

@bot.event
async def on_message(message):
    global whatsapp_page, is_locked
    if message.author == bot.user or message.channel.id != DISCORD_CHANNEL_ID:
        return

    # 🛡️ SECURITY CHECK: Handle !lock command permissions
    if message.content.strip() == "!lock":
        if message.author.id not in ADMIN_IDS:
            await message.channel.send(f"❌ <@{message.author.id}>, you do not have permission to lock this bot.")
            return
            
        if is_locked:
            await message.channel.send("🔒 The bot is already locked.")
        else:
            is_locked = True
            await message.channel.send(f"🔒 **Bot Locked by <@{message.author.id}>.** Command forwarding and chat mirroring are disabled.")
            print(f"🔒 System LOCKED by user ID: {message.author.id}")
        return

    # 🛡️ SECURITY CHECK: Handle !unlock command permissions
    if message.content.strip() == "!unlock":
        if message.author.id not in ADMIN_IDS:
            await message.channel.send(f"❌ <@{message.author.id}>, you do not have permission to unlock this bot.")
            return
            
        if not is_locked:
            await message.channel.send("🔓 The bot is already unlocked.")
        else:
            is_locked = False
            await message.channel.send(f"🔓 **Bot Unlocked by <@{message.author.id}>.** Resuming regular transmission tracking.")
            print(f"🔓 System UNLOCKED by user ID: {message.author.id}")
        return

    # 🎯 PREFIX TRIGGER: Check if locked and verify admin permissions before forwarding messages
    if message.content.startswith("!text "):
        if message.author.id not in ADMIN_IDS:
            await message.channel.send(f"❌ <@{message.author.id}>, only authorized bot administrators can use the text command.")
            return

        if is_locked:
            await message.channel.send("❌ Cannot forward message. The bot is currently locked. Type `!unlock` first.")
            return

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
    global whatsapp_page, last_seen_msg_id, is_locked
    
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
        
        await whatsapp_page.goto("https://whatsapp.com")
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
                if is_locked:
                    await asyncio.sleep(1)
                    continue

                messages = await whatsapp_page.query_selector_all('div[role="row"]')
                
                if messages:
                    last_msg_node = messages[-1]
                    raw_text_block = await last_msg_node.inner_text()
                    lines = [line.strip() for line in raw_text_block.split('\n') if line.strip()]
                    
                    if len(lines) >= 1:
                        unique_id = "_".join(lines)
                        
                        if unique_id != last_seen_msg_id:
                            last_seen_msg_id = unique_id
                            
                            is_reply = False
                            replied_to = "Someone"
                            original_msg = ""

                            if len(lines) >= 4 and (":" in lines[-1] or "am" in lines[-1].lower() or "pm" in lines[-1].lower()):
                                is_reply = True
                                replied_to = lines[1]
                                original_msg = lines[2]
                                
                                sender_name = lines[0]
                                message_content = lines[-2] if ":" in lines[-1] else lines[-1]
                            else:
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
                                    
                                    if is_reply:
                                        embed.set_author(name=f"💬 {sender_name} replied to {replied_to}")
                                        embed.add_field(name=f"Original Message from {replied_to}", value=f"*{original_msg}*", inline=False)
                                    else:
                                        embed.set_author(name=str(sender_name))
                                        
                                    await channel.send(embed=embed)
                                    print(f"🚀 Successfully relayed to Discord!")
                            except Exception:
                                pass
                                
            except Exception:
                pass
                
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    if DISCORD_BOT_TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        print("❌ Error: You forgot to set your DISCORD_BOT_TOKEN config variable!")
    else:
        bot.run(DISCORD_BOT_TOKEN)
