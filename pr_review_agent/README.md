# Çoklu Ajan Tabanlı PR Kod İnceleme Uygulaması

Bu proje, GitHub Pull Request URL'si alan ve bunu üç uzman ajanla analiz eden bir MVP uygulamasıdır:

- Mantık / Kod Kalitesi Ajanı
- Güvenlik Ajanı
- Test Üreten Ajanı

Ana orkestratör, LangGraph tabanlı akış üzerinden çıktıları birleştirir ve markdown review yorumunu oluşturur. İsterseniz yorumları GitHub PR API'sine de gönderebilirsiniz.

## Özellikler

- PR URL ile GitHub REST API üzerinden metadata ve diff çekme
- Değişen dosya listesi ve patch analizi
- Ajan bazlı değerlendirme
- Toplu markdown raporu
- GitHub issue comment yayınlama (isteğe bağlı)

## Kurulum

```bash
cd pr_review_agent
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Çalıştırma

```bash
python -m app.main --url https://github.com/microsoft/vscode/pull/12345
```

Yorumları doğrudan GitHub PR'a yayınlamak için:

```bash
python -m app.main --url https://github.com/microsoft/vscode/pull/12345 --post-comment --token YOUR_GITHUB_TOKEN
```

Alternatif olarak bir .env dosyası hazırlayabilirsiniz:

```env
GITHUB_TOKEN=...
GITHUB_API_BASE=https://api.github.com
```

## Örnek çıktı

```md
## PR Otomatik İnceleme Raporu

### Özet
- Toplam 4 bulgu bulundu.
- 2 güvenlik bulgusu tespit edildi.
- 1 mantık önerisi üretildi.
- 1 test önerisi eklenmeli.
```

## Not

Bu örnek, üretim seviyesinde tam bir güvenlik analizi değil, güçlü bir MVP ve örnek mimari sunar. Gerçek ortamda LLM tabanlı uzman ajanlar ile geliştirme için prompt ve output schema tasarımı daha da güçlendirilebilir.
