"""
One-time script to prepare RagMakaleler PDFs for the RAG knowledge base.
- Removes duplicate file
- Sanitizes filenames (ASCII-safe)
- Copies PDFs to knowledge_base/
- Updates metadata.json with titles, categories, and source_type
"""
import os
import sys
import json
import shutil
import re
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAG_DIR = os.path.join(ROOT, "RagMakaleler")
KB_DIR = os.path.join(ROOT, "knowledge_base")
METADATA_PATH = os.path.join(KB_DIR, "metadata.json")

# Mapping: original filename -> (sanitized_name, title, category)
ARTICLE_MAP = [
    (
        "10.11.pdf",
        "gebe_ve_diyabet.pdf",
        "Gebe ve Diyabet",
        "Klinik Tıp & Tanı-Tedavi",
    ),
    (
        "10.17343-sdutfd.264358-457336.pdf",
        "insulin_direnci_klinik_onemi.pdf",
        "İnsülin Direnci ve Klinik Önemi",
        "Genetik & Patofizyoloji",
    ),
    (
        "10.17826-cumj.551234-752737.pdf",
        "tip2_diyabet_semptom_hba1c.pdf",
        "Tip 2 Diyabetli Bireylerde Algılanan Semptom Düzeyi ile HbA1c İlişkisi",
        "Hemşirelik, Öz Bakım & Hasta Eğitimi",
    ),
    (
        "10.17942-sted.876596-1563838.pdf",
        "diyabet_risk_farkindaligi_metropol.pdf",
        "Diyabet Risk Farkındalığı: Bir Metropol Örneği",
        "Halk Sağlığı & Epidemiyoloji",
    ),
    (
        "10.18229-ktd.41969-161691.pdf",
        "insulin_direnci_derleme.pdf",
        "İnsülin Direnci",
        "Genetik & Patofizyoloji",
    ),
    (
        "10.18521-ktd.05733-107877.pdf",
        "diyabet_yasam_kalitesi_pilot.pdf",
        "Diyabet Tanısıyla İzlenen Hastalarda Yaşam Kalitesi ve İlişkili Faktörlerin İncelenmesi",
        "Psikoloji & Psikososyal Boyut",
    ),
    (
        "10.21763-tjfmpc.415456-650677.pdf",
        "diyabet_ruhsal_sorunlar_yonetimi.pdf",
        "Diyabete Eşlik Eden Ruhsal Sorunlar ve Diyabet Yönetimi",
        "Psikoloji & Psikososyal Boyut",
    ),
    (
        "10.24938-kutfd.1075896-2262790.pdf",
        "diyabetik_gebe_hba1c_sonuclar.pdf",
        "Diyabetik Gebelerde Yüksek Glikalize Hemoglobin Düzeylerinin Obstetrik ve Neonatal Sonuçlara Etkisi",
        "Klinik Tıp & Tanı-Tedavi",
    ),
    (
        "10.25048-tudod.1299744-3153988.pdf",
        "tip2_diyabet_yasam_bicimi_oz_yeterlilik.pdf",
        "Tip 2 Diyabet Hastalarında Sağlıklı Yaşam Biçimi Davranışlarının Belirlenmesi ve Diyabet Öz Yeterliliği",
        "Hemşirelik, Öz Bakım & Hasta Eğitimi",
    ),
    (
        "10.25048-tudod.723725-1062127.pdf",
        "yasli_tip2_diyabet_yuku.pdf",
        "Yaşlı Tip 2 Diyabetli Bireylerde Diyabet Yükünün İncelenmesi",
        "Hemşirelik, Öz Bakım & Hasta Eğitimi",
    ),
    (
        "10.46218-tshd.1483601-3928290.pdf",
        "tip1_diyabet_cocuk_sosyal_destek.pdf",
        "Tip 1 Diyabetli Çocuk ve Ergenlerde Algılanan Sosyal Desteğin Travma Sonrası Büyüme İle İlişkisi",
        "Psikoloji & Psikososyal Boyut",
    ),
    (
        "10.46483-deuhfed.865886-1524753.pdf",
        "orem_oz_bakim_diyabet_teknolojileri.pdf",
        "Orem'in Öz Bakım Eksikliği Kuramına Göre Diyabet Teknolojileri",
        "Hemşirelik, Öz Bakım & Hasta Eğitimi",
    ),
    (
        "10.5835-jecm.omu.29.s1.003-190194.pdf",
        "diyabet_tedavisi_hasta_egitimi.pdf",
        "Diyabet Tedavisinde Hasta Eğitimi",
        "Hemşirelik, Öz Bakım & Hasta Eğitimi",
    ),
    (
        "10.61399-ikcusbfd.1699367-4870468.pdf",
        "menopoz_ve_diyabet.pdf",
        "Menopoz ve Diyabet: Kadın Sağlığında Çift Yönlü Bir İlişki",
        "Cinsel Sağlık & Ürojinekoloji",
    ),
    (
        "2005-12-2-066-071.pdf",
        "tip2_diyabet_tedavisi_2005.pdf",
        "Tip 2 Diyabet Tedavisi",
        "Klinik Tıp & Tanı-Tedavi",
    ),
    (
        "2013-20-2-065-072.pdf",
        "diyabet_mikro_makrovaskuler_biyobelirtecler.pdf",
        "Diyabetin Mikrovasküler ve Makrovasküler Komplikasyonlarında Biyobelirteçlerin Yeri",
        "Komplikasyonlar & Biyobelirteçler",
    ),
    (
        "22410.pdf",
        "turkiye_florasi_diyabet_tibbi_bitkiler.pdf",
        "Türkiye Florasında Diyabet Tedavisinde Kullanılan Tıbbi Bitkiler",
        "Farmakognozi & Bitkisel Tedavi",
    ),
    (
        "22863.pdf",
        "diyabet_antidiyabetik_bitkiler_turkiye.pdf",
        "Diyabet ve Türkiye'de Antidiyabetik Olarak Kullanılan Bitkiler",
        "Farmakognozi & Bitkisel Tedavi",
    ),
    (
        "3c.pdf",
        "diyabet_3c_pankreatojenik.pdf",
        "Tip 3c (Pankreatojenik) Diyabet",
        "Klinik Tıp & Tanı-Tedavi",
    ),
    (
        "50794.pdf",
        "nk17_il17_diyabet_sureci_immunoloji.pdf",
        "NK-17/NK-1 ile IL-17/IFN-gama Miktarı ve Oranlarının Diyabet Süreciyle İlişkisinin Araştırılması",
        "Genetik & Patofizyoloji",
    ),
    (
        "Adaptation Of Diabetes Self Management Questionnaire To Turkish Society_ Validity and Reliability Study[#468294]-638912.pdf",
        "diyabet_oz_yonetim_skalasi_gecerlik.pdf",
        "Diyabet Öz Yönetim Skalası'nın Türk Toplumuna Uyarlanması: Geçerlik ve Güvenirlik Çalışması",
        "Hemşirelik, Öz Bakım & Hasta Eğitimi",
    ),
    (
        "C2-S2-diyabetle-mucadelede-diyabet-riskleri.pdf",
        "diyabet_risk_belirleme_tanilama.pdf",
        "Diyabetle Mücadelede Diyabet Risklerinin Belirlenmesi ve Tanılama",
        "Halk Sağlığı & Epidemiyoloji",
    ),
    (
        "Current_Approaches_in_the_Administration.pdf",
        "diyabet_kronik_komplikasyon_guncel_yaklasimlar.pdf",
        "Diyabete Bağlı Kronik Komplikasyonların Yönetiminde Güncel Yaklaşımlar",
        "Komplikasyonlar & Biyobelirteçler",
    ),
    (
        "DIABETES MELLITUS'UN KOMPLİKASYONLARI[#465088]-595268.pdf",
        "diabetes_mellitus_komplikasyonlari.pdf",
        "Diabetes Mellitus'un Komplikasyonları",
        "Komplikasyonlar & Biyobelirteçler",
    ),
    (
        "diabetesmellitus2024.pdf",
        "temd_diyabet_kilavuzu_2024_tam.pdf",
        "TEMD Diabetes Mellitus ve Komplikasyonlarının Tanı, Tedavi ve İzlem Kılavuzu 2024",
        "Klinik Tıp & Tanı-Tedavi",
    ),
    (
        "Diabetes_mellitusun_tanı_tedavi_ve_izlemi.pdf",
        "diabetes_mellitus_tani_tedavi_izlem_kitap.pdf",
        "Diabetes Mellitusun Tanı, Tedavi ve İzlemi",
        "Klinik Tıp & Tanı-Tedavi",
    ),
    (
        "diyabet afet yönetim.pdf",
        "diyabet_afet_yonetimi.pdf",
        "Diyabette Afet Yönetimi",
        "Halk Sağlığı & Epidemiyoloji",
    ),
    (
        "Diyabetin Komplikasyonlarından Korunmak için Tanı, Tedavi ve İzlem[#561524]-709540.pdf",
        "diyabet_komplikasyon_korunma_tani_tedavi.pdf",
        "Diyabetin Komplikasyonlarından Korunmak için Tanı, Tedavi ve İzlem",
        "Klinik Tıp & Tanı-Tedavi",
    ),
    (
        "Diyabette_Sira_Disi_Olgular_Kitabi_Sirali_Hali_SON.pdf",
        "diyabette_sira_disi_olgular_kitabi.pdf",
        "Diyabette Sıra Dışı Olgular Kitabı",
        "Klinik Tıp & Tanı-Tedavi",
    ),
    (
        "Diyabet_Hastalarının_Psikoloji.pdf",
        "diyabet_hastalari_psikolojik_sikinti_travma.pdf",
        "Diyabet Hastalarının Psikolojik Sıkıntı ve Travma Sonrası Gelişimlerinin İncelenmesi",
        "Psikoloji & Psikososyal Boyut",
    ),
    (
        "genetik.pdf",
        "diyabet_genetik_faktorler_arastirma.pdf",
        "Diyabette Genetik Faktörler",
        "Genetik & Patofizyoloji",
    ),
    (
        "Gençli\u0307kte_Ortaya_ÇIkan_Eri\u0307şk.pdf",
        "genclikte_ortaya_cikan_eriskin_tip_diyabet_mody.pdf",
        "Gençlikte Ortaya Çıkan Erişkin Tip Diyabet (MODY) Tanısı ile İzlenen Çocuklarda Yeni Nesil Dizi Analizi",
        "Klinik Tıp & Tanı-Tedavi",
    ),
    (
        "Gestasyonel Diyabet ve Risk Faktörleri[#1423781]-3676339.pdf",
        "gestasyonel_diyabet_risk_faktorleri.pdf",
        "Gestasyonel Diyabet ve Risk Faktörleri",
        "Beslenme, Obezite & Metabolizma",
    ),
    (
        "JAREN-59354-REVIEW-ANATACA.pdf",
        "diyabetik_ketoasidoz_hemsirelik.pdf",
        "Erişkin Hastalarda Diyabetik Ketoasidoz Tedavisi ve Hemşirelik Yaklaşımları",
        "Hemşirelik, Öz Bakım & Hasta Eğitimi",
    ),
    (
        "KoçÇocukDiyabetEkibiKlinikÖnerilerKitabı2023.pdf",
        "koc_cocuk_diyabet_klinik_oneriler_2023.pdf",
        "Koç Üniversitesi Çocuk Diyabet Ekibi Klinik Uygulama Önerileri 2023",
        "Klinik Tıp & Tanı-Tedavi",
    ),
    (
        "MANAGEMENT OF DIABETES IN CORRECTIONAL INSTITUTIONS[#21477]-19775.pdf",
        "ceza_infaz_kurumlari_diyabet_yonetimi.pdf",
        "Ceza İnfaz Kurumlarında Diyabet Yönetimi",
        "Halk Sağlığı & Epidemiyoloji",
    ),
    (
        "Obesity, Type 2 Diabetes and Nutrition[#600128]-776568.pdf",
        "obezite_tip2_diyabet_beslenme.pdf",
        "Obezite, Tip 2 Diyabet ve Beslenme",
        "Beslenme, Obezite & Metabolizma",
    ),
    (
        "Obezite, Tip 2 Diyabet ve İnsülin Direnci Arasındaki Bağlantı_ İnflamasyon[#469981]-552867.pdf",
        "obezite_tip2_diyabet_insulin_direnci_inflamasyon.pdf",
        "Obezite, Tip 2 Diyabet ve İnsülin Direnci Arasındaki Bağlantı: İnflamasyon",
        "Beslenme, Obezite & Metabolizma",
    ),
    (
        "OTD_31_SUP_EK_SAYI_1_6.pdf",
        "diyabet_kuresel_salgin_hastalik.pdf",
        "Diyabet: Küresel Bir Salgın Hastalık",
        "Halk Sağlığı & Epidemiyoloji",
    ),
    (
        "OTD_31_SUP_EK_SAYI_39_44.pdf",
        "diyabet_hastalarina_beslenme_yaklasimi.pdf",
        "Diyabet Hastalarına Beslenme Açısından Yaklaşım",
        "Beslenme, Obezite & Metabolizma",
    ),
    (
        "OTD_31_SUP_EK_SAYI_45_51.pdf",
        "diyabet_norolojik_hastaliklar.pdf",
        "Diyabet ve Nörolojik Hastalıklar",
        "Komplikasyonlar & Biyobelirteçler",
    ),
    (
        "pcos.pdf",
        "pcos_insulin_direnci_diyabet.pdf",
        "Polikistik Over Sendromu ve Diyabet İlişkisi",
        "Beslenme, Obezite & Metabolizma",
    ),
    (
        "PHD_7_2_61_67.pdf",
        "diyabetli_bireylerde_psikososyal_uyum.pdf",
        "Diyabetli Bireylerde Hastalığa Psikososyal Uyum",
        "Psikoloji & Psikososyal Boyut",
    ),
    (
        "SETB_49_4_238_242.pdf",
        "prediyabet_onemi_tedavi_yaklasimi.pdf",
        "Prediyabetin Önemi ve Tedavi Yaklaşımı",
        "Klinik Tıp & Tanı-Tedavi",
    ),
    (
        "spor.pdf",
        "diyabet_ve_spor_egzersiz.pdf",
        "Diyabet ve Spor/Egzersiz",
        "Beslenme, Obezite & Metabolizma",
    ),
    (
        "T06062.pdf",
        "tip1_diyabet_cinsellik_algilari_bakim.pdf",
        "Tip 1 Diabetes Mellitusu Olan Hastaların Cinsellik Algılarının ve Cinsel Bakım Gereksinimlerinin Belirlenmesi",
        "Cinsel Sağlık & Ürojinekoloji",
    ),
    (
        "tatlandırıcı.pdf",
        "diyabet_tatlandiricilar.pdf",
        "Diyabette Tatlandırıcı Kullanımı",
        "Beslenme, Obezite & Metabolizma",
    ),
    (
        "Toplumda Prediyabet Riski ve Tanılama Yöntemleri_ Güncel Ölçüm Araçlarına İlişkin Derleme[#970807]-1878429.pdf",
        "prediyabet_riski_tanilama_yontemleri.pdf",
        "Toplumda Prediyabet Riski ve Tanılama Yöntemleri: Güncel Ölçüm Araçlarına İlişkin Derleme",
        "Klinik Tıp & Tanı-Tedavi",
    ),
    (
        "traditional-and-novel-biochemical-markers-in-diagnosis-and-monitoring-of-diabetes-9223.pdf",
        "diyabet_tani_takip_biyokimyasal_belirtecler.pdf",
        "Diyabet Tanı ve Takibinde Geleneksel ve Yeni Biyokimyasal Belirteçler",
        "Komplikasyonlar & Biyobelirteçler",
    ),
    (
        "VTD-60963-REVIEW-DEMIR.pdf",
        "diyabetik_seksuel_disfonksiyon.pdf",
        "Diyabetik Erkek ve Kadınlarda Seksüel Disfonksiyon",
        "Cinsel Sağlık & Ürojinekoloji",
    ),
    (
        "Yenido__an Hipoglisemisinde Hiperins__lizmin Yeri[#391112]-420388.pdf",
        "yenidogan_hipoglisemi_hyperinsulizm.pdf",
        "Yenidoğan Hipoglisemisinde Hiperinsülizmin Yeri",
        "Klinik Tıp & Tanı-Tedavi",
    ),
    (
        "ÇOCUKLARDA DİYABET YÖNETİMİ[#33838]-29273.pdf",
        "cocuklarda_diyabet_yonetimi.pdf",
        "Çocuklarda Diyabet Yönetimi",
        "Klinik Tıp & Tanı-Tedavi",
    ),
]

# Duplicate to skip
DUPLICATE = "10.61399-ikcusbfd.1699367-4870468 (1).pdf"


def main():
    print("=" * 60)
    print("RagMakaleler -> Knowledge Base Preparation")
    print("=" * 60)

    # 1. Load existing metadata
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    existing_files = {m["file"] for m in metadata}
    print(f"\nExisting metadata entries: {len(metadata)}")

    # 2. Add source_type and category to existing entries
    for entry in metadata:
        if "source_type" not in entry:
            entry["source_type"] = "educational"
        if "category" not in entry:
            entry["category"] = None

    # 3. Copy PDFs and create new metadata entries
    copied = 0
    skipped = 0
    no_text_files = []

    for original, sanitized, title, category in ARTICLE_MAP:
        src = os.path.join(RAG_DIR, original)
        dst = os.path.join(KB_DIR, sanitized)

        if not os.path.exists(src):
            print(f"  WARNING: Source not found: {original}")
            skipped += 1
            continue

        if sanitized in existing_files:
            print(f"  SKIP (already exists): {sanitized}")
            skipped += 1
            continue

        # Copy file
        shutil.copy2(src, dst)
        copied += 1

        # Add metadata entry
        metadata.append({
            "file": sanitized,
            "title": title,
            "language": "tr",
            "category": category,
            "source_type": "research",
        })

        print(f"  COPIED: {original} -> {sanitized} [{category}]")

    # 4. Save updated metadata
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Done! Copied: {copied}, Skipped: {skipped}")
    print(f"Total metadata entries: {len(metadata)}")

    # 5. Print category summary
    from collections import Counter
    new_entries = [m for m in metadata if m.get("source_type") == "research"]
    cat_counts = Counter(m["category"] for m in new_entries)
    print(f"\nCategory distribution (research articles):")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
