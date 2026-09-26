# Skrip Demo AgriSafe AI

## Mesej utama
AgriSafe AI membantu petani menjawab tiga soalan: adakah kerja ini sesuai dibuat sekarang, apakah sebab risikonya, dan bila masa yang lebih selamat.

## Persediaan

1. Jalankan aplikasi pada port lalai:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn agrisafe_ai.app.main:app --host 0.0.0.0 --port 8011
   ```

2. Buka `http://localhost:8011`.
3. Pastikan bahasa ialah `Bahasa Melayu` dan `Guna mod demo` ditanda.

## Demo 3 minit

### 1. Tunjukkan kes berisiko

Pilih `Sembur racun ketika panas dan berangin` dalam menu `Demo pantas`, kemudian tekan `Semak keselamatan`.

Sebut:

> "Petani bukan hanya menerima warna merah. Sistem menerangkan sebabnya: suhu dan kelembapan meningkatkan tekanan haba, angin meningkatkan risiko semburan terbawa angin, dan PPE belum disahkan lengkap."

Tunjukkan bahagian `Kenapa keputusan ini?` dan `Apa yang patut saya buat?`.

### 2. Tunjukkan cadangan yang boleh diambil tindakan

Tekan `Cari masa yang lebih selamat`.

Sebut:

> "AgriSafe AI tidak berhenti pada 'jangan buat'. Ia membandingkan beberapa masa dan menunjukkan masa yang mempunyai skor risiko lebih rendah serta sebab setiap cadangan."

### 3. Tunjukkan kes yang lebih baik

Pilih `Cari masa lebih sesuai untuk semburan`, kemudian tekan `Semak keselamatan`.

Sebut:

> "Apabila masa, cuaca, PPE dan peralatan diperbaiki, keputusan berubah. Ini menunjukkan bagaimana petani boleh mengubah rancangan kerja, bukan sekadar menerima amaran."

### 4. Tutup dengan nilai sistem

> "Keputusan ini boleh diterangkan, direkodkan dan diulang untuk kerja seterusnya. Sistem menyokong keputusan petani; ia tidak menggantikan label produk, SDS atau SOP ladang."

## Nota keselamatan

Data demonstrasi menggunakan rekod bahan kimia contoh. Untuk penggunaan sebenar, gantikan data contoh dengan label produk dan SDS yang disahkan.
