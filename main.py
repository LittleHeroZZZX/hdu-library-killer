'''
Author: littleherozzzx zhou.xin2022.code@outlook.com
Date: 2023-01-12 16:38:00
LastEditTime: 2023-01-31 10:16:43
Software: VSCode
'''
import os
from time import sleep
from pprint import pprint
from pwinput import pwinput
from datetime import datetime
from datetime import datetime
from utils.killer import Killer
from threading import Thread
from threading import Thread



class UserInterface:
    def __init__(self):
        self.configFile = "./config/config.yaml"
        self.killer = Killer()
        self.funcs = [self.changePlan, self.changeTime, self.startNow, self.startAt, self.help, self.exit]
    
    def init(self):
        
        if not os.path.exists(self.configFile):
            print(f"未检测到配置文件，将在config目录下创建配置文件: {self.configFile}")
            self.killer.init(self.configFile)
        else:
            try:
                self.killer.init(self.configFile)              
            except Exception as e:
                print(f"配置文件解析失败，请检查配置文件是否正确。错误为：")
                print(e)
                print(f"若无法解决，请尝试删除{self.configFile}，重新运行程序。")
                exit(1)
            print(f"配置文件解析成功。")
            sleep(1)

    def setUserInfo(self):
        userInfo = {}
        userInfo["login_name"] = input("请输入学号：")
        userInfo["password"] = pwinput("请输入密码：")
        self.killer.userInfo = userInfo

    def login(self):
        flag = False
        while not flag:
            if self.killer.userInfo["login_name"]  and self.killer.userInfo["password"] :
                if self.killer.login():
                    print("登录成功")
                    self.killer.saveConfig()
                    self.th = Thread(target=self.killer.updateRooms)
                    self.th.start()
                    flag = True
                else:
                    print("配置文件中账号密码错误，请重新输入")
                    self.setUserInfo()
            else:
                self.setUserInfo()
    
    def showMenu(self):
        print("1. 添加/删除待选座位方案")   
        print("2. 批量修改方案中预约时间")
        print("3. 立即开始抢座")
        print("4. 定时抢座")
        print("5. 使用帮助")
        print("6. 退出")
    
    def changePlan(self):
        self.addPlan()
    
    def changeTime(self):
        pass
    
    def startNow(self):
        self.killer.start()

    def startAt(self):
        pass
    
    def help(self):
        pass
    
    def exit(self):
        exit(0)
        
    def run(self):
        ui.init()
        ui.login()
        while True:
            self.showMenu()
            try:
                choice = int(input("请输入选项："))
                self.funcs[choice-1]()
            except Exception as e:
                print("输入错误，请重新输入")
                sleep(1)
                continue

    def addPlan(self):
        try:
            print("请根据系统提示填写作为预约信息，过程中可随时使用ctrl+c取消填写。")       
            num = int(input("请输入使用人数(1-4)："))
            if num < 1 or num > 4:
                raise Exception("人数不合法")
            if self.th.is_alive():
                print("正在初始化楼层和座位信息（为避免频繁请求而导致封号，此过程可能需要几秒，请耐心等待）")
                for _ in "loading...":
                    print(_, end="", flush=True)
                    sleep(0.5 if self.th.is_alive() else 0.1)
                while self.th.is_alive():
                    print(".", end="", flush=True)
                    sleep(0.5)
            numRooms = len(self.killer.rooms)
            print("\n")
            for i in range(numRooms):
                print(f"{i+1}. {list(self.killer.rooms.keys())[i]}")
            print(f"请选择房间类型(1-{numRooms})：")
            roomName = int(input())
            if roomName < 1 or roomName > numRooms:
                raise Exception("房间类型不合法")
            roomName = list(self.killer.rooms.keys())[roomName-1]
            room = self.killer.rooms[roomName]
            floor = self.killer.getFloorNamesByRoom(roomName)
            print(f"请选择楼层(1-{len(floor)})：")
            for i in range(len(floor)):
                print(f"{i+1}. {floor[i]}")
            floorName = floor[int(input())-1]
            print(f'本房间最早开放时间为：{room["range"]["minBeginTime"]}时，最晚开放时间为：{room["range"]["maxEndTime"]}时')
            print(f"请输入开始使用时间（格式为yyyy-mm-dd hh:mm:ss，如2023-01-01 12:00:00）：")
            time = input()
            time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            if time.hour < room["range"]["minBeginTime"] or time.hour > room["range"]["maxEndTime"]:
                raise Exception("开始时间不在房间开放时间内")
            leftTime = room["range"]["maxEndTime"] - time.hour
            hours = int(input(f"请输入使用时长（1-{leftTime},单位为小时）："))
            if hours < 1 or hours > leftTime:
                raise Exception("使用时长不合法")
            seatsInfo = self.killer.getSeatsByRoomAndFloor(roomName, floorName)
            seats = input("请输入座位号（多个座位号用逗号隔开，如1,2,3）：")
            seats = seats+"," if seats[-1] != "," else seats
            seats = eval(f"({seats})")
            seatsDictList = []
            for seat in seats:
                seat = str(seat)
                seatInfo = [x for x in seatsInfo if x["title"] == seat]
                if len(seatInfo) == 0:
                    raise Exception(f"{floorName}中座位{seat}不存在")
                if len(seatInfo) > 1:
                    raise Exception(f"程序错误，{floorName}中座位{seat}存在多个\n"+str(seatInfo))
                seatsDictList.append({
                    "roomName": roomName,
                    "floorName": floorName,
                    "seatId": seatInfo[0]["id"],
                    "booker": self.killer.uid,
                })
            if len(seats) != num:
                raise Exception("座位数与人数不匹配")
            # TODO: 多人预约正确的uid
            seatBookers = (self.killer.uid, )
            self.killer.addPlan(roomName, time, hours, seatsDictList, seatBookers)
            print("添加成功")
            self.killer.saveConfig()
        except KeyboardInterrupt:
            print("已取消")
            return
        except Exception as e:
            print("\033[0;31m%s\033[0m" % e)
            print("输入错误，取消本次操作")
            sleep(1)
            return

if __name__ == "__main__":
    ui = UserInterface()
    ui.run()
    ui.run()