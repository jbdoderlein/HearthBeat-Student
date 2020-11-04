import discord
from discord.ext import commands
from cogs.HearthBeat import HearthBeat
import argparse
from aiohttp import web
from urllib.parse import unquote
import humanize
humanize.i18n.activate("fr_FR")


ap = argparse.ArgumentParser()
ap.add_argument("-t", "--token", required=True, help="Bot token")
ap.add_argument("-dbh", "--dbhost", type=str, default="localhost", help="Postgres hostname")
ap.add_argument("-dbd", "--dbdatabase", type=str, default=None, help="Postgres database")
ap.add_argument("-dbu", "--dbuser", type=str, default=None, help="Postgres username")
ap.add_argument("-dbp", "--dbpassword", type=str, default=None, help="Postgres password")
ap.add_argument("-adm", "--admin", nargs='+', type=int, default=[177375818635280384], help='Admin discord id list')

args = vars(ap.parse_args())

def is_dev():
    async def predicate(ctx):
        return ctx.author.id in args['admin']

    return commands.check(predicate)


description = '''Hearth Beat Student'''
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True
bot = commands.Bot(command_prefix='?', description=description, intents=intents)

bot.add_cog(HearthBeat(bot, host=args['dbhost'], database=args['dbdatabase'], username=args['dbuser'], password=args['dbpassword']))

@bot.event
async def on_ready():
    await bot.cogs['HearthBeat'].init()
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    activity = discord.Activity(name="classroom",
                                type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)

@bot.event
async def on_command_error(ctx, error):
    message = ""
    if isinstance(error, commands.BotMissingPermissions):
        message = "Bot need more permissions"
    elif isinstance(error, commands.BadArgument):
        message = "Bad argument"
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
        a = eval(ctx.message.content.replace('?eval ', ''))
        await ctx.send('Input : `' + ev + '`\nOutput : `' + str(a) + '`')
    except Exception as e:
        await ctx.send('Input : `' + ev + '`\nOutput (error) : `' + str(e) + '`')

@bot.command(hidden=True, aliases=['sht'])
@is_dev()
async def shutdown(ctx):
    """shutdown"""
    await bot.close()



async def web_service():
    routes = web.RouteTableDef()

    @routes.get('/')
    async def hello(request):
        return web.Response(text="hello ")

    @routes.get('/user/{guild}/{user}')
    async def get_user(request):
        #Trouver le memebre et les info discord
        guild_id = unquote(request.match_info['guild'])
        user_id = unquote(request.match_info['user'])
        guild = bot.get_guild(int(guild_id))
        if not guild: return web.Response(text="No guild")
        member = guild.get_member(int(user_id))
        if not member: return web.Response(text="No member")
        # Avoir les info hearthbeat
        data = await bot.cogs['HearthBeat'].get_info(guild_id, user_id)
        # Return
        return web.json_response({
            'name': member.name,
            'nick': member.nick,
            'avatar': member.avatar,
            'data': data
        })

    @routes.get('/users/{guild}')
    async def get_users(request):
        # Trouver le memebre et les info discord
        guild_id = unquote(request.match_info['guild'])
        guild = bot.get_guild(int(guild_id))
        if not guild: return web.Response(text="No guild")
        members = guild.members
        if not members: return web.Response(text="No members")
        # Avoir les info hearthbeat
        return web.json_response({member.id: {'name': member.name, 'avatar': member.avatar} for member in members})

    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host='127.0.0.1', port=8887, reuse_address=True)
    print("Starting http server port : ", 8887)
    await site.start()


try:
    bot.loop.create_task(web_service())
    pass
except Exception as e:
    print(e)

bot.run(args['token'])
