# view.py
import tools


class gameview():
    def __init__(self, d, reader, img_tool: tools.img_tool, str_tool: tools.str_tool, click_tool: tools.click_tool):
        self.d = d
        self.reader = reader
        self.img_tool = img_tool
        self.str_tool = str_tool
        self.click_tool = click_tool

    def choose_game(self):
        result = self.str_tool.get_text()

        conditions = {
            'main': ['對戰模式', '合作模式'],
            'news': ['公告'],
            'news1': ['在此可獲得 (隨機骰子)的最新資訊!'],
            'season': ['賽季出席簿'],
            'cooperation_first': ['卡片礦山'],
            'cooperation_second': ['結合其他骰友的力量', '並盡可能地阻擋出現的怪物'],
            'cooperation_third': ['與好友一起進行遊戲', '創建或加入房間', '來場合作模式吧!', '創建房間', '加入'],
            'cooperation_wait': ['合作模式', '合作模式待機中.'],
            'cooperation_join': ['加入', '請輸入編號!'],
            'network_error': ['網路連線不穩定'],
            'wait': ['正在替骰子拋光當中'],
            'wait1': ['登入中...'],
            'wait2': ['確認網路環境中:.'],
            'wait3': ['正在確認額外數據中'],
            'wait4': ['正在載入數據...'],
            'wait5': ['正進入遊戲等待隊伍中.'],
            'break': ['等待開始..'],
            'No_times': ['使用鑽石及觀看廣告', '補充1次', '補充5次'],
            'Known': ['合作模式入場次數補充完畢!']
        }

        for action, keywords in conditions.items():
            if all(keyword in result for keyword in keywords):
                return action
        return 'none'
