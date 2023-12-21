import discord
from discord.ext import commands, tasks
import asyncio
import random
import string

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

polls = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_polls.start()

@tasks.loop(seconds=30)  # Ellenőrzés minden 30 másodpercben
async def check_polls():
    current_time = asyncio.get_event_loop().time()
    for poll_id, poll_data in list(polls.items()):
        end_time = poll_data['end_time']
        if current_time >= end_time:
            channel_id = poll_data['channel_id']
            poll_message_id = poll_data['poll_message_id']
            await close_poll(channel_id, poll_message_id)
            del polls[poll_id]

@bot.command()
async def create_poll(ctx, duration_days: float, role: discord.Role, reminder_interval_hours: float, question, *options):
    end_time = asyncio.get_event_loop().time() + (duration_days * 24 * 3600)

    formatted_options = []
    emojis = generate_random_emojis(len(options))
    for i, option in enumerate(options):
        formatted_options.append(f"{emojis[i]} {option}")

    poll_question = f"{question}\n\n" + "\n".join(formatted_options)
    poll_message = await ctx.send(poll_question)

    # Emoji hozzáadása az üzenethez
    for emoji in emojis:
        await poll_message.add_reaction(emoji)

    await ctx.message.delete()

    # Azon szereplők kiválogatása, akik rendelkeznek a megadott szereppel és hozzáférnek a csatornához
    accessible_members = [member for member in role.members if ctx.channel.permissions_for(member).read_messages]

    poll_id = len(polls) + 1
    polls[poll_id] = {'end_time': end_time, 'channel_id': ctx.channel.id, 'poll_message_id': poll_message.id, 'voters': set(), 'options': options, 'question': question}

    # Emlékeztetők beállítása
    reminder_task = asyncio.ensure_future(send_reminders(ctx, accessible_members, reminder_interval_hours, poll_id, duration_days))
    polls[poll_id]['reminder_task'] = reminder_task

def generate_random_emojis(count):
    emojis = [get_random_emoji() for _ in range(count)]
    return emojis

def get_random_emoji():
    emoji_range = (0x1F300, 0x1F3F0)  # Unicode emoji tartomány
    random_code_point = random.randint(emoji_range[0], emoji_range[1])
    return chr(random_code_point)

async def send_reminders(ctx, members, reminder_interval_hours, poll_id, duration_days):
    while True:
        await asyncio.sleep(reminder_interval_hours * 3600)  # Várakozás az emlékeztetők között

        # Ellenőrzés, hogy a szavazás még aktív-e
        if poll_id not in polls:
            return

        # Ellenőrzés, hogy a szavazás lejárt-e
        current_time = asyncio.get_event_loop().time()
        end_time = polls[poll_id]['end_time']
        if current_time >= end_time:
            return

        # Azok a felhasználók, akiknek még nincs szavazatuk
        for member in members:
            if member.id not in polls[poll_id]['voters']:
                question = polls[poll_id]['question']
                reminder_message = f"{member.mention}, még nem szavaztál a következő kérdésre:\n\n{question}\n\n"
                reminder_message += f"[Szavazz most!]({ctx.message.jump_url})"
                await member.send(reminder_message)

@bot.command()
async def close_poll(ctx, poll_message_id):
    # Lezárás előtt az eredmények kinyerése az üzenetből
    poll_data = polls[int(poll_message_id)]
    channel = bot.get_channel(poll_data['channel_id'])
    poll_message = await channel.fetch_message(poll_data['poll_message_id'])
    reactions = poll_message.reactions

    # Eredmények elküldése privát üzenetben
    result_message = f"Eredmények a szavazásról {poll_message_id} üzenet alapján:\n"
    for i, reaction in enumerate(reactions):
        result_message += f"{i + 1}. {reaction.emoji}: {reaction.count - 1} szavazat\n"

    author = ctx.message.author
    user = await bot.fetch_user(author.id)
    await user.send(result_message)

    # Szavazás lezárása és emlékeztetők leállítása
    await ctx.send("A szavazás lezárult.")
    await poll_message.delete()
    del polls[int(poll_message_id)]

bot.run('Token')  # Token helyére a saját botod tokenjét helyezd el
