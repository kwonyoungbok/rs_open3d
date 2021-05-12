from controller.controller import Controller

import time

if __name__ == "__main__":
    start = time.time()
    controller = Controller()
    controller.start()
    result =  controller.capture()
    print("걸린 시간", time.time()-start)