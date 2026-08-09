# ImageToVideoGemini Full Starter

Aplikasi Android + backend FastAPI untuk image-to-video menggunakan Google Gemini API / Veo.

Google saat ini mendokumentasikan image-to-video dengan Veo 3.1 melalui Gemini API. Veo 3.1 mendukung gambar awal, rasio 9:16/16:9, durasi 4/6/8 detik, dan output dengan audio. Akses/model yang tersedia dapat berbeda berdasarkan akun/API project.

## Struktur
- `app/` = APK Android
- `backend/` = server yang menyimpan Gemini API key

## Urutan pemakaian
1. Buat API key Google AI.
2. Jalankan backend.
3. Isi `.env`.
4. Set `PUBLIC_BASE_URL` ke alamat backend.
5. Ubah `BACKEND_URL` di `MainActivity.kt`.
6. Build APK dari Android Studio.

Jangan menaruh `GEMINI_API_KEY` di APK.
