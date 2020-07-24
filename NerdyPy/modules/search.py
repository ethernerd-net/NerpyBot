""" Search Modul """
# -- coding: utf-8 --
import aiohttp
import config
import discord
from datetime import datetime
import utils.format as fmt
from lxml import etree
from utils.errors import NerpyException
from googleapiclient.discovery import build
from discord.ext.commands import Cog, command, group, bot_has_permissions


class Search(Cog):
    """search module"""

    def __init__(self, bot):
        bot.log.info(f"loaded {__name__}")

        self.bot = bot

    @command()
    @bot_has_permissions(send_messages=True)
    async def imgur(self, ctx, *, query):
        """may the meme be with you"""
        url = f"https://api.imgur.com/3/gallery/search/viral?q={query}"

        async with aiohttp.ClientSession(
            headers={"Authorization": f"Client-ID {config.imgur}"}
        ) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    err = f"The api-webserver responded with a code: {response.status} - {response.reason}"
                    raise NerpyException(err)
                data = await response.json()
                if data["success"] is True and len(data["data"]) > 0:
                    meme = data["data"][0]["link"]
                else:
                    meme = "R.I.P. memes"
                await ctx.send(meme)

    @command()
    @bot_has_permissions(send_messages=True)
    async def urban(self, ctx, *, query):
        """urban legend"""
        url = f"http://api.urbandictionary.com/v0/define?term={query}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    err = f"The api-webserver responded with a code: {response.status} - {response.reason}"
                    raise NerpyException(err)
                data = await response.json()
                emb = discord.Embed(title=f'"{query}" on Urban Dictionary:')
                if len(data["list"]) > 0:
                    item = data["list"][0]
                    emb.description = item["definition"]
                    emb.set_author(name=item["author"])
                    emb.url = item["permalink"]
                else:
                    emb.description = "no results - R.I.P. memes"
                await ctx.send(embed=emb)

    @command()
    @bot_has_permissions(send_messages=True)
    async def lyrics(self, ctx, *, query):
        """genius lyrics"""
        url = f"http://api.genius.com/search?q={query}&access_token={config.genius}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    err = f"The api-webserver responded with a code: {response.status} - {response.reason}"
                    raise NerpyException(err)
                data = await response.json()
                emb = discord.Embed(title=f'"{query}" on genius.com:')
                if len(data["response"]["hits"]) > 0:
                    item = data["response"]["hits"][0].get("result")
                    emb.description = item.get("full_title")
                    emb.set_thumbnail(url=item.get("header_image_thumbnail_url"))
                    emb.url = item.get("url")
                else:
                    emb.description = "R.I.P. memes"
                await ctx.send(embed=emb)

    @command()
    @bot_has_permissions(send_messages=True)
    async def youtube(self, ctx, *, query):
        """don't stick too long, you might get lost"""

        youtube = build("youtube", "v3", developerKey=config.ytkey)

        search_response = (
            youtube.search()
            .list(q=query, part="id,snippet", type="video", maxResults=1)
            .execute()
        )

        items = search_response.get("items", [])

        if len(items) > 0:
            msg = f'https://www.youtube.com/watch?v={items[0]["id"]["videoId"]}'
        else:
            msg = "And i thought everything is on youtube :open_mouth:"
        await ctx.send(msg)

    @command()
    @bot_has_permissions(send_messages=True)
    async def anime(self, ctx, *, query):
        """weeb search"""
        url = f"https://myanimelist.net/api/anime/search.xml?q={query}"
        auth = aiohttp.BasicAuth(
            login=config.malusr, password=config.malpwd, encoding="utf-8"
        )

        async with aiohttp.ClientSession(auth=auth) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    err = f"The api-webserver responded with a code: {response.status} - {response.reason}"
                    raise NerpyException(err)
                parser = etree.XMLParser(
                    ns_clean=True,
                    recover=True,
                    remove_blank_text=True,
                    encoding="utf-8",
                )
                raw_xml = await response.text()
                xml = etree.fromstring(raw_xml.encode("utf-8"), parser=parser)

                find_text = etree.XPath("/anime/entry[1]")
                entry = find_text(xml)

                msg = f"*Searchresult for {query}*\n\n"

                msg += f"__**{entry.xpath('//title')}**__\n"
                msg += f"*{entry.xpath('//english')}*\n"
                msg += f"Episodes: {entry.xpath('//episodes')}\n"
                msg += f"Start: {entry.xpath('//start_date')}\n"
                msg += f"End: {entry.xpath('//end_date')}\n"
                msg += f"Rating: {entry.xpath('//score')}\n"
                msg += f"URL: `https://myanimelist.net/anime/{entry.xpath('//id')}`\n\n"

                msg += entry.xpath("//image")

                await ctx.send(msg)

    @group(invoke_without_command=False)
    @bot_has_permissions(send_messages=True)
    async def imdb(self, ctx):
        """open movie database"""
        if ctx.invoked_subcommand is None:
            return

    @imdb.command()
    async def movie(self, ctx, *, query):
        """omdb movie informations"""
        rip, emb = await self.imdb_search("movie", query)
        await ctx.send(content=rip, embed=emb)

    @imdb.command()
    async def series(self, ctx, *, query):
        """omdb series informations"""
        rip, emb = await self.imdb_search("series", query)
        await ctx.send(content=rip, embed=emb)

    @imdb.command()
    async def episode(self, ctx, *, query):
        """omdb episode informations"""
        rip, emb = await self.imdb_search("episode", query)
        await ctx.send(content=rip, embed=emb)

    # noinspection PyMethodMayBeStatic
    async def imdb_search(self, query_type, query: str):
        emb = None
        rip = ""
        search_url = (
            f"http://www.omdbapi.com/?apikey={config.omdb}&type={query_type}&s={query}"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as search_response:
                if search_response.status != 200:
                    err = f"The api-webserver responded with a code:{search_response.status} - {search_response.reason}"
                    raise NerpyException(err)
                search_result = await search_response.json()

                if search_result["Response"] == "True":
                    id_url = (
                        f"http://www.omdbapi.com/?apikey={config.omdb}&i="
                        + search_result["Search"][0]["imdbID"]
                    )

                    async with session.get(id_url) as id_response:
                        if id_response.status != 200:
                            err = f"The api-webserver responded with a code:{id_response.status} - {id_response.reason}"
                            raise NerpyException(err)
                        id_result = await id_response.json()

                        emb = discord.Embed(title=id_result["Title"])
                        emb.description = id_result["Plot"]
                        emb.set_thumbnail(url=id_result["Poster"])
                        emb.add_field(
                            name=fmt.bold("Released"), value=id_result["Released"]
                        )
                        emb.add_field(name=fmt.bold("Genre"), value=id_result["Genre"])
                        emb.add_field(
                            name=fmt.bold("Runtime"), value=id_result["Runtime"]
                        )
                        emb.add_field(
                            name=fmt.bold("Country"), value=id_result["Country"]
                        )
                        emb.add_field(
                            name=fmt.bold("Language"), value=id_result["Language"]
                        )
                        emb.add_field(
                            name=fmt.bold("Director"), value=id_result["Director"]
                        )
                        emb.add_field(
                            name=fmt.bold("Actors"), value=id_result["Actors"]
                        )
                        emb.set_footer(text="Powered by https://www.omdbapi.com/")
                else:
                    rip = fmt.inline("No movie found with this search query")
        return rip, emb

    @command()
    @bot_has_permissions(send_messages=True)
    async def games(self, ctx, *, query):
        """killerspiele"""
        url = "https://api-v3.igdb.com/games"
        main_query = (
            f'search "{query}";'
            "fields name,first_release_date,aggregated_rating,summary,genres.name,url,cover.url;"
            "limit 6;"
        )

        async with aiohttp.ClientSession(
            headers={"user-key": config.igdb, "accept": "application/json"}
        ) as session:
            async with session.post(url, data=main_query) as response:
                if response.status != 200:
                    err = f"The api-webserver responded with a code: {response.status} - {response.reason}"
                    raise NerpyException(err)
                result = await response.json()

                if len(result) > 0:
                    data = result[0]
                    emb = discord.Embed(title=data["name"])
                    if "summary" in data:
                        emb.description = data["summary"]
                    else:
                        emb.description = (
                            "Lorem ipsum dolor sit amet, consectetur adipisici elit."
                        )

                    if "cover" in data:
                        emb.set_thumbnail(url="https:" + data["cover"]["url"])

                    if "first_release_date" in data:
                        dt = datetime.utcfromtimestamp(
                            int(data["first_release_date"])
                        ).strftime("%Y-%m-%d")
                        emb.add_field(name=fmt.bold("Release Date"), value=dt)
                    else:
                        emb.add_field(name=fmt.bold("Release Date"), value="no info")

                    if "aggregated_rating" in data:
                        emb.add_field(
                            name=fmt.bold("Genres"),
                            value=", ".join(g["name"] for g in data["genres"]),
                        )
                    else:
                        emb.add_field(name=fmt.bold("Genres"), value="no info")

                    if "aggregated_rating" in data:
                        emb.add_field(
                            name=fmt.bold("Rating"),
                            value=f"{int(data['aggregated_rating'])}/100",
                        )
                    else:
                        emb.add_field(name=fmt.bold("Rating"), value="no rating")

                    if len(result) > 1:
                        i = iter(result)
                        next(i)
                        emb.add_field(
                            name=fmt.bold("wrong answer? try:"),
                            value="\n".join(" - " + r["name"] for r in i),
                        )

                    emb.set_footer(text=data["url"])

                    await ctx.send(embed=emb)
                else:
                    await ctx.send(f"Nothing found for {query}.")


def setup(bot):
    """adds this module to the bot"""
    bot.add_cog(Search(bot))
