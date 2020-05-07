from discord.ext import command

class HearthBeat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True, hidden=True)
    async def startcourse(self, ctx):
        """Convert your message in morse ! """
        try:
            final = ""
            nolo = list(message.upper())
            for letter in nolo:
                lili = morseAlphabet[letter]
                final = final + lili + "  "
            await ctx.send("```" + final + "```")

        except:
            await ctx.send(ctx.message.channel, sys.exc_info()[1])