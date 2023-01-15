'''
Author: littleherozzzx zhou.xin2022.code@outlook.com
Date: 2023-01-12 16:38:00
LastEditTime: 2023-01-15 23:32:48
Software: VSCode
'''
import os
from time import sleep
from pprint import pprint
from pwinput import pwinput
from utils.killer import Killer



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
                    self.killer.saveConfig(self.configFile)
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
        pass
    
    def changeTime(self):
        pass
    
    def startNow(self):
        pass

    def startAt(self):
        pass
    
    def help(self):
        pass
    
    def exit(self):
        exit(0)
if __name__ == "__main__":
    ui = UserInterface()
    ui.init()
    ui.login()
    ui.showMenu()
 
        