#!/usr/bin/python3
import json
import asyncio
import logging

import discord
from discord.ext import tasks

import nmap

def flatten_dict(dd, separator='_', prefix=''):
  return { prefix + separator + k if prefix else k : v
    for kk, vv in dd.items()
    for k, v in flatten_dict(vv, separator, kk).items()
    } if isinstance(dd, dict) else { prefix : dd }

class AlertBot(discord.Client):
  def __init__(self, mac, channel_id, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.bg_task = self.send_alert.start()
    self.scanner = nmap.PortScanner()
    self.mac = mac.values()
    self.channel_id = channel_id

  async def on_ready(self):
    print(""" _______  _        _______  _______ _________ ______   _______ _________
      (  ___  )( \      (  ____ \(  ____ )\__   __/(  ___ \ (  ___  )\__   __/
      | (   ) || (      | (    \/| (    )|   ) (   | (   ) )| (   ) |   ) (   
      | (___) || |      | (__    | (____)|   | |   | (__/ / | |   | |   | |   
      |  ___  || |      |  __)   |     __)   | |   |  __ (  | |   | |   | |   
      | (   ) || |      | (      | (\ (      | |   | (  \ \ | |   | |   | |   
      | )   ( || (____/\| (____/\| ) \ \__   | |   | )___) )| (___) |   | |   
      |/     \|(_______/(_______/|/   \__/   )_(   |/ \___/ (_______)   )_(   """)

  @tasks.loop(seconds=300)
  async def send_alert(self):
    at_home = False
    scan = self.scanner.scan('192.168.0.0/24', arguments='-n -sP -PE -T5')
    channel = self.get_channel(self.channel_id)
    for mac in self.mac:
      if (not at_home) and (mac in flatten_dict(scan).values()):
        await channel.send('Device Found')
        at_home = True
      if (mac not in flatten_dict(scan).values()):
        at_home = False

  @send_alert.before_loop
  async def before_my_task(self):
    await self.wait_until_ready()

if __name__ == "__main__":
  logger = logging.getLogger('discord')
  logger.setLevel(logging.DEBUG)
  handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
  handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
  logger.addHandler(handler)
  conf = json.load(open('config.json'))
  client = AlertBot(conf['mac'], conf['channel_id'])
  client.run(conf['TOKEN'])
