# Quillastika

> Aplikasi manajemen keuangan pribadi untuk Android yang sederhana, privat, dan dapat digunakan secara offline.

Quillastika membantu pengguna mencatat pemasukan, pengeluaran, dan investasi dalam satu aplikasi. Pengguna dapat memantau budget bulanan, melihat perkembangan keuangan, serta mengekspor laporan dalam format PDF dan CSV.

Semua data disimpan secara lokal di perangkat tanpa akun dan tanpa server.

## Fitur

* Mencatat, mengubah, dan menghapus transaksi
* Informasi transaksi meliputi judul, jumlah, kategori, tanggal, dan catatan
* Mendukung transaksi pemasukan, pengeluaran, dan investasi
* Budget bulanan dengan progress pengeluaran
* Grafik donat arus keuangan
* Grafik tren laporan untuk periode 3, 6, dan 12 bulan
* Pencarian dan filter transaksi
* Ekspor laporan ke PDF
* Ekspor data ke CSV
* Berbagi file melalui dialog bawaan Android
* Penyimpanan data secara lokal menggunakan `localStorage`
* Tidak memerlukan akun atau server

## Teknologi

* HTML
* Tailwind CSS
* Alpine.js
* Chart.js
* jsPDF
* jsPDF AutoTable
* Capacitor 8
* Capacitor Filesystem
* Capacitor Share

Library `jsPDF` disimpan secara lokal di `www/vendor/` agar fitur ekspor PDF tetap dapat digunakan tanpa ketergantungan terhadap server eksternal.

## Struktur Proyek

```text
quillastika/
├── www/
│   ├── index.html
│   ├── services/
│   │   └── pdf/
│   └── vendor/
├── android/
├── capacitor.config.json
├── package.json
└── patch*.py
```

Keterangan:

* `www/` — source utama aplikasi web
* `www/index.html` — antarmuka dan logika utama aplikasi
* `www/services/pdf/` — modul pembuatan laporan PDF
* `www/vendor/` — library JavaScript lokal
* `android/` — project Android hasil sinkronisasi Capacitor
* `capacitor.config.json` — konfigurasi Capacitor
* `package.json` — dependency project
* `patch*.py` — script lama yang sudah tidak digunakan

## Menjalankan Project

### Browser

Install dependency terlebih dahulu:

```bash
npm install
```

Kemudian jalankan:

```bash
npx serve www
```

> Mode browser membutuhkan koneksi internet karena beberapa library seperti Tailwind CSS, Alpine.js, dan Chart.js masih dimuat melalui CDN.

### Android

Sinkronkan source web dengan project Android:

```bash
npx cap sync android
```

Kemudian buka folder `android/` menggunakan Android Studio dan jalankan aplikasi.

Atau build melalui terminal:

```bash
cd android
./gradlew assembleDebug
```

APK debug akan tersedia di:

```text
android/app/build/outputs/apk/debug/
```

## Development Workflow

Setelah melakukan perubahan pada file di dalam `www/`, jalankan:

```bash
npx cap sync android
```

sebelum melakukan build atau menjalankan aplikasi Android.

Alur pengembangan:

```text
Edit source di www/
        ↓
npx cap sync android
        ↓
Build / Run Android
```

## Informasi Aplikasi

| Informasi          | Detail              |
| ------------------ | ------------------- |
| Nama aplikasi      | Quillastika         |
| Platform           | Android             |
| Application ID     | `com.quill.finance` |
| Penyimpanan data   | `localStorage`      |
| Membutuhkan akun   | Tidak               |
| Membutuhkan server | Tidak               |

## Kompatibilitas Data

Application ID tetap menggunakan:

```text
com.quill.finance
```

Application ID tidak diubah agar Android tetap mengenali aplikasi sebagai aplikasi yang sama dan data pengguna sebelumnya tetap dapat dipertahankan.

Key `localStorage` berikut juga sengaja tidak diubah:

```text
quill_transactions
quill_target_budget
```

Hal ini memastikan data yang dibuat pada versi sebelumnya tetap dapat dibaca setelah proses rebranding dari Quill menjadi Quillastika.

## Status Project

Quillastika saat ini dikembangkan sebagai aplikasi manajemen keuangan pribadi berbasis Android dengan pendekatan offline-first.

## License

Project ini dikembangkan untuk keperluan personal dan pembelajaran.
