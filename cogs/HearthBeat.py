import datetime
import imgkit
import discord
from discord.ext import commands, tasks
import motor.motor_asyncio
import asyncio
import typing
import bson

HTML_TEMPLATE = """
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<link href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css" rel="stylesheet" />
<link href="https://cdnjs.cloudflare.com/ajax/libs/material-design-icons/3.0.1/iconfont/material-icons.min.css" rel="stylesheet" />
<table class="striped">
        <thead>
          <tr>
              <th>Nom/Prénom</th>
              {head}
          </tr>
        </thead>

        <tbody>
             {body}     
        </tbody>
      </table>"""


def is_admin():
    async def predicate(ctx):
        return bool((int(ctx.author.permissions) >> 3) & 1)

    return commands.check(predicate)


class HearthBeat(commands.Cog):
    def __init__(self, bot, host, username, password):
        self.bot = bot
        self.host = host
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

        self.screenchecker.start()

    @commands.command(pass_context=True, no_pm=True)
    async def appel(self, ctx, *, name: str):
        """Fait l'appel, syntaxe : `?appel *matiere*`"""
        if ctx.author.voice is not None:
            voice_channel = ctx.author.voice.channel
            print(voice_channel.members)
            appel = {
                'name': name,
                'date': datetime.datetime.now(),
                'present': [member.id for member in voice_channel.members],
                'channel': voice_channel.name,
                'guild': str(ctx.guild.id)
            }
            result = await self.db.appels.insert_one(appel)
            await ctx.send(
                f"Ajout de l'appel à la base de données, `{len(appel['present'])}` participants le `{appel['date']}` dans `{appel['channel']}`")
        else:
            await ctx.send("Il faut se connecter à un vocal")

    @commands.command(pass_context=True, no_pm=True)
    async def info(self, ctx, *, member: discord.Member):
        """Affiche les infos a propos d'un eleve"""
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
        async for document in self.db.appels.find({'guild': str(ctx.guild.id)}):

            if document['name'] not in type_appel:
                type_appel[document['name']] = [0, 0]
            type_appel[document['name']][1] += 1
            if member.id in document['present']:
                list_appel.append(
                    f"{document['name']} le {document['date'].day}/{document['date'].month} dans {document['channel']}")
                type_appel[document['name']][0] += 1

        embed.add_field(name="Nombre de cours", value=str(len(list_appel)))
        embed.add_field(name="Liste des cours : ", value="`" + "\n".join(list_appel) + "`")

        type_str = "`" + "\n".join([f"{a} : {i[0]}/{i[1]}" for a, i in type_appel.items()]) + "`"
        embed.add_field(name="Moyenne sur les cours : ", value=type_str)

        await ctx.send(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    async def classe(self, ctx, role: discord.Role, *, matiere: typing.Optional[str] = 'All'):
        """Affiche un tableau avec les présence"""
        msg = await ctx.send(":gear: Start to process data :floppy_disk:")
        appel_dic = {}  # Dico avec les appels, et les présents
        eleve_dic = {}  # dico index sur le nom pour le tri alphabétique qui contient l'id
        async for document in self.db.appels.find({'guild': str(ctx.guild.id)}):  # Pour tous les appels
            if matiere == "All" or document['name'] in matiere.split(" "):
                date = document['date']  # date du cours
                appel_dic[f"{document['name']} du {date.day}/{date.month}, {date.hour}:{date.minute}"] = document[
                    'present']
                # Ajout avec comme index le str d affichage et en value la liste des présents

        for member in role.members:  # Pour chaque eleve avec le role
            if member.nick is None:  # Si il n  pas de surnom pour le serv
                name = member.name
            else:
                name = member.nick
            if len(name.split(" ")) == 2:
                name = " ".join(name.split(" ")[::-1])
            eleve_dic[name] = member.id  # le nom de l'eleve en key pour le tri et son id en value

        head_str = "".join([f"<th>{appel}</th>" for appel in appel_dic.keys()])  # tete du tableau
        body_str = ""
        for nom in sorted(eleve_dic):
            elv_id = eleve_dic[nom]  # on prend l'id de l eleve
            base = f"<tr><td>{nom}</td>"  # premiere colonne nom
            for cours, present in appel_dic.items():
                if elv_id in present:  # Il est present
                    base += """
                    <td class="center">
                        <i class="material-icons green-text">check_box</i>
                    </td>
                    """
                else:  # Il n'est pas present
                    base += """
                    <td class="center">
                        <i class="material-icons red-text">indeterminate_check_box</i>
                    </td>
                """
            body_str += base + "</tr>"  # on ferme les balises
        await msg.edit(content=":gear: Generate HTML :page_with_curl:")
        if self.host == "localhost":
            imgkit.from_string(HTML_TEMPLATE.format(head=head_str, body=body_str), 'classe.jpg',
                               options={"xvfb": "", "zoom": 2.4})
        else:
            imgkit.from_string(HTML_TEMPLATE.format(head=head_str, body=body_str), 'classe.jpg', options={"zoom": 2.4})
        await msg.edit(content=":gear:Send Image :arrow_up:")
        with open('classe.jpg', 'rb') as f:
            picture = discord.File(f)
            await ctx.send(file=picture)
        await msg.delete()

    @commands.command(pass_context=True, no_pm=True, hidden=True)
    async def screen(self, ctx, duration: int, *, name: str):
        await ctx.send(f"Start {name} screenshot recording session in `{ctx.channel.name}` for `{duration}` minutes")
        self.bot.screenshot['channel'] = ctx.channel.id
        self.bot.screenshot['duration'] = duration
        self.bot.screenshot['start_time'] = datetime.datetime.now()
        self.bot.screenshot['label'] = name
        self.bot.screenshot['ctx'] = ctx

    @tasks.loop(seconds=10.0)
    async def screenchecker(self):
        if self.bot.screenshot['channel'] is not None:
            if not self.bot.screenshot['start_time'].timestamp() + 60 * self.bot.screenshot['duration'] > datetime.datetime.now().timestamp():
                await self.bot.screenshot['ctx'].send("La session a pris fin")
                self.bot.screenshot = {
                    'channel': None,
                    'start_time': None,
                    'duration': None,
                    'label': "Maths"
                }
