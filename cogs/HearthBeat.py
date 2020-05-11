import datetime

import discord
from discord.ext import commands
import motor.motor_asyncio
import asyncio

def is_admin():
    async def predicate(ctx):
        return bool((int(ctx.author.permissions) >> 3) & 1)

    return commands.check(predicate)

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
            name='Heart Beat',
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

    @commands.command(pass_context=True, no_pm=True, hidden=True)
    async def classe(self, ctx, *, role: discord.Role):
        membres_classe = [r.id for r in role.members]
        stat_membre = {}
        global_cour = {}
        async for document in self.db.appels.find({}): # Pour tous les appels
            if document['channel'] not in global_cour:
                global_cour[document['channel']] = 0
            global_cour[document['channel']] += 1
            for member in document['present']: # pour chaque membre présent
                if member in membres_classe:
                    if member not in stat_membre: # Si o na pas register le membre
                        stat_membre[member] = {}
                        discord_member = discord.utils.get(ctx.guild.members, id=member)
                        if discord_member.nick is None:
                            stat_membre[member]['name'] = discord_member.name
                        else:
                            stat_membre[member]['name'] = discord_member.nick

                    if document['channel'] not in stat_membre[member]:
                        stat_membre[member][document['channel']] = 0
                    stat_membre[member][document['channel']] += 1
        print(stat_membre)

        await ctx.send("Nombre de cours : "+str(" ".join([f"{i} : {d}" for i,d in global_cour.items()])))
        stat_str = "\n".join([f"{eleve['name']} :"+", ".join([f"{typ}({eleve.get(typ, 0)}/{ct})" for typ, ct in global_cour.items()]) for idd, eleve in stat_membre.items()])
        i = 0
        while i < len(stat_str):
            embed = discord.Embed(
                type="rich",
                color=discord.Colour.blue(),
            )
            embed.set_author(
                name='Heart Beat',
                icon_url="https://cdn.iconscout.com/icon/free/png-256/student-classroom-bench-tired-bore-rest-resting-46451.png"
            )
            if i+1000 < len(stat_str):
                embed.add_field(name="Stat", value=f"`{stat_str[i:i+1000]}`")
            else:
                embed.add_field(name="Stat", value=f"`{stat_str[i:]}`")
            await ctx.send(embed=embed)
            i += 1000