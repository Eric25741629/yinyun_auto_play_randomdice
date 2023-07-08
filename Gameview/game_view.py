from Image_processing import processing_ocr
import uiautomator2 as u2
import easyocr
import time
class gameview(processing_ocr.processing_img):
    def __init__(self, d, reader: easyocr.Reader):
        super().__init__(reader, d)
    def get_string(self):
        img = self.get_screenshot()
        # reader = easyocr.Reader(['ch_tra'], gpu = True)
        result = self.reader.readtext(img, detail=0)
        return result

    def choose_game(self):
        result = self.get_string()
        print(result)
        if ('應用程式版本不同' in result):
            print('需要更新')
        if ('任務' in result and '主要任務' in result and '每日任務' in result):
                self.d.click(0.896, 0.072)  
                return 'none' 
        if (('30' in str(result) or '0/' in str(result) )and '10/' not in str(result)):
            print('沒次數,補充') 
            return 'no_times'
        if '商店' in result and '背包' in result and '娛柴' in result and '社交' in result:
            print('遊戲主介面')
            return 'main'
        if '公告' in result:
            print('公告')
            return 'news'
        if '賽季出席簿' in result:
            print('賽季出席簿')
            return 'season'
        if '結合其他骰友的力量' in result and '並盡可能地阻擋出現的怪物' in result:
            print('合作模式第一層')
            return 'cooperation_first'
        if '與好友一起進行遊戲' in result and '來場合作模式吧' in result:
            print('合作模式第二層')
            return 'cooperation_second'
        if '合作模式待機中.' in result and '開始' in result:
            print('合作模式第三層')
            return 'cooperation_third'
            # d.click(265,666)
        if '加入' in result and '請輸入編號!' in result:
            print('合作模式第三層')
            return 'cooperation_join_ok'
        if '網路連線不穩定' in result:
            self.d.click(265, 588)
            time.sleep(2)
            self.d.click(265, 588)
            time.sleep(5)
            self.d.app_start("com.percent.royaldice",
                             use_monkey=True, stop=True)
            return 'network_error'
        if '確認' in result:
            print('確認')
            return 'confirm'
        return 'none'