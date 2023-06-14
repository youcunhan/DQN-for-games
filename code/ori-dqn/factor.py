import win32gui
import win32api
import win32process
import ctypes
import ctypes.wintypes
from ctypes import *

Psapi = ctypes.WinDLL('Psapi.dll')
Kernel32 = ctypes.WinDLL('kernel32.dll')
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010


def convert(s):  
    try:
        i = int(s, 10)  # convert from Dec to a Python int
        cp = pointer(c_int(i))  # make this into a c integer
        fp = cast(cp, POINTER(c_float))  # cast the int pointer to a float pointer
        a = fp.contents.value

    except:
        a = 0

    finally:
        return a




def EnumProcessModulesEx(hProcess):
    buf_count = 256
    while True:
        LIST_MODULES_ALL = 0x03
        buf = (ctypes.wintypes.HMODULE * buf_count)()
        buf_size = ctypes.sizeof(buf)
        needed = ctypes.wintypes.DWORD()
        if not Psapi.EnumProcessModulesEx(hProcess, ctypes.byref(buf), buf_size, ctypes.byref(needed),
                                          LIST_MODULES_ALL):
            raise OSError('EnumProcessModulesEx failed')
        if buf_size < needed.value:
            buf_count = needed.value // (buf_size // buf_count)
            continue
        count = needed.value // (buf_size // buf_count)
        return map(ctypes.wintypes.HMODULE, buf[:count])


class Gamefactors:
    def __init__(self):
        hd = win32gui.FindWindow(None, "OriAndTheWilloftheWisps")
        pid = win32process.GetWindowThreadProcessId(hd)[1]
        self.process_handle = win32api.OpenProcess(0x1F0FFF, False, pid)
        self.kernal32 = ctypes.windll.LoadLibrary(r"C:\\Windows\\System32\\kernel32.dll")

        self.hx = 0
        # get dll address
        hProcess = Kernel32.OpenProcess(
            PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
            False, pid)
        hModule = EnumProcessModulesEx(hProcess)
        for i in hModule:
            temp = win32process.GetModuleFileNameEx(self.process_handle, i.value)
            if temp[-15:] == "UnityPlayer.dll":  
                self.UnityPlayer = i.value
            if temp[-16:] == "GameAssembly.dll":  
                self.GameAseembly = i.value

    #get boss hp
    def get_boss_hp(self):
        base_address = self.GameAseembly + 0x04771768
        temp_L = ctypes.c_long()
        temp_H = ctypes.c_long()
        offset_list = [0x0, 0xB8, 0x00, 0x78, 0x30, 0x40]  
        offset_address = base_address
        for i in range(len(offset_list) - 1):
            self.kernal32.ReadProcessMemory(int(self.process_handle), ctypes.c_void_p(offset_address + offset_list[i]),
                                            ctypes.byref(temp_L), 4, None)
            self.kernal32.ReadProcessMemory(int(self.process_handle),
                                            ctypes.c_void_p(offset_address + 4 + offset_list[i]),
                                            ctypes.byref(temp_H), 4, None)
            offset_address = temp_H.value * 4294967296 + (
                    (temp_L.value + temp_H.value * 4294967296) & 0x0000FFFFFFFF)
        self.kernal32.ReadProcessMemory(int(self.process_handle), ctypes.c_void_p(offset_address + offset_list[-1]),
                                        ctypes.byref(temp_L), 4, None)
        print(convert(str(temp_L.value)))
        return temp_L.value

    #get self hp
    def get_self_hp(self):
        base_address = self.GameAseembly + 0x04739128
        temp_L = ctypes.c_long()
        temp_H = ctypes.c_long()
        offset_list = [0x0, 0xB8, 0x00, 0x10, 0x38, 0x44]  
        offset_address = base_address
        for i in range(len(offset_list) - 1):
            self.kernal32.ReadProcessMemory(int(self.process_handle), ctypes.c_void_p(offset_address + offset_list[i]),
                                            ctypes.byref(temp_L), 4, None)
            self.kernal32.ReadProcessMemory(int(self.process_handle),
                                            ctypes.c_void_p(offset_address + 4 + offset_list[i]),
                                            ctypes.byref(temp_H), 4, None)
            offset_address = temp_H.value * 4294967296 + (
                    (temp_L.value + temp_H.value * 4294967296) & 0x0000FFFFFFFF)  
        self.kernal32.ReadProcessMemory(int(self.process_handle), ctypes.c_void_p(offset_address + offset_list[-1]),
                                        ctypes.byref(temp_L), 4, None)
        print(convert(str(temp_L.value)))
        return temp_L.value

    # get self location
    def get_self_location(self):
        base_address = self.GameAseembly + 0x0473B3B0
        temp_L = ctypes.c_long()
        temp_H = ctypes.c_long()
        offset_list = [0x0, 0xB8, 0x0, 0x10, 0xA8, 0x28, 0x120]  
        offset_address = base_address
        for i in range(len(offset_list) - 1):
            self.kernal32.ReadProcessMemory(int(self.process_handle), ctypes.c_void_p(offset_address + offset_list[i]),
                                            ctypes.byref(temp_L), 4, None)
            self.kernal32.ReadProcessMemory(int(self.process_handle),
                                            ctypes.c_void_p(offset_address + 4 + offset_list[i]),
                                            ctypes.byref(temp_H), 4, None)
            offset_address = temp_H.value * 4294967296 + ((
                                                                  temp_L.value + temp_H.value * 4294967296) & 0x0000FFFFFFFF)  # 4294967296是16^8次方，这里是做一个位移的操作 有符号数的十六进制是挺麻烦的
        self.kernal32.ReadProcessMemory(int(self.process_handle), ctypes.c_void_p(offset_address + offset_list[-1]),
                                        ctypes.byref(temp_L), 4, None)
        return int(temp_L.value)


    # ori x location
    def location_addr(self):
        base_address = self.GameAseembly + 0x0473B3B0
        temp_L = ctypes.c_long()
        temp_H = ctypes.c_long()
        offset_list = [0x0, 0xB8, 0x0, 0x10, 0xA8, 0x28, 0x120] 
        offset_address = base_address
        for i in range(len(offset_list) - 1):
            self.kernal32.ReadProcessMemory(int(self.process_handle), ctypes.c_void_p(offset_address + offset_list[i]),
                                            ctypes.byref(temp_L), 4, None)
            self.kernal32.ReadProcessMemory(int(self.process_handle),
                                            ctypes.c_void_p(offset_address + 4 + offset_list[i]),
                                            ctypes.byref(temp_H), 4, None)
            offset_address = temp_H.value * 4294967296 + ((
                                                                  temp_L.value + temp_H.value * 4294967296) & 0x0000FFFFFFFF)  # 4294967296是16^8次方，这里是做一个位移的操作 有符号数的十六进制是挺麻烦的
        return offset_address + offset_list[-1]

    # self hp address
    def self_hp_addr(self):
        base_address = self.GameAseembly + 0x04739128
        temp_L = ctypes.c_long()
        temp_H = ctypes.c_long()
        offset_list = [0x0, 0xB8, 0x00, 0x10, 0x38, 0x44]  
        offset_address = base_address
        for i in range(len(offset_list) - 1):
            self.kernal32.ReadProcessMemory(int(self.process_handle), ctypes.c_void_p(offset_address + offset_list[i]),
                                            ctypes.byref(temp_L), 4, None)
            self.kernal32.ReadProcessMemory(int(self.process_handle),
                                            ctypes.c_void_p(offset_address + 4 + offset_list[i]),
                                            ctypes.byref(temp_H), 4, None)
            offset_address = temp_H.value * 4294967296 + (
                    (temp_L.value + temp_H.value * 4294967296) & 0x0000FFFFFFFF)  
        return offset_address + offset_list[-1]

    #boss hp adress
    def boss_hp_addr(self):
        base_address = self.GameAseembly + 0x04771768
        temp_L = ctypes.c_long()
        temp_H = ctypes.c_long()
        offset_list = [0x0, 0xB8, 0x00, 0x78, 0x30, 0x40] 
        offset_address = base_address
        for i in range(len(offset_list) - 1):
            self.kernal32.ReadProcessMemory(int(self.process_handle), ctypes.c_void_p(offset_address + offset_list[i]),
                                            ctypes.byref(temp_L), 4, None)
            self.kernal32.ReadProcessMemory(int(self.process_handle),
                                            ctypes.c_void_p(offset_address + 4 + offset_list[i]),
                                            ctypes.byref(temp_H), 4, None)
            offset_address = temp_H.value * 4294967296 + (
                    (temp_L.value + temp_H.value * 4294967296) & 0x0000FFFFFFFF)  
        return offset_address + offset_list[-1]

    #get adress balue
    def get_value(self, address):
        return_value = ctypes.c_void_p() 
        self.kernal32.ReadProcessMemory(int(self.process_handle), ctypes.c_void_p(address),
                                        ctypes.byref(return_value), 4, None)
        return convert(str(return_value.value))


if __name__ == "__main__":
    hp = Gamefactors()
    loc_address = hp.location_addr()
    self_address = hp.self_hp_addr()
    boss_address = hp.boss_hp_addr()
    while True:
        print(hp.get_value(boss_address))
        print(hp.get_value(self_address))
        print(hp.get_value(loc_address))

