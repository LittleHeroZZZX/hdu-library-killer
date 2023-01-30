'''
Author: littleherozzzx zhou.xin2022.code@outlook.com
Date: 2023-01-12 13:27:24
LastEditTime: 2023-01-30 19:17:01
Software: VSCode
'''
import os
import requests
import sys
import os
from urllib.parse import unquote
from time import sleep
import datetime as dt
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
        
    def saveConfig(self):
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
    
    def __querySeats(self):
        #  查询每个房间的作为信息
        time = dt.datetime.now()
        if time.hour >= 22:
            time = time + dt.timedelta(days=1)
            time = time.replace(hour=11, minute=0, second=0)
        for room in self.rooms.keys():
            data = {
                "beginTime": time.timestamp(),
                "duration": 3600,
                "num": 1,
                "space_category[category_id]": self.rooms[room]["space_category"]["category_id"],
                "space_category[content_id]": self.rooms[room]["space_category"]["content_id"],
            }
            resp = self.session.post(url=self.urls["query_seats"], data=data).json()
            self.rooms[room]["floors"] = {x["roomName"]:x for x in resp["allContent"]["children"][2]["children"]["children"]}
            for floor in self.rooms[room]["floors"].keys():
                self.rooms[room]["floors"][floor]["seats"] = self.rooms[room]["floors"][floor]["seatMap"]["POIs"]
            sleep(2)
    def updateRooms(self):
        self.rooms = self.__queryRooms()
        self.__querySeats()
        return list(self.rooms.keys())
    
    def getFloorNamesByRoom(self, roomName):
        floors = self.rooms[roomName]["floors"]
        return list(floors.keys())
    
    def getSeatsByRoomAndFloor(self, roomName, floorName):
        seats = self.rooms[roomName]["floors"][floorName]["seats"]
        return seats
    
    def addPlan(self, roomName, beginTime, duration, seatsInfo, seatBookers):
        self.plans.append({
            "roomName": roomName,
            "beginTime": beginTime,
            "duration": duration,
            "seatsInfo": seatsInfo,
            "seatBookers": seatBookers
        })
    
    def plan2data(self, plan):
        data = {}
        data["roomName"] = plan["roomName"]
        data["beginTime"] = plan["beginTime"]
        data["duration"] = plan["duration"]
        for i in range(len(plan["seats"])):
            data[f"seat{i}"] = plan["seatsInfo"][i]["seatId"]
            data[f"seatBooker{i}"] = plan["seatBookers"][i]
        return data
    
    def run(self):
        #  todo not finished
        for plan in self.plans:
            data = self.plan2data(plan)
            url = self.urls["book_seat"]
            res = self.session.post(url=url, data=data).json()
            print(res)
            if res["CODE"] == "ok":
                self.plans.remove(plan)
                self.saveConfig("./config/config.yaml")
            sleep(5)
        

if __name__ == "__main__":

    
    killer = Killer()
    killer.init("./config/config.yaml")
    print(killer.login())
    print(killer.updateRooms())
    print(killer.rooms)
    print(killer.getFloorNamesByRoom("自习室"))
        
        