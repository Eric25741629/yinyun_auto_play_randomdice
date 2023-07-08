import time
import uiautomator2 as u2
class open_game:
    def __init__(self, device: u2.Device):
        self.d = device
    def updata_game(self):
        self.d.click(368, 590)
        t = time.time()
        while time.time()-t < 30:
            if self.d.xpath('//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[1]/android.view.View[2]').exists:    # type: ignore
                self.d.xpath(
                    '//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[1]/android.view.View[2]').click()            # type: ignore
                break
        while not self.d.xpath('//*[@content-desc="開始玩"]'):  # type: ignore
            print('start')
        self.d.xpath('//*[@content-desc="開始玩"]').click()  # type: ignore

    def openapp(self, gamename: str) -> None:
        currentApp = self.d.app_list_running()
        if gamename not in currentApp:
            self.d.app_start(gamename, use_monkey=True, stop=True)

    def Check_if_it_is_running(self, gamename) -> bool:
        currentApp = self.d.app_list_running()
        for i in currentApp:
            if i == 'com.percent.royaldice':
                return True
        return False