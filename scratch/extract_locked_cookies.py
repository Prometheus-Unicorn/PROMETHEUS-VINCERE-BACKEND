import ctypes
from ctypes import wintypes
import os
import win32api
import win32con

ntdll = ctypes.WinDLL("ntdll.dll")
kernel32 = ctypes.WinDLL("kernel32.dll")

SystemHandleInformation = 16

# Get chrome PIDs
import psutil

chrome_pids = []
for p in psutil.process_iter(['pid', 'name', 'cmdline']):
    if p.info['name'] and 'chrome' in p.info['name'].lower():
        chrome_pids.append(p.info['pid'])

print("Chrome PIDs:", chrome_pids)

# Let's allocate buffer for NtQuerySystemInformation
size = 8 * 1024 * 1024
buf = ctypes.create_string_buffer(size)
ret_len = wintypes.ULONG()

status = ntdll.NtQuerySystemInformation(SystemHandleInformation, buf, size, ctypes.byref(ret_len))
if status != 0:
    size = ret_len.value + 1024 * 1024
    buf = ctypes.create_string_buffer(size)
    status = ntdll.NtQuerySystemInformation(SystemHandleInformation, buf, size, ctypes.byref(ret_len))

print("NtQuerySystemInformation status:", hex(status & 0xFFFFFFFF))

num_handles = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ulong)).contents.value
print("Total system handles:", num_handles)

offset = ctypes.sizeof(ctypes.c_ulong)
# On 64-bit systems alignment might require skipping 4 bytes or struct size 24 bytes
# Let's check entry struct
class SYSTEM_HANDLE_ENTRY(ctypes.Structure):
    _fields_ = [
        ("OwnerPid", wintypes.ULONG),
        ("ObjectType", ctypes.c_ubyte),
        ("HandleFlags", ctypes.c_ubyte),
        ("HandleValue", wintypes.USHORT),
        ("ObjectPointer", ctypes.c_void_p),
        ("AccessMask", wintypes.ULONG),
    ]

# In 64-bit Windows, SYSTEM_HANDLE_INFORMATION has ULONG_PTR NumberOfHandles (8 bytes)
# followed by array of SYSTEM_HANDLE_TABLE_ENTRY_INFO (24 bytes)
num_handles_64 = ctypes.cast(buf, ctypes.POINTER(ctypes.c_size_t)).contents.value
print("NumberOfHandles (64-bit):", num_handles_64)

entry_size = 24
offset = ctypes.sizeof(ctypes.c_size_t)

found_handle = None
target_pid = None

for i in range(min(num_handles_64, 500000)):
    entry_bytes = buf[offset : offset + entry_size]
    offset += entry_size
    pid = int.from_bytes(entry_bytes[0:4], "little")
    handle_val = int.from_bytes(entry_bytes[6:8], "little")
    if pid in chrome_pids:
        # Try duplicating
        h_proc = kernel32.OpenProcess(win32con.PROCESS_DUP_HANDLE, False, pid)
        if h_proc:
            dup_handle = wintypes.HANDLE()
            res = kernel32.DuplicateHandle(
                h_proc,
                handle_val,
                kernel32.GetCurrentProcess(),
                ctypes.byref(dup_handle),
                0,
                False,
                win32con.DUPLICATE_SAME_ACCESS
            )
            if res:
                # Query file path
                name_buf = ctypes.create_unicode_buffer(1024)
                name_len = kernel32.GetFinalPathNameByHandleW(dup_handle, name_buf, 1024, 0)
                if name_len > 0:
                    path = name_buf.value
                    if "cookies" in path.lower() and "profile 12" in path.lower() and not "journal" in path.lower():
                        print(f"FOUND COOKIES HANDLE! PID: {pid}, Handle: {hex(handle_val)}, Path: {path}")
                        found_handle = dup_handle.value
                        target_pid = pid
                        # Read file contents!
                        kernel32.SetFilePointer(found_handle, 0, None, 0)
                        file_size = kernel32.GetFileSize(found_handle, None)
                        print(f"File size: {file_size} bytes")
                        read_buf = ctypes.create_string_buffer(file_size)
                        bytes_read = wintypes.ULONG()
                        kernel32.ReadFile(found_handle, read_buf, file_size, ctypes.byref(bytes_read), None)
                        with open("scratch/live_cookies.db", "wb") as out_f:
                            out_f.write(read_buf.raw[:bytes_read.value])
                        print(f"SAVED {bytes_read.value} BYTES TO scratch/live_cookies.db!")
                        kernel32.CloseHandle(dup_handle)
                        kernel32.CloseHandle(h_proc)
                        break
                kernel32.CloseHandle(dup_handle)
            kernel32.CloseHandle(h_proc)

if found_handle:
    print("SUCCESSFULLY EXTRACTED LIVE COOKIES DATABASE!")
else:
    print("Could not find Cookies handle in Chrome processes.")
