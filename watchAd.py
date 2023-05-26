import time

import time

class watchAD():
    def __init__(self,d):
        self.d=d
    def watchvideo(self):
        # time.sleep(5)
        start=time.time()
        while(time.time()-start<60):
            #print(d.info['currentPackageName'])
            currentApp = self.d.app_list_running()
            for i in currentApp:
                if i=='com.android.ld.appstore':
                    #print('yes')
                    self.d.app_stop(i)
                if i=='com.android.vending':
                    #print('yes')
                    self.d.app_stop(i)
                    #return 1
                # print(i)
            if (self.d(resourceId="al_skipButton").click_exists()):
                time.sleep(5)
            if(self.d(resourceId="al_skipButton").exists()):
                self.d(resourceId="al_skipButton").click()
                print('yes')
            if(self.d(resourceId="al_closeButton").click_exists()):
                return 1
            if(self.d(resourceId="com.android.vending:id/0_resource_name_obfuscated", description="Close").click_exists()):   
                return 1
            if self.d.xpath('//*[@resource-id="video_container"]/android.view.View[1]/android.view.View[1]/android.widget.Button[1]').click_exists():
                return 1
        #self.d.click(0.9, 0.097)
        

