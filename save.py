import os
import shutil
import zipfile
import urllib.request
import urllib.parse
import tkinter as tk
from tkinter import messagebox, simpledialog

# Path Browser & Roblox
CHROME_PATH = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data')
EDGE_PATH = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data')
ROBLOX_REG_PATH = r"Software\Roblox\RobloxStudio"

# File Sementara
TEMP_ZIP = os.path.expandvars(r'%TEMP%\cloud_pc_backup.zip')
ROBLOX_REG_FILE = os.path.expandvars(r'%TEMP%\roblox_login.reg')

# API Catbox
CATBOX_API_URL = "https://catbox.moe/user/api.php"

def backup_folder(source_path, zip_object, arc_folder_name):
    if os.path.exists(source_path):
        for root_dir, dirs, files in os.walk(source_path):
            # Skip cache biar ukurannya cuma puluhan MB!
            if 'Cache' in root_dir or 'System Profile' in root_dir:
                continue
            for file in files:
                full_path = os.path.join(root_dir, file)
                rel_path = os.path.relpath(full_path, source_path)
                zip_object.write(full_path, os.path.join(arc_folder_name, rel_path))

def upload_to_catbox(file_path):
    """Fungsi untuk upload anonymous ke Catbox via API multipart/form-data"""
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    data = []
    
    # Argumen 1: reqtype = fileupload
    data.append(f'--{boundary}'.encode('utf-8'))
    data.append('Content-Disposition: form-data; name="reqtype"'.encode('utf-8'))
    data.append(''.encode('utf-8'))
    data.append('fileupload'.encode('utf-8'))
    
    # Argumen 2: fileToUpload (Isi file zip)
    data.append(f'--{boundary}'.encode('utf-8'))
    data.append(f'Content-Disposition: form-data; name="fileToUpload"; filename="{os.path.basename(file_path)}"'.encode('utf-8'))
    data.append('Content-Type: application/zip'.encode('utf-8'))
    data.append(''.encode('utf-8'))
    
    with open(file_path, 'rb') as f:
        file_content = f.read()
    data.append(file_content)
    data.append(f'--{boundary}--'.encode('utf-8'))
    
    # Gabungkan semua data payload
    payload = b'\r\n'.join(data)
    
    req = urllib.request.Request(CATBOX_API_URL, data=payload)
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    req.add_header('User-Agent', 'Mozilla/5.0')
    
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8').strip()

def auto_save_and_upload():
    try:
        status_label.config(text="Zipping data... Mohon tunggu.", fg="#f9e2af")
        root.update()

        # 1. Export Registry Roblox
        try:
            os.system(f'reg export "HKEY_CURRENT_USER\\{ROBLOX_REG_PATH}" "{ROBLOX_REG_FILE}" /y')
            has_roblox = True
        except:
            has_roblox = False

        # 2. Packing ke ZIP
        if os.path.exists(TEMP_ZIP):
            os.remove(TEMP_ZIP)

        with zipfile.ZipFile(TEMP_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.exists(CHROME_PATH):
                backup_folder(CHROME_PATH, zipf, 'Chrome')
            if os.path.exists(EDGE_PATH):
                backup_folder(EDGE_PATH, zipf, 'Edge')
            if has_roblox and os.path.exists(ROBLOX_REG_FILE):
                zipf.write(ROBLOX_REG_FILE, 'roblox_login.reg')
                os.remove(ROBLOX_REG_FILE)

        # 3. Otomatis Upload ke Catbox
        status_label.config(text="Mengupload ke Catbox cloud...", fg="#89b4fa")
        root.update()
        
        download_url = upload_to_catbox(TEMP_ZIP)
        
        # Hapus file zip sementara di lokal
        if os.path.exists(TEMP_ZIP):
            os.remove(TEMP_ZIP)

        status_label.config(text="Upload Berhasil!", fg="#a6e3a1")
        
        # Tampilkan Link dan otomatis salin ke clipboard
        root.clipboard_clear()
        root.clipboard_append(download_url)
        messagebox.showinfo("Sukses Ter-Upload!", f"Data BERHASIL disimpan di Cloud Catbox!\n\nLink Lo:\n{download_url}\n\n(Link sudah otomatis tersalin ke Clipboard lo, tinggal paste/simpan aja!)")
        
    except Exception as e:
        status_label.config(text="Proses Gagal!", fg="#f38ba8")
        messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}\n(Pastikan browser & Roblox sudah ditutup)")

def download_and_load():
    # Minta user input link Catbox-nya
    url_input = simpledialog.askstring("Load Data", "Masukkan URL Link Catbox lo:\n(Contoh: https://files.catbox.moe/xxxxxx.zip)")
    
    if not url_input:
        return
        
    if "catbox.moe" not in url_input:
        messagebox.showerror("Error", "Link yang lo masukkan bukan link Catbox yang valid!")
        return

    try:
        status_label.config(text="Mendownload data dari Cloud...", fg="#89b4fa")
        root.update()
        
        # Download file ZIP dari Catbox
        urllib.request.urlretrieve(url_input, TEMP_ZIP)
        
        status_label.config(text="Sedang merestore data...", fg="#f9e2af")
        root.update()

        # Ekstrak data
        temp_extract = os.path.expandvars(r'%TEMP%\temp_cloud_restore')
        if os.path.exists(temp_extract):
            shutil.rmtree(temp_extract)
            
        with zipfile.ZipFile(TEMP_ZIP, 'r') as zip_ref:
            zip_ref.extractall(temp_extract)

        # 1. Restore Chrome
        chrome_src = os.path.join(temp_extract, 'Chrome')
        if os.path.exists(chrome_src):
            if os.path.exists(CHROME_PATH):
                shutil.rmtree(CHROME_PATH)
            shutil.copytree(chrome_src, CHROME_PATH)

        # 2. Restore Edge
        edge_src = os.path.join(temp_extract, 'Edge')
        if os.path.exists(edge_src):
            if os.path.exists(EDGE_PATH):
                shutil.rmtree(EDGE_PATH)
            shutil.copytree(edge_src, EDGE_PATH)

        # 3. Restore Registry Roblox
        roblox_reg_src = os.path.join(temp_extract, 'roblox_login.reg')
        if os.path.exists(roblox_reg_src):
            os.system(f'reg import "{roblox_reg_src}"')

        # Bersihkan sisa file
        shutil.rmtree(temp_extract)
        if os.path.exists(TEMP_ZIP):
            os.remove(TEMP_ZIP)

        status_label.config(text="Load All Berhasil! Semua Akun Siap.", fg="#a6e3a1")
        messagebox.showinfo("Sukses", "Mantap! Semua akun (Chrome, Edge, Roblox) otomatis login kembali!")
        
    except Exception as e:
        status_label.config(text="Load Gagal!", fg="#f38ba8")
        messagebox.showerror("Error", f"Gagal restore data: {str(e)}\n(Pastikan link benar & browser ditutup!)")

# GUI Dashboard (Cyberpunk Dark Theme)
root = tk.Tk()
root.title("Cloud PC Auto-Cloud Save Manager")
root.geometry("450x280")
root.configure(bg="#1e1e2e")

title_label = tk.Label(root, text="CLOUD PC SAVE MANAGER V3", font=("Arial", 14, "bold"), bg="#1e1e2e", fg="#cba6f7")
title_label.pack(pady=15)

btn_backup = tk.Button(root, text="🔥 AUTO SAVE TO CLOUD", font=("Arial", 11, "bold"), bg="#89b4fa", fg="#11111b", width=28, command=auto_save_and_upload)
btn_backup.pack(pady=10)

btn_restore = tk.Button(root, text="⚡ DOWNLOAD & LOAD ALL", font=("Arial", 11, "bold"), bg="#a6e3a1", fg="#11111b", width=28, command=download_and_load)
btn_restore.pack(pady=10)

status_label = tk.Label(root, text="Status: Ready (Fitur Cloud Catbox Aktif)", font=("Arial", 9, "italic"), bg="#1e1e2e", fg="#a6adc8")
status_label.pack(pady=20)

root.mainloop()
  
