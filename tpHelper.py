# coding=utf-8
import time
import json
import os

# ========= 以下為可變變數 =========
# 指令前綴
Prefix = '!!tp'

# 請求過幾秒未回覆自動拒絕
tpRequestTimeout =15

# 同意請求後等待幾秒進行傳送(<=0代表不等待)
waitTpForRequest = 5

# 權限表 0:guest 1:user 2:helper 3:admin 4:owner
MinimumPermissionLevel = {
    'help':0,
    'yes': 1,
    'no': 1,
    'back':1,
    'tpToPlayer': 1,
    'tpToPosition': 2,
}

# ========= 以下為不可變變數 =========
getPos = 'no'
def getTpList():
    f = open('plugins/tpHelper/requests.json','r',encoding='utf8')
    data = json.load(f)
    f.close()
    return data

def writeTpList(data):
    f = open('plugins/tpHelper/requests.json','w',encoding='utf8')
    json.dump(data,f)
    f.close()

def getLastTpPosList():
    f = open('plugins/tpHelper/lastPos.json','r',encoding='utf8')
    data = json.load(f)
    f.close()
    return data

def writeLastTpPosList(data):
    f = open('plugins/tpHelper/lastPos.json','w',encoding='utf8')
    json.dump(data,f)
    f.close()

def getLastTpPos(name,drop=False):
    data = getLastTpPosList()
    if name in data:
        pos = data[name]
        if drop==True:
            del data[name]
            writeLastTpPosList(data)
        return pos
    else:
        return []

def writeLastTpPos(name,x,y,z):
    data = getLastTpPosList()
    data[name] = [x,y,z]
    writeLastTpPosList(data)
    
def findBy(tag,name):
    tplist = getTpList()
    for tp in tplist:
        if name == tp[tag]:
            return tp
    return None

def create_req(server,info,name,to):
    # 新增傳送請求
    tplist = getTpList()
    tplist.append({'name':name,'to':to,'status':'wait'})
    writeTpList(tplist)
    
    # 傳送請求文字
    timeout = tpRequestTimeout
    print_message(server,info,f"已傳送請求給 {to} ，正在等待回覆!")
    server.tell(to,f"[TPH] {name}想傳送到你身邊，你同意此請求嗎?")
    server.tell(to,f"[TPH] 請於{timeout}秒內輸入 !!tp yes/no 進行回覆")
    
    # 等待回覆
    while timeout>0:
        req = findBy('name',name)
        if req['status']=='wait':
            # 未回覆，繼續等待
            time.sleep(1)
            timeout -= 1
        elif req['status']=='yes':
            # 同意
            server.tell(to,f"[TPH] 已同意{name}的傳送請求，將於{waitTpForRequest}秒後進行傳送")
            server.tell(name,f"[TPH] {to}已同意傳送請求")
            tpAfterSeconds(server,name,to,waitTpForRequest)
            break
        elif req['status']=='no':
            # 不同意
            server.tell(to,f"[TPH] 已拒絕{name}的傳送請求，取消傳送")
            server.tell(name,f"[TPH] {to}已拒絕傳送請求，取消傳送")
            break
    
    # 請求等待逾時
    if timeout==0 and tpRequestTimeout!=0:
        server.tell(to,f"[TPH] 來自{name}的請求已逾時，自動拒絕")
        server.tell(name,f"[TPH] 傳送到{to}的請求已逾時，取消傳送")
    
    # 刪除傳送請求
    delete_req(name)

def responseTpRequests(to,answer):
    tplist = getTpList()
    for tp in tplist:
        if to == tp['to']:
            tp['status'] = answer
    writeTpList(tplist)

def tpAfterSeconds(server,name,to,sec=5):
    global getPos
    while sec>0:
        server.tell(name,f"將於{sec}秒後傳送到{to}身邊!")
        time.sleep(1)
        sec -= 1
    getPos = name
    server.execute(f"/execute positioned as {name} run tp {name} ~0 ~0 ~0")
    while getPos!='no':
        time.sleep(0.05)
    server.execute(f"/tp {name} {to}")

def delete_req(name):
    tplist = getTpList()
    find = -1
    for idx,tp in enumerate(tplist):
        if name == tp['name']:
            find = idx
    if find!=-1:
        tplist.pop(find)
        writeTpList(tplist)

def on_info(server, info):
    if not info.is_user:
        global getPos
        if "Teleported" in info.content and getPos!='no':
            cmdList = info.content.split(' ')
            if getPos == cmdList[1]:
                x = cmdList[3].split('.')[0]
                y = cmdList[4].split('.')[0]
                z = cmdList[5].split('.')[0]
                writeLastTpPos(getPos,x,y,z)
                getPos = 'no'
        return
    
    command = info.content.split()
    if len(command) == 0 or command[0] != Prefix:
        return
    cmd_len = len(command)
    
    # MCDR permission check
    # check permission for !!tp <x> <y> <z>
    global MinimumPermissionLevel
    if cmd_len >= 2 and command[1] in MinimumPermissionLevel.keys():
        if server.get_permission_level(info) < MinimumPermissionLevel[command[1]]:
            print_message(server, info, '§c權限不足！§r')
            return
    elif cmd_len >= 2 and command[1].lstrip('-').isdigit():
        if server.get_permission_level(info) < MinimumPermissionLevel['tpToPosition']:
            print_message(server, info, '§c權限不足！§r')
            return
    elif cmd_len == 2 and command[0]!='help':
        if server.get_permission_level(info) < MinimumPermissionLevel['tpToPlayer']:
            print_message(server, info, '§c權限不足！§r')
            return
    try:
        # !!tp
        if cmd_len == 1:
            show_help(server,info)
        # !!tp help/<playername>/yes/no
        elif cmd_len ==2:
            if command[1]=='help':
                # !!tp help
                show_help(server,info)
            elif command[1].lower() in ['yes','no']:
                # !!tp yes/no
                req = findBy('to',info.player)
                if req==None:
                    print_message(server,info,"目前沒有待確認的請求")
                else:
                    responseTpRequests(info.player,command[1].lower())
            elif command[1].lower()=='back':
                pos = getLastTpPos(info.player,True)
                if pos!=[]:
                    server.execute(f"/tp {info.player} {pos[0]} {pos[1]} {pos[2]}")
            else:
                # !!tp <playername>
                online_player_api = server.get_plugin_instance('OnlinePlayerAPI')
                find_player = online_player_api.check_online(command[1])
                if find_player==False:
                    print_message(server,info,"請求失敗，指定的玩家不存在或未上線")
                elif findBy('name',info.player):
                    print_message(server,info,"請求失敗，你已經有一個傳送請求正在等待被確認")
                elif findBy('to',command[1]):
                    print_message(server,info,"請求失敗，對方目前已有待確認的請求")
                else:
                    create_req(server,info,info.player,command[1])
        elif cmd_len in [4,5]:
            # !!tp <x> <y> <z> [<world>]
            world={
                '0':'overworld',
                '1' :'the_nether',
                '2':'the_end'
            }
            position = ' '.join(command[1:4])
            if cmd_len==5:
                if command[4] in world.keys():
                    cmd = f"execute as {info.player} in {world[command[4]]} run tp {position}"
                    server.execute(cmd)
                else:
                    print_message(server,info,"指令錯誤，傳送世界只能為0,1,2")
            else:
                server.execute(f"/tp {info.player} {position}")
        else:
            print_message(server,info,"!!tp 指令輸入錯誤!")
            show_help(server,info)
    except Exception as e:
        #print_message(server,info,str(e))
        print_message(server,info,"!!tp 運行錯誤，請確認指令輸入是否正確!")
        show_help(server,info)

def show_help(server,info):
    print_message(server,info,f'{Prefix} <x> <y> <z> [<world>] | 傳送自己到座標world:0=主世界(預設) 1=地獄 2=終界')
    print_message(server,info,f'{Prefix} <玩家> | 請求傳送自己到<玩家>身邊')
    print_message(server,info,f'{Prefix} <yes/no> | 同意/拒絕傳送到自己身邊的請求')

def print_message(server, info, msg, tell=True, prefix='[TPH] '):
    msg = prefix + msg
    if info.is_player and not tell:
        server.say(msg)
    else:
        server.reply(info, msg)

def on_load(server, old):
    server.add_help_message(f'{Prefix} help','顯示快速傳送幫助')
    if not os.path.exists('plugins/tpHelper'):
        os.mkdir('plugins/tpHelper')
    writeTpList([])
    writeLastTpPosList({})