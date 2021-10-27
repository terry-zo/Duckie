import json
import aiohttp
import datetime
import socket
import time
from collections import defaultdict


class Slackhook(object):

    def __init__(self, url, **kwargs):
        self.url = url
        self.color = kwargs.get('color')
        self.fields = kwargs.get('fields', [])

    def set_author(self, **kwargs):
        self.author = kwargs.get('name')
        self.author_icon = kwargs.get('icon')
        self.author_url = kwargs.get('url')

    def set_footer(self, **kwargs):
        self.footer = kwargs.get('text')
        self.footer_icon = kwargs.get('icon')

    def add_field(self, **kwargs):
        '''Adds a field to `self.fields`'''
        name = kwargs.get('name')
        value = kwargs.get('value')
        inline = kwargs.get('inline', False)

        field = {

            'title': name,
            'value': value,
            'short': inline

        }

        self.fields.append(field)

    @property
    def json(self, *arg):
        # timestamp, author name n icon, fields, footers

        data = {}

        data["attachments"] = []

        embed = defaultdict(dict)

        if self.color:
            embed["color"] = str(self.color).replace("0x", "")
        if self.author:
            embed["author_name"] = self.author
        if self.author_icon:
            embed["author_icon"] = self.author_icon
        if self.author_url:
            embed["author_link"] = self.author_url
        if self.footer:
            embed["footer"] = self.footer
        if self.footer_icon:
            embed["footer_icon"] = self.footer_icon
        if self.ts:
            embed["ts"] = self.ts

        if self.fields:
            embed["fields"] = []
            for field in self.fields:
                f = {}
                f["title"] = field['title']
                f["value"] = field['value']
                f["short"] = field['short']
                embed["fields"].append(f)

        data["attachments"].append(dict(embed))

        return json.dumps(data, indent=4)

    async def apost(self, **k):
        """
        Send the JSON formated object to the specified `self.url`.
        """
        self.ts = int(datetime.datetime.now().timestamp())
        self.set_author(name='Duckie', icon='https://cdn.discordapp.com/avatars/457075263377899521/9000264f1703a96b9ba0de74f8c0a31c.png?size=128')

        if k.get("question") is not None and k.get("output") is not None:
            if k.get("questionNumber") is not None:
                self.add_field(name=f"Question {k.get('questionNumber')}", value=k.get("question"), inline=False)
            else:
                self.add_field(name="Question", value=k.get("question"), inline=False)
            self.add_field(name="Answers:", value=k.get("output").replace("**", "*").replace(":regional_indicator_x:", ":x:").replace(":white_check_mark:", ":heavy_check_mark:"), inline=False)

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
