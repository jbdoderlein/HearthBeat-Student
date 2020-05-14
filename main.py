import asyncio
import discord
from discord.ext import commands
from cogs.HearthBeat import HearthBeat
import argparse


ap = argparse.ArgumentParser()
ap.add_argument("-t", "--token", required=True, help="bot token")
ap.add_argument("-dbh", "--dbhost", type=str, default="localhost", help="Mongod db hostname")
ap.add_argument("-dbu", "--dbuser", type=str, default=None, help="Mongod db username")
ap.add_argument("-dbp", "--dbpassword", type=str, default=None, help="Mongod db password")

args = vars(ap.parse_args())



def is_dev():
    async def predicate(ctx):
        return ctx.author.id == 177375818635280384 or ctx.author.id == 138688645908398080

    return commands.check(predicate)


description = '''Heart Beat'''
bot = commands.Bot(command_prefix='?', description=description)

bot.add_cog(HearthBeat(bot, host=args['dbhost'], username=args['dbuser'], password=args['dbpassword']))


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    activity = discord.Activity(name="la classe",
                                type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)

@bot.event
async def on_command_error(ctx, error):
    message = ""
    if isinstance(error, commands.BotMissingPermissions):
        message = "Bot need more permissions"
    elif isinstance(error, commands.BadArgument):
        message = "Mauvais argument (le role ou l'élève n'existe pas ?)"
    else:
        message = f"Fatal error : `{error}`"
    await ctx.send(message)



@bot.command(hidden=True)
@is_dev()
async def ping(ctx):
    """Return Pong"""
    await ctx.send("Pong !")


@bot.command(hidden=True, name='eval')
@is_dev()
async def _eval(ctx, ev: str):
    """Not for you !"""
    try:
        a = eval(ctx.message.content.replace('!!eval ', ''))
        await ctx.send('Input : `' + ev + '`\nOutput : `' + str(a) + '`')
    except Exception as e:
        await ctx.send('Input : `' + ev + '`\nOutput (error) : `' + str(e) + '`')

@bot.command(hidden=True, aliases=['sht'])
@is_dev()
async def shutdown(ctx):
    """shutdown"""
    await bot.close()

bot.run(args['token'])
