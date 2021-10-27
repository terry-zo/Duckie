import json
import time
import datetime
import aiohttp
import socket
import requests
import datetime
from collections import defaultdict


class Webhook:
    def __init__(self, url, **kwargs):
        """
        Initialise a Webhook Embed Object
        """

        self.url = url
        self.msg = kwargs.get('msg')
        self.color = kwargs.get('color')
        self.title = kwargs.get('title')
        self.title_url = kwargs.get('title_url')
        self.author = kwargs.get('author')
        self.author_icon = kwargs.get('author_icon')
        self.author_url = kwargs.get('author_url')
        self.desc = kwargs.get('desc')
        self.fields = kwargs.get('fields', [])
        self.image = kwargs.get('image')
        self.thumbnail = kwargs.get('thumbnail')
        self.footer = kwargs.get('footer')
        self.footer_icon = kwargs.get('footer_icon')
        self.ts = kwargs.get('ts')

    def add_field(self, **kwargs):
        '''Adds a field to `self.fields`'''
        name = kwargs.get('name')
        value = kwargs.get('value')
        inline = kwargs.get('inline', True)

        field = {

            'name': name,
            'value': value,
            'inline': inline

        }

        self.fields.append(field)

    def set_desc(self, desc):
        self.desc = desc

    def set_author(self, **kwargs):
        self.author = kwargs.get('name')
        self.author_icon = kwargs.get('icon')
        self.author_url = kwargs.get('url')

    def set_title(self, **kwargs):
        self.title = kwargs.get('title')
        self.title_url = kwargs.get('url')

    def set_thumbnail(self, url):
        self.thumbnail = url

    def set_image(self, url):
        self.image = url

    def set_footer(self, **kwargs):
        self.footer = kwargs.get('text')
        self.footer_icon = kwargs.get('icon')

    def del_field(self, index):
        self.fields.pop(index)

    @property
    def json(self, *arg):
        '''
        Formats the data into a payload
        '''

        data = {}

        data["embeds"] = []
        embed = defaultdict(dict)
        if self.msg:
            data["content"] = self.msg
        if self.author:
            embed["author"]["name"] = self.author
        if self.author_icon:
            embed["author"]["icon_url"] = self.author_icon
        if self.author_url:
            embed["author"]["url"] = self.author_url
        if self.color:
            embed["color"] = self.color
        if self.desc:
            embed["description"] = self.desc
        if self.title:
            embed["title"] = self.title
        if self.title_url:
            embed["url"] = self.title_url
        if self.image:
            embed["image"]['url'] = self.image
        if self.thumbnail:
            embed["thumbnail"]['url'] = self.thumbnail
        if self.footer:
            embed["footer"]['text'] = self.footer
        if self.footer_icon:
            embed['footer']['icon_url'] = self.footer_icon
        if self.ts:
            embed["timestamp"] = self.ts

        if self.fields:
            embed["fields"] = []
            for field in self.fields:
                f = {}
                f["name"] = field['name']
                f["value"] = field['value']
                f["inline"] = field['inline']
                embed["fields"].append(f)

        data["embeds"].append(dict(embed))

        empty = all(not d for d in data["embeds"])

        if empty and 'content' not in data:
            print('You cant post an empty payload.')
        if empty:
            data['embeds'] = []

        data["username"] = "Duckie"
        data["avatar_url"] = "https://cdn.discordapp.com/avatars/457075263377899521/9000264f1703a96b9ba0de74f8c0a31c.png?size=128"

        return json.dumps(data, indent=4)

    def post(self):
        """
        Send the JSON formated object to the specified `self.url`.
        """

        headers = {'Content-Type': 'application/json'}

        result = requests.post(self.url, data=self.json, headers=headers)

        if result.status_code == 400:
            print("Post Failed, Error 400")

    # async def apost(self, qnum, question_str, _output, a_time):
    #     """
    #     Send the JSON formated object to the specified `self.url`.
    #     """
        self.set_author(name='Duckie', icon='https://cdn.discordapp.com/avatars/457075263377899521/9000264f1703a96b9ba0de74f8c0a31c.png?size=128')
        self.add_field(name=f"Question {qnum}", value=question_str)
        self.add_field(name=f"Answers:", value=_output)
        # self.add_field(name="Announcement", value="I'm cutting down on some code to make the bot faster. Except the time to be around 1-2 seconds. Will send some test questions to see time.")
        self.set_footer(text=f"Answered in {a_time} | Created by Terry")
    #         return ""

    async def apost(self, **k):
        """
        Send the JSON formated object to the specified `self.url`.
        """
        self.ts = str(datetime.datetime.now())
        self.set_author(name='Duckie', icon='https://cdn.discordapp.com/avatars/457075263377899521/9000264f1703a96b9ba0de74f8c0a31c.png?size=128')

        if k.get("question") is not None and k.get("output") is not None:
            if k.get("questionNumber") is not None:
                self.add_field(name=f"Question {k.get('questionNumber')}", value=k.get("question"), inline=False)
            else:
                self.add_field(name="Question", value=k.get("question"), inline=False)
            self.add_field(name="Answers:", value=k.get("output"), inline=False)

        if k.get("Ended") is not None:
            self.add_field(name="Show Has Ended!", value=k.get("Ended"), inline=False)

        if k.get("startingTime") is not None:
            self.set_footer(text="Answered in %.2f" % (time.time() - k.get("startingTime")))
        else:
            self.set_footer(text="Duckie")

        try:
            async with aiohttp.ClientSession(headers={'Content-Type': 'application/json'}, connector=aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False,)) as session:
                async with session.post(self.url, data=self.json, timeout=7) as response:
                    return ""
        except Exception as e:
            print(e)
            return ""
