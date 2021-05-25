from controller.controller import Controller

import time

if __name__ == "__main__": 
    controller = Controller()
    controller.start()
   # result =  controller.capture()
    controller.capture_and_save(4)

    for i in range(150):
        controller.capture_and_save(i)

    # while True:
    #     val = input()
    #     if val =="c":
    #         result =  controller.capture_and_save()
            

  