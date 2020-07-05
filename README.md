# MCDRPlugin-tpHelper
This is a minecraft MCDR server plugin, it add /tp to not op player.

## 簡介
讓非op玩家可以傳送自己到指定位置  
如果要傳送到另一名玩家身邊，需要該名玩家同意才可進行傳送  
若玩家逾時未回覆傳送請求，則視同拒絕傳送請求  

## 指令
|指令|需求權限|作用|
|:--|:--:|:--:|
|`!!tp help`|guest|列出所有指令|
|`!!tp <player_name>`|user|向`<player_name>`發送傳送到他身邊的請求|
|`!!tp <yes|no>`|user|同意或拒絕來自其他玩家傳送到身邊的請求|
|`!!tp <x> <y> <z> [<world>]`|helper|傳送自己到座標world:0=主世界(預設) 1=地獄 2=終界|

## 安裝
1. 將`tpHelper.py`放到`plugins`資料夾內  
2. 到Minecraft中輸入`!!MCDR plugin load GoogleDriveBackup`載入插件即可