# GeoMag Studio

GeoMag Studio adalah aplikasi desktop untuk pemrosesan, koreksi, visualisasi,
interpretasi awal, dan export data magnetik geofisika.

## Fungsi utama

- Mengimpor data magnetometer SeaSPY2 dan Geometrics G-852 melalui adapter format yang terpisah.
- Menyimpan project agar pekerjaan dapat dibuka dan dilanjutkan kembali.
- Memvalidasi metadata, timestamp, koordinat, unit, dan kualitas data.
- Menyediakan database view, peta, dan profile view yang saling terhubung.
- Menandai data sebagai valid, suspect, excluded, interpolated, atau invalid.
- Mendeteksi spike dan outlier tanpa menghapus data mentah.
- Menyediakan koreksi magnetik seperti diurnal, IGRF, offset, lag, dan leveling secara bertahap.
- Menerapkan filtering, transformasi, dan gridding 2D.
- Mendukung reprojection CRS dan pengelolaan layer spasial.
- Membuat peta, profil, grid, serta export data untuk workflow GIS.
- Menyimpan parameter, riwayat processing, dan provenance agar hasil dapat ditelusuri.

## Prinsip desain

- Data mentah tidak diubah atau ditimpa.
- Deteksi outlier dipisahkan dari keputusan untuk mengecualikan data.
- Setiap hasil turunan memiliki referensi ke data sumber dan parameter proses.
- Workflow dapat diulang setelah parameter disimpan.
- Pengembangan dilakukan modular agar dapat diperluas ke modelling, inversi,
  dan metode geofisika lainnya.

## Fokus MVP

Versi awal berfokus pada data magnetik 2D/2.5D, import data, QC, koreksi
standar, filtering, gridding 2D, visualisasi, profile, dan export GIS.

Instrumen awal:

- SeaSPY2
- Geometrics G-852

## Status proyek

Proyek sedang berada pada tahap persiapan fondasi aplikasi dan desain format project.

