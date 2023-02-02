# 杭州电子科技大学图书馆抢座脚本

## 脚本介绍

本脚本用于杭电图书馆自习室座位预约，目前支持自动登录、批量预约、定时预约等功能，有以下五个模块：

* 查看/添加/删除待选座位方案
* 批量修改方案中预约时间
* 定时开始抢座

**本脚本仅限用于个人图书馆预约座位，请勿恶意囤座位！**

## 运行说明

0. 本脚本基于Python 3.10编写，请先安装Python 3.10。
1. 克隆本项目

``` shell
git clone git@github.com:LittleHeroZZZX/hdu-library-killer.git
cd hdu-library-killer
```

2. 安装依赖项

```shell
pip install -r requirements.txt
```

3. 运行脚本

``` shell
python main.py
```

4. 根据软件提示登录、查看使用说明。

## TODO

- [ ] 多人座位预约
- [ ] 取消预约

