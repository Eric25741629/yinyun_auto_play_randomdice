import time

class watchAD():
    def __init__(self,d):
        self.d=d
    def watchvideo(self):
        time.sleep(5)
        start=time.time()
        while(time.time()-start<40):
            #print(d.info['currentPackageName'])
            currentApp = self.d.app_list_running()
            for i in currentApp:
                # print(i)
                if i=='com.android.vending':
                    self.d.app_stop(i)
            if(self.d(resourceId="com.android.vending:id/0_resource_name_obfuscated", description="Close").exists):        
                self.d(resourceId="com.android.vending:id/0_resource_name_obfuscated", description="Close").click()