import discord
from discord.ext import commands, tasks
from discord import app_commands
import tls_client
import threading
import string
import colorama
import pystyle
import time
import ctypes
import random
import os
import requests
from base64 import b64encode
import json
from colorama import Fore, Style, Back,init

with open("config/config.json") as f:
    config = json.load(f)

gradient_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
class color:
   BOLD = '\033[1m'

def update_title(title):
    if update_title:
      ctypes.windll.kernel32.SetConsoleTitleW(title)
    else:
        return None

update_title('Oauth2 Boost Bot | @mur9er')

class Fore:
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
BUILD_NUMBER = 165486
CV = "108.0.0.0"
BOT_TOKEN = config["bot_token"]
CLIENT_SECRET = config["client_secret"]
CLIENT_ID = config["client_id"]
REDIRECT_URI = config["redirect_url"]
API_ENDPOINT = 'https://canary.discord.com/api/v9'
AUTH_URL = f"https://canary.discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify%20guilds.join"

SUPER_PROPERTIES = b64encode(
    json.dumps(
        {
            "os": "Windows",
            "browser": "Chrome",
            "device": "PC",
            "system_locale": "en-GB",
            "browser_user_agent": USER_AGENT,
            "browser_version": CV,
            "os_version": "10",
            "referrer": "https://discord.com/channels/@me",
            "referring_domain": "discord.com",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": BUILD_NUMBER,
            "client_event_source": None
        },
        separators=(',', ':')).encode()).decode()

def get_headers(token):
    return {
        "Authorization": token,
        "Origin": "https://canary.discord.com",
        "Accept": "*/*",
        "X-Discord-Locale": "en-GB",
        "X-Super-Properties": SUPER_PROPERTIES,
        "User-Agent": USER_AGENT,
        "Referer": "https://canary.discord.com/channels/@me",
        "X-Debug-Options": "bugReporterEnabled",
        "Content-Type": "application/json"
    }

def exchange_code(code):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(f"{API_ENDPOINT}/oauth2/token", data=data, headers=headers)
    if response.status_code in (200, 201, 204):
        return response.json()
    else:
        print(f"Error exchanging code: {response.status_code} - {response.text}")
        return False

def add_to_guild(access_token, user_id, guild_id):
    url = f"{API_ENDPOINT}/guilds/{guild_id}/members/{user_id}"
    bot_token = BOT_TOKEN
    data = {"access_token": access_token}
    headers = {"Authorization": f"Bot {bot_token}", 'Content-Type': 'application/json'}
    response = requests.put(url=url, headers=headers, json=data)
    return response.status_code

def rename(token, guild_id, nickname):
    if nickname:
        headers = get_headers(token)
        client = tls_client.Session(client_identifier="firefox_102")
        client.headers.update(headers)
        response = client.patch(
            f"https://canary.discord.com/api/v9/guilds/{guild_id}/members/@me",
            json={"nick": nickname}
        )
        if response.status_code in (200, 201, 204):
            print(f"{Fore.GREEN} ✅ INFO : Successfully Changed Nickname to - {nickname}!")
            return "ok"
        else:
            print(f"{Fore.RED} ❌ INFO : Failed to Change Nickname! Status: {response.status_code}, Response: {response.text}")
            return "error"

def update_pfp(token, image_path):
    if image_path and os.path.isfile(image_path):
        headers = get_headers(token)
        with open(image_path, "rb") as f:
            image_data = f.read()
        image_base64 = b64encode(image_data).decode('utf-8')
        response = requests.patch(
            f"{API_ENDPOINT}/users/@me",
            headers=headers,
            json={"avatar": f"data:image/png;base64,{image_base64}"}
        )
        if response.status_code in (200, 201, 204):
            print(f"{Fore.GREEN} ✅ INFO : Successfully Changed Profile Picture!")
            return "ok"
        else:
            print(f"{Fore.RED} ❌ INFO: Failed to Change Profile Picture!")
            return "error"

def get_user(access_token):
    response = requests.get(
        f"{API_ENDPOINT}/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if response.status_code == 200:
        response_json = response.json()
        return response_json['id']
    else:
        print(f"{Fore.RED} ❌ INFO : Failed to get User Information!")
        return None

def authorize(token, guild_id, nickname, pfp_path):
    headers = get_headers(token)
    response = requests.post(AUTH_URL, headers=headers, json={"authorize": "true"})
    if response.status_code in (200, 201, 204):
        location = response.json().get('location')
        code = location.replace("http://localhost:8080?code=", "")
        exchange = exchange_code(code)
        if exchange:
            access_token = exchange['access_token']
            user_id = get_user(access_token)
            if user_id:
                add_to_guild(access_token, user_id, guild_id)
                if nickname:
                    threading.Thread(target=rename, args=(token, guild_id, nickname)).start()
                if pfp_path:
                    threading.Thread(target=update_pfp, args=(token, pfp_path)).start()
                return "ok"
    print(f"{Fore.RED} ❌ INFO : Failed to Authorize the Bot in the Provided Guild!")
    return "error"

def generate_order_id(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def log_order_info(order_id, guild_id, amount_of_boosts, time_taken, tokens_used, status):
    with open("output/order_logs.txt", "a") as f:
        f.write(f"{order_id},{guild_id},{amount_of_boosts},{time_taken},{tokens_used},{status}\n")

def main(token, guild_id, order_id, nickname=None, pfp_path=None):
    authorization_result = authorize(token, guild_id, nickname, pfp_path)
    if authorization_result == "ok":
        headers = get_headers(token)
        client = tls_client.Session(client_identifier="firefox_102")
        client.headers.update(headers)
        response = client.get(f"{API_ENDPOINT}/users/@me/guilds/premium/subscription-slots")
        
        try:
            slots = response.json()
            if isinstance(slots, list):
                for slot in slots:
                    if isinstance(slot, dict) and 'id' in slot:
                        slot_id = slot['id']
                        payload = {"user_premium_guild_subscription_slot_ids": [slot_id]}
                        response = client.put(
                            f"{API_ENDPOINT}/guilds/{guild_id}/premium/subscriptions",
                            json=payload
                        )
                        if response.status_code in (200, 201, 204):
                            print(f"{Fore.GREEN} ✅ INFO : Successfully Boosted in the Server with Mentioned Guild ID - {guild_id}!")
                            status = "successful"
                        else:
                            print(f"{Fore.RED} ❌ INFO : Failed to Boost in the Server with Mentioned Guild ID - {guild_id}!")
                            status = "failed"

                        log_order_info(order_id, guild_id, len(slots), time.time(), 1, status)
            else:
                print(f"{Fore.RED} ❌ INFO : Unexpected Response Format - {slots}!")
        except json.JSONDecodeError as e:
            print(f"{Fore.RED} ❌ INFO : Failed to parse JSON response - {e}!")

bot_activity_config = config.get("bot_activity", {})
activity_type = bot_activity_config.get("type", "watching")
activity_name = bot_activity_config.get("name", "your activity")

@bot.event
async def on_ready():
    os.system('cls')
    await bot.tree.sync()
    total_commands = len(bot.tree.get_commands())
    print(f'''{Fore.YELLOW}
  {Fore.YELLOW} Developer: @mur9er
  
  
''')
    print(f"{Fore.GREEN} ✅ INFO : Logged in as {bot.user}")
    print(f"{Fore.GREEN} ✅ INFO : Fetched All Commands: {total_commands}")
    
    activity = discord.Activity(type=getattr(discord.ActivityType, activity_type, discord.ActivityType.watching), name=activity_name)
    await bot.change_presence(activity=activity)

ALLOWED_USER_IDS = config.get("authorized_user_ids", [])

def is_allowed_user():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id in ALLOWED_USER_IDS:
            return True
        embed = discord.Embed(title="Permission Denied", description="You are not allowed to use this command.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return False
    return app_commands.check(predicate)

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

def write_tokens_to_file(file_path, tokens):
    with open(file_path, "a") as f:
        for token in tokens:
            f.write(token + "\n")

@bot.tree.command(name="boost")
@is_allowed_user()
@app_commands.describe(guild_id="The ID of the guild", amount_of_boosts="The number of boosts to apply", nickname="The nickname to use", pfp_path="The path to the profile picture file")
async def boosts(interaction: discord.Interaction, guild_id: str, amount_of_boosts: int, nickname: str = None, pfp_path: str = None):
    if not guild_id or amount_of_boosts <= 0:
        embed = discord.Embed(title="Missing Arguments", description="Please provide the guild ID and a valid amount of boosts.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    order_id = generate_order_id(random.randint(8, 12))
    
    print("")
    print(f" ✅ INFO : Starting Boosting with Order ID: {order_id}")
    print("")

    start_embed = discord.Embed(title="Boosting Started", color=discord.Color.blue())
    start_embed.add_field(name="Order ID:", value=order_id, inline=False)
    start_embed.add_field(name="Guild ID:", value=guild_id, inline=False)
    start_embed.add_field(name="Amount of Boosts:", value=amount_of_boosts, inline=False)
    start_embed.add_field(name="Nickname:", value=nickname if nickname else "Not provided", inline=False)
    start_embed.add_field(name="Profile Picture:", value=pfp_path if pfp_path else "Not provided", inline=False)

    await interaction.response.send_message(embed=start_embed)

    start_time = time.time()
    tokens_needed = amount_of_boosts // 2
    with open("input/nitro_tokens.txt", "r") as f:
        tokens = f.readlines()

    if len(tokens) < tokens_needed:
        await interaction.followup.send(f"Not enough tokens available. Required: {tokens_needed}, Available: {len(tokens)}")
        return

    success_tokens = []
    failed_tokens = []

    for token in tokens[:tokens_needed]:
        token = token.strip()
        if ":" in token:
            try:
                token = token.split(":")[2]
            except IndexError:
                failed_tokens.append(token)
                continue
        
        success = main(token, guild_id, order_id, nickname, pfp_path)

        if success:
            success_tokens.append(token)
        else:
            failed_tokens.append(token)

    time_taken = time.time() - start_time
    log_order_info(order_id, guild_id, amount_of_boosts, time_taken, len(success_tokens), "successful" if success_tokens else "failed")

    remaining_tokens = tokens[tokens_needed:]
    with open("input/nitro_tokens.txt", "w") as f:
        f.writelines(remaining_tokens)

    write_tokens_to_file(os.path.join(output_dir, "success_tokens.txt"), success_tokens)
    write_tokens_to_file(os.path.join(output_dir, "failed_tokens.txt"), failed_tokens)

    end_status = "Successful" if success_tokens else "Failed"
    end_embed = discord.Embed(title="Boosting Completed", color=discord.Color.green() if end_status == "Successful" else discord.Color.red())
    end_embed.add_field(name="Order ID", value=order_id, inline=False)
    end_embed.add_field(name="Guild ID", value=guild_id, inline=False)
    end_embed.add_field(name="Amount of Boosts", value=amount_of_boosts, inline=False)
    end_embed.add_field(name="Status", value=end_status, inline=False)

    await interaction.followup.send(embed=end_embed)

@bot.tree.command(name="get_order_id")
@is_allowed_user()
@app_commands.describe(order_id="The Order ID to retrieve information for")
async def get_order_id(interaction: discord.Interaction, order_id: str):
    try:
        with open("output/order_logs.txt", "r") as f:
            lines = f.readlines()
        
        for line in lines:
            fields = line.strip().split(',')
            if len(fields) != 6:
                print(f"❌ INFO : Skipping malformed log entry: {line.strip()}")
                continue

            log_order_id, guild_id, amount_of_boosts, time_taken, tokens_used, status = fields
            
            if log_order_id == order_id:
                embed = discord.Embed(title="Order Information", color=discord.Color.green() if status == "successful" else discord.Color.red())
                embed.add_field(name="Status:", value=status.capitalize(), inline=False)
                embed.add_field(name="Order ID:", value=log_order_id, inline=False)
                embed.add_field(name="Guild ID:", value=guild_id, inline=False)
                embed.add_field(name="Amount of Boosts:", value=amount_of_boosts, inline=False)
                embed.add_field(name="Tokens Used:", value=tokens_used, inline=False)
                await interaction.response.send_message(embed=embed)
                return
        
        embed = discord.Embed(title="Order Not Found", description="The specified order ID does not exist.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
    
    except Exception as e:
        embed = discord.Embed(title="Error", description=f"An error occurred while retrieving order information: {str(e)}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="restock")
@is_allowed_user()
@app_commands.describe(code="Type Paste.ee Code", type="Type 1 here")
async def restock(interaction: discord.Interaction, code: str, type: int):
    if type == 1:
        file = "input/nitro_tokens.txt"
    else:
        await interaction.response.send_message("Invalid token type.", ephemeral=True)
        return
    code = code.replace("https://paste.ee/p/", "")
    temp_stock = requests.get(
        f"https://paste.ee/d/{code}",
        headers={"User -Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36"}
    ).text

    try:
        with open(file, "a", encoding="utf-8") as f:
            f.write(f"{temp_stock}\n")
    except Exception as e:
        await interaction.response.send_message(f"Failed to write to file: {str(e)}", ephemeral=True)
        return
    
    lst = temp_stock.split("\n")
    await interaction.response.send_message(
        embed=discord.Embed(
            title="**Success**",
            description=f"Successfully added {len(lst)} tokens to {file}",
            color=0x4598d2
        )
    )

@bot.tree.command(name="stock")
@is_allowed_user()
async def stock(interaction: discord.Interaction):
    with open("input/nitro_tokens.txt", "r") as f:
        tokens = f.readlines()
    
    amount_of_tokens = len(tokens)
    amount_of_boosts = amount_of_tokens * 2
    embed = discord.Embed(title="Current Stock", color=discord.Color.green())
    embed.add_field(name="Tokens", value=str(amount_of_tokens), inline="false")
    embed.add_field(name="Boosts", value=str(amount_of_boosts), inline="false")
    await interaction.response.send_message(embed=embed)
    
@bot.tree.command(name="send_tokens")
@is_allowed_user()
@app_commands.describe(user="The user to send tokens to", amount="The number of tokens to send")
async def send_tokens(interaction: discord.Interaction, user: discord.User, amount: int):
    if amount <= 0:
        embed = discord.Embed(title="Invalid Amount", description="Please provide a valid amount of tokens to send.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    with open("input/nitro_tokens.txt", "r") as f:
        tokens = f.readlines()

    if len(tokens) < amount:
        embed = discord.Embed(title="Insufficient Tokens", description=f"Not enough tokens available. Required: {amount}, Available: {len(tokens)}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    tokens_to_send = [token.strip() for token in tokens[:amount]]
    
    tokens_file_path = "output/sent_tokens.txt"
    with open(tokens_file_path, "w") as f:
        for token in tokens_to_send:
            f.write(token + "\n")
    try:
        await user.send(file=discord.File(tokens_file_path))
        embed = discord.Embed(title="Success", description=f"✅ Successfully Sent {amount} Nitro Tokens to {user.mention}!", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.Forbidden:
        embed = discord.Embed(title="❌ Failed to Send Tokens", description=f"Failed to send tokens to {user.mention}. They might have DMs disabled.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(title="❌ Error", description=f"An error occurred while sending tokens: {str(e)}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    remaining_tokens = tokens[amount:]
    with open("input/nitro_tokens.txt", "w") as f:
        f.writelines(remaining_tokens)

bot.run(BOT_TOKEN)  
