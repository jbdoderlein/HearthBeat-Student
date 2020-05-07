import datetime

import discord
from discord.ext import commands
import motor.motor_asyncio
import asyncio

class HearthBeat(commands.Cog):
    def __init__(self, bot, host, username, password):
        self.bot = bot
        if username is not None:
            client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://{username}:{password}@{host}".format(
                username=username,
                password=password,
                host=host
            ))
            self.db = client.hearthbeat
        else:
            client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://{host}".format(
                host=host
            ))
            self.db = client.hearthbeat


    @commands.command(pass_context=True, no_pm=True, hidden=True)
    async def appel(self, ctx):
        """Fait l'appel"""
        if ctx.author.voice is not None:
            voice_channel = ctx.author.voice.channel
            print(voice_channel.members)
            appel = {
                'date': datetime.datetime.now(),
                'present': [member.id for member in voice_channel.members],
                'channel': voice_channel.name,
            }
            result = await self.db.appels.insert_one(appel)
            await ctx.send(f"Ajout de l'appel à la base de données, `{len(appel['present'])}` participants le `{appel['date']}` dans `{appel['channel']}`")
        else:
            await ctx.send("Il faut se connecter à un vocal")

    @commands.command(pass_context=True, no_pm=True, hidden=True)
    async def info(self, ctx, *, member: discord.Member):
        """Affiche les infos a propos d'un utilisateur"""
        embed = discord.Embed(
            type="rich",
            color=discord.Colour.blue(),
        )
        embed.set_author(
            name='Hearth Beat',
            icon_url="https://cdn.iconscout.com/icon/free/png-256/student-classroom-bench-tired-bore-rest-resting-46451.png"
        )
        if member.nick is None:
            embed.title = f"Appel de {member.name}"
        else:
            embed.title = f"Appel de {member.nick}"

        list_appel = []
        type_appel = {}
        async for document in self.db.appels.find({}):
            if document['channel'] not in type_appel:
                type_appel[document['channel']] = [0, 0]
            type_appel[document['channel']][1] += 1
            if member.id in document['present']:
                list_appel.append(f"Cours le {document['date'].day}/{document['date'].month} dans {document['channel']}")
                type_appel[document['channel']][0] += 1

        embed.add_field(name="Nombre de cours", value=str(len(list_appel)))
        embed.add_field(name="Liste des cours : ", value="`"+"\n".join(list_appel)+"`")

        type_str = "`"+"\n".join([f"{a} : {i[0]}/{i[1]}" for a, i in type_appel.items()])+"`"
        embed.add_field(name="Moyenne sur les cours : ", value=type_str)

        await ctx.send(embed=embed)