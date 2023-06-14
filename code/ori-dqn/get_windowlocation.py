import win32gui
classname = "MozillaWindowClass"
titlename = "OriAndTheWilloftheWisps"

hwnd = win32gui.FindWindow(0, titlename)

left, top, right, bottom = win32gui.GetWindowRect(hwnd)
print(left,",",top,",",right,",",bottom)