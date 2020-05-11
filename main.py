import asyncio
import discord
from discord.ext import commands
from cogs.HearthBeat import HearthBeat
import argparse
import logging
import imgkit

logging.basicConfig(filename='example.log', level=logging.DEBUG)

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

    logging.debug("#"*16)
    try:
        imgkit.from_string("Salut", 'test.jpg')
        with open('test.jpg', 'rb') as f:
            picture = discord.File(f)
        logging.debug("SUCCESS FILE OPEN WITH ALL WE NEED")
    except Exception as e:
        logging.debug(e)


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
