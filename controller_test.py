from controller.controller import Controller


if __name__ == "__main__":
    controller = Controller()
    controller.start()
    result =  controller.capture()
    print(result)