# Logi_ActionRingRemapper
Remaps ActionRing on Logitech MX Master 4 mouse from "Do Nothing" to software Middle button emulation. (because a small indie startup "Logitech" can't create proper key remapping, lol)

coded by gemini 3.8 flash high, antigravity ide

there're a lot of bugs, but the core functionality is working, idk, you can fix them 🤷‍♂️

### i'm lazy, so below is a readable readme by ai:



# Logi Action Ring Remapper

Lightweight Windows background utility that remaps the Logitech MX Master thumb gesture button (Action Ring) directly to Middle Mouse Click without Logi Options+. Pure Python and WinAPI via ctypes (~2 MB RAM).

## Build

Compile into a standalone, windowless executable using Nuitka:

```powershell
python -m nuitka --standalone --onefile --windows-console-mode=disable --lto=yes --output-filename=logi_actionremapper.exe app2.py
```

## How It Works
Raw Input Capture: Uses RegisterRawInputDevices with RIDEV_INPUTSINK (HID pages 0xFF00, 0xFFA7, 0xFF43) to receive background reports without mouse hook latency (WH_MOUSE_LL).

HID++ Parsing: Intercepts WM_INPUT long reports (0x11), filtering for control ID 0x01A0 (Action Ring) and event 0x20 (Push).

Click Injection: Dispatches MOUSEEVENTF_MIDDLEDOWN and MOUSEEVENTF_MIDDLEUP via mouse_event.

Memory Trimming: Periodically calls psapi.EmptyWorkingSet on the app and its Nuitka onefile parent process.

System Integration: Single-instance mutex with tray wakeup, in-memory embedded icon, optional autostart, and Task Scheduler registration (/rl highest) for elevated window support.

CLI Options
--minimized: Start hidden in system tray (for autostart).
--register / -r: Copy to Program Files and create elevated logon task.
--unregister / -u: Remove installation, shortcuts, and scheduled task.
