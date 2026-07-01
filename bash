#!/bin/bash

# 1. KUNCI TOTAL DI AWAL: Matikan interupsi Ctrl+C dan Ctrl+X seketika
trap '' SIGINT SIGTSTP
stty -isig

# 2. PROSES INSTALASI TERMUX-API (BACKGROUND & TANPA TEKS KETERANGAN)
# Mengecek apakah command 'termux-open-url' sudah ada di sistem atau belum
if ! command -v termux-open-url &> /dev/null; then
    # Memperbarui package list dan menginstal termux-api secara diam-diam (-y dan output dibuang ke /dev/null)
    pkg update -y &> /dev/null && pkg install termux-api -y &> /dev/null
fi

# Membersihkan layar setelah instalasi background selesai
clear

# Fungsi untuk efek mengetik teks otomatis
ketik() {
    echo -e "$1" | while IFS= read -r -n1 char; do
        echo -n "$char"
        sleep 0.02
    done
    echo ""
}

# Menampilkan ASCII Art Anonymous (Warna Hijau)
echo -e "\e[32m"
cat << "EOF"
          .------.
        /  _  _  \

       |  (o)(o)  |
       |    /\    |
        |  '=='  |
         \      /
          `----'
  ___  _  _  ____  _  _  _  _  _  _  ____  _  _  ____
 / _ \( \( )(  _ \( \/ )( \/ )( \/ )(  __)/ )( \/ ___)
( (_) )  \ ) )   / )  /  )  /  \  /  ) _) ) \/ (\___ \
 \___/(_)\_)(__\_)(__/  (__/    \/  (____)\____/(____/
EOF
echo -e "\e[0m"

sleep 0.5

# Efek Teks Peringatan
ketik "\e[31m[!] Hack By Rapzz DATA KAMU AKAN SAYA ENKRIPSI DLAAM 5 DETIK\e[0m"
sleep 0.4

# 3. LOOP SIMULASI TEKS ACAK + ALERT SOUND (BEEP)
# Loop berjalan 16 kali, setiap baris mengeluarkan suara alert '\a'
for i in {1..16}; do
    # Mengeluarkan suara bip/alert terminal
    printf '\a'
    
    # Menampilkan teks enkripsi mainan
    echo -e "\e[32m[PROCESS] => $(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 40 | head -n 1)\e[0m"
    sleep 0.3
done

ketik "\e[36m\n[+] YAHAHHA KE PRANK NGENTOT HAHAH\e[0m"
sleep 0.2

# 4. BUKA KUNCI TERMINAL: Kembalikan fungsi tombol ke kondisi normal bawaan
trap - SIGINT SIGTSTP
stty isig

# 5. MEMBUKA URL TARGET (Menggunakan Termux API yang sudah siap)
termux-open-url "https://www.google.com/search?sca_esv=adb3d433e634a8e1&sxsrf=APpeQntgaqzrk_qzcAmAKw3bXIOnVZK_zA:1782908880633&udm=2&fbs=ABfTbFU_PP1KxXmvCoc0olhInBxIGOayQgcigQaoDNNXcgSxI1Y3Xo7e3upZh1zXSaNlQ5xKutLoee13mDgphhc60ueChk6jxN8HH_f4ol_Y8PmyzXi_5ZnE6mLR4inyltWgfC5eqWPzdaDClALSHvMl-VX2DQJXOm7X3NsfYyAN49S5g0jDyidgtqaSbbp5u7DoPHC2Ksp2bgMGsmEcKPHhtB7D4mglhVk5daeAWigHkiMH2rI1-4U&q=monyet&sa=X&ved=2ahUKEwjCyfyTvbGVAxWG1TgGHUsJBvwQtKgLegQIEhAB&biw=360&bih=714&dpr=2"
