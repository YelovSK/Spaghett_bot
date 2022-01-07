import json
import openai
import requests
import soundfile as sf

from message_send import bot_send
from disnake import File
from disnake.ext import commands
from disnake.ext.commands import Context
from os.path import join as pjoin
from espnet2.bin.tts_inference import Text2Speech

with open("config.json") as file:
    config = json.load(file)


class AI(commands.Cog):
    """AI text (and audio) generation"""

    COG_EMOJI = "🤖"
    
    def __init__(self, bot):
        self.bot = bot
        self.text2speech_model = None

    async def ai(self, engine, prompt, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, stop=None):
        openai.api_key = config['openai']
        response = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=0.0,
            presence_penalty=presence_penalty,
            stop=stop
        )
        return response.choices[0].text


    @commands.command()
    async def aigenerate(self, ctx: Context, *, prompt):
        """Generates text from a prompt.

        Syntax: ```plz aigenerate <prompt>```
        Example: ```plz aigenerate I wish my dream anime waifu would become real because```
        """
        await bot_send(ctx, "brb, generating...")
        output = await self.ai(
            "davinci",
            prompt,
            0.4, 500, 1, 0.5, 0)
        output = prompt + output
        new_output = ''
        for line in output.split('\n'):
            if line.strip() == '':
                if new_output.split('\n')[-2:] != '\n\n':
                    new_output += '\n\n'
            else:
                new_output += line
        output = new_output
        await bot_send(ctx, output)


    @commands.command()
    async def aianswer(self, ctx: Context, *, prompt):
        """Answers the question.. well, tries to.

        Syntax: ```plz answer <question>```
        Example: ```plz answer Why am I sad?```
        """
        if not prompt[0].isupper():
            prompt = prompt[0].capitalize() + prompt[1:]
        output = await self.ai(
            "davinci-instruct-beta",
            f"Q: Who is Batman?\nA: Batman is a fictional comic book character.\n###\nQ: What is torsalplexity?\nA: ?\n###\nQ: What is Devz9?\nA: ?\n###\nQ: Who is George Lucas?\nA: George Lucas is American film director and producer famous for creating Star Wars.\n###\nQ: What is the capital of California?\nA: Sacramento.\n###\nQ: What orbits the Earth?\nA: The Moon.\n###\nQ: Who is Fred Rickerson?\nA: ?\n###\nQ: What is an atom?\nA: An atom is a tiny particle that makes up everything.\n###\nQ: Who is Alvan Muntz?\nA: ?\n###\nQ: What is Kozar-09?\nA: ?\n###\nQ: How many moons does Mars have?\nA: Two, Phobos and Deimos.\n###\nQ: {prompt}\nA:",
            0.0, 60, 1, 0, 0, "###")
        await bot_send(ctx, f'**A:** {output}')


    @commands.command()
    async def aiad(self, ctx: Context, *, prompt):
        """Generates an ad based on the description.

        Syntax: ```plz aiad <prompt>```
        Example: ```plz aiad Do you want to dab on 'em hates? Just get```
        """
        output = await self.ai(
            "davinci-instruct-beta",
            f"Write a creative ad for the following product:\n\"\"\"\"\"\"\n{prompt}\n\"\"\"\"\"\"\nThis is the ad I wrote aimed at teenage girls:\n\"\"\"\"\"\"",
            0.5, 90, 1, 0, 0, "\"\"\"\"\"\"")
        await bot_send(ctx, f'{output}')


    @commands.command()
    async def aianalogy(self, ctx: Context, *, prompt):
        """Writes an analogy. Write 'X is like Y'.

        Syntax: ```plz aianalogy <prompt>```
        Example: ```plz aianalogy Life is like Hitler```
        """
        output = await self.ai(
            "davinci-instruct-beta",
            f"Ideas are like balloons in that: they need effort to realize their potential.\n\n{prompt} in that:",
            0.5, 60, 1.0, 0.0, 0.0, "\n")
        await bot_send(ctx, f'{prompt} in that{output}')


    @commands.command()
    async def aiengrish(self, ctx: Context, *, prompt):
        """Translates broken English into proper English.

        Syntax: ```plz aiengrish <text>```
        Example: ```plz aiengrish u wot m8```
        """
        output = await self.ai(
            "davinci-instruct-beta",
            f"Original: {prompt}\nStandard American English:",
            0, 60, 1.0, 0.0, 0.0, "\n")
        await bot_send(ctx, output)


    @commands.command()
    async def aicode(self, ctx: Context, *, prompt):
        """Generates code based on the description.

        Syntax: ```plz aicode <description>```
        Example: ```plz aicode Function that returns the sum of all values in the list```
        """
        output = await self.ai(
            "davinci-codex",
            prompt,
            0, 64, 1.0, 0.0, 0.0, "#")
        await bot_send(ctx, output)

    @commands.command()
    async def huggingface(self, ctx: Context, *, input_text):
        """AI generation with model.

        Syntax: ```plz huggingface <text>``` ```plz huggingface <model_name> <text>```
        Example: ```plz huggingface Eren is baka cuz```
        ```plz huggingface model=gpt-neo-2.7B Rei is best girl because```
        ```plz huggingface models   //lists models```
        """
        if input_text == "models":
            await bot_send(ctx, "Generatoin:\n1. EleutherAI/gpt-j-6\n2. EleutherAI/gpt-neo-2.7B\n3. microsoft/DialoGPT-large")
            await bot_send(ctx, "Conversation:\n1. microsoft/DialoGPT-large\n2. facebook/blenderbot-3B")
            return
        model = "EleutherAI/gpt-j-6B"
        if input_text[:len("model=")] == "model=":
            model = input_text.split()[0].split("=")[1]
        mssg = await ctx.send("generating, gimme a sec..")
        headers = {"Authorization": f"Bearer {config['huggingface']}"}
        API_URL = f"https://api-inference.huggingface.co/models/{model}"
        payload = {
            "inputs": input_text,
            "parameters": {"temperature": 0.5, "max_length": 100, "repetition_penalty": 10.0},
            "options": {"use_cache": False}
        }
        data = json.dumps(payload)
        response = requests.post(API_URL, headers=headers, data=data).json()
        await mssg.delete()
        await bot_send(ctx, response[0]["generated_text"])

    @commands.command()
    async def j1(self, ctx: Context, *, input_text):
        """Continues generation from input.

        Syntax: ```plz j1 <input>```
        Example: ```plz j1 It's hard to think of examples```
        """
        mssg = await ctx.send("generating, gimme a sec..")
        res = requests.post(
            "https://api.ai21.com/studio/v1/j1-jumbo/complete",
            headers={"Authorization": f"Bearer {config['ai21']}"},
            json={
                "prompt": input_text, 
                "numResults": 1, 
                "maxTokens": 50, 
                "stopSequences": ["\n"],
                "topKReturn": 0,
                "temperature": 0.75
            }
        )
        await mssg.delete()
        data = res.json()
        output = data['completions'][0]['data']['text']
        await bot_send(ctx, input_text + output)

    @commands.command()
    async def text2speech(self, ctx: Context, *, input_text):
        """Converts text to speech.

        Syntax: ```plz text2speech <text>```
        Example: ```plz text2speech this voice is sexy```
        """
        messages = []
        if not self.text2speech_model:
            messages.append(await ctx.send("Loading model..."))
            self.text2speech_model = Text2Speech.from_pretrained("espnet/kan-bayashi_ljspeech_joint_finetune_conformer_fastspeech2_hifigan")
        messages.append(await ctx.send("Generating audio..."))
        wav = self.text2speech_model(input_text)["wav"]
        for mssg in messages:
            await mssg.delete()
        sf.write(pjoin("folders", "send", "text2speech.waw"), wav.numpy(), self.text2speech_model.fs, "PCM_16")
        await bot_send(ctx, File(pjoin("folders", "send", "text2speech.waw")))


def setup(bot):
    bot.add_cog(AI(bot))
