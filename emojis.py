import random


def generate_random_emojis(count):
    emojis = []
    while count > 0:
        emoji = get_random_emoji()
        if emoji not in emojis:
            emojis.append(emoji)
            count -= 1
    return emojis


def get_random_emoji():
    emoji_range = (0x1F300, 0x1F3F0)  # Unicode emoji tartomány
    random_code_point = random.randint(emoji_range[0], emoji_range[1])
    return chr(random_code_point)
