from user import User


class Session():
    def __init__(self, id):
        self.User = User(id)
        # state = 0 - только стартовали и получили ИД, 1 - показали стили, но не выбрали
        # 2 - выбран стиль, 3 - есть стили и фотки и можно работать
        self.state = 0
        self.content_img_path = None
        self.style_img_path = None
        self.size = 256
