# encoding = utf-8
# =====================================================
#   Copyright (C) 2019 All rights reserved.
#
#   filename : smpic.py
#   version  : 0.1
#   author   : Jack Wang / 544907049@qq.com
#   date     : 2019-12-12 下午 1:45
#   desc     : 
# =====================================================


from os import path,remove

from threading import Timer,Thread
from webbrowser import open as openweb

import wx
import wx.adv
import yaml

from PIL import ImageGrab
from pynput import keyboard
from pyperclip import copy
import ClipBoard
from Smms import Smms

current_key_pressed = []
hotkey = ''
keycode = {}
listener = None


def write_keycode():
    # key code for function keys
    for i in range(1, 13):
        keycode['f' + str(i)] = 111 + i
    # key code for letter keys
    for i in range(26):
        keycode[chr(97 + i)] = 65 + i
    keycode['ctrl'] = 162
    keycode['alt'] = 164


def init_config():
    write_keycode()
    with open('config.yml', 'r', encoding='utf-8') as f:
        cont = f.read()
        config = yaml.load(cont, Loader=yaml.BaseLoader)
        try:
            global hotkey, token, keycode
            hotkey = config['hotkey'].lower().split('+')
            token = config['token']

            for i in range(len(hotkey)):
                hotkey[i] = keycode[hotkey[i]]

            return token

        except KeyError:
            pass


def set_token_0():
    with open('config.yml', 'r', encoding='utf-8') as f:
        cont = f.read()
        config = yaml.load(cont, Loader=yaml.BaseLoader)
        with open('config.yml', 'w', encoding='utf-8') as f:
            config['token'] = '0'
            yaml.dump(config, f, default_flow_style=False, encoding='utf-8', allow_unicode=True)


def get_pic_from_clipboard(window):
    try:
        im = ImageGrab.grabclipboard()

        if im:
            image = 'image.png'
            im.save(r'image.png')
        else:
            image = ClipBoard.get_clipboard_files()[0]

        ThreadUpload(image, token, window)

        try:
            if path.exists('image.png'):
                remove('image.png')
        except PermissionError:
            pass

        return True
    except AttributeError:
        return False


class ThreadKey(Thread):
    def __init__(self, window):
        Thread.__init__(self)
        self.window = window
        self.start()  # start the thread

    def run(self):
        global listener
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()

    def on_release(self, key):
        try:
            if key.value.vk in current_key_pressed:
                current_key_pressed.remove(key.value.vk)
        except AttributeError:
            if key.vk in current_key_pressed:
                current_key_pressed.remove(key.vk)

    def on_press(self, key):
        try:
            if key.value.vk not in current_key_pressed:
                current_key_pressed.append(key.value.vk)
        except AttributeError:
            if key.vk not in current_key_pressed:
                current_key_pressed.append(key.vk)

        if self.is_pressed():

            status = get_pic_from_clipboard(self.window)
            # toaster = ToastNotifier()
            if status:
                wx.CallAfter(self.window.Uploading)
            else:
                wx.CallAfter(self.window.UploadFailed)

    @staticmethod
    def is_pressed():
        pressed = False
        for key in hotkey:
            if key in current_key_pressed:
                pressed = True
            else:
                return False
        return pressed


class ThreadUpload(Thread):
    def __init__(self, filename, token, window):
        Thread.__init__(self)
        self.filename = filename
        self.token = token
        self.window = window
        self.start()  # start the thread

    def run(self):
        try:
            url = Smms.upload(self.filename, token=self.token)
            copy(url)
            wx.CallAfter(self.window.UploadSuccess)
        except ConnectionRefusedError:
            wx.CallAfter(self.window.LoginAgain)
        except ConnectionAbortedError:
            wx.CallAfter(self.window.UploadMax)


# class ThreadUpload(Thread):
#     def __init__(self, , window):
#         Thread.__init__(self)
#         self.window = window
#
#     def run(self):

class Trans(wx.Frame):
    def __init__(self, parent, title=' ', size=(700, 500)):
        wx.Frame.__init__(self, parent, title=title, size=size, style=wx.STAY_ON_TOP)

        label_user = wx.StaticText(self, -1, title, pos=(0, 0))

        # self.Text = wx.TextCtrl(self, size=(700, 500))
        # self.Text.SetBackgroundColour('Black'), self.Text.SetForegroundColour('Steel Blue')
        self.SetTransparent(100)  # 设置透明


class MyTaskBarIcon(wx.adv.TaskBarIcon):
    ICON = "logo.ico"  # 图标地址
    ID_ABOUT = wx.NewIdRef()  # 菜单选项“关于”的ID
    ID_EXIT = wx.NewIdRef()  # 菜单选项“退出”的ID
    ID_UPLOAD = wx.NewIdRef()  # 菜单选项“显示页面”的ID
    ID_LOGIN = wx.NewIdRef()  # 菜单选项“显示页面”的ID
    TITLE = "SMPIC"  # 鼠标移动到图标上显示的文字

    def __init__(self):
        wx.adv.TaskBarIcon.__init__(self)
        self.SetIcon(wx.Icon(self.ICON), self.TITLE)  # 设置图标和标题
        self.Bind(wx.EVT_MENU, self.onAbout, id=self.ID_ABOUT)  # 绑定“关于”选项的点击事件
        self.Bind(wx.EVT_MENU, self.onExit, id=self.ID_EXIT)  # 绑定“退出”选项的点击事件
        self.Bind(wx.EVT_MENU, self.onUpload, id=self.ID_UPLOAD)
        self.Bind(wx.EVT_MENU, self.OnLogin, id=self.ID_LOGIN)

        self.frame = wx.Frame(parent=None, title='登录', size=(250, 160))

        panel = wx.Panel(self.frame, -1)
        label_user = wx.StaticText(panel, -1, "账号:", pos=(10, 10))
        label_pass = wx.StaticText(panel, -1, "密码:", pos=(10, 50))

        self.entry_user = wx.TextCtrl(panel, -1, size=(160, 20), pos=(50, 10))
        self.entry_pass = wx.TextCtrl(panel, -1, size=(160, 20), pos=(50, 50), style=wx.TE_PASSWORD)

        self.but_login = wx.Button(panel, -1, "登陆", size=(50, 30), pos=(10, 80))
        self.but_register = wx.Button(panel, -1, "注册SM.MS账号", size=(110, 30), pos=(110, 80))

        self.but_login.Bind(wx.EVT_BUTTON, self.on_but_login)
        self.but_register.Bind(wx.EVT_BUTTON, self.on_but_register)

        self.frame.Center()
        token = init_config()
        if token == '0':
            self.frame.Show(True)
        else:
            self.frame.Show(False)

        self.frame.SetMaxSize((250, 160))
        self.frame.SetMinSize((250, 160))
        ThreadKey(self)

        self.frame2 = Trans(parent=None, title='上传中', size=(50, 20))
        self.frame2.Center()
        self.frame2.Show(False)

        self.frame3 = Trans(parent=None, title='上传成功', size=(50, 20))
        self.frame3.Center()
        self.frame3.Show(False)

        self.frame4 = Trans(parent=None, title='上传失败', size=(50, 20))
        self.frame4.Center()
        self.frame4.Show(False)

        self.frame5 = Trans(parent=None, title='每分钟限制上传10张，请等待冷却', size=(200, 20))
        self.frame5.Center()
        self.frame5.Show(False)

    # “关于”选项的事件处理器
    def onAbout(self, event):
        wx.MessageBox('Author：Jack Wang\nEmail Address：544907049@qq.com\nLatest Update：2019-12-13', "info")

    # “退出”选项的事件处理器
    def onExit(self, event):
        global listener
        listener.stop()
        wx.Exit()

    # “显示页面”选项的事件处理器
    def onUpload(self, event):
        get_pic_from_clipboard(self)

    def OnLogin(self, event):
        self.frame.Show()

    # 创建菜单选项
    def CreatePopupMenu(self):
        menu = wx.Menu()
        for mentAttr in self.getMenuAttrs():
            menu.Append(mentAttr[1], mentAttr[0])
        return menu

    # 获取菜单的属性元组
    def getMenuAttrs(self):
        return [('Upload Clipboard To GitHub', self.ID_UPLOAD),
                ('Login', self.ID_LOGIN),
                ('Info', self.ID_ABOUT),
                ('Exit', self.ID_EXIT)]

    def on_but_login(self, event):
        username = self.entry_user.GetValue()
        password = self.entry_pass.GetValue()
        try:
            token = Smms.get_token(username, password)
            with open('config.yml', 'r', encoding='utf-8') as f:
                cont = f.read()
                config = yaml.load(cont, Loader=yaml.BaseLoader)
                with open('config.yml', 'w', encoding='utf-8') as f:
                    config['token'] = token
                    yaml.dump(config, f, default_flow_style=False, encoding='utf-8', allow_unicode=True)
            self.frame.Show(False)
            wx.MessageBox('登陆成功', "温馨提示")
        except KeyError:
            wx.MessageBox('密码或账号错误', "警告")

    def on_but_register(self, event):
        openweb('https://sm.ms/register')

    def LoginAgain(self):  # 删除线程
        wx.MessageBox('登录已失效，需重新登录', "警告")
        self.frame.Show(True)

    def Uploading(self):
        def timestop():
            self.frame2.Show(False)
            timer.cancel()

        self.frame2.Show(True)
        timer = Timer(2.0, timestop)
        timer.start()

    def UploadSuccess(self):
        def timestop():
            self.frame3.Show(False)
            timer.cancel()

        self.frame3.Show(True)
        timer = Timer(2.0, timestop)
        timer.start()

    def UploadFailed(self):
        def timestop():
            self.frame4.Show(False)
            timer.cancel()

        self.frame4.Show(True)
        timer = Timer(2.0, timestop)
        timer.start()

    def UploadMax(self):
        def timestop():
            self.frame5.Show(False)
            timer.cancel()

        self.frame5.Show(True)
        timer = Timer(5.0, timestop)
        timer.start()


class MyApp(wx.App):
    def __init__(self):
        wx.App.__init__(self)

        MyFrame()


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self)
        MyTaskBarIcon()  # 显示系统托盘图标


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
