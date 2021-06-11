#!/usr/bin/python3
import json
import asyncio
import logging

import discord
from discord.ext import tasks

import nmap

class AlertBot(discord.Client):
  def __init__(self, mac, channel_id, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.bg_task = self.send_alert.start()
    self.mac = mac
    self.channel_id = channel_id
    self.scanner = nmap.PortScanner()
    self.at_home = False

  async def on_ready(self):
    channel = self.get_channel(self.channel_id)
    await channel.send("Starting Scan...")
    print(""" _______  _        _______  _______ _________ ______   _______ _________
(  ___  )( \      (  ____ \(  ____ )\__   __/(  ___ \ (  ___  )\__   __/
| (   ) || (      | (    \/| (    )|   ) (   | (   ) )| (   ) |   ) (
| (___) || |      | (__    | (____)|   | |   | (__/ / | |   | |   | |
|  ___  || |      |  __)   |     __)   | |   |  __ (  | |   | |   | |
| (   ) || |      | (      | (\ (      | |   | (  \ \ | |   | |   | |
| )   ( || (____/\| (____/\| ) \ \__   | |   | )___) )| (___) |   | |
|/     \|(_______/(_______/|/   \__/   )_(   |/ \___/ (_______)   )_(   """)

  @staticmethod
  def mac_in_scan(scan):
    addr = lambda dic, ip : dic['scan'][ip]['addresses']
    return [addr(scan, i)['mac'] for i in scan['scan'].keys() if 'mac' in addr(scan, i).keys()]

  @tasks.loop(seconds=3600)
  async def send_alert(self):
    scan = self.scanner.scan('192.168.0.0/24', arguments='-n -sP -PE -T5')
    channel = self.get_channel(self.channel_id)
    connected_device_mac = self.mac_in_scan(scan)
    for device in self.mac:
      if (not self.at_home) and (self.mac[device] in connected_device_mac):
        await channel.send(f'{device} Just Connected')
        self.at_home = True
      if (self.mac[device] not in connected_device_mac):
        self.at_home = False

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
