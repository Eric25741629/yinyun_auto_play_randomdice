import load_models
import os
from multiprocessing import Process
import random
import threading
import time
import easyocr
from adbutils import adb
from pic_tranform import *
from main import *
from queue import Queue
from PrepareGame import *


def dicer_att(adb_devices, dicemodel, reader, q: Queue, wavemodel):
    attctrl = prepareGame(adb_devices, reader, q, act='att')
    d = attctrl.d
    attctrl.opengame()
    attctrl.open_oproom()
    print('攻擊方準備完畢')
    q.get()
    d.click(250, 700)
    attack_game_ctrl = play(d, dicemodel, reader, q, 'att',
                            attctrl.img_tool, attctrl.str_tool, attctrl.click_tool, wavemodel)

    check = attack_game_ctrl.yinyun_attack()
    if (check != 0):
        attack_game_ctrl.level_up([0])
    while (not attack_game_ctrl.end_game()):
        if (attack_game_ctrl.gameview.choose_game() == "main"):
            return
        time.sleep(5)
    q.put(1)


def dicer_sup(adb_devices, dicemodel, reader, q: Queue, wavemodel):

    supctrl = prepareGame(adb_devices, reader, q, act='sup')
    d = supctrl.d
    supctrl.opengame()
    supctrl.open_oproom()
    print('輔助方準備完畢')
    sup_game_ctrl = play(d, dicemodel, reader, q, 'sup',
                         supctrl.img_tool, supctrl.str_tool, supctrl.click_tool, wavemodel)
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
    dicemodel, wavemodel = load_models.load_model()
    reader = easyocr.Reader(['ch_tra'], gpu=True)
    for i in range(10):
        queue = Queue(3)
        tsup = threading.Thread(
            target=dicer_sup, args=('127.0.0.1:5565', dicemodel, reader, queue, wavemodel))
        tatt = threading.Thread(
            target=dicer_att, args=('127.0.0.1:5555', dicemodel, reader, queue, wavemodel))
        tatt.start()
        tsup.start()
        tatt.join(2500)
        tsup.join(2500)
