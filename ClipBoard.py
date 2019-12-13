# encoding = utf-8
# =====================================================
#   Copyright (C) 2019 All rights reserved.
#
#   filename : CF_HDROP.py
#   version  : 0.1
#   author   : Jack Wang / 544907049@qq.com
#   date     : 2019-12-13 下午 1:39
#   desc     : 
# =====================================================

from ctypes import windll, create_unicode_buffer, c_void_p, c_uint, c_wchar_p

kernel32 = windll.kernel32
GlobalLock = kernel32.GlobalLock
GlobalLock.argtypes = [c_void_p]
GlobalLock.restype = c_void_p
GlobalUnlock = kernel32.GlobalUnlock
GlobalUnlock.argtypes = [c_void_p]

user32 = windll.user32
GetClipboardData = user32.GetClipboardData
GetClipboardData.restype = c_void_p

DragQueryFile = windll.shell32.DragQueryFileW
DragQueryFile.argtypes = [c_void_p, c_uint, c_wchar_p, c_uint]

CF_HDROP = 15


def get_clipboard_files():
    file_list = []

    if user32.OpenClipboard(None):
        hGlobal = user32.GetClipboardData(CF_HDROP)
        if hGlobal:
            hDrop = GlobalLock(hGlobal)
            if hDrop:
                count = DragQueryFile(hDrop, 0xFFFFFFFF, None, 0)
                for i in range(count):
                    length = DragQueryFile(hDrop, i, None, 0)
                    buffer = create_unicode_buffer(length)
                    DragQueryFile(hDrop, i, buffer, length + 1)
                    file_list.append(buffer.value)

                GlobalUnlock(hGlobal)

        user32.CloseClipboard()

    return file_list



