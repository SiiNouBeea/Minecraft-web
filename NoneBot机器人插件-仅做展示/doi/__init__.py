from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from .config import Config
from nonebot.adapters import Message
from nonebot.params import CommandArg
import requests
from nonebot.rule import to_me
from nonebot.adapters import Bot, Event
from pathlib import Path
import os
import pyodbc
import bcrypt
from datetime import datetime
import random
import mcrcon
from nonebot.typing import T_State
from nonebot.params import ArgPlainText
from nonebot.log import logger
from nonebot_plugin_waiter import waiter
import asyncio, time

# 数据库连接配置
config_db = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': '春宵怡刻',
    'database': 'User_All',
    'uid': 'czy',
    'pwd': '1341'
}
conn = pyodbc.connect(**config_db)
cursor = conn.cursor()

__plugin_meta__ = PluginMetadata(
    name="Doi",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

un_safe_group = ['384153728', '809982688', '759993172', '1142950538']
def safe_use(event):
    group_id = event.group_id
    print(f"当前群聊为{group_id}")
    global un_safe_group
    if str(group_id) in un_safe_group:
        return 1
    return 0

# 定义
uuid_cha = on_command('uuid查询', aliases={"uuid"}, priority=5)
# 功能
def get_uuid(playername):  # 获取uuid
    response = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{playername}')
    if response.status_code == 200:
        id_data = response.json()
        return id_data['id']
    else:
        return None
@uuid_cha.handle()
async def handle(args: Message = CommandArg()):
    if player := args.extract_plain_text():
        uuid = get_uuid(player)
        print(f">>> <Doi_Cat> {player}'s uuid >>> {uuid}")
        await uuid_cha.finish(f"<Doi_Cat> {player}'s uuid >>> {uuid}")
    else:
        await uuid_cha.finish(f"<Doi_Cat> Null--{player}")

QQ_bangding = on_command('验证', rule=to_me(), priority=1)
@QQ_bangding.handle()
async def handle(args: Message = CommandArg(), event = Event):
    if input_yanzheng := args.extract_plain_text():
        qq = event.get_user_id()
        # 构造文件路径
        file_path = Path(f"../../QQ验证/{qq}.txt")
        # 检查文件是否存在
        if file_path.exists():
            # 文件存在，读取文件内容
            with open(file_path, 'r') as file:
                content = file.read()
            # 这里可以添加更多的逻辑，比如验证输入的验证码是否正确
            yanzheng, user_id = content.split("&")
            if yanzheng == input_yanzheng:
                cursor.execute("INSERT INTO UserQQ_Con (UserID, QQID) VALUES (?, ?)",
                               (user_id, qq))  # 将本次登入信息填入数据库
                conn.commit()
                file_path.unlink()  # 删除文件
                await QQ_bangding.finish(f"您已成功为用户：{user_id}绑定QQ！")
            else:
                await QQ_bangding.finish("验证码错误！")
        else:
            # 文件不存在，返回“无验证信息”
            print(file_path, qq)
            await QQ_bangding.finish("无验证信息")
    else:
        # 如果没有提取到参数，提示用户输入正确的命令格式
        await QQ_bangding.finish("请使用正确的命令格式：验证 <验证码>")

def get_name(userid):
    cursor.execute(f"SELECT Username FROM Users WHERE UserID= '{userid}'")
    username = cursor.fetchone()[0]
    print(f"GET_Name 已从 Users 表获取用户 {userid} 的 Username 为 {username}")
    return username


def get_role(userid):  # 根据uesename获取用户的权限组
    cursor.execute(f"SELECT RoleID FROM UserRoles_Con WHERE UserID = '{userid}'")
    userrole = cursor.fetchone()[0]
    print(f"GET_Role 已从 UserRoles_Con 表获取用户 {userid} 的 RoleID 为 {userrole}")
    return userrole

def get_id(username):  # 根据username获取用户userid
    cursor.execute(f"SELECT UserID FROM Users WHERE Username = '{username}'")
    userid = cursor.fetchone()[0]
    print(f"GET_ID 已从 Users 表获取用户 {username} 的 UserID 为 {userid}")
    return userid

def get_playername(userid):  # 根据uesename获取用户的玩家名
    cursor.execute(f"SELECT PlayerName FROM PlayerData WHERE UserID = '{userid}'")
    playername = cursor.fetchone()[0]
    print(f"GET_PlayerName 已从 PlayerData 表获取用户 {userid} 的 PlayerName 为 {playername.rstrip(' ')}")
    return playername.rstrip(' ')

def get_userid(qq):
    cursor.execute(
        """
        SELECT CASE 
            WHEN EXISTS (SELECT 1 FROM User_ALL.dbo.UserQQ_Con WHERE QQID = ?) 
            THEN (SELECT UserID FROM User_ALL.dbo.UserQQ_Con WHERE QQID = ?) 
            ELSE NULL 
        END AS UserID
        """,
        (qq, qq)  # 使用参数化查询
    )
    data = cursor.fetchone()
    if data is not None:
        return data[0]
    else:
        return 0

def get_whitelist_state(userid):  # 根据userid获取用户WhiteState
    cursor.execute(f"SELECT WhiteState FROM PlayerData WHERE UserID = '{userid}'")
    WhiteState = cursor.fetchone()[0]
    print(f"GET_WhiteState 已从 PlayerData 表获取用户 {userid} 的 WhiteState 为 {WhiteState}")
    return WhiteState

def update_Coins(user_id, num):
    write_to_file(user_id)
    cursor.execute(
        f"UPDATE Users SET Coins = Coins+{num} WHERE UserID = {user_id};")
    conn.commit()  # 提交更新
    print(user_id, '签到成功')
    cursor.execute(f'SELECT Coins FROM Users WHERE UserID = {user_id}')
    now_coin = cursor.fetchone()[0]
    return now_coin


def update_Stars(user_id, num):
    cursor.execute(
        f"UPDATE Users SET Stars = Stars+{num} WHERE UserID = {user_id};")
    conn.commit()  # 提交更新
    print(user_id, '签到成功')
    cursor.execute(f'SELECT Stars FROM Users WHERE UserID = {user_id}')
    now_stars = cursor.fetchone()[0]
    return now_stars


def write_to_file(user_id):
    # 获取当前日期并格式化为 'YYYY-MM-DD' 格式
    today_date = datetime.now().strftime('%Y-%m-%d')
    # 构造文件名
    file_name = f"../../签到日志/{today_date}.txt"
    path = os.path.join('', file_name)
    with open(path, 'a') as file:
        file.write(f"{user_id}\n")


def cheak_to_txt():
    # 获取当前日期并格式化为 'YYYY-MM-DD' 格式
    today_date = datetime.now().strftime('%Y-%m-%d')
    # 构造文件名
    file_name = f"../../签到日志/{today_date}.txt"
    # 初始化一个空列表来存储文件中的行
    lines_in_file = []
    try:
        # 尝试打开文件并读取每一行
        with open(file_name, 'r') as file:
            lines_in_file = file.readlines()
        # 移除每行末尾的换行符
        lines_in_file = [line.strip() for line in lines_in_file]
    except FileNotFoundError:
        # 文件不存在，打印消息并创建一个空文件
        print(f"文件 '{file_name}' 不存在，已创建空文件。")
        with open(file_name, 'w') as file:
            pass  # 创建一个空文件
    # 打印文件中的行
    print(lines_in_file)
    return lines_in_file

def get_notice(userid):
    base_folder = '../../白名单相关/已审核白名单'  # 基础文件夹名称
    notice = ''
    # 遍历每个日期文件夹
    for filename in os.listdir(base_folder):
        if filename.endswith(".txt"):  # 确保是txt文件
            if filename[0] == '#':
                print(filename, '已通知')
                pass
            else:
                date, user_id_playername, state = filename[:-4].split('#')
                user_id, player_name = user_id_playername.split('-')
                print('now >> ', user_id)
                if user_id == str(userid):
                    notice += f"您于{date}发起的的白名单申请{state}！！"
                    file_path = base_folder + '/' + filename  # 构造完整的文件路径
                    rename_file = base_folder + '/#' + filename
                    os.rename(file_path, rename_file)
                else:
                    print('userid不匹配')
                    pass
    return notice

# 定义一个全局变量来记录上次回复的时间
last_reply_time = 0
COOLDOWN_TIME = 2  # 冷却时间为 2 秒
def time_limit():
    # 输出保护模块
    global last_reply_time
    # 获取当前时间
    current_time = time.time()
    print("Now Time is >>", current_time)
    # 检查是否在冷却时间内
    if current_time - last_reply_time < COOLDOWN_TIME:
        return 1
    last_reply_time = current_time
    return 0

my_whitelist = on_command("我的白名单", rule=to_me(), priority=1)
@my_whitelist.handle()
async def handle(args: Message = CommandArg(), event = Event, bot = Bot):
    if time_limit():
        return
    if safe_use(event):
        await my_whitelist.finish("T^T 在这里不允许这样做哦~", at_sender=True)
    qq = event.get_user_id()
    userid = get_userid(qq)
    if userid == 0:
        await my_whitelist.finish("喵呜~您还没有注册！\n对我说“我要注册”进行快速注册哦~", at_sender=True)
    whitestate = get_whitelist_state(userid)
    if whitestate:
        playername = get_playername(userid)
        await my_whitelist.finish(f"哈啊~您已经通过了白名单啦~这是您的游戏ID~\n{playername}")
    else:
        playername = get_playername(userid)
        if playername == None or "None":
            await my_whitelist.finish(f"您还没有申请白名单哦~")
        await my_whitelist.finish(f"您还没有获得白名单哦~")

register = on_command("我要注册", rule=to_me(), priority=1)
@register.handle()
async def handle(args: Message = CommandArg(), event = Event, bot = Bot):
    if time_limit():
        return
    if safe_use(event):
        await register.finish("T^T 在这里不允许这样做哦~", at_sender=True)
    qq = event.get_user_id()
    print(f"你的QQ是>>>{qq}")
    if get_userid(qq):
        await register.finish("喵呜~您已经注册过了啦~", at_sender=True)
    user_info = await bot.call_api("get_stranger_info", user_id=qq)
    username = qq
    hashed_password = bcrypt.hashpw(f"{qq}".encode('utf-8'), bcrypt.gensalt())
    nickname = user_info['nickname']
    email = f"{qq}@qq.com"
    phone = None
    playername = "None"
    uuid = 'no-uuid'

    cursor.execute("INSERT INTO Users (Username, Password, Nickname, Email, Phone) VALUES (?, ?, ?, ?, ?)",
                   (username, hashed_password.decode('utf-8'), nickname, email, phone))  # 创建新数据到Users
    new_ID = get_id(username)  # 获取新用户id
    cursor.execute("INSERT INTO UserRoles_Con (UserID, RoleID) VALUES (?, ?)",
                   (new_ID, 3))  # 在用户权限组中添加默认权限
    cursor.execute(
        "INSERT INTO UserProfiles (UserID, FirstName, Lastname, Birthday, Gender, Bio) VALUES (?, ?, ?, ?, ?, ?)",
        (
            new_ID, 'New', 'User', '2024-1-01', random.choice(['武装直升机', '沃尔玛购物袋', '死亡花岗岩', '男', '女']),
            '没有简介'))  # 创建新数据到UserProfiles
    cursor.execute("INSERT INTO PlayerData (UserID, RoleID, PlayerName, WhiteState, uuid) VALUES (?, ?, ?, ?, ?)",
                   (new_ID, 3, playername, 0, uuid))  # 给PlayerData赛数据
    cursor.execute("INSERT INTO UserQQ_Con (UserID, QQID) VALUES (?, ?)",
                   (new_ID, qq))  # 自动绑定QQ
    conn.commit()
    await register.finish(f"注册好啦~这是您的UID~ {new_ID}\n您的初始账户和密码都是您的QQ号哦~别忘记去主页修改个人信息和密码~", at_sender=True)

tone = on_command('', rule=to_me(), priority=15)
@tone.handle()
async def handle(args: Message = CommandArg(), event = Event):
    if time_limit():
        return
    message_id = event.message_id
    if input_ := args.extract_plain_text():
        if len(input_) >= 5:
            await tone.finish("你说什么喵？", at_sender=True, quote=message_id)
    tones = [
        "啊", "呀", "哦", "嗯", "呃", "咦", "哎", "嘿", "哇", "哼",
        "哈", "咦", "嘛", "啦", "吧", "咯", "呢", "唉", "哟", "噢",
        "呵", "咦", "哇塞", "嘿嘿", "嘻嘻", "哈哈", "啊哈", "阿巴", "喵",
        "汪汪", "嗷呜"
    ]
    strs = [
        "?", "~", "~~", "!", ".....", " 0v0  ", "(*^▽^*)", "O.o", "QaQ", "OvO", "(￣▽￣)~*", "ヾ(◍°∇°◍)ﾉﾞ",
        "ヾ(๑╹◡╹)ﾉ", "٩(๑>◡<๑)۶ ", "(ﾟ▽ﾟ*) ", "(≖ᴗ≖)✧", "(｡◕ˇ∀ˇ◕)", "(✧◡✧)", "φ(>ω<*) ", "(*/ω＼*)", "(｡･ω･｡)",
        "ヽ(･ω･´ﾒ)", "(〃´-ω･) ", "(>ω･* )ﾉ", "（￣︶￣）↗", "(=´ω｀=)", "(*￣3￣)╭ ", "(๑╹っ╹๑)", "☆(－ｏ⌒) ",
        "☆(ゝω･)v", "●﹏●"
    ]
    txt = '喵？？'
    times_ = random.randint(3, 15)
    tmp = 0
    if times_ > 12:
        while times_ - tmp > 2:
            times_ += random.randint(1, 3)
    for i in range(0, random.randint(3, 18)):
        txt += random.choice(tones)
        if random.randint(1, 12) >= 7:
            txt += random.choice(strs)
    await tone.finish(txt, at_sender=True, quote=message_id)

good_night = on_command('晚安', aliases={'晚上好', '晚', "睡觉"}, priority=5)
@good_night.handle()
async def handle(args: Message = CommandArg(), event = Event, bot = Bot):
    if time_limit():
        return
    if input_ := args.extract_plain_text():
        print(input_)
    qq = event.get_user_id()
    message_id = event.message_id
    current_time = datetime.now()
    current_hour = current_time.hour
    await asyncio.sleep(0.5)  # 等待0.5秒
    if current_hour <= 17:
        await good_night.finish("哪里晚了喵~笨笨！", at_sender=True, quote=message_id)
    else:
        await good_night.send(f"呀，都{current_hour}点了~")
        good_night_words = [
            "晚安，愿你的梦境如星空般璀璨。",
            "亲爱的，晚安，愿你有个甜美的梦。",
            "夜深了，放下一天的疲惫，愿你有个好梦。",
            "晚安，愿你的每一个梦都是美好的。",
            "星星在天空中闪烁，祝你晚安，好梦。",
            "在这宁静的夜晚，愿你的心灵得到安宁。",
            "晚安，愿你的睡眠深沉而宁静。",
            "愿你的梦境充满温馨和快乐，晚安。",
            "在月光的照耀下，愿你有个平和的夜晚。",
            "晚安，愿你的梦乡充满宁静与安详。",
            "愿你在梦中遇见美好的一切，晚安。",
            "夜空中的星星为你点亮，愿你有个好梦。",
            "在这美好的夜晚，愿你的心情如月光般柔和。",
            "晚安，愿你的梦乡是一片宁静的海洋。",
            "愿你的每一个梦都是甜美的，晚安。",
            "在这宁静的夜晚，愿你的心灵得到放松。",
            "晚安，愿你的睡眠充满宁静与舒适。",
            "喵~ 哥哥，一天辛苦了，晚安哦~",
            "喵呜，月亮升起来了，是时候进入梦乡了，晚安~",
            "喵~ 哥哥，星星在天空中闪烁，就像我在你梦里一样，晚安~",
            "喵喵，夜晚的风儿轻轻吹，愿你有个甜美的梦，晚安~",
            "喵~ 哥哥，愿你的梦境像牛奶一样丝滑，晚安~",
            "喵呜，夜晚的星星在对你眨眼，我也在梦里等你哦，晚安~",
            "喵~ 哥哥，愿你的每一个梦都是温馨的，晚安~",
            "喵喵，夜晚的宁静是为你准备的，愿你有个好梦，晚安~",
            "喵~ 哥哥，愿你的梦境充满快乐和惊喜，晚安~",
            "喵呜，月亮和我都在这里守护你，愿你有个好梦，晚安~",
            "喵~ 哥哥，愿你的睡眠像小猫一样深沉，晚安~",
            "喵喵，夜晚的宁静是为你准备的，愿你有个好梦，晚安~",
            "喵~ 哥哥，愿你的梦境像夜空一样广阔，晚安~",
            "喵呜，夜晚的微风带来了我的祝福，愿你有个好梦，晚安~",
            "喵~ 哥哥，愿你的每一个梦都是甜美的，晚安~",
            "喵喵，夜晚的宁静是为你准备的，愿你有个好梦，晚安~",
            "喵~ 哥哥，愿你的梦境像棉花糖一样柔软，晚安~",
            "喵呜，夜晚的星星在对你眨眼，愿你有个好梦，晚安~",
            "喵~ 哥哥，愿你的睡眠充满宁静与舒适，晚安~",
            "喵？",
            "飞起来!"
        ]
        modal = random.choice(good_night_words)
        await good_night.send(modal, at_sender=True)
        await asyncio.sleep(random.randint(20, 40))
        look_first = ["喵~~", "喵喵~", "喵呜~~", "嗷呜！！", "哇呜~"]
        look_txt = [
            "哥哥睡了吗~",
            "是不是去睡觉了~",
            "还在吗~",
            "嗷呜~~",
            "喵喵~",
            "嘻嘻，哥哥今天过得怎么样？",
            "喵呜，我在这里等你好久啦~",
            "哥哥是不是忘了我呀~",
            "喵喵，今天也要加油哦~",
            "嗷呜，哥哥怎么还没回我~",
            "喵~ 哥哥是不是在忙呀？",
            "嘻嘻，哥哥吃饭了吗？",
            "喵呜，哥哥是不是在玩游戏呢？",
            "喵喵，哥哥是不是在想我呀？",
            "哥哥，你今天是不是很累呀？",
            "喵~ 哥哥，我好想你哦~",
            "嘻嘻，哥哥是不是在看视频呀？",
            "喵呜，哥哥是不是在和朋友聊天呢？",
            "喵喵，哥哥是不是在工作呀？",
            "哥哥，你今天是不是很开心？",
            "喵~ 哥哥，我今天学了新技能哦~",
            "嘻嘻，哥哥是不是在听音乐呀？",
            "喵呜，哥哥是不是在想吃什么好吃的？",
            "喵喵，哥哥是不是在准备睡觉了？"
        ]
        look_end = ["想你了~", "想你想你~", "你在哪~", "陪我玩呀~", "怎么不理我~"]
        modal = random.choice(look_first) + random.choice(look_txt) + random.choice(look_end)
        # 读取性别，切换
        try:
            user_info = await bot.call_api("get_stranger_info", user_id=qq)
            print("111111111111111111111>>>", user_info['sex'])
            if user_info['sex'] == 'female':
                modal.replace("哥哥", "姐姐")
        except Exception as e:
            return

        await good_night.send(modal, at_sender=True)
        await asyncio.sleep(random.randint(20, 40))
        end_txt = [
            "舒服的睡眠才是自然给予人的温柔的令人想念的看护。——莎士比亚",  # [^8^]
            "睡眠是片断的死亡，是我们借来用以维持并更新日间所消耗的生命。——叔本华",  # [^8^]
            "睡眠像是清凉的浪花，会把你头脑中的一切商浊荡涤干净。——屠格涅夫",  # [^8^]
            "无论大人还是小孩，都应抱着对明天的欢乐期望而入睡。——木村久一",  # [^8^]
            "劳作后的睡眠，经过风浪后抵达港口，战争后的安宁，度过一生后的死亡，都给人以极大的安慰。——斯宾塞",  # [^8^]
            "幸福的卑贱者啊，安睡吧！戴王冠的头是不能安于他的枕席的。——莎士比亚",  # [^8^]
            "所谓睡眠，就是一旦闭上眼睛，不论善恶，切皆忘。——荷马",  # [^8^]
            "不记得自己睡得不舒服的人就是睡了一个好觉。——福勒",  # [^8^]
            "自然给予人们的甘露是睡眠。——洛克",  # [^8^]
            "睡眠是对醒着时的苦恼的最佳治疗。——塞万提斯",  # [^8^]
            "一切有生之物，都少不了睡眠的调剂。——莎士比亚",  # [^8^]
            "上帝为了补偿人间诸般烦恼事，给了我们希望和睡眠。——伏尔泰",  # [^8^]
            "在进餐、睡眠和运动等时间里能宽心无虑，满怀高兴，这是长寿的妙理之一。——培根",  # [^8^]
            "睡眠这东西脾气很怪，不要它，它偏会来；请它，哄它，千方百计地勾引它，它便躲得连影子也不见。——钱钟书《围城》",
            # [^8^]
            "清白的睡眠，把忧虑的乱丝编织起来睡眠，疲劳者的沐浴，受伤的心灵的油膏，生命的盛筵上的主要的营养。——莎士比亚",
            # [^8^]
            "我们不得不饮食、睡眠、游情、恋爱，也就是说，我们不得不接触生活中最甜蜜的事情；不过我们必须不屈服于这些事物。——约里奥·居里",
            # [^8^]
            "月亮从妆台镜子中望出一百万英里（或许也带着骄傲，望着自己但她从未，从未露出微笑）至远远超越睡眠的地方，或者她大概是个白昼睡眠者。——狄金森",
            # [^7^]
            "为我破碎的心自豪，因为你已将它击碎，为痛苦骄傲，我对这痛苦毫无察觉直到遇见你，为我的夜晚骄傲，因为你用月亮使夜平缓，而我的谦恭并不分享你的情意。——罗伯特·勃莱",
            # [^7^]
            "在书桌前工作数周后，我终于起身去散步。月亮已经过去，在脚下耕犁，没有星星，没有一丝光亮！——罗伯特·勃莱",  # [^7^]
            "八月十五夜，月色随处好。不择茅檐与市楼，况我官居似蓬岛。——苏轼",  # [^9^]
            "春风又绿江南岸，明月何时照我还。——王安石",  # [^9^]
            "前年江外，儿女传杯兄弟会。此夜登楼，小谢清吟慰白头。——黄庭坚",  # [^9^]
            "若得长圆如此夜，人情未必看承别。——辛弃疾",  # [^9^]
            "去年今夜此堂前，人正清歌月正圆。今夜秋来人且散，不如云雾蔽青天。——宋白",  # [^9^]
            "一江春水何年尽，万古清光此夜圆。——元好问",  # [^9^]
            "此夜中秋月，清光十万家。吴歌闻隔院，边调入征笳。——邹祗谟",  # [^9^]
            "即使没有月亮，心中也是一片皎洁。——路遥",  # [^9^]
            "星星打扮好了都在下山，月亮犹犹疑疑却不孤独。——顾城",  # [^9^]
            "一个能够升起月亮的身体，必然驮住了无数次日落。——余秀华",  # [^9^]
            "月亮里一间简陋的草房里，住着一位纺纱的老太婆。——泰戈尔",  # [^13^]
            "月亮听着，笑着，一声不吭。她高举着双手，想沿着睡乡的海滩上那条来到人间的路，重返她月亮里的草房。——泰戈尔",
            # [^13^]
            "我见月亮点点头，月亮见我招招手。上帝保佑月亮，上帝保佑我。——英国儿歌",  # [^13^]
            "我见月亮点点头，月亮见我招招手。上帝保佑月亮，上帝保佑我。——《The Moon》",  # [^13^]
            "寂寂独看金烬落，纷纷只见玉山颓。自羞不是高阳侣，一夜星星骑马回。——刘禹锡",  # [^14^]
            "星垂平野阔，月涌大江流。——杜甫",  # [^14^]
            "云母屏风烛影深，长河渐落晓星沉。——李商隐",  # [^14^]
            "危楼高百尺，手可摘星辰。——李白",  # [^14^]
            "梦入蓝桥，几点疏星映朱户。——吴文英",  # [^14^]
            "王维【赠裴F将军】腰间宝剑七星文，臂上雕弓百战勋。见说云中擒黠虏，始知天上有将军。——王维",  # [^14^]
            "刘禹锡【扬州春夜李端公益张侍御登段侍御平路…以志其事】寂寂独看金烬落，纷纷只见玉山颓。自羞不是高阳侣，一夜星星骑马回。——刘禹锡",
            # [^14^]
            "温庭筠【春日野行】骑马踏烟莎，青春奈怨何。蝶翎朝粉尽，鸦背夕阳多。柳艳欺芳带，山愁萦翠蛾。别情无处说，方寸是星河。——温庭筠",
            # [^14^]
            "白居易【独眠吟二首】夜长无睡起阶前，寥落星河欲曙天。十五年来相似夜，团圆如旧几人全。——白居易",  # [^14^]
            "天接云涛连晓雾，星河欲转千帆舞。——李清照",  # [^15^]
            "拜华星之坠几，约明月之浮槎。——文天祥",  # [^15^]
            "一声已动物皆静，四座无言星欲稀。——李颀",  # [^15^]
            "昨夜斗回北，今朝岁起东。——孟浩然",  # [^15^]
            "夜は眠るためにある、眠らない夜は意味がありません。",  # 夜晚是为了睡眠而存在的，不眠之夜没有意义。
            "星の光が夜空を照らし、私たちの心も眠りの中で明らかになれる。",  # 星光照亮夜空，我们的心也在睡眠中变得明亮。
            "月の光は静かに眠る大地を守護している。",  # 月光静静地守护着沉睡的大地。
            "夜更けの静けさは、心の奥底に潜む想いを掘り起こす。",  # 深夜的寂静能唤起内心深处潜藏的思绪。
            "眠る間、時間は止まらない、但我们在睡眠中，时间不会停止。",  # 睡眠中、時間が止まらない。
            "夜は人々の心を癒す時間であり、眠りはその癒しの鍵です。",  # 夜晚是治愈人心的时间，睡眠是治愈的钥匙。
            "星屑の夜空の下、私たちは眠る前に一日のことを思い出す。",  # 在星光璀璨的夜空下，我们在睡前回忆一天的事情。
            "月の明かりが照らす道、それは眠る前に見た夢の道。",  # 月光照亮的道路，那是睡前所见梦的道路。
            "夜の静けさは、私たちの心を落ち着かせ、眠りに就くのを助ける。",  # 夜晚的宁静使我们的心平静，帮助我们入睡。
            "星の数ほどの悩みを抱えているが、夜の眠りはその全部を忘れさせる。",  # 尽管烦恼如繁星般多，但夜晚的睡眠能让我们忘记一切。
            "Ночью, как зверь, она завоет, То заплачет, как дитя, То по кровле обветшалой Вдруг соломой зашумит, То, как путник запоздалый, К нам в окошко застучит.",
            "Вечером синим, вечером лунным, Был я когда-то красивым и юным.",
            "В ночи, когда покоися мир, Мой размышляющий дух просыпается.",
            "В ночи, когда все сонят, Мои сонные ворота открываются.",
            "Ночь — это время, когда сердце забывает о суете и находит покой.",
            "Лунный свет ночи, как искра в темноте, пронзагорает в моей душе.",
            "В ночи, когда все мирно сонят, Моя душа просыпается.",
            "Ночь — это тайный союзник фантазии, который открывает воображению неограниченные горизонты.",
            "В ночи, когда все безмолвно сонят, Моя душа вечно vigilance.",
            "Ночь — это время, когда мир затмкнут, а сердце заговорит с самим собой.",
            "The night is dark, and full of terrors.",
            "A Song of Ice and Fire",
            "Good night! Sweet dreams, that flow by like rivers of silver.",
            "I have spread my dreams under your feet; Tread softly because you tread on my dreams.",
            "I am the master of my fate: I am the captain of my soul.", "Invictus",
            "The best lack all conviction, while the worst are full of passionate intensity.",
            "The Second Coming",
            "In the deep night, every dream begins to whisper to itself.",
            "Not everything that is faced can be changed, but nothing can be changed until it is faced.",
            "The night is an instrument for the怕 (fear), a bag for all sorts of cares.",
            "The stars change, but the mind remains the same.",
            "Heautontimorum",
            "The night is a time of rest, a time to dream and to heal.",
        ]
        await good_night.finish(random.choice(end_txt), at_sender=True)

daily_sign = on_command('早安', aliases={'早上好', '早'}, priority=5)
@daily_sign.handle()
async def handle(args: Message = CommandArg(), event = Event, bot = Bot):
    if time_limit():
        return
    if input_ := args.extract_plain_text():
        print(input_)
    qq = event.get_user_id()
    message_id = event.message_id
    ran_do = random.randint(1, 100)
    if ran_do >= 90:
        await daily_sign.finish(f"*猫猫不想理你，并且白了你一眼", at_sender=True, quote=message_id)
    good_morning_words = [
        "早安，愿你的每一天都像阳光一样灿烂！",
        "喵呜~ 哥哥，新的一天开始了，加油哦！",
        "早上好，愿你的心情像这清晨一样清新宁静。",
        "早安，愿你的每一步都坚定而有力。",
        "喵~ 哥哥，今天也要元气满满哦！",
        "清晨的第一缕阳光，为你带来新的希望，早上好！",
        "早安，愿你的每一天都充满爱与希望。",
        "喵喵~ 哥哥，愿你的今天比昨天更精彩！",
        "早上好，愿你的生活如诗如画，精彩纷呈。",
        "早安，愿你的每个梦想都能照进现实。",
        "喵~ 哥哥，愿你的每一天都充满阳光和笑声。",
        "清晨的微风轻轻吹过，早安！愿你的一天轻松愉快，如沐春风。",
        "早安，愿你的每一天都像彩虹一样绚丽多彩。",
        "喵呜~ 哥哥，愿你的今天充满无限可能！",
        "早上好，愿你的每一天都像清晨的露珠一样晶莹剔透，充满希望。",
        "早安，愿你的每个早晨都充满动力和灵感。",
        "喵~ 哥哥，愿你的每一天都像阳光一样明媚，像歌声一样欢快。",
        "清晨的阳光照亮心房，早安！愿你的一天充满温馨和喜悦。",
        "早安，愿你的每一天都像清晨的鸟鸣一样清脆悦耳，轻松自在。",
        "喵呜~ 哥哥，愿你的今天如同这欢快的旋律，轻松自在。",
        "早上好，愿你的每一天都像清晨的绿叶一样摇曳着生命的活力。",
        "早安，愿你的每个梦想都像清晨的露珠一样闪耀着希望的光芒。",
        "早安？都几点了。飞起来！"
    ]
    strs = [
         " 0v0  ", "(*^▽^*)", "O.o", "QaQ", "OvO", "(￣▽￣)~*", "ヾ(◍°∇°◍)ﾉﾞ","☆(ゝω･)v", "●﹏●", "awa",
        "ヾ(๑╹◡╹)ﾉ", "٩(๑>◡<๑)۶ ", "(ﾟ▽ﾟ*) ", "(≖ᴗ≖)✧", "(｡◕ˇ∀ˇ◕)", "(✧◡✧)", "φ(>ω<*) ", "(*/ω＼*)", "(｡･ω･｡)",
        "ヽ(･ω･´ﾒ)", "(〃´-ω･) ", "(>ω･* )ﾉ", "（￣︶￣）↗", "(=´ω｀=)", "(*￣3￣)╭ ", "(๑╹っ╹๑)", "☆(－ｏ⌒) ",
    ]
    modal = random.choice(good_morning_words) + random.choice(strs)
    userid = get_userid(qq)
    if userid:
        to_day = cheak_to_txt()
        print(f"当前用户：{userid}")
        notice = get_notice(userid)  # 进行白名单通知
        if notice:
            modal += f'\n对啦~您有新的通知哦~~~  {notice}' + random.choice(strs)
        if str(userid) in to_day:
            print(f"早安喵~ {userid} 今日已签到")
            modal += f'\n哥哥今天已经签过到了，猫猫就不帮哥哥签到啦~' + random.choice(strs)
        else:
            sign_get = random.randint(1, 10)
            print(f"用户: {userid} 今日未签到")
            if get_role(userid) <= 2:
                sign_get_vip = random.randint(1, 5)  # 会员额外获得硬币
                now_coin = update_Coins(userid, sign_get + sign_get_vip)
                modal += f'''\n哎呀，是我哒会员哥哥~猫猫为您签到了哦~~本次签到获得{sign_get}+{sign_get_vip}枚硬币~~ {random.choice(strs)}\n哥哥现在一共有{now_coin}枚硬币啦~什么时候给猫猫买点小鱼干呀~ {random.choice(strs)}'''
            else:
                now_coin = update_Coins(userid, sign_get)
                modal += f"\n是哥哥！(屁颠屁颠跑去签到板)给哥哥签到啦~本次签到获得了{sign_get}枚硬币~" + random.choice(strs)
                if sign_get <= 3:
                    modal += f"\n唔...不好，硬币好少..不过哥哥别生气~猫猫会努力给你找更多硬币的！！明天...或许后天~ \n不过，说起来哥哥现在一共有{now_coin}枚硬币啦~" + random.choice(strs)

                else:
                    modal += f"说起来哥哥现在一共有{now_coin}枚硬币啦~{random.choice(strs)} 什么时候给猫猫买点小鱼干呀~~{random.choice(strs)}"

            stars_random = random.randint(0, 100)  # 星星获取随机数
            if stars_random < 5:  # 5%获得 1 星星
                now_stars = update_Stars(userid, 1)
                modal += f'''\n（神神秘秘）哥哥猜猜猫猫找到了什么~~~哈哈~是星星！{random.choice(strs)}哥哥一共有{now_stars}颗星星啦~猫猫棒不棒~快夸夸我~{random.choice(strs)}'''
            elif stars_random == 99:  # 1%获得 5 星星
                now_stars = update_Stars(userid, 5)
                modal += f'''\n(超级激动)你猜！我找到什么了~\n是5颗星星！{random.choice(strs)}\n这样下来，哥哥就有{now_stars}颗星星了~{random.choice(strs)}'''
    else:
        modal += f"\n不过猫猫不认识这位哥哥，不能给哥哥签到了~{random.choice(strs)}"
        # 读取性别，切换输出
        try:
            user_info = await bot.call_api("get_stranger_info", user_id=qq)
            print(qq, "性别>>>", user_info['sex'])
            if user_info['sex'] == 'female':
                modal.replace("哥哥", "姐姐")
        except Exception as e:
            return
    await daily_sign.finish(modal, at_sender=True, quote=message_id)

def read_whitelist_applications():
    dia = {}
    base_folder = '../../白名单相关/白名单申请'  # 基础文件夹名称
    path_date_list = []  # 存储日期文件夹路径

    # 获取所有日期形式的文件夹
    for item in os.listdir(base_folder):
        item_path = os.path.join(base_folder, item)
        if os.path.isdir(item_path):
            path_date_list.append(item_path)

    # 遍历每个日期文件夹
    for path_date in path_date_list:
        for filename in os.listdir(path_date):
            if filename.endswith(".txt"):  # 确保是txt文件
                user_id, playername = filename[:-4].split('-')  # 获取userid和playername
                file_path = os.path.join(path_date, filename)  # 构造完整的文件路径

                with open(file_path, 'r', encoding='gbk') as file:  # 打开文件
                    genuine = 0  # 默认设置为0
                    paper = ''  # 初始化paper变量
                    for line in file:
                        if '申请人ID' in line:
                            continue  # 跳过第一行
                        elif '游玩方式：' in line:
                            if '正版' in line:
                                genuine = 1  # 如果是正版，设置genuine为1
                        elif '申请介绍：' in line:
                            # 读取申请介绍，直到遇到空行或文件结束
                            paper = line.split('申请介绍：', 1)[1].strip() if '申请介绍：' in line else ''
                            break  # 读取到申请介绍后，跳出循环

                # 构造字典
                dia_key = f'{os.path.basename(path_date)}#{user_id}'
                dia[dia_key] = {'playername': playername, 'genuine': genuine, 'paper': paper}

    return dia
def do_in_Server(command):
    # 创建 RCON 连接
    rcon = mcrcon.MCRcon('127.0.0.1', 'IloveCzy', 25575)  # 服务器地址、密码、端口号
    # 连接到服务器
    rcon.connect()
    # 执行 RCON 命令并获得命令响应
    response = rcon.command(command)
    # 输出命令响应
    print(response)
    # 关闭 RCON 连接
    rcon.disconnect()
    return response

def install_whitelist_json(userid):
    playername = get_playername(userid)
    do_in_Server(f'wid add {playername}')
    print(f'{playername} 已添加至白名单！')

def check_permission(qq: str):
    userid = get_userid(qq)
    if userid == 0:
        return 0
    role = get_role(userid)
    return role == 1

do_in_Server_ = on_command("Do:", rule=to_me(), priority=1)

@do_in_Server_.handle()
async def handle(event: Event, command : Message = CommandArg()):
    if time_limit():
        return
    if safe_use(event):
        await do_in_Server_.finish("T^T 在这里不允许这样做哦~", at_sender=True)
    qq = event.get_user_id()
    message_id = event.message_id
    if not check_permission(str(qq)):
        await do_in_Server_.finish("你没有权限")
    if command := command.extract_plain_text():
        if command[0:4] == "kill":
            modal = "不安全的命令： 使用/kill"
        elif command[0:2] == "op":
            modal = "不安全的命令： 使用/op"
        else:
            res = do_in_Server(command)
            modal = f"命令\"/{command}\"已执行！反馈>>>{res}"
    else:
        modal = "未知命令"
    await do_in_Server_.finish(modal, quote=message_id)


whitelist_review = on_command('白名单审核台', aliases={'审核白名单'}, priority=5)
@whitelist_review.handle()
async def handle_start(bot: Bot, event: Event, session: T_State):
    if safe_use(event):
        await whitelist_review.finish("T^T 在这里不允许这样做哦~", at_sender=True)
    qq = event.get_user_id()
    message_id = event.message_id
    print(qq)
    if not check_permission(str(qq)):
        await whitelist_review.finish("你没有权限", quote=message_id)
    applications = read_whitelist_applications()
    if not applications:
        await whitelist_review.finish("当前没有待审核的白名单申请。", quote=message_id)
    else:
        print(applications)
        session['applications'] = applications  # 存储申请信息
        await handle_next_application(bot, event, session)

async def handle_next_application(bot: Bot, event: Event, session: T_State):
    @waiter(waits=["message"], keep_session=True)
    async def get_response(event: Event):
        logger.debug(event.get_message())
        return event.get_plaintext()
    message_id = event.message_id
    applications = session.get('applications', [])
    print("applications",applications)
    if not applications:
        await whitelist_review.finish("所有申请已经审核完毕。", quote=message_id)
    else:
        current_key, current_app = applications.popitem()  # 获取第一条申请并从列表中移除
        print("current_app", current_app)
        print("current_key", current_key)
        session['current_app'] = current_app
        session['current_key'] = current_key
        await whitelist_review.send(
            f"待审核申请：游戏名 {session['current_app']['playername']}，正版状态 {session['current_app']['genuine']}\n申请介绍：{session['current_app']['paper']}\n输入 同意 or 拒绝 来审核\n输入 不看了 退出")
        doing = await get_response.wait(timeout=30)

        print(doing)
        if doing == '同意':
            current_app = session.get('current_app')
            playername = current_app['playername']
            date, user_id = current_key.split('#')[0], current_key.split('#')[1]
            # ... 执行同意操作的代码
            state_str = "已通过"
            cursor.execute('''UPDATE PlayerData
                            SET WhiteState = 1, PassDate = ?
                            WHERE UserID = ?''', datetime.strptime(date, '%Y-%m-%d'), (user_id))
            conn.commit()
            install_whitelist_json(user_id)
            await whitelist_review.send(f"用户{user_id}对游戏名{playername}的白名单申请已通过！")
        elif doing == '拒绝':
            current_app = session.get('current_app')
            playername = current_app['playername'].split('-')[0]
            date, user_id = current_key.split('#')[0], current_key.split('#')[1]
            playername = get_playername(user_id)
            # ... 执行拒绝操作的代码
            state_str = "未通过"
            await whitelist_review.send(f"用户{user_id}对游戏名{playername}的白名单申请未通过")
        elif doing == '不看了':
            await whitelist_review.finish("白名单控制台已关闭。")
        else:
            await whitelist_review.reject(f"你的操作 {doing} 我没能理解，请重新输入！")
        # 构建原始文件路径和目标文件路径
        original_path = f"../../白名单相关/白名单申请/{date}/{user_id}-{playername}.txt"
        target_path = f"../../白名单相关/已审核白名单/{date}#{user_id}-{playername}#{state_str}.txt"
        print('即将进行移动：', original_path, '>>>', target_path)
        # 确保目标目录存在
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        # 移动文件
        os.rename(original_path, target_path)
        print("已完成移动")
        await handle_next_application(bot, event, session) # 自动进入下一条审核
