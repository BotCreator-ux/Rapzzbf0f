#!/bin/bash

TARGET_SCRIPT="save.py"
INSTALLER_NAME="python_setup_env.exe"

echo "=== [1/5] Memeriksa Instalasi Python di Sistem... ==="
if command -v python &> /dev/null; then
    echo "✔ Python sudah terinstall! Versi: $(python --version)"
    SKIP_INSTALL=true
else
    PYTHON_DIR="/c/Users/$USER/AppData/Local/Programs/Python/Python311"
    if [ -d "$PYTHON_DIR" ]; then
        echo "✔ Menemukan folder Python di direktori lokal. Mengaktifkan PATH..."
        export PATH="$PYTHON_DIR/Scripts:$PYTHON_DIR:$PATH"
        SKIP_INSTALL=true
    else
        echo "⚠ Python tidak ditemukan. Menyiapkan proses download..."
        SKIP_INSTALL=false
    fi
fi

if [ "$SKIP_INSTALL" = false ]; then
    echo "=== [2/5] Mendownload Python Installer... ==="
    curl -L -o "./$INSTALLER_NAME" https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

    if [ $? -eq 0 ] && [ -f "./$INSTALLER_NAME" ]; then
        echo "✔ Download Python sukses!"
    else
        echo "❌ Download Python gagal!"
        exit 1
    fi

    echo "=== [3/5] Menginstall Python secara Silent... ==="
    ./"$INSTALLER_NAME" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    echo "Menunggu instalasi sistem selesai..."
    sleep 8
    rm -f "./$INSTALLER_NAME"
    
    PYTHON_DIR="/c/Users/$USER/AppData/Local/Programs/Python/Python311"
    export PATH="$PYTHON_DIR/Scripts:$PYTHON_DIR:$PATH"
    echo "✔ Instalasi Python selesai!"
else
    echo "=== [2/5 & 3/5] Langkah Instalasi Python Dilewati (Sudah Ada) ==="
fi

echo "=== [4/5] Memastikan PIP & PyInstaller Terpasang... ==="
python -m pip install --upgrade pip --quiet
pip install pyinstaller --quiet

echo "=== [5/5] Mendownload Script GUI dari GitHub... ==="
rm -f "./$TARGET_SCRIPT"
curl -L -o "./$TARGET_SCRIPT" https://raw.githubusercontent.com/BotCreator-ux/Rapzzbf0f/refs/heads/main/save.py

if [ $? -eq 0 ]; then
    echo "✔ File $TARGET_SCRIPT berhasil diperbarui dari GitHub!"
else
    echo "❌ Gagal mendownload script dari GitHub. Pastikan Anda sudah mengupdate file save.py di repositori."
    exit 1
fi

echo "=== [BONUS] MEMULAI PROSES COMPILE TO EXE... ==="
rm -rf build dist

pyinstaller --onefile --noconsole "$TARGET_SCRIPT"

if [ $? -eq 0 ]; then
    echo "========================================="
    echo "🎉 PROSES SELESAI & COMPILE SUKSES!"
    echo "========================================="
    echo "Silahkan cek folder 'dist', file 'save.exe' lo"
    echo "yang bebas bug sudah siap dipakai! 🤖🔥"
    echo "========================================="
else
    echo "❌ Proses compile ke EXE gagal."
fi
