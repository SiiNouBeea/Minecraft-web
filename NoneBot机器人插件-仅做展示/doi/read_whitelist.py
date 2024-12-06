import os

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

def generate_html_from_dia(dia):
    html_output = ''
    if not dia:  # 没有读到内容
        html_output += '<h2 style="text-align: center;">当前没有白名单申请</>'
        return html_output
    for key, value in dia.items():
        date, user_id = key.split('#')[0], key.split('#')[1]  # 从key中提取UserID, Date
        html_output += f'<div class="application">'
        html_output += f'<div class="header">UserID: <span style="color: #66ccff">{user_id}</span>&nbsp&nbsp&nbspPlayerName: <span style="color: #66ccff">{value["playername"]}</span></div>'
        html_output += f'<div class="content">{value["paper"]}<br><br></div>'
        html_output += '<div class="button-container">'
        html_output += f"""
    <form action="/approve_applicationt" method="post">
    <input type="hidden" name="userid" value="{user_id}">
    <input type="hidden" name="date" value="{date}">
    <input type="hidden" name="state" value=1>
    <button type="submit" class="green-gradient-button">同意</button>
    </form>
    <form action="/approve_applicationt" method="post">
    <input type="hidden" name="userid" value="{user_id}">
    <input type="hidden" name="date" value="{date}">
    <input type="hidden" name="state" value=0>
    <button type="submit" class="red-gradient-button">拒绝</button>
    </form>
        """
        html_output += '</div>'
        html_output += '</div>'

    return html_output


