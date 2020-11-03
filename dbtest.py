import asyncio
import asyncpg
import json
import humanize
humanize.i18n.activate("fr_FR")


async def run():
    print("start")
    conn = await asyncpg.connect(user='postgres', password='root',
                                 database='heathbeat', host='localhost')
    guild = 687745167351873546
    user = 177375818635280384
    appels = await conn.fetch('SELECT * FROM appel WHERE guild=$1', str(guild))
    data = {}
    for appel in appels:
        if not appel['name'] in data:
            data[appel['name']] = {'total': 0, 'present': []}
        data[appel['name']]['total'] += 1
        if user in json.loads(appel['present']):
            data[appel['name']]['present'].append(f"{appel['name']}, {humanize.naturaldate(appel['date'])} dans {appel['channel']}")
    print(data)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())