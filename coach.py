import random
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents
intents = discord.Intents.default()
intents.message_content = True  # Needed for commands in discord.py 2.x
intents.members = True
intents.voice_states = True

# Running tasks
running_tasks = {}

# Prefix
bot = commands.Bot(command_prefix="coach! ", intents=intents)

# Pictures for the guard command
COACH_GUARD = [
    f"https://cdn.imgchest.com/files/4jdcvmaarx4.png",
    f"https://cdn.imgchest.com/files/739cx8qqon7.png",
]
weights_guard = [100, 1]

# Audio files, organized by state
COACH_START = ["Audio/INTRO/CALISTHENICS.mp3"]
COACH_COMMANDS = ["Audio/UP.mp3", "Audio/LEFT.mp3", "Audio/RIGHT.mp3"]
COACH_FCOMMANDS = ["Audio/FASTER/FUP.mp3", "Audio/FASTER/FLEFT.mp3", "Audio/FASTER/FRIGHT.mp3"]
DOWN_RELAX = ["Audio/DOWN.mp3", "Audio/RELAX.mp3"]
COACH_PUTP = ["Audio/FASTER/PUTP.mp3"]

COACH_INTRO = [
    "Audio/INTRO/FA.mp3",
    "Audio/INTRO/LOOKSLIKE.mp3",
    "Audio/INTRO/PAN.mp3",
]



COACH_OUTRO = [
    "Audio/OUTRO/PITIFUL.mp3", 
    "Audio/OUTRO/DONTMESSWTC.mp3",
    "Audio/OUTRO/OXBOWSONG.mp3",
    "Audio/OUTRO/SUCCSONG.mp3",
    "Audio/OUTRO/THATSBEAUTY.mp3",
    "Audio/OUTRO/THATSMORELIKEIT.mp3",
    "Audio/OUTRO/THATSRIGHTBABY.mp3",
    "Audio/OUTRO/UNFORGIVEN.mp3",
    "Audio/OUTRO/DAISY.mp3",
] 
# Weights to determine how likely an outro is
weights_out = [1, 0.8, 0.2, 0.3, 0.5, 0.8, 0.8, 0.1, 0.6]

# Options for the coach! math command
COACH_MATH = [
    "multiplication",
    "division",
    "addition"
    "subtraction",
    "ancient mystic formula",
]


# Helper funcction to play an audio file then wait till it's done
async def play_audio(voice_client, file_path):
    finished = asyncio.Event()
    loop = asyncio.get_running_loop()

    def after_play(error):
        #finished.set()
        loop.call_soon_threadsafe(finished.set)

    voice_client.play(discord.FFmpegPCMAudio(file_path), after=after_play)
    await finished.wait()

def get_channel_with_users(guild):
    for channel in guild.voice_channels:
        # Only join if 2 thugs are chillin out in the call
        real_members = [m for m in channel.members if not m.bot]
        if len(real_members) >=2:
            return channel
    return None

# Starts the loop. 
@bot.command()
async def calisthenics(ctx):
    if ctx.guild.id in running_tasks and not running_tasks[ctx.guild.id].done():
        await ctx.send("You kids sure do love your neck calisthenics. Give your coach a good 45, then we'll see who's tough... enough!")
        return
    task = bot.loop.create_task(run_sequence(ctx.guild))
    running_tasks[ctx.guild.id] = task
    await ctx.send(f"Get ready, cuz it ain't gonna be easy.")
    
# Allows coach to join every once in a while. (30m - 1h45m)
async def run_sequence(guild):
    while True:
        # Randomly decide how long to wait, ranges from 45m to 6h
        wait_time = random.randint(3600, 21600) # (3600, 21600)
        await asyncio.sleep(wait_time)

        channel = get_channel_with_users(guild)
        if not channel:
            continue # Try again if connection failed
        # Connect 
        try:
            voice = await channel.connect()
        except discord.ClientException:
            # If bot is already connected
            voice = discord.utils.get(bot.voice_clients, guild=guild)

        # Calisthenics sequence

        try: 

            for file in COACH_START:
                await play_audio(voice, file)

            file in COACH_INTRO
            file = random.choice(COACH_INTRO)
            await play_audio(voice, file)

            for _ in range(3):
                sequence = random.sample(COACH_COMMANDS, len(COACH_COMMANDS))
                for file in sequence:
                    await play_audio(voice, file)

            for file in DOWN_RELAX:
                await play_audio(voice, file)

            # 30% Chance for Coach T. to pick up the pace  
            if random.random() < 0.30:
                for file in COACH_PUTP:
                    await play_audio(voice, file)

                last_file = None
                for _ in range(3):
                    sequence = random.sample(COACH_FCOMMANDS, len(COACH_FCOMMANDS))
                    if last_file and sequence[0] == last_file:
                        # Swap first and another random audio file to avoid repeat
                        swap_idx = random.randint(1, len(sequence)-1)
                        sequence[0], sequence[swap_idx] = sequence[swap_idx], sequence[0]
                    for file in sequence:
                        await play_audio(voice, file)
                    last_file = sequence[-1]

                for file in DOWN_RELAX:
                    await play_audio(voice, file)

            file in COACH_OUTRO
            file = random.choices(COACH_OUTRO, weights=weights_out, k=1)[0]
            await play_audio(voice, file)

        finally:

            while voice.is_playing():
                await asyncio.sleep(1)
            await asyncio.sleep(1.5)
            await voice.disconnect()

# relax command, stops the loop
@bot.command()
async def relax(ctx):
    task = running_tasks.get(ctx.guild.id)
    if task and not task.done():
        task.cancel()
        await ctx.send("We'll do calisthenics some other time then...")
    else:
        await ctx.send("I ain't even in there.")

# guard command, sends image of coach guarding bank viw imgchest.
# has <1% chance to show his BCC 
@bot.command()
async def guard(ctx):
    bank = random.choices(COACH_GUARD, weights=weights_guard, k=1)[0]
    await ctx.send(bank)

# flip command, decides on a 50/50 chance if something is "Tough enough" or "pitiful"
@bot.command()
async def flip(ctx):
    responses = [f"Oh, you know that it's tough. Enough!", f"Boy, that's pitiful. Just pitiful."]
    reply = random.choice(responses)
    await ctx.send(reply)

# question command, chooses from a huge list of quotes at random to reply with.
@bot.command()
async def question(ctx):
    # Get all non-bot members
    members = [m for m in ctx.guild.members if not m.bot]
    random_member = random.choice(members)

    responses = [
    f"I don't know about that, son.",
    f"Pitiful. That's just pitiful.",
    f"You sound like you're from Northern Southwest Eastern High. Stop talking.",
    f"Sounds like you ain't tough. Enough.",
    f"I oughta snap your thin lil' chicken neck for that.",
    f"Not by the hair on my big, bulgin' chest.",
    f"That's YOUR fault.",
    f"Some are wise. Most, are otherwise.",
    f"I feel so bad for you right now, you can call me fluffy. I wouldn't even care.",
    f"You know what son, that's so elite, it's e-lite.",
    f"That's what I'm talkin' about!",
    f"That is frivolosly unnecessary.",
    f"It's tough bein' tough.",
    f"You should probably kill yourself.",
    f"I'd rather tend to the grass on my football field",
    f"You know how I got this big, son? Neck calisthenics.",
    f"Relax.",
    f"You wanna be the best? Then don't mess. With the chest.",
    f"Nice. Very nice.",
    f"Who even says nook and cranny anymore? I don't even know what a cranny is.",
    f"That's enough to bring a tear to your eye...",
    f"You there, {random_member.mention}, why aren't you doing your neck calisthenics?",
    f"You gotta have have calves the size of cantalopes... or honeydew...",
    f"You gotta have a chest so big, no one can get within 5 feet of ya!",
    f"You need to have a personal relationship with Jesus Christ.",
    f"You kids sure do know your bible stories.",
    f"...Super.",
    ]
    reply = random.choice(responses)
    await ctx.send(reply)

# math command, will take 2 numbers from the command author and make random calculations
# @bot.command()
# async def math(ctx):
#    await ctx.send(f"What kinda math problem we talkin' about?")
#    
#    # checks for text in the command authors message, and filters key words
#    def check(m):
#        return (
#            m.author == ctx.author and 
#            m.channel == ctx.channel
#            any(word in m.content.lower() and for word in COACH_MATH)
#         )
#    try:
#        msg = await bot.wait_for('message', check=check, timeout=30.0)
#    except asyncio.TimeoutError:
#        await ctx.send("You took to long. Now yo coach is gone. That's what happens.")
#        return
#    
#    content_lower = msg.content_lower()
#    found_keywords = [(kw, content_lower.find(kw)) for kw in COACH_MATH if kw in content_lower]
#    # filter out keywords that weren't found
#    found_keywords = [item for item in found_keywords if item[1] != -1]
#    if found_keywords:
#        # pick first keyword in message if someone sends multiple like a retard
#        first_keyword = sorted(fount_keywords, key=lambda x: x[1])[0][0]
#        response = COACH_MATH[first_keyword]
#        await ctx.send(response)
#   else:
#       await ctx.send("I don't even know what {msg.content} is.")


bot.run(TOKEN)
