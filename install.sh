#!/bin/bash

# 1. Tentukan nama file installer di folder aktif saat ini (bukan di %TEMP%)
INSTALLER_NAME="python_setup_env.exe"
TARGET_SCRIPT="save.pyw"

echo "=== [1/5] Mendownload Python Installer... ==="
# Download Python versi 3.11.9 resmi langsung ke folder saat ini
curl -L -o "./$INSTALLER_NAME" https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

if [ $? -eq 0 ] && [ -f "./$INSTALLER_NAME" ]; then
    echo "✔ Download Python sukses!"
else
    echo "❌ Download Python gagal! Folder terproteksi atau koneksi terputus."
    exit 1
fi

echo "=== [2/5] Menginstall Python secara Silent (Background)... ==="
# Menjalankan installer dari folder lokal aktif secara silent
./"$INSTALLER_NAME" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0

# Berikan jeda waktu agar Windows selesai mengekstrak file installer
echo "Menunggu instalasi sistem selesai..."
sleep 8

# Hapus file installer setelah selesai biar bersih
rm -f "./$INSTALLER_NAME"
echo "✔ Instalasi Python selesai!"

echo "=== [3/5] Konfigurasi Environment PATH di Git Bash... ==="
# Mengarahkan langsung ke lokasi instalasi lokal Windows
PYTHON_DIR="/c/Users/$USER/AppData/Local/Programs/Python/Python311"
SCRIPTS_DIR="$PYTHON_DIR/Scripts"

# Menyuntikkan secara paksa ke PATH Git Bash agar langsung aktif
export PATH="$SCRIPTS_DIR:$PYTHON_DIR:$PATH"

# Verifikasi ulang deteksi Python
if command -v python &> /dev/null; then
    echo "✔ Python berhasil terdeteksi: $(python --version)"
else
    echo "❌ Python masih belum terbaca di PATH sistem Cloud PC lo."
    exit 1
fi

echo "=== [4/5] Mengupdate PIP & Menginstall PyInstaller... ==="
python -m pip install --upgrade pip --quiet
pip install pyinstaller

echo "=== [5/5] Mendownload Script GUI dari GitHub Lo... ==="
# Proses download file save.py milik lo dari GitHub ke folder saat ini
curl -L -o "./$TARGET_SCRIPT" https://raw.githubusercontent.com/BotCreator-ux/Rapzzbf0f/refs/heads/main/save.py

if [ $? -eq 0 ]; then
    echo "✔ File $TARGET_SCRIPT berhasil didownload!"
else
    echo "❌ Gagal mendownload script dari GitHub."
    exit 1
fi

echo "========================================="
echo "🎉 SEMUANYA SELESAI & SIAP PAKAI!"
echo "========================================="
echo "Silahkan cek folder tempat lo menjalankan script ini,"
echo "File '$TARGET_SCRIPT' sudah siap di-klik 2x! 🥰"
echo "========================================="
