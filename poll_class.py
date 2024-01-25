import asyncio
from emojis import generate_random_emojis


class Poll:
    def __init__(self, ctx, bot, channel, max_votes, duration_days, reminder_interval_hours, role, question, options):
        self.ctx = ctx
        self.bot = bot
        self.channel = channel

        self.max_votes = max_votes
        self.role = role

        self.duration_days = duration_days
        self.reminder_interval_hours = reminder_interval_hours
        self.end_time = asyncio.get_event_loop().time() + (duration_days * 24 * 3600)

        self.question = question
        self.options = options

        self.emojis = generate_random_emojis(len(options))

        # Azon szereplők kiválogatása, akik rendelkeznek a megadott szereppel és hozzáférnek a csatornához
        accessible_members = [member for member in self.role.members if self.channel.permissions_for(member).read_messages]
        self.not_voted = accessible_members
        self.voters = accessible_members

        # A szavazás üzenet megszerkesztése
        formatted_options = [f"{index}. {emoji}: {self.options[index]}" for index, emoji in enumerate(self.emojis)]
        self.poll_message_text = f"{self.question}\n\n" + "\n".join(formatted_options)
        self.poll_message = None

    async def create(self):
        self.poll_message = await self.channel.send(self.poll_message_text)
        for emoji in self.emojis:
            await self.poll_message.add_reaction(emoji)

        # Emlékeztetők és a szavazás végének beállítása
        iter = (self.duration_days * 24) // self.reminder_interval_hours
        reminder_task = asyncio.create_task(self.send_reminders(iter))
        close_poll = asyncio.create_task(self.close())
        await reminder_task
        await close_poll

    async def update_not_voted_members(self):
        # Azok a felhasználók kiválogatása, akik még egy emojit sem tettek az üzenetre
        message = await self.ctx.channel.fetch_message(self.poll_message.id)

        # Ellenőrizzük, hogy az üzenet reakciói vannak-e
        if message.reactions:
            for reaction in message.reactions:
                # Lekérjük a reakcióhoz tartozó felhasználókat és azok ID-jait
                users = [user async for user in reaction.users()]
                for user in users:
                    if user in self.voters:
                        self.not_voted.remove(user)

    async def send_reminders(self, iter):
        for _ in range(int(iter), 0, -1):
            await asyncio.sleep(self.reminder_interval_hours * 3600)  # Várakozás az emlékeztetők között
            await self.update_not_voted_members()
            print(self.not_voted)

            for member in self.not_voted:
                reminder_message = f"{member.mention}, még nem szavaztál a következő kérdésre:\n"
                reminder_message += "------------------------------\n"
                reminder_message += self.poll_message_text
                reminder_message += "\n------------------------------\n"
                reminder_message += f"[Szavazz most!]({self.ctx.message.jump_url})"
                await member.send(reminder_message)

    async def close(self):
        await asyncio.sleep(self.duration_days * 24 * 60 * 60)
        # Lezárás előtt az eredmények kinyerése az üzenetből
        message = await self.channel.fetch_message(self.poll_message.id)
        reactions = message.reactions

        # Eredmények elküldése privát üzenetben
        result_message = f"Eredmények a szavazásról {self.ctx.message.jump_url} üzenet alapján:\n"
        for i, reaction in enumerate(reactions):
            result_message += f"{i + 1}. {reaction} {self.options[i]}: {reaction.count - 1} szavazat\n"

        await self.ctx.author.send(result_message)

        # Szavazás lezárása és emlékeztetők leállítása
        new_text = "A szavazás lezárult.\n" "------------------------------\n" + self.poll_message_text
        await message.clear_reactions()
        await message.edit(content=new_text)
        # await self.channel.send("A szavazás lezárult.")
