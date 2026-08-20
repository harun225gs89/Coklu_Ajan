# GitHub Pull Request (PR) — Detaylı Araştırma

## 1. PR Nedir?

GitHub Pull Request (Çekme İsteği), yazılım geliştirme sürecinde kod değişikliklerini incelemek, tartışmak ve birleştirmek için kullanılan temel bir iş akışı aracıdır.

### Temel Tanım
- **PR:** Bir dalda (branch) yapılan değişiklikleri başka bir dala (genellikle `main` veya `develop`) birleştirme isteğidir.
- **Amacı:** Kod kalitesini kontrol etmek, güvenliği sağlamak, ve takım üyeleri arasında bilgi paylaşımını kolaylaştırmak.

### PR Yaşam Döngüsü

```
1. Yazar Dalı Oluşturur (Feature Branch)
        ↓
2. Kod Yazılır ve Commit Yapılır
        ↓
3. PR Açılır (Pull Request Created)
        ↓
4. Code Review (Kod İnceleme)
        ↓
5. Reviewers Açıklama Yapar (Comments/Suggestions)
        ↓
6. Değişiklikler Yapılır (Changes Made)
        ↓
7. PR Onaylandı (Approved)
        ↓
8. Merge (Birleştirilir)
        ↓
9. Branch Silinir (Cleanup)
```

## 2. PR'ın Temel Bileşenleri

### 2.1 PR Metadata'sı
- **PR Number:** Kimlik numarası (ör: #12345)
- **Title:** Başlık
- **Description:** PR'ın amacı, bağlam ve özet
- **Author:** Kim tarafından açıldığı
- **Base Branch:** Hedef dal (nereye merge olacak)
- **Head Branch:** Kaynak dal (nereden değişiklikler gelecek)
- **Status:** Draft / Open / Closed
- **Created At / Updated At:** Tarihler

### 2.2 Changed Files
Her PR'da değişen dosyalar ve satırlar listelenir:
- Dosya yolu
- Status: `added` / `modified` / `deleted`
- Additions: Eklenen satır sayısı
- Deletions: Silinen satır sayısı
- Patch: Gerçek diff (kodu gösteren patch)

### 2.3 Reviews ve Comments
- **Review:** Reviewer'ın bütün PR'a verdiği genel yorum (Approve / Request Changes / Comment)
- **Comments:** Dosya bazlı veya satır bazlı spesifik yorumlar
- **Reactions:** 👍 / ❤️ / 🎉 gibi emoji reaksiyonlar

### 2.4 Checks ve Statuses
- **CI/CD Checks:** Otomatik test, lint, build komutlarının sonuçları
- **Status Checks:** Branch protection kurallarından gelen gereklemeler
- **Merge Conflicts:** Merge yaparken çakışma var mı?

## 3. GitHub PR API

GitHub, PR'lar hakkında veri almak ve yönetmek için kapsamlı bir REST API sunar.

### 3.1 En Kullanılan PR Endpoints'leri

#### Bir PR'ı Almak
```bash
GET /repos/{owner}/{repo}/pulls/{pull_number}
```
Yanıt örneği:
```json
{
  "id": 1,
  "number": 1347,
  "state": "open",
  "title": "feat: add login flow",
  "body": "Implements OAuth2 login",
  "user": {
    "login": "octocat",
    "avatar_url": "..."
  },
  "created_at": "2011-01-26T19:01:12Z",
  "updated_at": "2011-01-26T19:01:12Z",
  "merged_at": null,
  "changed_files": 3,
  "additions": 100,
  "deletions": 50,
  "head": {
    "ref": "feature-branch",
    "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e"
  },
  "base": {
    "ref": "main",
    "sha": "3d7ac37e0a9c7c12f23a12345"
  }
}
```

#### PR'daki Değişen Dosyaları Almak
```bash
GET /repos/{owner}/{repo}/pulls/{pull_number}/files?per_page=100
```
Yanıt örneği:
```json
[
  {
    "filename": "src/auth.js",
    "status": "added",
    "additions": 50,
    "deletions": 0,
    "patch": "@@ -0,0 +1,50 @@\n+function login() {\n+ ...\n+}"
  }
]
```

#### PR'a Yorum Yazmak
```bash
POST /repos/{owner}/{repo}/issues/{pull_number}/comments
```
Body:
```json
{
  "body": "## PR Otomatik İnceleme Raporu\n\n..markdown content.."
}
```

#### PR'ı Review'lemek (Approve/Request Changes)
```bash
POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews
```
Body:
```json
{
  "body": "Looks good!",
  "event": "APPROVE"
}
```

#### PR'a Commit Bazlı Yorum Yazmak
```bash
POST /repos/{owner}/{repo}/pulls/{pull_number}/comments
```
Body:
```json
{
  "body": "This line has a potential bug",
  "commit_id": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
  "path": "src/auth.js",
  "line": 42
}
```

### 3.2 Rate Limiting

GitHub REST API rate limit'leri:
- **Unauthenticated:** 60 istek/saat
- **Authenticated (token):** 5000 istek/saat
- **GitHub App:** İyi durumda 15000 istek/saat

Hata: `403 {"message":"API rate limit exceeded"}`

### 3.3 Pagination

Büyük sonuç setleri için sayfalandırma:
```bash
GET /repos/owner/repo/pulls?per_page=100&page=1
```

## 4. PR Code Review Best Practices

### 4.1 İyi Bir PR Açmak
- Clear başlık yazın
- Açıklamaya neyi neden yaptığınızı yazın
- Bir dosyada 300+ satırdan kaçının (küçük PR'lar daha iyi review ediliyor)
- Ekran görüntüsü/screenshot ekleyin (UI değişikliği varsa)
- Test aldığını kanıtlayın (CI/CD checks geçsin)

### 4.2 İyi Bir Review Yapmak
- Anlaş (be nice) — insanlara saygı duyun
- "Why" soruları sorun — yazarın niyetini anlayın
- Alternatif öner — sadece hata göstermekle kalmayın
- Denemek iste (typo/logic hatası varsa, test et)
- Otomatik tool'lara güven — linter/type-check'i çalıştırın

### 4.3 Yakın Gelecek: PR Otomasyonu
- Otomatik code quality checker
- Security scan (SAST/DAST)
- Dependency check
- Test coverage taraması
- AI-powered code review (our project!)

## 5. GitHub PR Analiz Senaryoları

### Senaryo 1: Güvenlik Açısından PR Değerlendirmesi
```markdown
Kontrol Listesi:
- [ ] SQL injection riski var mı?
- [ ] XSS vulnerability var mı?
- [ ] Authentication/Authorization check eksik mi?
- [ ] Hardcoded secret/API key var mı?
- [ ] External API çağrısı güvenli mi?
- [ ] CORS configuration doğru mu?
- [ ] Rate limiting var mı?
```

### Senaryo 2: Test Coverage Açısından
```markdown
Kontrol Listesi:
- [ ] Unit test yazıldı mı?
- [ ] Edge case test yok mu?
- [ ] Error path test yok mu?
- [ ] Coverage ne kadar arttı?
- [ ] Integration test gerekli mi?
```

### Senaryo 3: Performance Açısından
```markdown
Kontrol Listesi:
- [ ] N+1 query problem var mı?
- [ ] Loop içinde DB query var mı?
- [ ] Memory leak riski var mı?
- [ ] Async/await doğru kullanıldı mı?
```

## 6. Pratik Kullanım

### GitHub CLI ile PR Almak
```bash
gh pr list --repo microsoft/vscode
gh pr view 12345 --repo microsoft/vscode
gh pr diff 12345 --repo microsoft/vscode
```

### GitHub REST API ile PR Bilgisi Almak (curl)
```bash
curl -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.github.com/repos/microsoft/vscode/pulls/12345
```

### Kodda PR Bilgilerini Kullanmak (Python requests)
```python
import requests

token = "your_github_token"
repo = "microsoft/vscode"
pr_num = 12345

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {token}"
}

# PR'ı al
pr = requests.get(
    f"https://api.github.com/repos/{repo}/pulls/{pr_num}",
    headers=headers
).json()

print(f"Title: {pr['title']}")
print(f"Changed files: {pr['changed_files']}")

# Değişen dosyaları al
files = requests.get(
    f"https://api.github.com/repos/{repo}/pulls/{pr_num}/files",
    headers=headers,
    params={"per_page": 100}
).json()

for file in files:
    print(f"{file['filename']}: +{file['additions']} -{file['deletions']}")
```

## 7. PR'da Sık Karşılaşılan Sorunlar

| Sorun | Neden | Çözüm |
|-------|-------|-------|
| Merge conflict | Başka branch ile aynı satırlar değiştirilmiş | Conflict'i çözüp merge'ü tamamla |
| Stale PR | Long-running branch | Düzenli olarak `main` ile rebase et |
| Review eksikliği | CODEOWNERS tanımlı değil | CODEOWNERS dosyası ekle |
| CI/CD fail | Test, lint veya build hatası | Hataları düzelt ve push et |
| Large PR | Çok büyük dosya listesi | PR'ı parça parça aç |

## 8. Sonuç

GitHub PR'lar yazılım projelerin geliştirilmesinde temel bir mekanizmadır. Bunu otomatikleştirmek, güvenlik anlamında taramak ve kalitesini artırmak için:

- PR metadata'sını düzenli taramak
- Diff'leri semantic olarak analiz etmek
- Security patterns'ı kontrol etmek
- Test coverage'ı ölçmek
- Otomatik feedback sağlamak

...gibi yapılar oluşturulabilir. Bu proje tam da bunu yapmak için tasarlandı!
