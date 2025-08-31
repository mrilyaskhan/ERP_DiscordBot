import os
import discord
import aiohttp
import random
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")  # Keep this for potential future use

# --- Bot setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# Create a session for async HTTP requests
async def create_session():
    return aiohttp.ClientSession()


# Initialize session when bot starts
@bot.event
async def on_ready():
    bot.session = await create_session()
    print(f"✅ {bot.user} is online!")
    await bot.change_presence(activity=discord.Game(name="Chat with me!"))


# --- Free AI Chat API using Hugging Face Inference API ---
async def free_ai_chat(prompt):
    """
    Use Hugging Face's free inference API with a reliable model
    """
    try:
        # Using a more reliable and faster model
        API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"

        headers = {
            "Authorization": f"Bearer {HF_API_KEY}" if HF_API_KEY and HF_API_KEY != "your_hugging_face_api_key_here" else None
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 100,
                "temperature": 0.7,
                "do_sample": True,
                "top_p": 0.9,
            }
        }

        async with bot.session.post(API_URL, headers=headers, json=payload, timeout=8) as response:
            if response.status == 200:
                data = await response.json()

                # Handle response format
                if isinstance(data, list) and len(data) > 0:
                    if "generated_text" in data[0]:
                        generated_text = data[0]["generated_text"]
                        # Clean up the response
                        if generated_text.startswith(prompt):
                            generated_text = generated_text[len(prompt):].strip()
                        return generated_text if generated_text else get_smart_response(prompt)

                elif isinstance(data, dict):
                    if "generated_text" in data:
                        generated_text = data["generated_text"]
                        if generated_text.startswith(prompt):
                            generated_text = generated_text[len(prompt):].strip()
                        return generated_text if generated_text else get_smart_response(prompt)

                return get_smart_response(prompt)

            else:
                return get_smart_response(prompt)

    except (asyncio.TimeoutError, aiohttp.ClientError):
        return get_smart_response(prompt)
    except Exception as e:
        return get_smart_response(prompt)


# --- Smart response system ---
def get_smart_response(prompt):
    """
    Generate intelligent responses based on the input
    """
    prompt_lower = prompt.lower()

    # Greetings
    if any(word in prompt_lower for word in ["hello", "hi", "hey", "greetings", "hola"]):
        return random.choice([
            "Hello there! 👋 How can I help you today?",
            "Hi! 😊 Nice to chat with you!",
            "Hey! What's on your mind?",
            "Greetings! How can I assist you?"
        ])

    # How are you
    elif any(word in prompt_lower for word in ["how are you", "how do you feel", "how's it going"]):
        return random.choice([
            "I'm doing great, thanks for asking! How about you?",
            "I'm functioning well! Always ready to chat. How are you doing?",
            "I'm good! What about you?",
            "All systems operational! How are you today?"
        ])

    # Python related
    elif any(word in prompt_lower for word in ["python", "programming", "code", "developer"]):
        return random.choice([
            "Yes! I know Python. I was created using Python and discord.py!",
            "Python is awesome! It's one of the best programming languages.",
            "I love Python! It's great for building bots like me.",
            "Python programming? That's my foundation! 🐍"
        ])

    # Name questions
    elif any(word in prompt_lower for word in ["your name", "who are you", "what are you"]):
        return random.choice([
            "I'm SuperBot, your friendly AI assistant! 🤖",
            "I'm SuperBot! Here to chat and help with anything.",
            "You can call me SuperBot! I'm an AI chatbot.",
            "I'm SuperBot, created to be your conversational partner!"
        ])

    # Thanks
    elif any(word in prompt_lower for word in ["thank", "thanks", "appreciate"]):
        return random.choice([
            "You're welcome! 😊",
            "Happy to help!",
            "Anytime! That's what I'm here for.",
            "No problem! Feel free to ask anything else."
        ])

    # Questions about capabilities
    elif any(word in prompt_lower for word in ["what can you do", "help me", "abilities"]):
        return random.choice([
            "I can chat with you, answer questions, tell jokes, and more! Try asking me anything.",
            "I'm here to have conversations, help with information, and be your friendly AI companion!",
            "I can discuss various topics, tell quotes, roll dice, and have meaningful conversations!",
            "I'm designed to be conversational! Ask me about anything and I'll do my best to respond."
        ])

    # Jokes
    elif any(word in prompt_lower for word in ["joke", "funny", "laugh"]):
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "What do you call a fake noodle? An impasta!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a bear with no teeth? A gummy bear!"
        ]
        return random.choice(jokes)

    # Default intelligent responses
    else:
        responses = [
            "That's interesting! Tell me more about that.",
            "I appreciate you sharing that with me. What else would you like to talk about?",
            "That's a good point! I'm always learning from our conversations.",
            "Thanks for the message! I'm here to chat about anything you'd like.",
            "I'm listening! What's on your mind?",
            "That's worth discussing! I'm designed to understand various topics.",
            "I'm glad we're having this conversation. What would you like to know?",
            "Interesting perspective! I'm here to engage in meaningful dialogue.",
            "I appreciate your input. Let's continue our conversation!",
            "That's a great topic! I'm always ready to learn and discuss new things."
        ]
        return random.choice(responses)


# --- Events ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Process commands first
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    # Don't respond to very short messages
    if len(message.content.strip()) < 2:
        return

    # Respond to regular messages
    async with message.channel.typing():
        try:
            # Use the free AI chat function
            reply = await free_ai_chat(message.content)
            await message.reply(reply)
        except Exception as e:
            # Fallback to smart response if anything goes wrong
            reply = get_smart_response(message.content)
            await message.reply(reply)


# --- Commands ---
@bot.command(name="hi", help="Greet the bot")
async def hi(ctx):
    await ctx.send(f"Hello {ctx.author.mention}! 👋 How can I help you today?")


@bot.command(name="ping", help="Check bot latency")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: {latency} ms")


@bot.command(name="ask", help="Ask the AI a question")
async def ask(ctx, *, question):
    if not question:
        await ctx.send("Please provide a question. Example: `!ask What is AI?`")
        return

    async with ctx.typing():
        try:
            reply = await free_ai_chat(question)
            await ctx.send(reply)
        except Exception as e:
            reply = get_smart_response(question)
            await ctx.send(reply)


@bot.command(name="dice", help="Roll a dice")
async def dice(ctx, sides: int = 6):
    if sides < 2:
        await ctx.send("Dice must have at least 2 sides!")
        return

    roll = random.randint(1, sides)
    await ctx.send(f"🎲 You rolled a {roll} (1-{sides})")


@bot.command(name="quote", help="Get a random inspirational quote")
async def quote(ctx):
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
        "The way to get started is to quit talking and begin doing. - Walt Disney",
        "Life is what happens when you're busy making other plans. - John Lennon",
        "The purpose of our lives is to be happy. - Dalai Lama",
        "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
        "Believe you can and you're halfway there. - Theodore Roosevelt"
    ]
    await ctx.send(random.choice(quotes))


@bot.command(name="helpme", help="Show all available commands")
async def helpme(ctx):
    embed = discord.Embed(
        title="SuperBot Help 🚀",
        description="Here are all the commands you can use:",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🤖 AI Commands",
        value="• `!ask [question]` - Ask me anything\n• Just chat normally - I'll respond!",
        inline=False
    )

    embed.add_field(
        name="🎲 Fun Commands",
        value="• `!hi` - Greet me\n• `!dice [sides]` - Roll a dice\n• `!quote` - Get inspiration",
        inline=False
    )

    embed.add_field(
        name="🔧 Utility Commands",
        value="• `!ping` - Check my speed\n• `!helpme` - Show this help",
        inline=False
    )

    embed.set_footer(text="SuperBot - Your friendly AI assistant • Just start chatting!")

    await ctx.send(embed=embed)


# --- Error handling ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Sorry, I don't recognize that command. Type `!helpme` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You're missing some arguments. Type `!helpme` for more information.")
    else:
        await ctx.send("An error occurred. Please try again!")


# --- Cleanup ---
@bot.event
async def on_disconnect():
    if hasattr(bot, 'session'):
        await bot.session.close()


# --- Run bot ---
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ ERROR: Discord token not found. Please check your .env file.")
    else:
        bot.run(DISCORD_TOKEN)