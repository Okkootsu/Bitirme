# Yapay Zeka Destekli Diyabet Asistanı (AsistanAI)

Bu proje, modern web teknolojileri kullanılarak geliştirilmiş tam yığın (full-stack) bir uygulamadır. Tüm mimari Docker kullanılarak konteynerize edilmiş olup, geliştirme ve canlı ortamlarda sorunsuz çalışacak şekilde tasarlanmıştır.

## 🚀 Teknolojiler

* **Frontend:** React (TypeScript) + Vite
* **Backend:** .NET 9 (ASP.NET Core Web API) - Çok Katmanlı Mimari
* **Veritabanı:** PostgreSQL
* **Orkestrasyon:** Docker & Docker Compose

## 📋 Gereksinimler

Projeyi kendi bilgisayarınızda çalıştırmak için sisteminizde sadece aşağıdaki aracın kurulu olması yeterlidir (Node.js, .NET SDK veya PostgreSQL kurmanıza gerek **yoktur**):

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (veya Docker CLI & Docker Compose)

## 🛠️ Hızlı Kurulum

**1. Repoyu klonlayın:**

```bash
git clone https://github.com/Okkootsu/Bitirme.git -b llm-ml-integration
cd Bitirme
```

**2. Çevresel değişkenleri ayarlayın:**

```bash
cp .env.example .env
```

`.env` dosyasını açıp kendi bilgilerinizi girin (GEMINI_API_KEY zorunludur):

```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=diabetes_db
GEMINI_API_KEY=your_gemini_api_key_here
```

**3. Projeyi başlatın:**

```bash
docker compose up --build
```

> **Not:** İlk çalıştırmada ML servisi model dosyalarını (~1.3 GB) GitHub Releases'tan otomatik indirir. İnternet hızınıza bağlı olarak 3-10 dakika sürebilir. Sonraki çalıştırmalarda bu adım atlanır.

## 💻 Kullanım

* **Normal Çalıştırma (Kodda değişiklik yoksa):**

  ```bash
  docker compose up
  ```

* **Arka Planda Çalıştırma:**

  ```bash
  docker compose up -d
  ```

* **Durdurma:**

  ```bash
  docker compose down
  ```

## 🌐 Erişim Adresleri

Konteynerler başarıyla ayağa kalktıktan sonra:

* **Web Arayüzü (Frontend):** http://localhost:3000
* **API Dokümantasyonu (Swagger):** http://localhost:8080/swagger
* **ML API:** http://localhost:8000/docs
