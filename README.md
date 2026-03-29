# Proje Adı (Buraya Projenin Adını Yazın)

Bu proje, modern web teknolojileri kullanılarak geliştirilmiş tam yığın (full-stack) bir uygulamadır. Tüm mimari Docker kullanılarak konteynerize edilmiş olup, geliştirme ve canlı ortamlarda sorunsuz çalışacak şekilde tasarlanmıştır.

## 🚀 Teknolojiler

* **Frontend:** React (TypeScript) + Vite
* **Backend:** .NET 9 (ASP.NET Core Web API) - Çok Katmanlı Mimari
* **Veritabanı:** PostgreSQL
* **Orkestrasyon:** Docker & Docker Compose

## 📋 Gereksinimler

Projeyi kendi bilgisayarınızda çalıştırmak için sisteminizde sadece aşağıdaki aracın kurulu olması yeterlidir (Node.js, .NET SDK veya PostgreSQL kurmanıza gerek **yoktur**):

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (veya Docker CLI & Docker Compose)

## 🛠️ Kurulum Adımları

**1. Çevresel Değişkenleri Ayarlayın**

Güvenlik gereği veritabanı şifreleri versiyon kontrol sistemine (Git) dahil edilmemiştir. Projeyi çalıştırmadan önce ana dizinde (bu dosyanın bulunduğu yerde) bir `.env` dosyası oluşturun ve içine şu bilgileri kendi belirleyeceğiniz şifrelerle ekleyin:

```env
DB_USER=root
DB_PASSWORD=kendi_guvenli_sifrenizi_yazin
DB_NAME=projedb
```

## 💻 Projeyi Çalıştırma
Terminalinizi proje ana dizininde açın ve durumunuza uygun komutu çalıştırın:

* **İlk Kurulum veya Kod Güncellemesi Sonrası:**
Kodu ilk kez indirdiğinizde veya projede (C# veya React tarafında) bir değişiklik yaptığınızda, imajların baştan derlenmesi için aşağıdaki komutu kullanın:

  ```bash
  docker compose up --build
  ```

* **Normal Çalıştırma (Kodda değişiklik yoksa):**
Sistemi daha hızlı ayağa kaldırmak için:

  ```bash
  docker compose up
  ```

* **Arka Planda Çalıştırma (Terminali meşgul etmemek için):**
Komutların sonuna -d parametresini ekleyebilirsiniz (örn: docker compose up -d). Sistemi durdurmak için ise docker compose down komutunu kullanabilirsiniz.

## 🌐 Erişilebilirlik
Konteynerler başarıyla ayağa kalktıktan sonra uygulamaya şu adreslerden erişebilirsiniz:

* **Web Arayüzü (Frontend): http://localhost:3000**

* **API Dökümantasyonu (Swagger): http://localhost:8080/swagger**