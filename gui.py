import PySimpleGUI as sg
from steganography import *


# sg.theme('Dark Red')


def error_window(text):
    window = sg.Window('Ошибка', layout=[[sg.Text('ОШИБКА!')],
                                         [sg.Text(text)],
                                         [sg.Button('Ок', enable_events=True)]], element_justification='c')

    while True:
        event, values = window.read()
        if event in (None, 'Ок', sg.WIN_CLOSED):
            break
    window.close()


def start():
    type_frame = sg.Frame('Что вы хотите сделать?', [
                [sg.Radio('Зашифровать сообщение', 1, default=True, key='Encrypt', enable_events=True)],
                [sg.Radio('Расшифровать сообщение', 1, enable_events=True)]])

    file_frame_encr = sg.Frame(f'Выберите файл для сокрытия информации', [
        [sg.Input(key='File_jpg', visible=True, enable_events=True),
         sg.FileBrowse(button_text='Выбрать', file_types=(("Изображения", "*.jpg", "*png"),), key='FileBrowse_jpg')]])

    file_frame_decr = sg.Frame(f'Выберите файл', [
                     [sg.Input(key='File_png', visible=True, enable_events=True),
                      sg.FileBrowse(button_text='Выбрать', file_types=(("Изображения .png", "*.png"),),
                                    key='FileBrowse_png')]],
                               visible=False)

    method_frame = sg.Frame('Выберите метод стеганографии', [
                  [sg.Combo(['LSB', 'PVD'], key='Method', default_value='LSB')]],
                            visible=True, element_justification='c')

    length_frame = sg.Frame('Выберите длину вставок', [
                 [sg.Spin([i for i in range(1, 4)], initial_value=1, key='t'), sg.Text('Бит')]])

    text_frame = sg.Frame('Введите текст, который хотите сокрыть', [[sg.InputText('Only English', key='Text')]],
                          visible=True)

    window = sg.Window('Стеганография', layout=[[type_frame],
                                                [method_frame, length_frame],
                                                [file_frame_encr, file_frame_decr],
                                                [text_frame],
                                                [sg.Button('Далее')]], element_justification='c')

    while True:
        event, values = window.read()
        if event in (None, sg.WIN_CLOSED):
            window.close()
            break
        if values['Encrypt']:
            text_frame.update(visible=True)
            file_frame_encr.update(visible=True)
            file_frame_decr.update(visible=False)
        else:
            text_frame.update(visible=False)
            file_frame_encr.update(visible=False)
            file_frame_decr.update(visible=True)
        if event == 'Далее':
            if values['Encrypt']:
                if values['File_jpg']:
                    window.close()
                    try:
                        encrypt_end(values['File_jpg'], values['Method'], values['Text'], values['t'])
                    except ImageSizeError:
                        error_window(ImageSizeError)
                        start()
                    break
                else:
                    error_window('Некорректный формат файла')
            else:
                if values['File_png']:
                    window.close()
                    decrypt_end(values['File_png'], values['Method'], values['t'])
                    break
                else:
                    error_window('Некорректный формат файла')


def encrypt_end(image_path, method, text, t):
    image = SteganoImg(image_path)
    if method == 'LSB':
        image.lsb_encrypt(text, t)
    else:
        image.pvd_encrypt(text, t)
    image.save_pic(f'Encrypted{method}{str(t)}.png')
    layout = [[sg.Text(f'Готовое изображение')],
              [sg.Image(f'Encrypted{method}{str(t)}.png')],
              [sg.InputText(visible=False, enable_events=True, key='Path'),
               sg.FileSaveAs(key='Save As', file_types=(('Изображения .png', '.png'),), enable_events=True),
               sg.Text('Файл сохранён', visible=False, key='After')],
              [sg.Button('Назад', visible=False, key='Back'), sg.Button('Готово', visible=False, key='Done')]]

    window = sg.Window('Стеганография', layout, element_justification='c')

    while True:
        event, values = window.read()

        if event in (None, sg.WIN_CLOSED):
            window.close()
            break
        if event == 'Path' and values['Path'] != '':
            image.save_pic(values['Path'])
            window['Save As'].update(visible=False)
            window['After'].update(f"Файл {values['Path']} сохранён", visible=True)
            window['Back'].update(visible=True)
            window['Done'].update(visible=True)
        if event == 'Done':
            window.close()
            break
        if event == 'Back':
            window.close()
            start()
            break


def decrypt_end(image_path, method, t):
    image = SteganoImg(image_path)

    if method == 'LSB':
        text = image.lsb_decrypt(t)
    else:
        text = image.pvd_decrypt(t)

    if text[:6] == '%start':
        text = text[6:]
        window = sg.Window('Стеганография', layout=[[sg.Text(f'В изображении было зашифровано: {text}')],
                                                    [sg.Button('Назад', key='Back'), sg.Button('Готово', key='Done')]],
                           element_justification='c')

        while True:
            event, values = window.read()
            if event in (None, 'Done', sg.WIN_CLOSED):
                window.close()
                break
            if event == 'Back':
                window.close()
                start()
                break
    else:
        error_window('Стеготекст не найден')
        start()
