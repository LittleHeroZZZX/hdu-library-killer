'''
Author: littleherozzzx zhou.xin2022.code@outlook.com
Date: 2023-01-12 13:27:24
LastEditTime: 2023-02-01 11:19:38
Software: VSCode
'''
import os
import requests
import sys
import os
from urllib.parse import unquote
from prettytable import PrettyTable
from time import sleep
import datetime as dt
import hashlib
import base64
import json
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
        self.plans = self.cfg["plans"]
        
    def saveConfig(self):
        self.cfg['seat_list'] = self.seat_list
        self.cfg['user_info'] = self.userInfo
        self.cfg['plans'] = self.plans
        self.cfg['plans'] = self.plans
        self.configParser.saveConfig(self.cfg)
    
    def __initSession(self):
        import urllib3
        urllib3.disable_warnings()
        self.session = requests.Session()
        self.session.headers.clear()
        self.session.headers = self.sessionCfg['headers']
        self.session.trust_env = self.sessionCfg['trust_env']
        self.session.verify = self.sessionCfg['verify']
        self.session.params = self.sessionCfg['params']
    
    def login(self):
        url = self.urls["login"]
        loginRes = self.session.post(url=url, data=self.userInfo).json()
        if loginRes["CODE"] == "ok":
            self.uid = loginRes["DATA"]["uid"]
            self.name = loginRes["DATA"]["user_info"]["name"]
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
            "seatsInfo": list(seatsInfo),
            "seatBookers": list(seatBookers),
        })
    
    def plan2data(self, plan):
        data = {}
        data["beginTime"] = int(plan["beginTime"].timestamp())
        data["duration"] = plan["duration"]*3600
        for i in range(len(plan["seatsInfo"])):
            data[f"seats[{i}]"] = plan["seatsInfo"][i]["seatId"]
        data["is_recommend"] = 0
        data["api_time"] = int(dt.datetime.now().timestamp())
        for i in range(len(plan["seatsInfo"])):
            data[f"seatBookers[{i}]"] = plan["seatBookers"][i]
        apiToken = f"post&/Seat/Index/bookSeats?LAB_JSON=1&api_time{data['api_time']}&beginTime{data['beginTime']}&duration{data['duration']}&is_recommend0&seatBookers[0]{data['seatBookers[0]']}&seats[0]{data['seats[0]']}"
        md5 = hashlib.md5(apiToken.encode("utf-8")).hexdigest()
        apiToken = base64.b64encode(md5.encode("utf-8"))
        return data, apiToken
    
    def showPlan(self):
        print(f"当前共有{len(self.plans)}个预约方案")
        if len(self.plans) == 0:
            return
        table = PrettyTable(["序号", "房间名", "楼层名", "座位号", "开始时间", "持续时间", "预约人"])
        for i, plan in enumerate(self.plans):
            seat = plan["seatsInfo"][0]
            table.add_row([f"{i+1}", seat['roomName'], seat['floorName'], ",".join([x["seatNum"] for x in plan["seatsInfo"]]), plan['beginTime'], str(plan['duration'])+"小时", ",".join([x["bookerName"] for x in plan["seatsInfo"]])])
        print(table)
    
    def deletePlan(self, index):
        index = set(index)
        self.plans = [x for i, x in enumerate(self.plans) if i not in index]
    def run(self, plan):
            data, Api_Token = self.plan2data(plan)
            url = self.urls["book_seat"]
            self.session.headers["Api-Token"] = Api_Token.decode()
            self.session.headers["Content-Length"] = "114"
            res = self.session.post(url=url, data=data).json()
            return res
            
    def changeTime(self, index, beginTime, duration):
        for i in index:
            self.plans[i]["beginTime"] = beginTime
            self.plans[i]["duration"] = duration
        

if __name__ == "__main__":

    
    killer = Killer()
    killer.init("./config/config.yaml")
    print(killer.login())
    killer.run(killer.plans[0])
        
        