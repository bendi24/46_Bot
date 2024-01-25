import discord
import asyncio
from chatGPT import bot, polls


async def update_not_voted_members(poll_id):
    channel_id = polls[poll_id]['channel_id']
    poll_message_id = polls[poll_id]['poll_message_id']

    # Csatorna és üzenet lekérése
    channel = bot.get_channel(channel_id)
    poll_message = await channel.fetch_message(poll_message_id)

    # Azok a felhasználók kiválogatása, akik még egy emojit sem tettek az üzenetre
    not_voted_members = []
    for member in polls[poll_id]['not_voted']:
        reactions = poll_message.reactions
        reacted_emojis = [reaction.emoji for reaction in reactions]
        member_emojis = [str(emoji) for emoji in member.emojis]
        if not any(emoji in member_emojis for emoji in reacted_emojis):
            not_voted_members.append(member)

    # Frissítés az új listával
    polls[poll_id]['not_voted'] = not_voted_members


async def poll_status(poll_id):
    if poll_id in polls:
        channel_id = polls[poll_id]['channel_id']
        poll_message_id = polls[poll_id]['poll_message_id']

        # Csatorna és üzenet lekérése
        channel = bot.get_channel(channel_id)
        poll_message = await channel.fetch_message(poll_message_id)

        # Az előző emojik állapotának mentése
        previous_emojis = polls[poll_id].get('emojis', [])

        # Az jelenlegi emojik lekérése
        current_emojis = [str(reaction.emoji) for reaction in poll_message.reactions]

        # Ha változás történt, elvégezzük a szükséges műveleteket
        if current_emojis != previous_emojis:
            # A változások feldolgozása (pl. visszavonás)
            # ...

            # Az új emojik mentése
            polls[poll_id]['emojis'] = current_emojis


async def watch_for_votes(delta_t):
    while True:
        await asyncio.sleep(delta_t)  # Várunk a következő ellenőrzésig

        # Ellenőrizzük az emojik állapotát
        for poll_id in polls:
            await poll_status(poll_id)
