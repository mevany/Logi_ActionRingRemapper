# -*- coding: utf-8 -*-
"""
Logi Actions Ring Remapper v2.0.0 (Ultra-Low Memory Edition)
- Remaps Logitech Actions Ring (0x01A0) to Middle Mouse Button (WinAPI).
- 100% Pure WinAPI via ctypes (Zero external dependencies: No Tkinter, No Pillow, No pystray).
- Embedded Base64 Icon decoded directly into an in-memory native Win32 HICON.
- Settings and actions accessible directly from the system tray popup menu.
- System installation, Task Scheduler autostart, and Add/Remove Programs integration.
- Extreme low memory footprint (~1.5 - 3 MB RAM) via psapi.EmptyWorkingSet.
- 100% compatible with Nuitka compilation (no plugins, no hidden imports required).

Nuitka compilation command:
    python -m nuitka --standalone --onefile --windows-disable-console --output-filename=logi_actionremapper.exe app2.py
"""

import sys
import os
import base64
import struct
import ctypes
from ctypes import wintypes
import winreg
import subprocess
import shutil

# --- 1. High-DPI Awareness ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware v2
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# --- 2. Embedded Base64 Icon (In-Memory Resource) ---
ICON_BASE64 = """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"""

_cached_hicon16 = None
_cached_hicon32 = None

def get_icon_handle(size=16):
    """Decodes the embedded base64 icon directly into a native WinAPI HICON in memory."""
    global _cached_hicon16, _cached_hicon32
    if size <= 16 and _cached_hicon16:
        return _cached_hicon16
    if size > 16 and _cached_hicon32:
        return _cached_hicon32

    try:
        raw_data = base64.b64decode(ICON_BASE64)
        dwImageOffset = struct.unpack_from('<I', raw_data, 18)[0]
        dwBytesInRes = struct.unpack_from('<I', raw_data, 14)[0]
        icon_bytes = raw_data[dwImageOffset : dwImageOffset + dwBytesInRes]
        hicon = user32.CreateIconFromResourceEx(
            icon_bytes, dwBytesInRes, True, 0x00030000, size, size, 0
        )
        if size <= 16:
            _cached_hicon16 = hicon
        else:
            _cached_hicon32 = hicon
        return hicon
    except Exception:
        return user32.LoadIconW(None, ctypes.c_void_p(32512))  # IDI_APPLICATION fallback

# --- 3. WinAPI Constants & Typed Signatures ---
APP_TITLE = "Logi Action Ring Remapper"
APP_NAME = "LogiActionsRemapper"
APP_VERSION = "2.0.0"
INSTALL_FOLDER_NAME = "logi_actionremapper"
CLASS_NAME = "LogiActionRemapperMsgClass"
WINDOW_TITLE = "LogiActionRemapperMsgWindow"
SINGLE_INSTANCE_MUTEX = "LogiActionRemapper_SingleInstance_Mutex_v2"

# Windows Messages
WM_DESTROY       = 0x0002
WM_CLOSE         = 0x0010
WM_TIMER         = 0x0113
WM_INPUT         = 0x00FF
WM_COMMAND       = 0x0111
WM_LBUTTONUP     = 0x0202
WM_RBUTTONUP     = 0x0205
WM_NULL          = 0x0000
WM_USER          = 0x0400
WM_TRAY_CALLBACK = WM_USER + 20
WM_WAKEUP_NOTIFY = WM_USER + 30

ERROR_ALREADY_EXISTS = 183
RIDEV_INPUTSINK      = 0x00000100
RID_INPUT            = 0x10000003

# Mouse Events
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP   = 0x0040

# Tray Notify Constants
NIM_ADD    = 0x00000000
NIM_MODIFY = 0x00000001
NIM_DELETE = 0x00000002

NIF_MESSAGE = 0x00000001
NIF_ICON    = 0x00000002
NIF_TIP     = 0x00000004
NIF_INFO    = 0x00000010
NIIF_INFO   = 0x00000001

# Menu Flags
MF_STRING    = 0x00000000
MF_GRAYED    = 0x00000001
MF_DISABLED  = 0x00000002
MF_CHECKED   = 0x00000008
MF_UNCHECKED = 0x00000000
MF_SEPARATOR = 0x00000800

TPM_RIGHTBUTTON = 0x0002
TPM_RETURNCMD   = 0x0100
TPM_NONOTIFY    = 0x0080

# Menu Item Identifiers
ID_MENU_HEADER    = 1000
ID_MENU_STATUS    = 1001
ID_MENU_REMAP     = 1002
ID_MENU_AUTOSTART = 1003
ID_MENU_INSTALL   = 1004
ID_MENU_UNINSTALL = 1005
ID_MENU_ELEVATE   = 1006
ID_MENU_EXIT      = 1007

# Registry Paths
RUN_KEY       = r"Software\Microsoft\Windows\CurrentVersion\Run"
UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall" + "\\" + APP_NAME
CONFIG_KEY    = r"Software" + "\\" + APP_NAME

IS_64BIT = (ctypes.sizeof(ctypes.c_void_p) == 8)
LRESULT = ctypes.c_int64 if IS_64BIT else ctypes.c_long
WPARAM = ctypes.c_size_t
LPARAM = ctypes.c_size_t
ULONG_PTR = ctypes.c_size_t

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
shell32 = ctypes.windll.shell32
psapi = ctypes.windll.psapi

WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, WPARAM, LPARAM)

class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HICON),
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]

class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [
        ("usUsagePage", wintypes.USHORT),
        ("usUsage", wintypes.USHORT),
        ("dwFlags", wintypes.DWORD),
        ("hwndTarget", wintypes.HWND),
    ]

class RAWINPUTHEADER(ctypes.Structure):
    _fields_ = [
        ("dwType", wintypes.DWORD),
        ("dwSize", wintypes.DWORD),
        ("hDevice", wintypes.HANDLE),
        ("wParam", WPARAM),
    ]

class NOTIFYICONDATAW(ctypes.Structure):
    class VERSION_OR_TIMEOUT(ctypes.Union):
        _fields_ = [
            ('uTimeout', wintypes.UINT),
            ('uVersion', wintypes.UINT)
        ]
    class GUID(ctypes.Structure):
        _fields_ = [
            ('Data1', wintypes.ULONG),
            ('Data2', wintypes.WORD),
            ('Data3', wintypes.WORD),
            ('Data4', wintypes.BYTE * 8)
        ]
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('hWnd', wintypes.HWND),
        ('uID', wintypes.UINT),
        ('uFlags', wintypes.UINT),
        ('uCallbackMessage', wintypes.UINT),
        ('hIcon', wintypes.HICON),
        ('szTip', wintypes.WCHAR * 128),
        ('dwState', wintypes.DWORD),
        ('dwStateMask', wintypes.DWORD),
        ('szInfo', wintypes.WCHAR * 256),
        ('version_or_timeout', VERSION_OR_TIMEOUT),
        ('szInfoTitle', wintypes.WCHAR * 64),
        ('dwInfoFlags', wintypes.DWORD),
        ('guidItem', GUID),
        ('hBalloonIcon', wintypes.HICON)
    ]
    _anonymous_ = ['version_or_timeout']

# Explicit WinAPI Function Signatures
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
kernel32.GetCurrentProcess.argtypes = []
kernel32.GetCurrentProcess.restype = wintypes.HANDLE
kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.CreateMutexW.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.GetLastError.argtypes = []
kernel32.GetLastError.restype = wintypes.DWORD

psapi.EmptyWorkingSet.argtypes = [wintypes.HANDLE]
psapi.EmptyWorkingSet.restype = wintypes.BOOL

user32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASSW)]
user32.RegisterClassW.restype = wintypes.ATOM
user32.CreateWindowExW.argtypes = [
    wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID
]
user32.CreateWindowExW.restype = wintypes.HWND
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, WPARAM, LPARAM]
user32.DefWindowProcW.restype = LRESULT
user32.DestroyWindow.argtypes = [wintypes.HWND]
user32.DestroyWindow.restype = wintypes.BOOL
user32.PostQuitMessage.argtypes = [ctypes.c_int]
user32.PostQuitMessage.restype = None

user32.GetRawInputData.argtypes = [wintypes.HANDLE, wintypes.UINT, wintypes.LPVOID, ctypes.POINTER(wintypes.UINT), wintypes.UINT]
user32.GetRawInputData.restype = wintypes.UINT
user32.RegisterRawInputDevices.argtypes = [ctypes.POINTER(RAWINPUTDEVICE), wintypes.UINT, wintypes.UINT]
user32.RegisterRawInputDevices.restype = wintypes.BOOL
user32.mouse_event.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ULONG_PTR]
user32.mouse_event.restype = None

user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
user32.GetCursorPos.restype = wintypes.BOOL
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, WPARAM, LPARAM]
user32.PostMessageW.restype = wintypes.BOOL
user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.FindWindowW.restype = wintypes.HWND
user32.MessageBoxW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]
user32.MessageBoxW.restype = ctypes.c_int

user32.CreatePopupMenu.argtypes = []
user32.CreatePopupMenu.restype = wintypes.HMENU
user32.AppendMenuW.argtypes = [wintypes.HMENU, wintypes.UINT, ctypes.c_size_t, wintypes.LPCWSTR]
user32.AppendMenuW.restype = wintypes.BOOL
user32.DestroyMenu.argtypes = [wintypes.HMENU]
user32.DestroyMenu.restype = wintypes.BOOL
user32.TrackPopupMenuEx.argtypes = [wintypes.HMENU, wintypes.UINT, ctypes.c_int, ctypes.c_int, wintypes.HWND, wintypes.LPVOID]
user32.TrackPopupMenuEx.restype = wintypes.UINT

user32.CreateIconFromResourceEx.argtypes = [ctypes.c_char_p, wintypes.DWORD, wintypes.BOOL, wintypes.DWORD, ctypes.c_int, ctypes.c_int, wintypes.UINT]
user32.CreateIconFromResourceEx.restype = wintypes.HICON
user32.RegisterWindowMessageW.argtypes = [wintypes.LPCWSTR]
user32.RegisterWindowMessageW.restype = wintypes.UINT

user32.SetTimer.argtypes = [wintypes.HWND, ctypes.c_size_t, wintypes.UINT, ctypes.c_void_p]
user32.SetTimer.restype = ctypes.c_size_t
user32.KillTimer.argtypes = [wintypes.HWND, ctypes.c_size_t]
user32.KillTimer.restype = wintypes.BOOL

user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = wintypes.BOOL
user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.TranslateMessage.restype = wintypes.BOOL
user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.restype = LRESULT

shell32.Shell_NotifyIconW.argtypes = [wintypes.DWORD, ctypes.POINTER(NOTIFYICONDATAW)]
shell32.Shell_NotifyIconW.restype = wintypes.BOOL
shell32.ShellExecuteW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.c_int]
shell32.ShellExecuteW.restype = wintypes.HINSTANCE
shell32.IsUserAnAdmin.argtypes = []
shell32.IsUserAnAdmin.restype = ctypes.c_int

# --- 4. System & Memory Helpers ---
def trim_memory():
    """Drops process working set RAM consumption to minimal (~1.5 - 3 MB)."""
    try:
        psapi.EmptyWorkingSet(kernel32.GetCurrentProcess())
    except Exception:
        pass
    # If launched via Nuitka onefile bootstrap loader, trim the parent process too
    try:
        ppid = os.getppid()
        if ppid > 0:
            h_parent = kernel32.OpenProcess(0x0100 | 0x0400, False, ppid)  # PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION
            if h_parent:
                psapi.EmptyWorkingSet(h_parent)
                kernel32.CloseHandle(h_parent)
    except Exception:
        pass

def is_admin():
    try:
        return bool(shell32.IsUserAnAdmin())
    except Exception:
        return False

def request_uac_elevation(action_arg: str = "") -> bool:
    curr_exe = get_current_executable_path()
    if getattr(sys, 'frozen', False) or curr_exe.lower().endswith(".exe"):
        file_to_run = curr_exe
        params = action_arg
    else:
        file_to_run = sys.executable
        script = os.path.abspath(sys.argv[0])
        params = f'"{script}" {action_arg}'.strip()

    hinst = shell32.ShellExecuteW(
        None,
        "runas",
        file_to_run,
        params,
        None,
        1  # SW_SHOWNORMAL
    )
    return int(ctypes.cast(hinst, ctypes.c_void_p).value or 0) > 32

def get_current_executable_path():
    if getattr(sys, 'frozen', False):
        return os.path.abspath(sys.executable)
    return os.path.abspath(sys.argv[0])

def get_program_files_dir():
    base_pf = os.environ.get("ProgramFiles", r"C:\Program Files")
    return os.path.join(base_pf, INSTALL_FOLDER_NAME)

def get_installed_exe_path():
    return os.path.join(get_program_files_dir(), "logi_actionremapper.exe")

def is_running_installed():
    try:
        curr = os.path.normcase(os.path.abspath(get_current_executable_path()))
        inst = os.path.normcase(os.path.abspath(get_installed_exe_path()))
        return curr == inst
    except Exception:
        return False

def get_start_menu_programs_dir():
    appdata = os.environ.get("APPDATA", "")
    return os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs")

def get_startup_dir():
    appdata = os.environ.get("APPDATA", "")
    return os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Startup")

def create_windows_shortcut(target_path, shortcut_path, icon_path=None, description=""):
    try:
        ps_lines = [
            '$WshShell = New-Object -ComObject WScript.Shell',
            f'$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")',
            f'$Shortcut.TargetPath = "{target_path}"',
            '$Shortcut.Arguments = "--minimized"',
            f'$Shortcut.WorkingDirectory = "{os.path.dirname(target_path)}"',
            f'$Shortcut.Description = "{description}"'
        ]
        if icon_path and os.path.exists(icon_path):
            ps_lines.append(f'$Shortcut.IconLocation = "{icon_path},0"')
        ps_lines.append('$Shortcut.Save()')
        ps_script = "; ".join(ps_lines)
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            capture_output=True,
            creationflags=0x08000000
        )
    except Exception:
        pass

def get_saved_setting(name, default):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CONFIG_KEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, name)
            return val
    except Exception:
        return default

def save_setting(name, val):
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, CONFIG_KEY) as key:
            if isinstance(val, int):
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, val)
            else:
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, str(val))
    except Exception:
        pass

def is_autostart_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, APP_NAME)
            if val:
                return True
    except Exception:
        pass
    startup_dir = get_startup_dir()
    if startup_dir and os.path.exists(os.path.join(startup_dir, f"{APP_TITLE}.lnk")):
        return True
    return False

def set_autostart(enable: bool):
    dest_exe = get_installed_exe_path()
    exe_path = dest_exe if os.path.exists(dest_exe) else get_current_executable_path()
    run_cmd = f'"{exe_path}" --minimized'
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if enable:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, run_cmd)
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
    except Exception:
        pass

    startup_dir = get_startup_dir()
    if startup_dir:
        startup_lnk = os.path.join(startup_dir, f"{APP_TITLE}.lnk")
        if enable:
            dest_ico = os.path.join(get_program_files_dir(), "app.ico")
            create_windows_shortcut(exe_path, startup_lnk, dest_ico if os.path.exists(dest_ico) else None, APP_TITLE)
        else:
            if os.path.exists(startup_lnk):
                try:
                    os.remove(startup_lnk)
                except Exception:
                    pass

def is_system_registered():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, "DisplayName")
            if val == APP_TITLE:
                return True
    except Exception:
        pass
    return os.path.exists(get_installed_exe_path())

def register_system_install():
    try:
        target_dir = get_program_files_dir()
        os.makedirs(target_dir, exist_ok=True)

        curr_exe = get_current_executable_path()
        dest_exe = get_installed_exe_path()

        if curr_exe.lower().endswith(".exe"):
            if os.path.normcase(curr_exe) != os.path.normcase(dest_exe):
                shutil.copy2(curr_exe, dest_exe)
        else:
            # Script mode: copy script to target directory
            try:
                shutil.copy2(curr_exe, os.path.join(target_dir, os.path.basename(curr_exe)))
            except Exception:
                pass

        # Write icon for shortcuts and Add/Remove Programs
        dest_ico = os.path.join(target_dir, "app.ico")
        try:
            with open(dest_ico, "wb") as f:
                f.write(base64.b64decode(ICON_BASE64))
        except Exception:
            pass

        launch_target = dest_exe if os.path.exists(dest_exe) else curr_exe

        # Start Menu Shortcut
        programs_dir = get_start_menu_programs_dir()
        if programs_dir:
            start_menu_lnk = os.path.join(programs_dir, f"{APP_TITLE}.lnk")
            create_windows_shortcut(launch_target, start_menu_lnk, dest_ico, APP_TITLE)

        # Autostart configuration
        set_autostart(True)

        # Elevated Task Scheduler task for highest privileges at logon
        try:
            cmd = f'schtasks /create /tn "{APP_NAME}" /tr "\\"{launch_target}\\" --minimized" /sc onlogon /rl highest /f'
            subprocess.run(cmd, shell=True, capture_output=True, creationflags=0x08000000)
        except Exception:
            pass

        # Add/Remove Programs entry
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY) as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_TITLE)
                winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, APP_VERSION)
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Logitech MX Master Remapper")
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, target_dir)
                if os.path.exists(dest_ico):
                    winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, f'"{dest_ico}",0')
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{launch_target}" --uninstall')
                winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
        except Exception:
            pass

        return True, "Application registered in system successfully!"
    except Exception as e:
        return False, str(e)

def unregister_system_install():
    try:
        set_autostart(False)

        try:
            subprocess.run(f'schtasks /delete /tn "{APP_NAME}" /f', shell=True, capture_output=True, creationflags=0x08000000)
        except Exception:
            pass

        programs_dir = get_start_menu_programs_dir()
        if programs_dir:
            start_menu_lnk = os.path.join(programs_dir, f"{APP_TITLE}.lnk")
            if os.path.exists(start_menu_lnk):
                try:
                    os.remove(start_menu_lnk)
                except Exception:
                    pass

        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY)
        except Exception:
            pass

        return True, "Application registration removed from system."
    except Exception as e:
        return False, str(e)

# --- 5. Main Application Class ---
class LogiRemapperApp:
    def __init__(self):
        self.enabled_actions_ring = bool(get_saved_setting("RemapActionsRing", 1))
        self.is_actions_ring_pressed = False
        self.hwnd = None
        self.nid = None

        # Taskbar restart message
        self.wm_taskbar_created = user32.RegisterWindowMessageW("TaskbarCreated")

        self._init_window()
        self._init_raw_input()
        self._init_tray_icon()

        # Memory trimming timer: fires every 60 seconds
        user32.SetTimer(self.hwnd, 1, 60000, None)

        # Initial memory trim
        trim_memory()

    def _init_window(self):
        # Keep WNDPROC reference alive
        self._wndproc = WNDPROC(self.wnd_proc)

        hinstance = kernel32.GetModuleHandleW(None)
        wc = WNDCLASSW()
        wc.style = 0
        wc.lpfnWndProc = self._wndproc
        wc.cbClsExtra = 0
        wc.cbWndExtra = 0
        wc.hInstance = hinstance
        wc.hIcon = get_icon_handle(32)
        wc.hCursor = None
        wc.hbrBackground = None
        wc.lpszMenuName = None
        wc.lpszClassName = CLASS_NAME

        user32.RegisterClassW(ctypes.byref(wc))

        self.hwnd = user32.CreateWindowExW(
            0, CLASS_NAME, WINDOW_TITLE, 0,
            0, 0, 0, 0,
            None, None, hinstance, None
        )

    def _init_raw_input(self):
        devices = (RAWINPUTDEVICE * 4)(
            RAWINPUTDEVICE(0xFF00, 0x0001, RIDEV_INPUTSINK, self.hwnd),
            RAWINPUTDEVICE(0xFF00, 0x0002, RIDEV_INPUTSINK, self.hwnd),
            RAWINPUTDEVICE(0xFFA7, 0x0001, RIDEV_INPUTSINK, self.hwnd),
            RAWINPUTDEVICE(0xFF43, 0x0202, RIDEV_INPUTSINK, self.hwnd),
        )
        user32.RegisterRawInputDevices(devices, len(devices), ctypes.sizeof(RAWINPUTDEVICE))

    def _get_tooltip(self):
        status = "ON" if self.enabled_actions_ring else "OFF"
        return f"{APP_TITLE} (Remap: {status})"

    def _init_tray_icon(self):
        self.nid = NOTIFYICONDATAW()
        self.nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
        self.nid.hWnd = self.hwnd
        self.nid.uID = 1001
        self.nid.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
        self.nid.uCallbackMessage = WM_TRAY_CALLBACK
        self.nid.hIcon = get_icon_handle(16)
        self.nid.szTip = self._get_tooltip()
        shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(self.nid))

    def _update_tray_tooltip(self):
        if self.nid:
            self.nid.uFlags = NIF_TIP
            self.nid.szTip = self._get_tooltip()
            shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(self.nid))

    def _remove_tray_icon(self):
        if self.nid:
            try:
                shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(self.nid))
            except Exception:
                pass

    def show_tray_menu(self):
        pt = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(pt))

        hmenu = user32.CreatePopupMenu()
        if not hmenu:
            return

        # Title & Status Header
        user32.AppendMenuW(hmenu, MF_STRING | MF_DISABLED, ID_MENU_HEADER, f"{APP_TITLE} v{APP_VERSION}")

        status_text = (
            "Status: Installed in Program Files" if is_running_installed()
            else ("Status: Registered in System" if is_system_registered() else "Status: Portable Mode")
        )
        user32.AppendMenuW(hmenu, MF_STRING | MF_DISABLED, ID_MENU_STATUS, status_text)
        user32.AppendMenuW(hmenu, MF_SEPARATOR, 0, None)

        # Toggle Remap Actions Ring
        remap_flag = MF_CHECKED if self.enabled_actions_ring else MF_UNCHECKED
        user32.AppendMenuW(hmenu, MF_STRING | remap_flag, ID_MENU_REMAP, "Remap Action Ring (0x01A0) -> Middle Button")

        # Toggle Autostart
        autostart_flag = MF_CHECKED if is_autostart_enabled() else MF_UNCHECKED
        user32.AppendMenuW(hmenu, MF_STRING | autostart_flag, ID_MENU_AUTOSTART, "Start with Windows")

        user32.AppendMenuW(hmenu, MF_SEPARATOR, 0, None)

        # System Registration / Unregistration
        if not is_system_registered():
            user32.AppendMenuW(hmenu, MF_STRING, ID_MENU_INSTALL, "Install / Register in System (Program Files)")
        else:
            user32.AppendMenuW(hmenu, MF_STRING, ID_MENU_UNINSTALL, "Uninstall / Remove Registration")

        # Restart as Administrator (if standard user)
        if not is_admin():
            user32.AppendMenuW(hmenu, MF_STRING, ID_MENU_ELEVATE, "Restart as Administrator (Elevate)")

        user32.AppendMenuW(hmenu, MF_SEPARATOR, 0, None)
        user32.AppendMenuW(hmenu, MF_STRING, ID_MENU_EXIT, "Exit")

        user32.SetForegroundWindow(self.hwnd)
        cmd = user32.TrackPopupMenuEx(
            hmenu,
            TPM_RIGHTBUTTON | TPM_RETURNCMD | TPM_NONOTIFY,
            pt.x, pt.y,
            self.hwnd,
            None
        )
        user32.PostMessageW(self.hwnd, WM_NULL, 0, 0)
        user32.DestroyMenu(hmenu)

        if cmd:
            self.handle_menu_command(cmd)

    def handle_menu_command(self, cmd):
        if cmd == ID_MENU_REMAP:
            self.enabled_actions_ring = not self.enabled_actions_ring
            save_setting("RemapActionsRing", int(self.enabled_actions_ring))
            self._update_tray_tooltip()
            trim_memory()

        elif cmd == ID_MENU_AUTOSTART:
            new_state = not is_autostart_enabled()
            set_autostart(new_state)
            trim_memory()

        elif cmd == ID_MENU_INSTALL:
            if not is_admin():
                ret = user32.MessageBoxW(
                    self.hwnd,
                    "Installing into Program Files and setting up elevated Task Scheduler requires Administrator privileges.\\n\\nRestart as Administrator now?",
                    APP_TITLE,
                    0x00000004 | 0x00000030  # MB_YESNO | MB_ICONQUESTION
                )
                if ret == 6:  # IDYES
                    request_uac_elevation("--register")
                    self.quit()
                return

            ok, msg = register_system_install()
            if ok:
                user32.MessageBoxW(
                    self.hwnd,
                    f"{msg}\\nInstalled to Program Files and scheduled with highest privileges.",
                    APP_TITLE,
                    0x00000040  # MB_ICONINFORMATION
                )
            else:
                user32.MessageBoxW(
                    self.hwnd,
                    f"Installation failed:\\n{msg}",
                    APP_TITLE,
                    0x00000010  # MB_ICONERROR
                )
            trim_memory()

        elif cmd == ID_MENU_UNINSTALL:
            if not is_admin() and is_running_installed():
                ret = user32.MessageBoxW(
                    self.hwnd,
                    "Removing from Program Files requires Administrator privileges.\\n\\nRestart as Administrator now?",
                    APP_TITLE,
                    0x00000004 | 0x00000030
                )
                if ret == 6:
                    request_uac_elevation("--unregister")
                    self.quit()
                return

            ok, msg = unregister_system_install()
            user32.MessageBoxW(self.hwnd, msg, APP_TITLE, 0x00000040)
            trim_memory()

        elif cmd == ID_MENU_ELEVATE:
            if not is_admin():
                if request_uac_elevation(""):
                    self.quit()

        elif cmd == ID_MENU_EXIT:
            self.quit()

    def process_raw_input(self, lparam):
        try:
            size = wintypes.UINT(0)
            header_size = ctypes.sizeof(RAWINPUTHEADER)
            user32.GetRawInputData(lparam, RID_INPUT, None, ctypes.byref(size), header_size)
            if size.value == 0:
                return

            buf = ctypes.create_string_buffer(size.value)
            if user32.GetRawInputData(lparam, RID_INPUT, buf, ctypes.byref(size), header_size) != size.value:
                return

            raw_offset = 32 if IS_64BIT else 24
            raw_bytes = bytes(buf.raw[raw_offset:])

            # Logitech HID++ 0x11 long report: byte[3]=event_type, byte[4..5]=ctrl_id, byte[6]=state
            if len(raw_bytes) >= 7 and raw_bytes[0] == 0x11:
                event_type = raw_bytes[3]
                ctrl_id = (raw_bytes[4] << 8) | raw_bytes[5]
                state = raw_bytes[6]

                # Actions Ring ID (0x01A0) and Push Event (0x20)
                if ctrl_id == 0x01A0 and event_type == 0x20:
                    if state == 1 and not self.is_actions_ring_pressed:
                        self.is_actions_ring_pressed = True
                        if self.enabled_actions_ring:
                            user32.mouse_event(MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)
                    elif state == 0 and self.is_actions_ring_pressed:
                        self.is_actions_ring_pressed = False
                        if self.enabled_actions_ring:
                            user32.mouse_event(MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)
        except Exception:
            pass

    def wnd_proc(self, hwnd, msg, wp, lp):
        if msg == WM_INPUT:
            self.process_raw_input(lp)
            return 0

        elif msg == WM_TRAY_CALLBACK:
            # Mouse event on tray icon (Right Click or Left Click opens settings menu)
            if lp in (WM_RBUTTONUP, WM_LBUTTONUP):
                self.show_tray_menu()
            return 0

        elif hasattr(self, "wm_taskbar_created") and msg == self.wm_taskbar_created:
            # Explorer restarted, re-create tray icon
            self._init_tray_icon()
            return 0

        elif msg == WM_WAKEUP_NOTIFY:
            # Secondary instance launched; notify user via tray balloon
            try:
                self.nid.uFlags = NIF_INFO
                self.nid.szInfo = "Application is running in the system tray.\\nClick this icon to open settings."
                self.nid.szInfoTitle = APP_TITLE
                self.nid.dwInfoFlags = NIIF_INFO
                shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(self.nid))
            except Exception:
                pass
            return 0

        elif msg == WM_TIMER:
            trim_memory()
            return 0

        elif msg == WM_CLOSE or msg == WM_DESTROY:
            self.quit()
            return 0

        return user32.DefWindowProcW(hwnd, msg, wp, lp)

    def quit(self):
        self._remove_tray_icon()
        if self.hwnd:
            user32.KillTimer(self.hwnd, 1)
            user32.DestroyWindow(self.hwnd)
            self.hwnd = None
        user32.PostQuitMessage(0)

# --- 6. Entry Point ---
def main():
    # Handle command-line setup
    if "--register" in sys.argv or "-r" in sys.argv:
        ok, msg = register_system_install()
        if ok:
            user32.MessageBoxW(None, f"{msg}\\nInstalled to Program Files and scheduled with highest privileges at logon.", APP_TITLE, 0x40)
        else:
            user32.MessageBoxW(None, f"Registration failed:\\n{msg}", APP_TITLE, 0x10)
        sys.exit(0)

    elif "--unregister" in sys.argv or "--uninstall" in sys.argv or "-u" in sys.argv:
        ok, msg = unregister_system_install()
        user32.MessageBoxW(None, msg, APP_TITLE, 0x40)
        sys.exit(0)

    # Single-instance enforcement
    h_mutex = kernel32.CreateMutexW(None, True, SINGLE_INSTANCE_MUTEX)
    last_err = kernel32.GetLastError()

    if last_err == ERROR_ALREADY_EXISTS:
        # Signal primary instance to show notification
        hwnd_existing = user32.FindWindowW(CLASS_NAME, WINDOW_TITLE)
        if hwnd_existing:
            user32.PostMessageW(hwnd_existing, WM_WAKEUP_NOTIFY, 0, 0)
        else:
            user32.MessageBoxW(None, f"{APP_TITLE} is already running in the system tray.", APP_TITLE, 0x40)
        if h_mutex:
            kernel32.CloseHandle(h_mutex)
        sys.exit(0)

    # Run application
    app = LogiRemapperApp()

    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

    if h_mutex:
        kernel32.CloseHandle(h_mutex)

if __name__ == "__main__":
    main()
