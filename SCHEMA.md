# LLM Wiki Şeması: Kişisel Bilgi Tabanı

Bu belge wiki'nin nasıl yapılandırıldığını, bakıldığını ve geliştirildiğini tanımlar. LLM'yi disiplinli bir wiki yöneticisine dönüştüren konfigürasyon belgesidir.

## Genel Bakış

Hedefleri, sağlığı, psikolojiyi ve kişisel gelişimi izlemek için bir kişisel bilgi tabanı. LLM, zamanla birikerek gelen, birbiriyle bağlantılı markdown dosyalarından oluşan kalıcı bir koleksiyonu yönetir.

**Üç katman:**
- **raw/**: Değişmez kaynak belgeler (makaleler, PDF'ler, günlük notları, kopyalar)
- **wiki/**: LLM tarafından oluşturulan markdown dosyaları (özetler, kişi sayfaları, kavram sayfaları, analizler)
- **SCHEMA.md**: Bu dosya — kurallar, iş akışları ve operasyonel yönergeler

---

## Wiki Yapısı

```
Proje_2/
├── raw/                          # Kaynak belgeler (salt okunur)
│   ├── articles/                 # Makaleler ve yazılar
│   ├── journal/                  # Günlük notları
│   ├── research/                 # Araştırma kaynakları
│   └── assets/                   # Resimler, PDF'ler, medya
├── wiki/                         # Bilgi tabanı (LLM tarafından yönetilen)
│   ├── _index.md                 # İçerik kataloğu
│   ├── _log.md                   # Ek-olarak-sadece aktivite günlüğü
│   ├── people/                   # Kişi sayfaları: arkadaşlar, mentorlar, rol modeller
│   ├── goals/                    # Hedef sayfaları: takip, ilerleme, revizyon
│   ├── concepts/                 # Fikirler: psikoloji, felsefe, çerçeveler
│   ├── health/                   # Fiziksel ve zihinsel sağlık takibi
│   ├── patterns/                 # Kişisel alışkanlıklar, davranışlar, tekrarlayan temalar
│   └── syntheses/                # Analizler, karşılaştırmalar ve keşifler
├── SCHEMA.md                     # Bu dosya
└── [diğer çalışma alanı dosyaları]
```

---

## Sayfa Kuralları

### Ön Bilgiler (Frontmatter)
Her wiki sayfası YAML ön bilgiler ile başlar:

```markdown
---
id: [kısa-ad]                     # Benzersiz tanımlayıcı (tire-ile-ayrılmış)
title: [başlık]
date_created: [YYYY-MM-DD]        # Sayfanın oluşturulma tarihi
date_updated: [YYYY-MM-DD]        # Son düzenleme tarihi
sources: [2, 5, 7]                # Raw/ kaynaklara referanslar (isteğe bağlı)
tags: [tag1, tag2, tag3]          # Obsidian ve dataview sorguları için
status: active|dormant|archived   # active = aktif çalışma; dormant = eski; archived = yerine geçildi
---
```

### Sayfa Türleri

1. **Kişi Sayfaları** (ör., hedefler, insanlar, sağlık durumları)
   - En üstte tek satırlık özet
   - Mevcut durum / son ne aşamada
   - Tarihçe / nasıl gelişti
   - İlgili sayfalar (wikilink'ler)
   - Kaynak referansları

2. **Kavram Sayfaları** (ör., çerçeveler, fikirler, psikoloji modelleri)
   - Tanım / bu nedir?
   - Temel içgörüler
   - Hayatınıza uygulamalar
   - İlgili kavramlar
   - Kaynaklar

3. **Sentez Sayfaları** (ör., analizler, karşılaştırmalar)
   - Soru veya tema
   - Cevap / analiz
   - Wiki sayfalarından kanıtlar
   - Açık sorular / boşluklar

4. **Günlük Özet Sayfaları** (ay/çeyrek başına bir sayfa)
   - Ortaya çıkan temalar
   - Hedef ilerleme durumu
   - Sağlık metrikleri
   - Önemli kararlar veya içgörüler
   - İlgili kavram ve hedef sayfalarına bağlantılar

### Wikilink Kuralı
İç bağlantılar için `[[sayfa-adı]]` kullan. LLM bu bağlantıları dikkatlice yönetir — bir sayfa güncellendiğinde, ilgili tüm çapraz referanslar kontrol edilir ve güncellenir.

---

## İş Akışları

### 1. Yeni Kaynak İşleme (İngest)

**Tetikleyici:** Kullanıcı bir dosyayı `raw/` dosyasına ekler ve "İşle [kaynak]" der

**Akış:**
1. Kaynağı oku ve özetle
2. Temel bulguları çıkar → kullanıcı ile tartış
3. Bir veya daha fazla wiki sayfası oluştur:
   - Bir kişi hakkındaysa: kişi sayfasını güncelle veya oluştur
   - Bir kavram hakkındaysa: kavram sayfasını güncelle veya oluştur
   - Sağlık/hedefler hakkındaysa: ilgili hedef veya sağlık sayfasını güncelle
   - Kaynak metaveri ile özet sayfası oluştur
4. `_index.md` yeni/değiştirilen sayfalar ile güncelle
5. Etkilenen sayfalar arasında wikilink'leri güncelle
6. `_log.md` ye giriş ekle: `## [YYYY-MM-DD] ingest | [Kaynak Başlığı]`

**Kullanıcı katılımı:** Yüksek. Özetleri gözden geçir, vurguyu yönlendir, güncellemeleri kontrol et.

### 2. Wiki'yi Sorgula

**Tetikleyici:** Kullanıcı bir soru sorar veya analiz ister

**Akış:**
1. İlgili sayfaları bulmak için `_index.md` ara
2. İlgili sayfaları oku ve cevabı sentezle
3. Cevap önemliyse/yeniden kullanılabilirse, onu yeni bir sentez sayfası olarak dosyala
4. Cevabı wiki sayfalarına referanslarla ver (ör., "bkz. [[kavram-adı]]")
5. `_log.md` ye ekle: `## [YYYY-MM-DD] query | [Soru kısa-adı]`

**Not:** İyi cevaplar sohbet geçmişinde kaybolmaz — wiki sayfası olarak dosyalanır, böylece bilginiz birikir.

### 3. Wiki'yi Kontrol Et (Lint)

**Tetikleyici:** Kullanıcı "kontrol et" der veya planlı dönemlerde (ör., aylık)

**Akış:**
1. Tüm sayfaları taray:
   - Yalnız sayfalar (gelen bağlantı yok)
   - Çelişkiler (yeni kaynaklar eski iddiaları çürütüyor)
   - Eski durum bayrakları (dormant olarak işaretli ama referans edilen sayfalar)
   - Eksik çapraz referanslar
   - Veri boşlukları (konseptler bahsedildiği ama açıklanmadığı yerler)
2. Öner:
   - Birleştirilecek veya emekli edilecek sayfalar
   - Oluşturulacak yeni sayfalar
   - İncelecek sorular
   - Aranacak kaynaklar
3. Spesifik düzenlemeleri öner
4. `_log.md` ye ekle: `## [YYYY-MM-DD] lint | [bulgular özeti]`

---

## İndeksleme ve Günlüğe Kaydetme

### `_index.md` — İçerik Kataloğu
- Kategoriye göre düzenlenmiş (insanlar, hedefler, kavramlar, sağlık, alışkanlıklar, sentezler, günlük)
- Her giriş: `- [[sayfa-adı]]` — [bir satırlık özet]`
- Her ingest'te güncellenir
- Navigasyon ve arama için kullanılır

### `_log.md` — Aktivite Zaman Çizelgesi
- Sadece ek (append-only)
- Format: `## [YYYY-MM-DD] [işlem] | [detaylar]`
- Örnekler:
  - `## [2026-08-20] ingest | Makale: "Uykunun Bilimi"`
  - `## [2026-08-20] query | Uyku hedeflerimi nasıl etkiliyor?`
  - `## [2026-08-20] lint | 3 yalnız sayfa, 1 çelişki bulundu`
- Aranabilir: `grep "^## \[" _log.md | tail -10` son 10 olayı gösterir

---

## Bakım Kuralları

1. **Bir kaynak, birçok güncelleme.** Bir kaynak işlediğinizde, 5-15 wiki sayfasına dokunabilir. LLM tüm bu güncellemeleri tek geçişte yapmalıdır.

2. **Wikilink'ler kutsal.** Her wikilink doğru olmalıdır. Bir sayfa yeniden adlandırıldığında, tüm gelen bağlantılar güncellenir. Bir kavram bahsedildiğinde, ona bağlantı verilir (veya eksik sayfası varsa işaretlenir).

3. **Durum gerçektir.** Sayfaları `active` olarak işaretle sadece aktif olarak çalışıyorsan. `dormant` eski ama potansiyel olarak ilgili için. `archived` güncelliğini yitirmiş için.

4. **Kaynaklar atıflandırılır.** Wiki sayfasındaki bir iddia bir kaynaktan geliyorsa, ön bilgilerde veya satır içinde not et. LLM varsayılan olarak kaynakları atıflandırmalıdır.

5. **Ön bilgiler güncel tutulur.** `date_updated` sayfa her değiştiğinde revize edilir. Etiketler ilgili kalır. Kaynaklar listesi doğrudur.

---

## Çıktı Formatları

Varsayılan olarak, tüm çıktılar wiki'de saklanan markdown dosyalarıdır. Genişletilmiş çıktılar mümkündür:

- **Tablolar**: Markdown tabloları (ör., hedef ilerleme, sağlık metrikleri)
- **Zaman çizelgeleri**: Kronolojik yapı ile markdown
- **Karşılaştırma matrisleri**: Markdown tabloları
- **Diyagramlar**: Mermaid sözdizimi (Obsidian'de render edilir)
- **Slaytlar**: Marp formatı (Obsidian eklentisi kullanılabilir)
- **Canvas**: Görsel taslaklar (Obsidian yerleşik)

Çıktı formatı soruya göre belirlenir. Basit kavram sorgusu → markdown sayfa. Üç hedefi karşılaştırma → tablo. Sağlık zaman çizelgesi → grafik veya canvas. LLM cevaba en uygun formatı seçer ve wiki'de dosyalar.

---

## Başlarken

1. **Kullanıcı kaynakları seçer.** `raw/` ye dosya ekle. Küçük başla.
2. **İlk işleme.** Kullanıcı kaynak ekler ve "İşle [kaynak]" der. LLM okur, temel bulguları çıkarır, wiki yapısını önerir, ilk sayfaları oluşturur.
3. **Keşfet ve sor.** Kullanıcı sorular sorar. LLM wiki'de ara, cevaplar ve yeniden kullanılabilir içgörüleri yeni sayfalar olarak dosyalar.
4. **Tekrar et.** Daha fazla kaynak ekle. Daha fazla soru sor. Wiki'nin büyüdüğünü ve birbiriyle bağlandığını izle.

---

## Bu Oturum İçin İpuçları

- **Ben (LLM) wiki'nin tamamından sorumlu.** Kaynakları sen seçer, sorular sorarsın. Yazma, düzenleme ve bakım işi tamamen bana aittir.
- **Obsidian senin IDE'n.** Ben düzenlemeler yaparım; sen gözden geçir, bağlantıları takip et, grafik görünümü kontrol et, geri bildirim ver.
- **Dar başla.** Bir alan oluştur (ör., tek bir hedef veya sağlık odağı) sonra her şeyi bağlamayı dene. Wiki doğal olarak genişleyecektir.
- **Sürece güven.** LLM wiki modeli işler çünkü LLM bakımdan bıkmaz. Wiki yararlı kalır çünkü güncel kalır.

---

## Şema Gelişimi

Bu şema yaşayan bir belgedir. Beraber çalışırken, neyin işe yaradığını keşfeder ve onu geliştiririz. Şunları tekrar gözden geçirmeyi bekle:
- Dizin yapısı (kategorileri yeniden organize edebiliriz)
- Sayfa şablonları (alan ekleyebilir veya kaldırabiliriz)
- İş akışları (toplu işleme yerine bir kez işleme, veya yeni işlemler ekleyebiliriz)
- Araçlar (arama ekleyebiliriz, harici sistemlerle bütünleştirmek yapabiliriz)

SCHEMA.md'ye yapılan güncellemeler kendileri `_log.md` ye kaydedilir.
