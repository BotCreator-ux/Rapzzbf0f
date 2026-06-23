#!/bin/bash

# 1. Tentukan nama file installer dan target script
INSTALLER_NAME="python_setup.exe"
INSTALLER_PATH="$TEMP/$INSTALLER_NAME"
TARGET_SCRIPT="save.pyw"  # Diubah ke .pyw agar saat diklik langsung memunculkan GUI tanpa CMD hitam

echo "=== [1/5] Mendownload Python Installer... ==="
# Download Python versi 3.11.9 resmi
curl -L -o "$INSTALLER_PATH" https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

if [ $? -eq 0 ]; then
    echo "✔ Download Python sukses!"
else
    echo "❌ Download Python gagal! Periksa koneksi internet Cloud PC lo."
    exit 1
fi

echo "=== [2/5] Menginstall Python secara Silent (Background)... ==="
# Menjalankan installer Windows lewat Bash secara background
./"$INSTALLER_PATH" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0

# Tunggu proses instalasi selesai di Windows background
sleep 5

# Hapus file installer setelah selesai biar bersih
rm -f "$INSTALLER_PATH"
echo "✔ Instalasi Python selesai!"

echo "=== [3/5] Konfigurasi Environment PATH di Git Bash... ==="
# Definisikan lokasi install Python standar di Windows lokal user
PYTHON_DIR="/c/Users/$USER/AppData/Local/Programs/Python/Python311"
SCRIPTS_DIR="$PYTHON_DIR/Scripts"

# Masukkan ke PATH sesi Git Bash saat ini biar langsung bisa dipanggil
export PATH="$SCRIPTS_DIR:$PYTHON_DIR:$PATH"

# Cek apakah python sudah terbaca dengan benar
if command -v python &> /dev/null; then
    echo "✔ Python berhasil terdeteksi: $(python --version)"
else
    echo "❌ Python belum terdeteksi di PATH. Coba restart Git Bash lo nanti."
    exit 1
fi

echo "=== [4/5] Mengupdate PIP & Menginstall PyInstaller... ==="
python -m pip install --upgrade pip --quiet
pip install pyinstaller

if command -v pyinstaller &> /dev/null; then
    echo "✔ PyInstaller berhasil terinstall!"
else
    echo "❌ Gagal menginstall PyInstaller."
fi

echo "=== [5/5] Mendownload Script GUI dari GitHub Lo... ==="
# Proses download file save.py milik lo langsung dari GitHub
curl -L -o "$TARGET_SCRIPT" https://raw.githubusercontent.com/BotCreator-ux/Rapzzbf0f/refs/heads/main/save.py

if [ $? -eq 0 ]; then
    echo "✔ File $TARGET_SCRIPT berhasil didownload!"
else
    echo "❌ Gagal mendownload script dari GitHub. Periksa kembali URL-nya."
    exit 1
fi

echo "========================================="
echo "🎉 SEMUANYA SELESAI & SIAP PAKAI!"
echo "========================================="
echo "1. Lo bisa langsung klik 2x file '$TARGET_SCRIPT' untuk membuka GUI."
echo "2. Atau kalau lo tetap mau dicompile ke EXE, jalankan perintah ini:"
echo "   pyinstaller --onefile --noconsole $TARGET_SCRIPT"
echo "========================================="
