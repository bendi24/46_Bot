import discord
from discord.ext import commands
import poll_class

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

polls = []


@bot.command()
async def create_poll(ctx, max_votes: int, duration_days: float, reminder_interval_hours: float, role: discord.Role,
                      question, *options):
    poll = poll_class.Poll(ctx, bot, ctx.channel, max_votes, duration_days, reminder_interval_hours, role, question, options)
    await poll.create()


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


bot.run(
    'MTE4NzMzMzg5OTgwNjg0MjkzMQ.GfQD1I.FGsCFt90PHuuaK7eJUyzxhgXFkQ71I-JHij6qY')  # Token helyére a saját botod tokenjét helyezd el
