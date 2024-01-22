import win32gui
import win32ui
import win32con
import ctypes
import time
from threading import Lock, Thread
from PIL import Image


class Fast_Screenshot():
    def __init__(self, handle):
        self.handle = handle
        self.zoom = self.get_dpi_scaling_factor()
        self.left, self.top, self.width, self.height = self.get_windows_high_and_width()
        self.lock = Lock()
        self.setting_screen()
        self.thread = Thread(target=self.look)
        self.thread.start()

    def get_windows_high_and_width(self):
        left, top, right, bottom = win32gui.GetWindowRect(self.handle)
        width = right - left
        height = bottom - top
        return left, top, width, height

    def look(self):
        # 获取初始窗口大小
        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(self.handle, ctypes.byref(rect))
        initial_width = rect.right - rect.left
        initial_height = rect.bottom - rect.top

        while True:
            # 定期检查窗口大小是否发生变化
            ctypes.windll.user32.GetWindowRect(self.handle, ctypes.byref(rect))
            current_width = rect.right - rect.left
            current_height = rect.bottom - rect.top
            if current_width != initial_width or current_height != initial_height:
                # 上鎖
                initial_width = current_width
                initial_height = current_height
                self.lock.acquire()
            time.sleep(0.1)  # 等待一段时间再次检查窗口大小

    def setting_screen(self):
        self.hwndDC = win32gui.GetWindowDC(self.handle)
        self.mfcDC = win32ui.CreateDCFromHandle(self.hwndDC)
        self.saveDC = self.mfcDC.CreateCompatibleDC()
        self.saveBitMap = win32ui.CreateBitmap()
        self.saveBitMap.CreateCompatibleBitmap(
            self.mfcDC, self.width, self.height)
        self.saveDC.SelectObject(self.saveBitMap)

    def del_setting_screen(self):
        self.saveDC.DeleteDC()
        win32gui.DeleteObject(self.saveBitMap.GetHandle())
        self.mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.handle, self.hwndDC)

    def update_screen(self):
        while (win32gui.FindWindowEx(self.handle, None, None, None) != 0):
            self.left, self.top, self.width, self.height = self.get_windows_high_and_width()
            print('更新畫面')
            self.del_setting_screen()
            self.setting_screen()

    def get_dpi_scaling_factor(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 设置DPI感知级别
            dpi_scaling_factor = ctypes.windll.shcore.GetScaleFactorForDevice(
                0) / 100.0
            return dpi_scaling_factor
        except Exception as e:
            print(f"获取缩放因子出错: {e}")
            return None

    def screenshot(self) -> Image:
        if self.lock.locked():
            print('上鎖中，請稍後再試')
            # 更新畫面
            self.left, self.top, self.width, self.height = self.get_windows_high_and_width()
            self.setting_screen()
            self.update_screen()
            self.lock.release()

        self.saveDC.BitBlt((0, 0), (int(self.width*self.zoom),
                           int(self.height*self.zoom)), self.mfcDC, (0, 0), win32con.SRCCOPY)
        bmpinfo = self.saveBitMap.GetInfo()
        bmpstr = self.saveBitMap.GetBitmapBits(True)
        image = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1
        )
        return image
