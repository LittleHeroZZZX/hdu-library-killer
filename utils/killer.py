'''
Author: littleherozzzx zhou.xin2022.code@outlook.com
Date: 2023-01-12 13:27:24
LastEditTime: 2023-01-30 11:08:41
Software: VSCode
'''
import os
import requests
import sys
import os
from urllib.parse import unquote
from time import sleep
sys.path.append(os.getcwd())

from config.config import ConfigParser

class Killer:
    def __init__(self):
        pass
    
    def init(self, configFile):
        self.loadConfig(configFile)
        self.__initSession()
    
    def loadConfig(self, configFile):
        self.configParser = ConfigParser(configFile)
        if not os.path.exists(configFile):
            self.configParser.createConfig()
        self.cfg = self.configParser.parseConfig()
        self.sessionCfg = self.cfg['session']
        self.urls = self.cfg['urls']
        self.seat_list = self.cfg["seat_list"]
        self.data = self.cfg["data"]
        self.settings = self.cfg["settings"]
        self.userInfo = self.cfg["user_info"]
        self.plans = self.cfg["plans"]
        
    def saveConfig(self, configFile):
        self.cfg['seat_list'] = self.seat_list
        self.cfg['user_info'] = self.userInfo
        self.cfg['plans'] = self.plans
        self.configParser.saveConfig(self.cfg)
    
    def __initSession(self):
        import urllib3
        urllib3.disable_warnings()
        self.session = requests.Session()
        self.session.headers = self.sessionCfg['headers']
        self.session.trust_env = self.sessionCfg['trust_env']
        self.session.verify = self.sessionCfg['verify']
        self.session.params = self.sessionCfg['params']
    
    def login(self):
        url = self.urls["login"]
        loginRes = self.session.post(url=url, data=self.userInfo).json()
        if loginRes["CODE"] == "ok":
            self.uid = loginRes["DATA"]["uid"]
        return loginRes["CODE"] == "ok"

    def __queryRooms(self):
        # 查询所有可用的房间类型，返回一个字典，键为房间名，值为房间对应的请求参数
        url = self.urls["query_rooms"]
        queryRoomsRes = self.session.get(url=url).json()
        rawRooms = queryRoomsRes["content"]["children"][1]["defaultItems"]
        rooms = {x["name"]: unquote(x["link"]["url"]).split('?')[1] for x in rawRooms}
        for room in rooms.keys():
            rooms[room] = self.session.get(url=self.urls["query_seats"] + "?" + rooms[room]).json()["data"]
            sleep(2)
        return rooms
    
    def updateRooms(self):
        self.rooms = self.__queryRooms()
        return list(self.rooms.keys())
    
    def addPlan(self, roomName, beginTime, duration, seats, seatBookers):
        self.plans.append({
            "roomName": roomName,
            "beginTime": beginTime,
            "duration": duration,
            "seats": seats,
            "seatBookers": seatBookers
        })
        

if __name__ == "__main__":

    
    killer = Killer()
    killer.init("./config/config.yaml")
    print(killer.login())
    print(killer.updateRooms())
    print(killer.rooms)
        
        