import datetime
import random
import threading

import discord
from discord.ext import commands

# 46 test bot token
TOKEN = "MTE4NzMzMzg5OTgwNjg0MjkzMQ.GGLhWK.HR07DWRmW3SOu6HMCRF7UNzh7aOgxilLp4DmU8"

# 46 sima bot token
# TOKEN = "MTE4MjAxOTA5OTY3NzcwMDE1Nw.Gil52k.c_efXpjDhnUHgdRMLapneOplrFUr5IG_GedrCM"

# Initialize Bot and Denote The Command Prefix
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
global guild
guild = bot.get_guild(1182427420352061560)  # Szerver ID
emoji_list = ['🫠', '🥶', '🙀', '👨‍🍳', '🧖', '💃']


async def send_poll_answer(author, poll, msg):
    await author.send("# Véget ért az általad meghirdetett szavazás!\n")
    await author.send(poll)
    msg = await msg.channel.fetch_message(msg.id)
    reacts = ""
    for i in range(len(msg.reactions)):
        reacts += str(msg.reactions[i]) + " : " + str(msg.reactions[i].count) + "\n"
    await author.send(reacts)
    await msg.unpin()


async def send_poll_reminder(participants, poll, time):  # Mindenkinek küld egy emlékeztetőt
    for person in participants:
        await person.send(f"# Még nem szavaztál!\nMár csak {time/(60*60)} óra van hátra a szavazás végig!\n")
        await person.send(poll)


# Runs when Bot Succesfully Connects
@bot.event
async def on_ready():
    print(f'{bot.user} succesfully logged in!')


# !poll
@bot.command()
async def poll(ctx, question, deadline, role: discord.Role, *options):
    """
    Szavazás indítása
    :param ctx:
    :param question: A kérdés
    :param deadline: Határidő órában megadva
    :param role: A szavazásban résztvevők rangjának megadása
    :param options: A lehetőségek felsorolása ","-vel elválasztva
    """
    await ctx.channel.purge(limit=1)
    options = list(options[0].split(","))

    # A rang szerinti résztvevők kilistázása
    participants = role.members  # hiba lehet ha nem létező rangot kap, nem lehet több rangot megadni

    message = [["\n----------\n", question, "\n----------"]]
    for i in options:
        e = random.choice(emoji_list)
        message.append([i, ".", e, ":"])
        emoji_list.remove(str(e))
    message_str = ""
    for part in message:
        for k in part:
            message_str += k + ""
        message_str += "\n\n"
    yeet = await ctx.send("```" + message_str + "```")
    await yeet.pin()
    for j in range(1, len(message)):
        await yeet.add_reaction(message[j][2])

    if deadline == "0" or 0:
        print("Nincs határidő beállítva!")

    else:
        author = ctx.author
        now = datetime.datetime.now()
        run_at = now + datetime.timedelta(hours=float(deadline))
        delay = (run_at - now).total_seconds()

        # időzített események bállítása
        days = delay//(24*60*60)
        print(delay)
        for i in range(1, int(days)):
            message_time = float(i*24*60*60)
            # print(message_time)
            threading.Timer(message_time, await send_poll_reminder(participants, message_str, delay)).start()
        threading.Timer(delay, await send_poll_answer(author, message_str, yeet)).start()

bot.run(TOKEN)
