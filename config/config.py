'''
Author: littleherozzzx zhou.xin2022.code@outlook.com
Date: 2023-01-12 12:49:30
LastEditTime: 2023-01-31 10:11:32
Software: VSCode
'''

import yaml
import os

class ConfigParser():
    def __init__(self, configFile):
        self.configFile = configFile
        self.config = None
        self.template = """
data:
  query_data:
    beginTime: null
    duration: null
    num: '1'
    space_category[category_id]: '591'
    space_category[content_id]: '3'
seat_list: []
session:
  headers:
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101
      Firefox/101.0
  params:
    LAB_JSON: '1'
  trust_env: false
  verify: false
urls:
  book_seat: https://hdu.huitu.zhishulib.com/Seat/Index/bookSeats
  login: https://hdu.huitu.zhishulib.com/User/Index/login
  query_seats: https://hdu.huitu.zhishulib.com/Seat/Index/searchSeats
  query_rooms: https://hdu.huitu.zhishulib.com/Space/Category/list
  index: https://hdu.huitu.zhishulib.com/
  index: https://hdu.huitu.zhishulib.com/
settings:
  interval: 3
  max_try_times: 50
user_info:
  login_name: 
  org_id: '104'
  password: 
plans: []
plans: []
        """
    
    def createConfig(self):
        with open(self.configFile, 'w+', encoding="utf-8") as f:
            self.config = yaml.load(self.template, Loader=yaml.FullLoader)
            yaml.dump(self.config, f, encoding="utf-8", allow_unicode=True)
    
    def parseConfig(self):
        with open(self.configFile, 'r', encoding="utf-8") as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        return self.config
      
    def saveConfig(self, config):
        with open(self.configFile, 'w', encoding="utf-8") as f:
            yaml.dump(config, f, encoding="utf-8", allow_unicode=True)


if __name__ == "__main__":
    config = ConfigParser("config.yaml")
    config.createConfig(config)