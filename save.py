import os
import shutil
import zipfile
import urllib.request
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

# Path Browser & Roblox
CHROME_PATH = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data')
EDGE_PATH = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data')
ROBLOX_REG_PATH = r"Software\Roblox\RobloxStudio"

TEMP_ZIP = os.path.expandvars(r'%TEMP%\cloud_pc_backup.zip')
ROBLOX_REG_FILE = os.path.expandvars(r'%TEMP%\roblox_login.reg')
CATBOX_API_URL = "https://catbox.moe/user/api.php"

def backup_folder(source_path, zip_object, arc_folder_name):
    if os.path.exists(source_path):
        for root_dir, dirs, files in os.walk(source_path):
            if 'Cache' in root_dir or 'System Profile' in root_dir:
                continue
            for file in files:
                full_path = os.path.join(root_dir, file)
                rel_path = os.path.relpath(full_path, source_path)
                
                # --- FIX ERROR TIMESTAMPS BEFORE 1980 ---
                try:
                    zinfo = zipfile.ZipInfo.from_file(full_path, os.path.join(arc_folder_name, rel_path))
                    
                    # Jika timestamp file di bawah tahun 1980, paksa set ke 1980 agar ZIP tidak crash
                    if zinfo.date_time[0] < 1980:
                        zinfo.date_time = (1980, 1, 1, 0, 0, 0)
                        
                    with open(full_path, 'rb') as f:
                        zip_object.writestr(zinfo, f.read(), zipfile.ZIP_DEFLATED)
                except Exception:
                    # Lewati file jika corrupt atau dikunci oleh sistem lain
                    continue

def upload_to_catbox(file_path):
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    data = []
    data.append(f'--{boundary}'.encode('utf-8'))
    data.append('Content-Disposition: form-data; name="reqtype"'.encode('utf-8'))
    data.append(''.encode('utf-8'))
    data.append('fileupload'.encode('utf-8'))
    
    data.append(f'--{boundary}'.encode('utf-8'))
    data.append(f'Content-Disposition: form-data; name="fileToUpload"; filename="{os.path.basename(file_path)}"'.encode('utf-8'))
    data.append('Content-Type: application/zip'.encode('utf-8'))
    data.append(''.encode('utf-8'))
    
    with open(file_path, 'rb') as f:
        data.append(f.read())
    data.append(f'--{boundary}--'.encode('utf-8'))
    
    payload = b'\r\n'.join(data)
    req = urllib.request.Request(CATBOX_API_URL, data=payload)
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    req.add_header('User-Agent', 'Mozilla/5.0')
    
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8').strip()

def toggle_save_all():
    val = save_all_var.get()
    save_chrome_var.set(val)
    save_roblox_var.set(val)
    save_edge_var.set(val)

def toggle_load_all():
    val = load_all_var.get()
    load_chrome_var.set(val)
    load_roblox_var.set(val)
    load_edge_var.set(val)

def run_save():
    if not (save_chrome_var.get() or save_roblox_var.get() or save_edge_var.get()):
        messagebox.showwarning("Peringatan", "Pilih minimal satu aplikasi untuk di-save!")
        return
        
    try:
        update_status("Menutup browser otomatis...", "#f9e2af")
        root.update()
        
        # --- FIX ERRNO 13: PAKSA TUTUP BROWSER BIAR LOCKFILE TIDAK DIKUNCI ---
        if save_chrome_var.get():
            os.system("taskkill /f /im chrome.exe >nul 2>&1")
        if save_edge_var.get():
            os.system("taskkill /f /im msedge.exe >nul 2>&1")
            
        update_status("Membuat file backup... Mohon tunggu.", "#f9e2af")
        root.update()
        
        if os.path.exists(TEMP_ZIP):
            os.remove(TEMP_ZIP)

        with zipfile.ZipFile(TEMP_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if save_chrome_var.get() and os.path.exists(CHROME_PATH):
                backup_folder(CHROME_PATH, zipf, 'Chrome')
            if save_edge_var.get() and os.path.exists(EDGE_PATH):
                backup_folder(EDGE_PATH, zipf, 'Edge')
            if save_roblox_var.get():
                try:
                    os.system(f'reg export "HKEY_CURRENT_USER\\{ROBLOX_REG_PATH}" "{ROBLOX_REG_FILE}" /y')
                    if os.path.exists(ROBLOX_REG_FILE):
                        zipf.write(ROBLOX_REG_FILE, 'roblox_login.reg')
                        os.remove(ROBLOX_REG_FILE)
                except:
                    pass

        update_status("Mengupload ke Cloud Catbox...", "#89b4fa")
        root.update()
        
        download_url = upload_to_catbox(TEMP_ZIP)
        if os.path.exists(TEMP_ZIP):
            os.remove(TEMP_ZIP)

        root.clipboard_clear()
        root.clipboard_append(download_url)
        update_status("Backup Berhasil! Link disalin.", "#a6e3a1")
        messagebox.showinfo("Sukses Ter-Upload!", f"Data berhasil disimpan di Cloud!\n\nLink Lo:\n{download_url}\n\n(Link otomatis tersalin ke clipboard!)")
    except Exception as e:
        update_status("Proses Save Gagal!", "#f38ba8")
        messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

def run_load():
    if not (load_chrome_var.get() or load_roblox_var.get() or load_edge_var.get()):
        messagebox.showwarning("Peringatan", "Pilih minimal satu aplikasi untuk di-load!")
        return
        
    url_input = simpledialog.askstring("Load Data", "Masukkan URL Link Catbox lo:")
    if not url_input: return
    if "catbox.moe" not in url_input:
        messagebox.showerror("Error", "Link tidak valid!")
        return

    try:
        update_status("Downloading dari Cloud...", "#89b4fa")
        root.update()
        urllib.request.urlretrieve(url_input, TEMP_ZIP)
        
        update_status("Restoring data...", "#f9e2af")
        root.update()

        # Matikan browser target sebelum merestore biar overwrite aman
        if load_chrome_var.get(): os.system("taskkill /f /im chrome.exe >nul 2>&1")
        if load_edge_var.get(): os.system("taskkill /f /im msedge.exe >nul 2>&1")

        temp_extract = os.path.expandvars(r'%TEMP%\temp_cloud_restore')
        if os.path.exists(temp_extract): shutil.rmtree(temp_extract)
        with zipfile.ZipFile(TEMP_ZIP, 'r') as zip_ref:
            zip_ref.extractall(temp_extract)

        if load_chrome_var.get() and os.path.exists(os.path.join(temp_extract, 'Chrome')):
            if os.path.exists(CHROME_PATH): shutil.rmtree(CHROME_PATH)
            shutil.copytree(os.path.join(temp_extract, 'Chrome'), CHROME_PATH)
            
        if load_edge_var.get() and os.path.exists(os.path.join(temp_extract, 'Edge')):
            if os.path.exists(EDGE_PATH): shutil.rmtree(EDGE_PATH)
            shutil.copytree(os.path.join(temp_extract, 'Edge'), EDGE_PATH)
            
        if load_roblox_var.get() and os.path.exists(os.path.join(temp_extract, 'roblox_login.reg')):
            os.system(f'reg import "{os.path.join(temp_extract, "roblox_login.reg")}"')

        shutil.rmtree(temp_extract)
        if os.path.exists(TEMP_ZIP): os.remove(TEMP_ZIP)

        update_status("Load Berhasil! Semua Akun Siap.", "#a6e3a1")
        messagebox.showinfo("Sukses", "Mantap! Data pilihan lo berhasil di-restore!")
    except Exception as e:
        update_status("Load Gagal!", "#f38ba8")
        messagebox.showerror("Error", f"Gagal restore: {str(e)}")

def update_status(text, color):
    status_label.config(text=f"Status: {text}", fg=color)

# --- INITIALIZE GUI ---
root = tk.Tk()
root.title("Rapzz Save Manager")
root.geometry("450x380")
root.configure(bg="#1e1e2e")

style = ttk.Style()
style.theme_use('default')
style.configure('TNotebook', background='#1e1e2e', borderwidth=0)
style.configure('TNotebook.Tab', background='#313244', foreground='#cdd6f4', padding=[15, 5], font=('Arial', 10, 'bold'))
style.map('TNotebook.Tab', background=[('selected', '#b4befe')], foreground=[('selected', '#11111b')])

# FIX TKINTER PADDING BUG: Menggunakan padx dan pady (bukan padding=10)
header_frame = tk.Frame(root, bg="#11111b", padx=10, pady=10)
header_frame.pack(fill="x")
logo_title = tk.Label(header_frame, text="🤖 Rapzz Save Manager", font=("Arial", 16, "bold"), bg="#11111b", fg="#cba6f7")
logo_title.pack()

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# Variabel Checkbox
save_all_var, save_chrome_var, save_roblox_var, save_edge_var = tk.BooleanVar(), tk.BooleanVar(value=True), tk.BooleanVar(), tk.BooleanVar()
load_all_var, load_chrome_var, load_roblox_var, load_edge_var = tk.BooleanVar(), tk.BooleanVar(value=True), tk.BooleanVar(), tk.BooleanVar()

# TAB 1: SAVE
tab_save = tk.Frame(notebook, bg="#1e1e2e")
notebook.add(tab_save, text=" SAVE ")
tk.Label(tab_save, text="PILIH DATA YANG MAU DI-SAVE:", font=("Arial", 10, "bold"), bg="#1e1e2e", fg="#a6adc8").pack(pady=10)
tk.Checkbutton(tab_save, text="ALL (PILIH SEMUA)", variable=save_all_var, command=toggle_save_all, bg="#1e1e2e", fg="#f9e2af", selectcolor="#313244", font=("Arial", 10, "bold")).pack(anchor="w", padx=40, pady=2)
tk.Checkbutton(tab_save, text="GOOGLE CHROME", variable=save_chrome_var, bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244").pack(anchor="w", padx=60, pady=2)
tk.Checkbutton(tab_save, text="ROBLOX STUDIO", variable=save_roblox_var, bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244").pack(anchor="w", padx=60, pady=2)
tk.Checkbutton(tab_save, text="MICROSOFT EDGE", variable=save_edge_var, bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244").pack(anchor="w", padx=60, pady=2)
tk.Button(tab_save, text="🔥 EXECUTE AUTO SAVE", font=("Arial", 11, "bold"), bg="#89b4fa", fg="#11111b", width=25, command=run_save, bd=0, cursor="hand2").pack(pady=15)

# TAB 2: LOAD
tab_load = tk.Frame(notebook, bg="#1e1e2e")
notebook.add(tab_load, text=" LOAD ")
tk.Label(tab_load, text="PILIH DATA YANG MAU DI-LOAD:", font=("Arial", 10, "bold"), bg="#1e1e2e", fg="#a6adc8").pack(pady=10)
tk.Checkbutton(tab_load, text="ALL (PILIH SEMUA)", variable=load_all_var, command=toggle_load_all, bg="#1e1e2e", fg="#f9e2af", selectcolor="#313244", font=("Arial", 10, "bold")).pack(anchor="w", padx=40, pady=2)
tk.Checkbutton(tab_load, text="GOOGLE CHROME", variable=load_chrome_var, bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244").pack(anchor="w", padx=60, pady=2)
tk.Checkbutton(tab_load, text="ROBLOX STUDIO", variable=load_roblox_var, bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244").pack(anchor="w", padx=60, pady=2)
tk.Checkbutton(tab_load, text="MICROSOFT EDGE", variable=load_edge_var, bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244").pack(anchor="w", padx=60, pady=2)
tk.Button(tab_load, text="⚡ DOWNLOAD & RESTORE", font=("Arial", 11, "bold"), bg="#a6e3a1", fg="#11111b", width=25, command=run_load, bd=0, cursor="hand2").pack(pady=15)

# TAB 3: CREDIT
tab_credit = tk.Frame(notebook, bg="#1e1e2e")
notebook.add(tab_credit, text=" CREDIT ")
tk.Label(tab_credit, text="THANKS TO", font=("Arial", 12, "bold"), bg="#1e1e2e", fg="#f38ba8").pack(pady=15)
tk.Label(tab_credit, text="👑 RAPZZ DEV", font=("Arial", 14, "bold"), bg="#1e1e2e", fg="#cba6f7").pack(pady=5)
tk.Label(tab_credit, text="🤖 GEMINI (FOR CODE)", font=("Arial", 11, "italic"), bg="#1e1e2e", fg="#94e2d5").pack(pady=5)

status_label = tk.Label(root, text="Status: Ready", font=("Arial", 9, "italic"), bg="#1e1e2e", fg="#a6adc8")
status_label.pack(side="bottom", fill="x", pady=5)

root.mainloop()
