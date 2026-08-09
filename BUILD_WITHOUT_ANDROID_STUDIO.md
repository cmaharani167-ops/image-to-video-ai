# Build APK tanpa Android Studio

1. Buat akun GitHub.
2. Buat repository baru.
3. Upload semua isi ZIP ini ke repository.
4. Buka tab Actions.
5. Pilih workflow Build Release APK.
6. Tekan Run workflow.
7. Tunggu sampai selesai.
8. Download artifact ImageToVideoGemini-release.
9. Di dalam artifact terdapat app-release.apk.

Catatan:
- Backend tetap diperlukan agar Generate Video bekerja.
- Ubah BACKEND_URL di MainActivity.kt ke server backend kamu.
- Jangan masukkan GEMINI_API_KEY langsung ke APK.
