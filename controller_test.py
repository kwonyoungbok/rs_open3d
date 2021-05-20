from controller.controller import Controller

import time

if __name__ == "__main__": 
    controller = Controller()
    controller.start()
   # result =  controller.capture()

    while True:
        val = input()
        if val =="c":
            result =  controller.capture()
            

  