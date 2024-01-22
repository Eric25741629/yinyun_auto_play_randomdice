import load_models
import os
from multiprocessing import Process
import random
import threading
import time
import easyocr
from adbutils import adb
from pic_tranform import *
from control_game import *
from queue import Queue
from PrepareGame import *
from Tools.Img_tool import img_tools
import tools
import win32gui


def handle_find(name: str) -> int:
    '''
    input: name of window
    return: handle of window'''
    handle = win32gui.FindWindow(None, name)
    if handle == 0:
        return False
    while (win32gui.FindWindowEx(handle, None, None, None) != 0):
        handle = win32gui.FindWindowEx(handle, None, None, None)
    return handle


def dicer_att(window_name, adb_devices, q: Queue, AI_model: load_models.AI_model):
    handle_num = handle_find(window_name)
    if (handle_num == False):
        print('找不到視窗')
        return
    d = u2.connect(adb_devices)
    img_tool = img_tools(handle_num, adb_devices, d)
    str_tool = tools.str_tool(img_tool, AI_model.reader)
    click_tool = tools.click_tool(
        d, AI_model.reader, img_tool)
    attctrl = prepareGame(d, adb_devices, AI_model.reader,
                          q, img_tool, str_tool, click_tool, act='att')
    attctrl.opengame()
    attctrl.open_oproom()
    print('攻擊方準備完畢')
    q.get()
    d.click(250, 700)
    attack_game_ctrl = play(d, q, 'att',
                            attctrl.img_tool, attctrl.str_tool, attctrl.click_tool, AI_model)

    check = attack_game_ctrl.yinyun_attack()
    if (check != 0):
        attack_game_ctrl.level_up([0])
    while (not attack_game_ctrl.end_game()):
        if (attack_game_ctrl.gameview.choose_game() == "main"):
            return
        time.sleep(5)
    q.put(1)


def dicer_sup(window_name, adb_devices, q: Queue, AI_model: load_models.AI_model):
    handle_num = handle_find(window_name)
    if (handle_num == False):
        print('找不到視窗')
        return
    d = u2.connect(adb_devices)
    img_tool = img_tools(handle_num, adb_devices, d)
    str_tool = tools.str_tool(img_tool, AI_model.reader)
    click_tool = tools.click_tool(
        d, AI_model.reader, img_tool)
    supctrl = prepareGame(d, adb_devices, AI_model.reader,
                          q, img_tool, str_tool, click_tool, act='sup')
    supctrl.opengame()
    supctrl.open_oproom()
    print('輔助方準備完畢')
    sup_game_ctrl = play(d,  q, 'sup',
                         img_tool, str_tool, click_tool, AI_model)
    while (q.empty()):
        sup_game_ctrl.call_dice()
        time.sleep(1)
    time.sleep(3)

    check = sup_game_ctrl.sup_yinyun(55)
    if (check == 1):
        sup_game_ctrl.level_up([4])
        sup_game_ctrl.bubble_sup()


if __name__ == '__main__':
    os.system("adb devices")

    ai_model = load_models.AI_model()
    for i in range(10):
        queue = Queue(3)
        tsup = threading.Thread(
            target=dicer_sup, args=('BlueStacks App Player 1', '127.0.0.1:5565',  queue, ai_model))
        tatt = threading.Thread(
            target=dicer_att, args=('BlueStacks App Player', '127.0.0.1:5555',  queue, ai_model))
        tatt.start()
        tsup.start()
        tatt.join(2500)
        tsup.join(2500)
