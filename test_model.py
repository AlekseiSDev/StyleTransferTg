import model


# TODO: файлик для тестирования модели
def test_model(model, style, content, out):
    style_path = f"data/style/{style}"
    content_path = f"data/content/{content}"
    out_path = f"data/out/{out}"
    model.inference(content_path=content_path, style_path=style_path, out_path=out_path)


def start():
    # TODO: создадим экз модели
    x = 3
    Model = model.Model()

    # TODO игручшеное 1е обращение
    test_model(Model, style='19.jpg', content='1.jpg', out='1.jpg')

    # TODO: цикл, ожидающий отклика юзера и что он даст пути


if __name__ == '__main__':
    start()
