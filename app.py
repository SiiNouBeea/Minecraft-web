from flask import Flask, request, jsonify, render_template, render_template_string, url_for, redirect, make_response, \
    session
from datetime import datetime
import os
import pyodbc
import bcrypt
import http.client, urllib, json
import random
import requests
from pathlib import Path
import read_whitelist
import mcrcon

app = Flask(__name__)
app.secret_key = 'ABuL1314'

# 数据库连接配置
config = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': '春宵怡刻',
    'database': 'User_All',
    'uid': 'czy',
    'pwd': '1341'
}

# 连接数据库
conn = pyodbc.connect(**config)
cursor = conn.cursor()


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


# 从数据库中获取所有用户数据
# 从数据库中获取所有用户数据及其角色名称
def get_users_with_roles():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 查询所有用户及其角色名称
    query = """
    SELECT U.UserID, U.Username, U.Nickname, U.Email, R.RoleName 
    FROM Users U
    JOIN UserRoles_Con UC ON U.UserID = UC.UserID
    JOIN UserRoles R ON UC.RoleID = R.RoleID
    """
    cursor.execute(query)
    users = cursor.fetchall()

    # 将查询结果转换为字典列表
    users_data = []
    for user in users:
        users_data.append({
            'UserID': user.UserID,
            'Username': user.Username,
            'Nickname': user.Nickname,
            'Email': user.Email,
            'RoleName': user.RoleName
        })

    cursor.close()
    conn.close()
    return users_data


def get_id(username):  # 根据username获取用户userid
    cursor.execute(f"SELECT UserID FROM Users WHERE Username = '{username}'")
    userid = cursor.fetchone()[0]
    print(f"GET_ID 已从 Users 表获取用户 {username} 的 UserID 为 {userid}")
    return userid


def get_name(userid):
    cursor.execute(f"SELECT Username FROM Users WHERE UserID= '{userid}'")
    username = cursor.fetchone()[0]
    print(f"GET_Name 已从 Users 表获取用户 {userid} 的 Username 为 {username}")
    return username


def get_role(username):  # 根据uesename获取用户的权限组
    userid = get_id(username)
    cursor.execute(f"SELECT RoleID FROM UserRoles_Con WHERE UserID = '{userid}'")
    userrole = cursor.fetchone()[0]
    print(f"GET_Role 已从 UserRoles_Con 表获取用户 {userid} 的 RoleID 为 {userrole}")
    return userrole


def get_playername(userid):  # 根据uesename获取用户的玩家名
    cursor.execute(f"SELECT PlayerName FROM PlayerData WHERE UserID = '{userid}'")
    playername = cursor.fetchone()[0]
    print(f"GET_PlayerName 已从 PlayerData 表获取用户 {userid} 的 PlayerName 为 {playername.rstrip(' ')}")
    return playername.rstrip(' ')


def add_leader(dia):
    tmp = []
    now = 1
    for i in dia:
        tmp.append([now] + list(i))
        now += 1
    return tmp


def coin_leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT UserID, NickName, Coins FROM Users ORDER BY Coins DESC")
    leaderboard = cursor.fetchall()
    cursor.close()
    conn.close()
    return add_leader(leaderboard)


def star_leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT UserID, NickName, Stars FROM Users ORDER BY Stars DESC")
    leaderboard = cursor.fetchall()
    cursor.close()
    conn.close()
    return add_leader(leaderboard)


def get_public_ip():  # 获取公网ip
    response = requests.get('https://httpbin.org/ip')
    if response.status_code == 200:
        ip_data = response.json()
        return ip_data['origin']
    else:
        return request.remote_addr


def get_uuid(playername):  # 获取uuid
    response = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{playername}')
    if response.status_code == 200:
        id_data = response.json()
        return id_data['id']
    else:
        return request.remote_addr


def get_address(ip):  # 获取ip属地
    conn = http.client.HTTPSConnection('apis.tianapi.com')  # 接口域名
    params = urllib.parse.urlencode({'key': 'd607167f4b227eb77fb2c23210bbedbc', 'ip': ip, 'full': '1'})
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    conn.request('POST', '/ipquery/index', params, headers)
    tianapi = conn.getresponse()
    result = tianapi.read()
    data = result.decode('utf-8')
    dict_data = json.loads(data)
    return dict_data


# 渲染注册页面
@app.route('/register')
def show_register():
    return render_template('register.html')


# 用户注册路由
@app.route('/register', methods=['POST'])
def register():
    # 获取表单数据
    username = request.form.get('username')
    password = request.form.get('password')
    nickname = request.form.get('nickname')
    playername = request.form.get('player-name')
    email = request.form.get('email')
    phone = request.form.get('phone')

    print(username, password, nickname, playername, email, phone)
    # 检查用户名、邮箱和手机号是否已存在
    cursor.execute(
        f"SELECT Username, Email, Phone FROM Users WHERE Username = '{username}' OR Email = '{email}' OR Phone = '{phone}'")
    existing_user = cursor.fetchone()
    print(existing_user)
    name_e = 0
    email_e = 0
    phone_e = 0
    if existing_user:
        if existing_user[0] == username:
            name_e = 1
        elif existing_user[1] == email:
            email_e = 1
        elif existing_user[2] == phone:
            phone_e = 1
        return render_template('register.html', a=name_e, b=email_e, c=phone_e)

    # 加密密码
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    print(hashed_password)

    # 插入数据到数据库
    try:
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
                       (new_ID, 3, playername, 0, get_uuid(playername)))  # 给PlayerData赛数据
        conn.commit()
        return render_template('register_success.html')
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})


# 渲染登入界面
@app.route('/login')
def show_login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    # 获取表单数据
    username = request.form.get('username')
    password = request.form.get('password')

    # 这里添加数据库查询和验证逻辑
    # 假设您的数据库用户表名为 'Users'，并且有一个用户名字段 'username' 和密码字段 'password'
    print(username, password)
    cursor.execute(f"SELECT Password FROM Users WHERE Username = '{username}'")
    password_yes = cursor.fetchone()[0]
    print(password_yes, password)
    if bcrypt.checkpw(password.encode('utf-8'),
                      password_yes.encode('utf-8')):  # if bcrypt.checkpw(user_input_password, hashed_password):
        # 登录成功，重定向到登录成功页面
        userid = get_id(username)
        ip_adress = get_public_ip()
        adress_all = get_address(ip_adress)
        adress = f"{adress_all['result']['country']}-{adress_all['result']['province']}-{adress_all['result']['city']}"  # 获取ip对应的地理位置
        print(ip_adress, adress)
        cursor.execute(
            f"INSERT INTO UserLoginRecords (UserID, IPAddress, Address) VALUES ({userid}, '{ip_adress}', '{adress}')", )  # 将本次登入信息填入数据库
        conn.commit()
        session['UserID'] = userid
        session['RoleID'] = get_role(username)
        session['query_step'] = 0
        return render_template('login_success.html')  # 给登陆成功页面传入数据
    else:
        # 登录失败，返回错误消息
        return jsonify({'error': '用户名或密码错误'})


# # 渲染主界面
# @app.route('/index')
# def  show_index():
#
#     print('RoleID >>>', session['RoleID'])
#     if session['RoleID'] == 1:
#         return render_template('index_ower.html')
#     if session['RoleID'] == 2:
#         return render_template('index_vip.html')
#     if session['RoleID'] == 3:
#         return render_template('index_user.html')
#     if session['RoleID'] == 4:
#         return render_template('index.html')
#     if session['RoleID'] == 5:
#         return render_template('index_banned.html')

# 连接数据库
def get_db_connection():
    return pyodbc.connect(**config)


'''
# 执行数据库操作
@app.route('/index', methods=['POST','GET'])
def execute_query():
    print(f"Now query_step is {session['query_step']}")
    # 选择表-1
    if session['query_step'] == 0:
        table_nameHTML_all = '<label for ="table-select" > 选择数据表:</label ><select id = "table-select" name = "table_name" ><option value = "Users" > Users </option ><option value = "UserRoles" > UserRoles </option ><option value = "UserRoles_Con" > UserRoles_Con </option ><option value = "UserLoginRecords" > UserLoginRecords </option ><option value = "UserProfiles" > UserProfiles </option ><option value = "PlayerData" > PlayerData </option ></select >'
        table_nameHTML_use = '<label for ="table-select" > 选择数据表:</label ><select id = "table-select" name = "table_name" ><option value = "Users" > Users </option ><option value = "UserRoles" > UserRoles </option ><option value = "UserRoles_Con" > UserRoles_Con </option ><option value = "PlayerData" > PlayerData </option ></select >'
        if session['RoleID'] == 1:
            session['query_step'] = 1
            return render_template('index_ower.html', table_nameHTML=table_nameHTML_all)
        if session['RoleID'] == 2:
            session['query_step'] = 1
            return render_template('index_vip.html', table_nameHTML=table_nameHTML_all)
        if session['RoleID'] == 3:
            session['query_step'] = 1
            return render_template('index_user.html', table_nameHTML=table_nameHTML_use)
        if session['RoleID'] == 4:
            session['query_step'] = 1
            return render_template('index.html', table_nameHTML=table_nameHTML_use)
    # 选择操作-2
    if session['query_step'] == 1:
        conn = get_db_connection()
        cursor = conn.cursor()
        table_name = request.form.get('table_name')
        session['query_table'] = table_name
        table_nameHTML = f'<label for ="table-select" > 选择数据表(您已作出选择):</label ><select id = "table-select" name = "table_name" ><option value = "{table_name}" > {table_name} </option ></select>'
        queryHTML_all = '<label for="operation-select">选择操作:</label><select id="operation-select" name="operation"><option value="query">查询表</option><option value="update">更新表</option></select>'
        queryHTML_use = '<label for="operation-select">选择操作:</label><select id="operation-select" name="operation"><option value="query">查询表</option></select>'
        if session['RoleID'] == 1:
            session['query_step'] = 2
            return render_template('index_ower.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML_all)
        if session['RoleID'] == 2:
            session['query_step'] = 2
            return render_template('index_vip.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML_use)
        if session['RoleID'] == 3:
            session['query_step'] = 2
            return render_template('index_user.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML_use)
        if session['RoleID'] == 4:
            session['query_step'] = 2
            return render_template('index.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML_use)

    # 选择列-3
    if session['query_step'] == 2:
        operation_dia = {'query': '查询表', 'update': '更新表'}
        conn = get_db_connection()
        cursor = conn.cursor()
        operation = request.form.get('operation')
        session['query_operation'] = operation
        table_name = session['query_table']
        table_nameHTML = f'<label for ="table-select" > 选择数据表(您已作出选择):</label ><select id = "table-select" name = "table_name" ><option value = "{table_name}" > {table_name} </option ></select>'
        queryHTML = f'<label for="operation-select">选择操作(您已做出选择):</label><select id="operation-select" name="operation"><option value="{operation}">{operation_dia[operation]}</option></select>'

        if operation == 'query':
            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
            columns = [row[0] for row in cursor.fetchall()]
            print(table_name, ">>>", columns)
            listHTML = render_template_string(
                '<label for="list-select">选择目标列:</label><select id="list-select" name="list_name">{index}</select>'.format(
                    index=''.join([f'<option value="{row}">{row}</option>' for row in columns])
                )
            )
            listHTML += '<label for="relation-select">选择关系运算:</label><select id="relation-select" name="relation"><option value="=">等于 (=)</option><option value=">">大于 (>)</option><option value=">=">大于等于 (>=)</option><option value="<">小于 (<)</option><option value="<=">小于等于 (<=)</option><option value="!=">不等于 (!=)</option></select>'
            listHTML += '<label for="query-input">查询条件:</label><input type="text" id="query-input" name="query" placeholder="Enter condition..." maxlength="15">'
            print(listHTML)
            if session['RoleID'] == 1:
                session['query_step'] = 3
                return render_template('index_ower.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML, listHTML=listHTML)
            if session['RoleID'] == 2:
                session['query_step'] = 3
                return render_template('index_vip.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML, listHTML=listHTML)
            if session['RoleID'] == 3:
                session['query_step'] = 3
                return render_template('index_user.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML, listHTML=listHTML)
            if session['RoleID'] == 4:
                session['query_step'] = 3
                return render_template('index.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML, listHTML=listHTML)
        elif operation == 'update':
            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
            columns = [row[0] for row in cursor.fetchall()]
            listHTML = render_template_string(
                '<label for="list-select-while">选择更新依据列:</label><select id="list-select-while" name="while_list_name">{index}</select>'.format(
                    index=''.join([f'<option value="{row}">{row}</option>' for row in columns])
                )
            )
            listHTML += '<label for="relation-select">选择关系运算:</label><select id="relation-select" name="relation"><option value="=">等于 (=)</option><option value=">">大于 (>)</option><option value=">=">大于等于 (>=)</option><option value="<">小于 (<)</option><option value="<=">小于等于 (<=)</option><option value="!=">不等于 (!=)</option></select>'
            listHTML += '<label for="query-input">查询条件:</label><input type="text" id="query-input" name="query" placeholder="Enter condition..." maxlength="15">'
            listTMP = render_template_string(
                '<label for="list-select-set">选择被更新列:</label><select id="list-select-set" name="set_list_name">{index}</select>'.format(
                    index=''.join([f'<option value="{row}">{row}</option>' for row in columns])
                )
            )
            listHTML += listTMP
            listHTML += '<label for="update-input">更新为:</label><input type="text" id="update-input" name="update_data" placeholder="Enter New value..." maxlength="15">'
            print(listHTML)
            if session['RoleID'] == 1:
                session['query_step'] = 3
                return render_template('index_ower.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
            if session['RoleID'] == 2:
                session['query_step'] = 3
                return render_template('index_vip.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                        listHTML=listHTML)
            if session['RoleID'] == 3:
                session['query_step'] = 3
                return render_template('index_user.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
            if session['RoleID'] == 4:
                session['query_step'] = 3
                return render_template('index.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
    # 运算
    if session['query_step'] == 3:
        operation_dia = {'query': '查询表', 'update': '更新表'}
        conn = get_db_connection()
        cursor = conn.cursor()
        table_name = session['query_table']
        operation = session['query_operation']
        table_nameHTML = f'<label for ="table-select" > 选择数据表(您已作出选择):</label ><select id = "table-select" name = "table_name" ><option value = "{table_name}" > {table_name} </option ></select>'
        queryHTML = f'<label for="operation-select">选择操作(您已做出选择):</label><select id="operation-select" name="operation"><option value="{operation}">{operation_dia[operation]}</option></select>'
        try:
            if operation == 'query':  # 查询
                # 获取操作
                list_name = request.form.get('list_name')  # 目标列
                query = request.form.get('query')  # 条件
                relation = request.form.get(('relation'))  # 条件运算符

                cursor.execute(f"SELECT * FROM {table_name} WHERE {list_name} {relation} {query}")
                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()
                print(columns, results)
                print(len(results))
                if table_name == 'Users':
                    for i in range(0, len(results)):
                        results[i][2] = '*受保护*'
                tableHTML = render_template_string(
                    '<h3>表: {table_name}</h3><table><tr>{headers}</tr>{rows}</table>'.format(
                        table_name=table_name,
                        headers=''.join([f'<th>{column}</th>' for column in columns]),
                        rows=''.join(
                            ['<tr>' + ''.join([f'<td>{cell}</td>' for cell in row]) + '</tr>' for row in results])
                    )
                )
                session['query_step'] = 0
                print(tableHTML)
                listHTML = f'<span>SELECT * FROM {table_name} WHERE {list_name} {relation} {query}</span>'
                if session['RoleID'] == 1:
                    return render_template('index_ower.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
                if session['RoleID'] == 2:
                    return render_template('index_vip.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
                if session['RoleID'] == 3:
                    return render_template('index_user.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
                if session['RoleID'] == 4:
                    return render_template('index.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)

            elif operation == 'update':  # 更新
                while_list_name = request.form.get('while_list_name')  # 条件列
                set_list_name = request.form.get('set_list_name')  # 目标列
                query = request.form.get('query')  # 条件
                relation = request.form.get(('relation'))  # 条件运算符
                update_data = request.form.get('update_data')  # 更新值

                cursor.execute(f"SELECT * FROM {table_name} WHERE {while_list_name} {relation} {query}")
                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()
                print(columns, results)
                print(len(results))
                if table_name == 'Users':
                    for i in range(0, len(results)):
                        results[i][2] = '*受保护*'
                tableHTML = render_template_string(
                    '<h3>旧表: {table_name}</h3><table><tr>{headers}</tr>{rows}</table>'.format(
                        table_name=table_name,
                        headers=''.join([f'<th>{column}</th>' for column in columns]),
                        rows=''.join(
                            ['<tr>' + ''.join([f'<td>{cell}</td>' for cell in row]) + '</tr>' for row in results])
                    )
                )

                # 更新
                cursor.execute(f"UPDATE {table_name} SET {set_list_name} = {update_data} WHERE {while_list_name} {relation} {query};")
                conn.commit()  # 提交更新
                print("OKOKOKOK")

                cursor.execute(f"SELECT * FROM {table_name} WHERE {while_list_name} {relation} {query}")
                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()
                print(columns, results)
                print(len(results))
                if table_name == 'Users':
                    for i in range(0, len(results)):
                        results[i][2] = '*受保护*'
                tableTMP = render_template_string(
                    '<h3>更新后表: {table_name}</h3><table><tr>{headers}</tr>{rows}</table>'.format(
                        table_name=table_name,
                        headers=''.join([f'<th>{column}</th>' for column in columns]),
                        rows=''.join(
                            ['<tr>' + ''.join([f'<td>{cell}</td>' for cell in row]) + '</tr>' for row in results])
                    )
                )
                tableHTML += tableTMP
                listHTML = f'<span>UPDATE {table_name} SET {set_list_name} = {update_data} WHERE {while_list_name} {relation} {query}</span>'
                session['query_step'] = 0
                if session['RoleID'] == 1:
                    return render_template('index_ower.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
                if session['RoleID'] == 2:
                    return render_template('index_vip.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
                if session['RoleID'] == 3:
                    return render_template('index_user.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
                if session['RoleID'] == 4:
                    return render_template('index.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
        except Exception as e:
            return render_template('index.html', error=str(e))
        finally:
            cursor.close()
            conn.close()


    print(table_name, operation, query)
'''


def update_Coins(user_id, num):
    # 这里添加更新数据库的代码

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
    file_name = f"签到日志/{today_date}.txt"
    path = os.path.join('', file_name)
    with open(path, 'a') as file:
        file.write(f"{user_id}\n")


def cheak_to_txt():
    # 获取当前日期并格式化为 'YYYY-MM-DD' 格式
    today_date = datetime.now().strftime('%Y-%m-%d')
    # 构造文件名
    file_name = f"签到日志/{today_date}.txt"
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
    base_folder = '白名单相关/已审核白名单'  # 基础文件夹名称
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


@app.route('/index', methods=['POST', 'GET'])
def index():
    to_day = cheak_to_txt()
    if session.get('UserID') is not None:
        modalHTML = ''
        userid = session['UserID']
        notice = get_notice(userid)  # 进行白名单通知
        if notice:
            modalHTML += f'<p style="color: #a00000;">白名单审核通知：{notice}</p>'
        if str(userid) in to_day:
            print(f"用户: {userid} 今日已签到")
            modalHTML += f'<p>您今日已签到！</p>'
        else:
            sign_get = random.randint(1, 10)
            print(f"用户: {userid} 今日未签到")
            if session['RoleID'] <= 2:
                sign_get_vip = random.randint(1, 5)  # 会员额外获得硬币
                now_coin = update_Coins(userid, sign_get + sign_get_vip)
                modalHTML += f'''
            <p>尊敬的VIP用户：签到成功！本次签到获得{sign_get}+<span style="color: #FFD700;">{sign_get_vip}</span>枚硬币！</p><p style="font-size: 12px; line-height: 0.8px">VIP用户可以获得额外签到硬币哦~</p>
            <p>您现在一共有{now_coin}枚硬币！</p>
                '''
            else:
                now_coin = update_Coins(userid, sign_get)
                modalHTML += f'''
                            <p>尊敬的用户：签到成功！本次签到获得{sign_get}枚硬币！</p>
                            <p>您现在一共有{now_coin}枚硬币！</p>
                                '''

            stars_random = random.randint(0, 100)  # 星星获取随机数
            if stars_random < 5:  # 5%获得 1 星星
                now_stars = update_Stars(userid, 1)
                modalHTML += f'''
                            <p>幸运！本次签到获得 <span style="color: #66CCFF;">1</span> 颗星星！</p>
                            <p>您现在一共有 <span style="color: #66CCFF;">{now_stars}</span> 颗星星！</p>
                            '''
            elif stars_random == 99:  # 1%获得 5 星星
                now_stars = update_Stars(userid, 5)
                modalHTML += f'''
                            <p><span style="color: #FFD700;">大幸运！！！</span>本次签到获得 <span style="color: #66CCFF;">5</span> 颗星星！</p>
                            <p>您现在一共有 <span style="color: #66CCFF;">{now_stars}</span> 颗星星！</p>
                            '''
    else:
        modalHTML = f'<p>您还未登陆！</p>'
    coin_l = coin_leaderboard()
    star_l = star_leaderboard()
    print(coin_l)
    print(star_l)
    coinleader = render_template_string(
        '<table><tr><th>名次</th><th>UID</th><th>昵称</th><th>硬币</th></tr>{rows}</table>'.format(
            rows=''.join(
                ['<tr>' + ''.join([f'<td>{cell}</td>' for cell in row]) + '</tr>' for row in coin_l])
        )
    )
    starsleader = render_template_string(
        '<table><tr><th>名次</th><th>UID</th><th>昵称</th><th>星星</th></tr>{rows}</table>'.format(
            rows=''.join(
                ['<tr>' + ''.join([f'<td>{cell}</td>' for cell in row]) + '</tr>' for row in star_l])
        )
    )
    print(coinleader, starsleader)
    if session.get('RoleID') is None:
        return render_template('index.html', coin=coinleader, stars=starsleader, modalHTML=modalHTML)
    print('RoleID >>>', session['RoleID'])
    if session['RoleID'] == 1:
        return render_template('index_ower.html', coin=coinleader, stars=starsleader, modalHTML=modalHTML)
    if session['RoleID'] == 2:
        return render_template('index_vip.html', coin=coinleader, stars=starsleader, modalHTML=modalHTML)
    if session['RoleID'] == 3:
        return render_template('index_user.html', coin=coinleader, stars=starsleader, modalHTML=modalHTML)
    if session['RoleID'] == 4:
        return render_template('index.html', coin=coinleader, stars=starsleader, modalHTML=modalHTML)
    if session['RoleID'] == 5:
        return render_template('index_banned.html')
    else:
        return render_template('index.html', coin=coinleader, stars=starsleader, modalHTML=modalHTML)


def write_to_file_whitelist(user_id, paper, genuiner):
    # 获取当前日期并格式化为 'YYYY-MM-DD' 格式
    today_date = datetime.now().strftime('%Y-%m-%d')
    playername = get_playername(user_id)
    if genuiner:
        genuiner = '正版'
    else:
        genuiner = '离线'
    # 构造文件名
    file_name = f"白名单相关/白名单申请/{today_date}/{user_id}-{playername}.txt"
    path = os.path.join('', file_name)
    # 检查文件夹是否存在
    folder_path = os.path.dirname(file_name)
    # 检查文件夹是否存在，如果不存在则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # 构造完整的文件路径
    path = os.path.join(os.getcwd(), file_name)
    with open(path, 'a') as file:
        file.write(f"申请人ID: {user_id}:{playername.rstrip(' ')}\n游玩方式：{genuiner}\n申请介绍：{paper}\n")


def look_whitelist(user_id):  # 检查是否重复申请
    # 获取当前日期并格式化为 'YYYY-MM-DD' 格式
    today_date = datetime.now().strftime('%Y-%m-%d')
    playername = get_playername(user_id)
    path_name = Path(f"白名单相关/白名单申请/{today_date}")
    # 构造文件名
    file_name = f"{user_id}-{playername}.txt"
    haven_look_file_name = f"looked#{user_id}-{playername}.txt"
    file_path = path_name / file_name
    haven_file_path = path_name / haven_look_file_name
    # 初始化一个空列表来存储文件中的行
    # 检查文件是否存在
    if file_path.is_file() or haven_file_path.is_file():
        print(f"文件 {file_name} 已存在。用户重复申请！")
        return False
    else:
        print(f"文件 {file_name} 不存在。可以申请！")
        return True


def look_white(bool, user_id):
    if bool:
        return "已通过"
    else:
        if look_whitelist(user_id):
            return "未通过 <a href='/get_white' style='font-size: 12px;'>去申请</a>"
        else:
            return "未通过 <a  style='font-size: 12px;'>今日已申请！请等待审核结果</a>"


# 个人主页
@app.route('/My', methods=['POST', 'GET'])
def show_My():
    session['query_step'] = 0
    userid = session['UserID']
    roleid = get_role(get_name(userid))
    print(userid)
    cursor.execute(f"SELECT Stars, Coins, CreatedAt, Email, NickName FROM Users WHERE UserID = {userid}")
    userdata = cursor.fetchone()
    user_info = {'UserID': userid, 'RoleID': roleid, 'Stars': userdata[0], 'Coins': userdata[1],
                 'CreateAt': userdata[2], 'Email': userdata[3], 'NickName': userdata[4]}
    # 权限组id
    cursor.execute(f"SELECT RoleName FROM UserRoles WHERE RoleID = {roleid}")
    userdata = cursor.fetchone()[0]
    user_info['RoleName'] = userdata
    # 生日
    cursor.execute(f"SELECT FORMAT(Birthday, 'yyyy-MM-dd') AS FormattedDate FROM UserProfiles WHERE UserID = {userid}")
    userdata = cursor.fetchone()[0]
    user_info['Birthday'] = userdata
    # 姓名、性别、简介
    cursor.execute(f"SELECT FirstName,LastName,Gender,Bio FROM UserProfiles WHERE UserID = {userid}")
    userdata = cursor.fetchone()
    user_info['FirstName'] = userdata[0]
    user_info['LastName'] = userdata[1]
    user_info['Gender'] = userdata[2]
    user_info['Bio'] = userdata[3]
    # 游戏数据
    cursor.execute(f"SELECT PlayerID, uuid, PlayerName, WhiteState FROM PlayerData WHERE UserID = {userid}")
    userdata = cursor.fetchone()
    user_info.update({'PlayerID': userdata[0], 'UUID': userdata[1].rstrip(),
                      'PlayerName': userdata[2].rstrip(), 'WhiteState': look_white(userdata[3], userid)})

    print(user_info)
    # 之后在这添加
    cursor.execute(f"SELECT * FROM UserLoginRecords WHERE UserID = {userid}")
    columns = [column[0] for column in cursor.description]
    results = cursor.fetchall()
    LoginHTML = render_template_string(
        '<table><tr>{headers}</tr>{rows}</table>'.format(
            headers=''.join([f'<th>{column}</th>' for column in columns]),
            rows=''.join(['<tr>' + ''.join([f'<td>{cell}</td>' for cell in row]) + '</tr>' for row in results])
        )
    )
    print(userid, ">>", LoginHTML)
    session['User_info'] = user_info
    if roleid == 1:  # 操作台
        users = get_users_with_roles()
        print(users)

        return render_template('Owner.html', user_info=user_info, LoginHTML=LoginHTML, users=users)
    return render_template('My.html', user_info=user_info, LoginHTML=LoginHTML)


@app.route('/set_Profile')
def show_set_Profile():
    return render_template('set_Profile.html', user_info=session['User_info'])


# 个人信息修改
@app.route('/set_Profile', methods=['POST'])
def set_Profile():
    first_name = request.form.get('FirstName')
    last_name = request.form.get('LastName')
    gender = request.form.get('Gender')
    birthday = request.form.get('Birthday')
    bio = request.form.get('Bio')
    print(first_name)
    # 连接数据库并执行更新语句
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''UPDATE UserProfiles
        SET FirstName = ?, LastName = ?, Gender = ?, Birthday = ?, Bio = ?
        WHERE UserID = ?''', (first_name, last_name, gender, birthday, bio, session['User_info']['UserID']))
        conn.commit()
        return render_template('set_profile_success.html')  # 重定向到个人主页
    except pyodbc.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


@app.route('/get_white')
def show_get_white():
    if look_whitelist(session['User_info']['UserID']):
        return render_template('get_white.html', user_info=session['User_info'])
    else:
        return render_template('haven_get_whist.html')


# 个人信息修改
@app.route('/get_white', methods=['POST'])
def get_white():
    playername = request.form.get('PlayerName')
    genuine = request.form.get('Genuine')
    paper = request.form.get('paper')
    print(playername, genuine, paper)

    # 连接数据库并执行更新语句
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''UPDATE PlayerData
        SET PlayerName = ?, Genuine = ?, uuid = ?
        WHERE UserID = ?''', (playername, genuine, get_uuid(playername), session['User_info']['UserID']))
        conn.commit()
        write_to_file_whitelist(session['User_info']['UserID'], paper, genuine)
        return render_template('get_whitelist_success.html')  # 重定向到个人主页
    except pyodbc.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


def install_whitelist_json(userid):
    playername = get_playername(userid)
    do_in_Server(f'wid add {playername}')
    print(f'{playername} 已添加至白名单！')


# 白名单审核页面
@app.route('/Whitelist_table', methods=['GET'])
def whitelist_table():
    # 这里应该是获取所有待审核申请的逻辑
    # 例如，从dia字典中获取所有申请
    applications = read_whitelist.read_whitelist_applications()
    applyHTML = read_whitelist.generate_html_from_dia(applications)
    return render_template('Whitelist_table.html', applyHTML=applyHTML)


# 白名单审核
@app.route('/approve_applicationt', methods=['POST'])
def approve_application():
    userid = request.form.get('userid')
    date = request.form.get('date')
    state = request.form.get('state')
    playername = get_playername(userid)
    if state == '1':
        state_str = "已通过"
        cursor.execute('''UPDATE PlayerData
                SET WhiteState = 1, PassDate = ?
                WHERE UserID = ?''', datetime.strptime(date, '%Y-%m-%d'), (userid))
        conn.commit()
        install_whitelist_json(userid)
        print(f"用户{userid}对游戏名{playername}的白名单申请已通过！")
    else:
        state_str = "未通过"
        print(f"用户{userid}对游戏名{playername}的白名单申请未通过")
    # 构建原始文件路径和目标文件路径
    original_path = f"白名单相关/白名单申请/{date}/{userid}-{playername}.txt"
    target_path = f"白名单相关/已审核白名单/{date}#{userid}-{playername}#{state_str}.txt"
    print('即将进行移动：', original_path, '>>>', target_path)
    # 确保目标目录存在
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    # 移动文件
    os.rename(original_path, target_path)
    print("已完成移动")
    # 重定向回审核页面或执行其他操作
    return redirect(url_for('whitelist_table'))


# 执行数据库操作
@app.route('/Owner_table', methods=['POST', 'GET'])
def execute_query_1():
    if session['RoleID'] != 1:
        return '您没有权限！'
    print(f"{session['UserID']}>>>正在使用数据库控制系统")
    print(f"Now query_step is {session['query_step']}")
    if session['query_step'] == 0:
        table_nameHTML_all = '<label for ="table-select" > 选择数据表:</label ><select id = "table-select" name = "table_name" ><option value = "Users" > Users </option ><option value = "UserRoles" > UserRoles </option ><option value = "UserRoles_Con" > UserRoles_Con </option ><option value = "UserLoginRecords" > UserLoginRecords </option ><option value = "UserProfiles" > UserProfiles </option ><option value = "PlayerData" > PlayerData </option ></select >'
        table_nameHTML_use = '<label for ="table-select" > 选择数据表:</label ><select id = "table-select" name = "table_name" ><option value = "Users" > Users </option ><option value = "UserRoles" > UserRoles </option ><option value = "UserRoles_Con" > UserRoles_Con </option ><option value = "PlayerData" > PlayerData </option ></select >'
        if session['RoleID'] == 1:
            session['query_step'] = 1
            return render_template('Owner_table.html', table_nameHTML=table_nameHTML_all)
        if session['RoleID'] == 2:
            session['query_step'] = 1
            return render_template('index_vip.html', table_nameHTML=table_nameHTML_all)
        if session['RoleID'] == 3:
            session['query_step'] = 1
            return render_template('index_user.html', table_nameHTML=table_nameHTML_use)
        if session['RoleID'] == 4:
            session['query_step'] = 1
            return render_template('index.html', table_nameHTML=table_nameHTML_use)
    # 选择操作-2

    if session['query_step'] == 1:
        conn = get_db_connection()
        cursor = conn.cursor()
        table_name = request.form.get('table_name')
        session['query_table'] = table_name
        table_nameHTML = f'<label for ="table-select" > 选择数据表(您已作出选择):</label ><select id = "table-select" name = "table_name" ><option value = "{table_name}" > {table_name} </option ></select>'
        queryHTML_all = '<label for="operation-select">选择操作:</label><select id="operation-select" name="operation"><option value="query">查询表</option><option value="update">更新表</option></select>'
        queryHTML_use = '<label for="operation-select">选择操作:</label><select id="operation-select" name="operation"><option value="query">查询表</option></select>'
        if session['RoleID'] == 1:
            session['query_step'] = 2
            return render_template('Owner_table.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML_all)
        if session['RoleID'] == 2:
            session['query_step'] = 2
            return render_template('index_vip.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML_use)
        if session['RoleID'] == 3:
            session['query_step'] = 2
            return render_template('index_user.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML_use)
        if session['RoleID'] == 4:
            session['query_step'] = 2
            return render_template('index.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML_use)

        # 选择列-3
    if session['query_step'] == 2:
        operation_dia = {'query': '查询表', 'update': '更新表'}
        conn = get_db_connection()
        cursor = conn.cursor()
        operation = request.form.get('operation')
        session['query_operation'] = operation
        table_name = session['query_table']
        table_nameHTML = f'<label for ="table-select" > 选择数据表(您已作出选择):</label ><select id = "table-select" name = "table_name" ><option value = "{table_name}" > {table_name} </option ></select>'
        queryHTML = f'<label for="operation-select">选择操作(您已做出选择):</label><select id="operation-select" name="operation"><option value="{operation}">{operation_dia[operation]}</option></select>'

        if operation == 'query':
            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
            columns = [row[0] for row in cursor.fetchall()]
            print(table_name, ">>>", columns)
            listHTML = render_template_string(
                '<label for="list-select">选择目标列:</label><select id="list-select" name="list_name">{index}</select>'.format(
                    index=''.join([f'<option value="{row}">{row}</option>' for row in columns])
                )
            )
            listHTML += '<label for="relation-select">选择关系运算:</label><select id="relation-select" name="relation"><option value="=">等于 (=)</option><option value=">">大于 (>)</option><option value=">=">大于等于 (>=)</option><option value="<">小于 (<)</option><option value="<=">小于等于 (<=)</option><option value="!=">不等于 (!=)</option></select>'
            listHTML += '<label for="query-input">查询条件:</label><input type="text" id="query-input" name="query" placeholder="Enter condition..." maxlength="15">'
            print(listHTML)
            if session['RoleID'] == 1:
                session['query_step'] = 3
                return render_template('Owner_table.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
            if session['RoleID'] == 2:
                session['query_step'] = 3
                return render_template('index_vip.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
            if session['RoleID'] == 3:
                session['query_step'] = 3
                return render_template('index_user.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
            if session['RoleID'] == 4:
                session['query_step'] = 3
                return render_template('index.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
        elif operation == 'update':
            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
            columns = [row[0] for row in cursor.fetchall()]
            listHTML = render_template_string(
                '<label for="list-select-while">选择更新依据列:</label><select id="list-select-while" name="while_list_name">{index}</select>'.format(
                    index=''.join([f'<option value="{row}">{row}</option>' for row in columns])
                )
            )
            listHTML += '<label for="relation-select">选择关系运算:</label><select id="relation-select" name="relation"><option value="=">等于 (=)</option><option value=">">大于 (>)</option><option value=">=">大于等于 (>=)</option><option value="<">小于 (<)</option><option value="<=">小于等于 (<=)</option><option value="!=">不等于 (!=)</option></select>'
            listHTML += '<label for="query-input">查询条件:</label><input type="text" id="query-input" name="query" placeholder="Enter condition..." maxlength="15">'
            listTMP = render_template_string(
                '<label for="list-select-set">选择被更新列:</label><select id="list-select-set" name="set_list_name">{index}</select>'.format(
                    index=''.join([f'<option value="{row}">{row}</option>' for row in columns])
                )
            )
            listHTML += listTMP
            listHTML += '<label for="update-input">更新为:</label><input type="text" id="update-input" name="update_data" placeholder="Enter New value..." maxlength="15">'
            print(listHTML)
            if session['RoleID'] == 1:
                session['query_step'] = 3
                return render_template('Owner_table.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
            if session['RoleID'] == 2:
                session['query_step'] = 3
                return render_template('index_vip.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
            if session['RoleID'] == 3:
                session['query_step'] = 3
                return render_template('index_user.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
            if session['RoleID'] == 4:
                session['query_step'] = 3
                return render_template('index.html', table_nameHTML=table_nameHTML, queryHTML=queryHTML,
                                       listHTML=listHTML)
        # 运算
    if session['query_step'] == 3:
        operation_dia = {'query': '查询表', 'update': '更新表'}
        conn = get_db_connection()
        cursor = conn.cursor()
        table_name = session['query_table']
        operation = session['query_operation']
        table_nameHTML = f'<label for ="table-select" > 选择数据表(您已作出选择):</label ><select id = "table-select" name = "table_name" ><option value = "{table_name}" > {table_name} </option ></select>'
        queryHTML = f'<label for="operation-select">选择操作(您已做出选择):</label><select id="operation-select" name="operation"><option value="{operation}">{operation_dia[operation]}</option></select>'
        try:
            if operation == 'query':  # 查询
                # 获取操作
                list_name = request.form.get('list_name')  # 目标列
                query = request.form.get('query')  # 条件
                relation = request.form.get(('relation'))  # 条件运算符

                cursor.execute(f"SELECT * FROM {table_name} WHERE {list_name} {relation} {query}")
                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()
                print(columns, results)
                print(len(results))
                if table_name == 'Users':
                    for i in range(0, len(results)):
                        results[i][2] = '*受保护*'
                tableHTML = render_template_string(
                    '<h3>表: {table_name}</h3><table><tr>{headers}</tr>{rows}</table>'.format(
                        table_name=table_name,
                        headers=''.join([f'<th>{column}</th>' for column in columns]),
                        rows=''.join(
                            ['<tr>' + ''.join([f'<td>{cell}</td>' for cell in row]) + '</tr>' for row in results])
                    )
                )
                session['query_step'] = 0
                print(tableHTML)
                listHTML = f'<span>SELECT * FROM {table_name} WHERE {list_name} {relation} {query}</span>'
                if session['RoleID'] == 1:
                    return render_template('Owner_table.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML,
                                           queryHTML=queryHTML,
                                           listHTML=listHTML)
                if session['RoleID'] == 2:
                    return render_template('index_vip.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML,
                                           queryHTML=queryHTML,
                                           listHTML=listHTML)
                if session['RoleID'] == 3:
                    return render_template('index_user.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML,
                                           queryHTML=queryHTML,
                                           listHTML=listHTML)
                if session['RoleID'] == 4:
                    return render_template('index.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML,
                                           queryHTML=queryHTML,
                                           listHTML=listHTML)

            elif operation == 'update':  # 更新
                while_list_name = request.form.get('while_list_name')  # 条件列
                set_list_name = request.form.get('set_list_name')  # 目标列
                query = request.form.get('query')  # 条件
                relation = request.form.get(('relation'))  # 条件运算符
                update_data = request.form.get('update_data')  # 更新值

                cursor.execute(f"SELECT * FROM {table_name} WHERE {while_list_name} {relation} {query}")
                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()
                print(columns, results)
                print(len(results))
                if table_name == 'Users':
                    for i in range(0, len(results)):
                        results[i][2] = '*受保护*'
                tableHTML = render_template_string(
                    '<h3>旧表: {table_name}</h3><table><tr>{headers}</tr>{rows}</table>'.format(
                        table_name=table_name,
                        headers=''.join([f'<th>{column}</th>' for column in columns]),
                        rows=''.join(
                            ['<tr>' + ''.join([f'<td>{cell}</td>' for cell in row]) + '</tr>' for row in results])
                    )
                )

                # 更新
                cursor.execute(
                    f"UPDATE {table_name} SET {set_list_name} = {update_data} WHERE {while_list_name} {relation} {query};")
                conn.commit()  # 提交更新
                print("OKOKOKOK")

                cursor.execute(f"SELECT * FROM {table_name} WHERE {while_list_name} {relation} {query}")
                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()
                print(columns, results)
                print(len(results))
                if table_name == 'Users':
                    for i in range(0, len(results)):
                        results[i][2] = '*受保护*'
                tableTMP = render_template_string(
                    '<h3>更新后表: {table_name}</h3><table><tr>{headers}</tr>{rows}</table>'.format(
                        table_name=table_name,
                        headers=''.join([f'<th>{column}</th>' for column in columns]),
                        rows=''.join(
                            ['<tr>' + ''.join([f'<td>{cell}</td>' for cell in row]) + '</tr>' for row in results])
                    )
                )
                tableHTML += tableTMP
                listHTML = f'<span>UPDATE {table_name} SET {set_list_name} = {update_data} WHERE {while_list_name} {relation} {query}</span>'
                session['query_step'] = 0
                if session['RoleID'] == 1:
                    return render_template('Owner_table.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML,
                                           queryHTML=queryHTML,
                                           listHTML=listHTML)
                if session['RoleID'] == 2:
                    return render_template('index_vip.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML,
                                           queryHTML=queryHTML,
                                           listHTML=listHTML)
                if session['RoleID'] == 3:
                    return render_template('index_user.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML,
                                           queryHTML=queryHTML,
                                           listHTML=listHTML)
                if session['RoleID'] == 4:
                    return render_template('index.html', tableHTML=tableHTML, table_nameHTML=table_nameHTML,
                                           queryHTML=queryHTML,
                                           listHTML=listHTML)
        except Exception as e:
            return render_template('index.html', error=str(e))
        finally:
            cursor.close()
            conn.close()


# 指令执行
@app.route('/do_command', methods=['post'])
def do_command():
    if session['RoleID'] == 1:
        session['query_step'] = 0
        print(f"{session['UserID']}>>>正在使用指令控制系统")
        commamd = request.form.get('command')
        if commamd[0:4] == "kill":
            modalHTML = f"<p style='color: #66ccff'>出于安全考虑，命令\"/{commamd}\"无法执行！</p><span style='color: #66cc00'>反馈>>></span> 你不能这么做！原因：使用/kill指令"
            print(f"{session['UserID']}已拦截命令：{commamd}，原因：使用/kill")
        elif commamd[0:2] == "op":
            modalHTML = f"<p style='color: #66ccff'>出于安全考虑，命令\"/{commamd}\"无法执行！</p><span style='color: #66cc00'>反馈>>></span> 你不能这么做！原因：尝试使用/op指令"
            print(f"{session['UserID']}已拦截命令：{commamd}，原因：尝试使用/op")
        else:
            res = do_in_Server(commamd)
            modalHTML = f"<p style='color: #66ccff'>命令\"/{commamd}\"已执行！</p><span style='color: #66cc00'>反馈>>></span>{res}"
        return render_template('Owner_table.html', modalHTML=modalHTML, lastcommand=commamd)
    else:
        return "您没有权限使用！"


# 登出
@app.route('/logout')
def logout():
    # 清除会话中的所有数据
    session.clear()
    # 重定向到登录页面
    return render_template('logout.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
