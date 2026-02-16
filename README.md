# Prompt Refiner ✦

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![Cerebras](https://img.shields.io/badge/AI-Cerebras-black?style=for-the-badge)

**Ubah prompt sederhana menjadi instruksi level produksi yang kuat, terstruktur, dan efektif.**

Prompt Refiner adalah aplikasi berbasis AI yang membantu Anda meningkatkan kualitas prompt untuk LLM (Large Language Models). Dengan pendekatan "Interview & Refine", aplikasi ini menganalisis maksud Anda, mengajukan pertanyaan klarifikasi, dan menghasilkan prompt yang sangat optimal dalam format profesional (RTF, xml, markdown, dll).

---

## Fitur Utama

- **Analisis Cerdas**: AI menganalisis prompt awal Anda untuk menemukan ambiguitas.
- **Mode Wawancara**: Mengajukan pertanyaan spesifik (Umum, Teknis, Kreatif, dll) untuk menggali konteks.
- **Template Siap Pakai**: Beragam template prompt built-in untuk Coding, Writing, Learning, dan lainnya.
- **Dukungan Bilingual**: Antarmuka penuh dalam **Bahasa Inggris** dan **Bahasa Indonesia**.
- **UI Minimalis & Modern**: Desain antarmuka "Dark Mode" yang fokus pada konten dan pengalaman pengguna.
- **Aman & Privat**: Tidak ada penyimpanan kunci API di kode, konfigurasi keamanan ketat.

## Teknologi

- **Frontend**: [Streamlit](https://streamlit.io/) dengan kustomisasi CSS tingkat lanjut.
- **AI Engine**: [Cerebras Cloud SDK](https://cerebras.net/) untuk inferensi super cepat.
- **UI Components**: `streamlit-antd-components` untuk navigasi modern.

## Instalasi & Setup

Ikuti langkah-langkah berikut untuk menjalankan aplikasi di komputer lokal Anda.

### Prasyarat

- Python 3.10 atau lebih baru.
- API Key dari [Cerebras Cloud](https://cloud.cerebras.net/).

### Langkah-langkah

1. **Clone Repository**

   ```bash
   git clone https://github.com/username/Prompt-Improver.git
   cd Prompt-Improver
   ```

2. **Buat Virtual Environment**

   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install Dependensi**

   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi Environment**

   Salin file `.env.example` menjadi `.env` dan masukkan API Key Anda.

   ```bash
   cp .env.example .env
   ```

   Edit file `.env`:

   ```ini
   CEREBRAS_API_KEY=your_api_key_here
   ```

5. **Jalankan Aplikasi**

   ```bash
   streamlit run app.py
   ```

## Cara Penggunaan

1. **Pilih Template (Opsional)**: Buka sidebar bagian "Template" dan pilih kasus penggunaan (misal: *Coding - Optimize*).
2. **Input Prompt**: Masukkan ide awal Anda di kotak teks utama.
3. **Analisis**: Klik tombol **Analisis Prompt**. AI akan memberikan beberapa pertanyaan klarifikasi.
4. **Jawab Pertanyaan**: Berikan konteks tambahan dengan menjawab pertanyaan yang muncul.
5. **Generate**: Klik **Refine Prompt**.
6. **Hasil**: Salin prompt yang sudah dioptimalkan dan gunakan di ChatGPT, Claude, atau model lainnya.

## Struktur Proyek

```text
Prompt-Improver/
├── .streamlit/         # Konfigurasi tema Streamlit
├── Command/            # Dokumentasi & panduan
├── data/               # File konfigurasi JSON (models, templates, translations)
├── prompts/            # System prompts untuk AI (interviewer, refiner)
├── tests/              # Unit tests
├── utils/              # Modul logika (ai_engine, auth, security, ui)
├── app.py              # Entry point aplikasi utama
├── requirements.txt    # Daftar dependensi
└── README.md           # Dokumentasi proyek
```

## Kreator

Dibuat oleh:

- **Syaasr** - [GitHub](https://www.github.com/Syaasr)
- **Syaikhasril Maulana F.** - [LinkedIn](https://www.linkedin.com/in/syaikhasrilmf/)

---

> *"Reduction is the ultimate sophistication."*
