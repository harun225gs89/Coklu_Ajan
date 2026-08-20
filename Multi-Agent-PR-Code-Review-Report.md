# Çoklu Ajan Tabanlı Otomatik Kod İnceleme ve Güvenlik Analisti

## 1) Proje hedefi

Bu sistem, bir GitHub Pull Request (PR) bağlantısını alır; PR içindeki dosya değişikliklerini, diff'leri ve metadataları analiz eder; ardından ayrı uzman ajanlar tarafından:

- mantık hataları ve kod kalitesi sorunları,
- OWASP Top 10 güvenlik açıkları,
- eksik veya zayıf test senaryoları

incelenir. Sonrasında bir ana orkestratör tüm çıktıları birleştirir ve GitHub PR API'sine markdown yorum olarak yayınlar.

Bu yaklaşımın avantajı tek bir LLM çağrısı yerine, her ajan kendi uzmanlık alanına odaklanır. Böylece:

- daha tutarlı sonuçlar elde edilir,
- farklı hata türleri ayrıştırılır,
- güvenlik ve kalite değerlendirmeleri daha net hale gelir,
- PR üzerinde yorumlar daha yapılandırılmış ve uygulanabilir olur.

---

## 2) Bu uygulamayı kurmak için öğrenmeniz gereken ana başlıklar

### 2.1 LLM tabanlı ajan mimarisi

Öğrenmeniz gerekenler:

- Ajan nedir? ReAct, Plan-and-Execute, Tool Use, Memory, Role Prompting
- Çoklu ajan sistemi nedir?
- Orkestrasyon mantığı: hangi ajanın ne zaman çağrılacağı
- Ajanlar arası iletişim ve veri akışı
- Hata yönetimi ve fallback/rollback tasarımı

Özellikle şunları öğrenin:

- LangGraph: state graph, nodes, edges, conditional routing, state management
- AutoGen: agent runtime, group chat, tools, function calling, nested chats
- OpenAI / Azure OpenAI / Anthropic / Groq gibi model sağlayıcıları

Üst seviye fark:

- LangGraph daha akış odaklı, deterministik bir orchestrator tasarımına uygun
- AutoGen daha doğal konuşma/çoklu ajan koordinasyonuna uygun

Bu proje için en uygun seçenek genelde LangGraph olur; çünkü PR analizi bir veri akışı ve iş hattı gibi çalışır.

### 2.2 GitHub PR API ve otomasyon

Öğrenmeniz gerekenler:

- GitHub REST API
- PR endpoint'leri:
  - GET /repos/{owner}/{repo}/pulls/{pull_number}
  - GET /repos/{owner}/{repo}/pulls/{pull_number}/files
  - GET /repos/{owner}/{repo}/pulls/{pull_number}/comments
  - POST /repos/{owner}/{repo}/issues/{pull_number}/comments
  - POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews
- GitHub App veya PAT kullanımı
- PR diff parse etme yaklaşımı
- Rate limit ve erişim kontrolü

Dikkat edilmesi gerekenler:

- PR başlığı, açıklaması, değişen dosyalar, patch bilgileri ve yorumlar ayrıştırılmalı
- Diff tek tek parse edilip ajanlara verilmeli
- Büyük PR'lar için chunking gerekir

### 2.3 Kod analizi ve diff işleme

Öğrenmeniz gerekenler:

- patch/diff formatı
- dosya bazlı değişiklik analizi
- eklenen satırlar ve silinen satırlar ayrımı
- “before/after” kod bağlamını koruma
- büyük diff'i küçük parçalara bölme

Yapısal olarak şunlara bakmalısınız:

- AST (Abstract Syntax Tree) analiz araçları
- Python için ast, tree-sitter, libcst
- JavaScript/TypeScript için ts-morph, TypeScript compiler API, eslint custom rules
- Java / C# için javac AST veya Roslyn benzeri araçlar

Not: Bu sistem tek bir dil için değil, çoğu projede multi-language için genel yorum üretmeye çalışır. Bu yüzden diff anlatımı ve güvenlik incelemesi için semantic context çok önemlidir.

### 2.4 Güvenlik analizi (OWASP Top 10)

Öğrenmeniz gerekenler:

- OWASP Top 10 temel kavramları:
  - Broken Access Control
  - Cryptographic Failures
  - Injection
  - Insecure Design
  - Security Misconfiguration
  - Vulnerable and Outdated Components
  - Identification and Authentication Failures
  - Software and Data Integrity Failures
  - Security Logging and Monitoring Failures
  - Server-Side Request Forgery
- Kod incelemesinde güvenlik sinyalleri
- Input validation, authz/authn, unsafe deserialization, SSRF, XSS, SQLi, CSRF
- Secret exposure ve hardcoded credentials
- Dependency güvenlik taraması

Önemli: Güvenlik ajanı sadece “güvenli değil” diye yorum yazmamalı. Aşağıdaki şablonla yorum üretmeli:

- Zafiyet adı
- Risk seviyesi (Low / Medium / High / Critical)
- Olası etki
- Neden oluştuğu
- Fix önerisi
- Kod satırı veya diff bölümü referansı

### 2.5 Test üretimi (unit test generation)

Öğrenmeniz gerekenler:

- Unit test nedir?
- Arrange / Act / Assert kalıbı
- Test coverage ve edge cases
- Mutation testing ve sınır değer testleri
- TDD ve PR öncesi test önerileri

Bu ajanın öğrenmesi gerekenler:

- yeni fonksiyon veya method ne işe yarıyor?
- hangi girişler hata verir?
- null/empty/invalid data senaryoları
- timeout, exception, boundary, concurrency, auth/permission cases

Örnek çıktılar:

- “Bu metod için Missing/Invalid input için test eklenmeli”
- “Edge case: empty array, null value, malformed token için test üretilebilir”
- “Mevcut testler branch coverage eksik”

### 2.6 Orkestrasyon ve iş akışı tasarımı

Öğrenmeniz gerekenler:

- pipeline / workflow tasarımı
- per-PR run lifecycle
- state graph yönetimi
- ajanların çıktıları için ortak JSON şablonu
- sonuç birleştirme ve deduplication

Örnek ortak veri yapısı:

```json
{
  "pr_id": 123,
  "repo": "owner/repo",
  "files": [
    {
      "path": "src/auth/service.py",
      "status": "modified",
      "patch": "..."
    }
  ],
  "findings": {
    "logic": [],
    "security": [],
    "tests": []
  }
}
```

Ajanlar şunları üretmeli:

- title
- severity
- description
- evidence
- suggestion
- file_path
- line_hint

### 2.7 GitHub PR yorumlama ve markdown formatı

Öğrenmeniz gerekenler:

- GitHub Markdown desteği
- issue comment ve review yorumları arasındaki fark
- review body üretimi
- summary + findings + next steps yapısı

Örnek yorum şablonu:

```md
## PR Otomatik İnceleme Raporu

### Özet
- Toplam 4 bulgu bulundu.
- 2 güvenlik sorunu tespit edildi.
- 1 mantık hatası önerildi.
- 1 test senaryosu üretildi.

### Güvenlik
- [High] SQL injection riski: `query = "SELECT * FROM users WHERE id = " + userId`
  - Neden: kullanıcı girdisi doğrudan SQL sorgusuna ekleniyor.
  - Öneri: prepared statement kullanın.

### Kod Kalitesi
- [Medium] `handleRequest` fonksiyonu çok fazla sorumluluk üstleniyor.
  - Neden: auth, validation ve DB çağrısı aynı method içinde.
  - Öneri: ayrı helper method / service katmanı oluşturun.

### Test Önerileri
- Empty input için test eklenmeli.
- `invalid_token` akışında exception handling kontrol edilmeli.

### Sonuç
- Bu PR için yeniden gözden geçirme önerilir.
```

### 2.8 Uygulama dili ve teknoloji stack'i

Önerilen kombinasyon:

- Python için backend veya agent runtime
- LangGraph veya AutoGen
- FastAPI veya Flask
- PostgreSQL veya SQLite (opsiyonel, log/artefact depolama için)
- GitHub App / PAT için auth
- Pydantic modelleme
- OpenAI veya Azure OpenAI SDK
- GitPython veya requests
- pytest
- redis veya memory store (opsiyonel)

Alternatifler:

- Node.js + TypeScript + LangChain + Express
- .NET + Semantic Kernel + GitHub Actions + Azure Functions

### 2.9 Güvenlik ve etik dikkatler

Bu yapının kendisi de güvenlik riski taşıyabilir. Aşağıdakileri mutlaka öğrenin:

- GitHub token güvenliği
- Secret management
- CI/CD pipeline güvenliği
- LLM output validation
- Prompt injection riskleri
- PR içindeki dışarıdan gelebilecek komutların işlenmesi

Kural:

- token'lar `.env` veya secret manager içinde tutulmalı
- loglarda raw diff / sensitive data yazılmamalı
- GitHub yorum üretiminde kullanıcıya ait special token bilgisi asla sürdürülememeli

---

## 3) Mimari önerisi: Multi-Agent yapı

### 3.1 Ajan 1: Kod Kalitesi ve Mantık Hatası Ajanı

Sorumluluk alanı:

- fonksiyonel hata tespiti
- dead code / unreachable logic
- null handling
- exception handling
- naming consistency
- complexity / maintainability review
- refactor önerileri

Örnek sorular:

- Bu kod gerçekten doğru iş yapıyor mu?
- Edge case var mı?
- Hata yakalama doğru mu?
- Şu değişiklik fonksiyonel olarak davranışı bozar mı?
- Bu method fazla sorumluluk taşıyor mu?

### 3.2 Ajan 2: Güvenlik Ajanı

Sorumluluk alanı:

- OWASP Top 10 taraması
- authn/authz kontrolleri
- validation ve sanitization
- secret leakage
- command injection / SSRF / SQLi / XSS
- dependency zafiyetleri

Örnek sorular:

- Kullanıcı girdisi güvenli şekilde işleniyor mu?
- Yetkilendirme kontrolü eksik mi?
- Session veya token güvenliği uygun mu?
- Çıktı kullanıcıya yönlendirilirken escaping var mı?

### 3.3 Ajan 3: Test Üreten Ajan

Sorumluluk alanı:

- değiştirilen kodu test etme senaryoları üretmek
- fail-case, edge-case ve success-case için öneri üretmek
- mevcut testleri gözden geçirip eksik noktaları belirtmek
- unit test örneği üretmek

Örnek sorular:

- Bu fonksiyon için hangi girişler test edilmeli?
- Hangi hata türü beklenmeli?
- Çatallı koşullar için testlerin coverage'ı yeterli mi?

### 3.4 Ana Orkestratör

Sorumluluk alanı:

- PR diff ve metadata'yi toplayıp ajanlara dağıtmak
- her ajanın çıktısını normalleştirmek
- bulguları önceliklendirmek
- markdown rapor üretmek
- GitHub API üzerinden comment / review oluşturmak

Örnek akış:

1. PR URL al
2. GitHub API ile metadata çek
3. değişen dosyaları listelenir
4. diff'ler parse edilir
5. her dosya/patch ajanlara iletilir
6. ajanlar sonuç üretir
7. orchestrator normalize eder
8. severity sıralaması yapar
9. markdown comment üretir
10. GitHub API'ye gönderir

---

## 4) Önerilen iş akışı

### 4.1 Adım adım süreç

1. PR URL girişi alınır.
2. GitHub API ile PR bilgisi çekilir.
3. `pulls/{id}/files` ve `pulls/{id}` çağrıları yapılır.
4. diff ve dosya listesi çıkarılır.
5. Dosyalar toplanır ve agent input paketleri hazırlanır.
6. Ajan 1 çalıştırılır: kod kalitesi ve mantık analizi.
7. Ajan 2 çalıştırılır: güvenlik analizi.
8. Ajan 3 çalıştırılır: test önerileri ve test üretimi.
9. Orkestratör sonuçları birleştirir.
10. Markdown yorum oluşturur.
11. GitHub PR yorum API'sine post eder.

### 4.2 Sık kullanılan veri modelleri

#### PR context model

```python
class PRContext(BaseModel):
    repo: str
    owner: str
    pull_number: int
    title: str
    description: str
    changed_files: list[str]
    diff_text: str
```

#### Finding model

```python
class Finding(BaseModel):
    agent: str
    severity: str  # info, low, medium, high, critical
    category: str
    title: str
    description: str
    evidence: str
    file_path: str | None = None
    line_hint: str | None = None
    recommendation: str
```

#### Review model

```python
class ReviewResult(BaseModel):
    summary: str
    findings: list[Finding]
    recommendation: str
    generated_at: str
```

---

## 5) Teknik öğrenme yolu

### 5.1 İlk 2 hafta hedefi

Hafta 1:

- Python temelleri ve async kavramı
- REST API kullanımı
- HTTP, requests, FastAPI
- GitHub API incelemesi
- LangGraph veya AutoGen temelleri

Hafta 2:

- state management
- tool calling
- agent output normalization
- markdown yorum üretimi
- temel PR diff parsing

### 5.2 Sonraki 2 hafta hedefi

- güvenlik zafiyet sınıflandırması
- OWASP Top 10 örnekleri
- unit test generation süreci
- orchestrator loglama ve monitoring
- CI/CD ile entegre çalıştırma

### 5.3 İleri seviye hedefler

- multi-repo review
- semantic chunking
- code graph / dependency graph analizi
- branch-based review
- GitHub check run integration
- AI review score (confidence / trust score)

---

## 6) Uygulama için önerilen dosya yapısı

```text
project/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── github_client.py
│   ├── models.py
│   └── orchestrator.py
├── agents/
│   ├── logic_agent.py
│   ├── security_agent.py
│   ├── test_agent.py
│   └── prompts.py
├── utils/
│   ├── diff_parser.py
│   ├── markdown_formatter.py
│   └── logger.py
├── tests/
│   ├── test_github_client.py
│   ├── test_orchestrator.py
│   └── test_prompt_templates.py
├── .env.example
├── requirements.txt
├── README.md
└── docker-compose.yml
```

---

## 7) Örnek prompt tasarımı

### 7.1 Mantık / Kod Kalitesi ajanı için örnek prompt

```text
Sen bir yazılım mühendisliği kod inceleme uzmanısın.
Bu PR'ın diff'ini inceleyeceksin.
Görevlerin:
1. Mantık hatası var mı kontrol et.
2. Edge case / null / exception / overengineering sorunlarını bul.
3. Kod okunabilirliği ve maintainability açısından değerlendirme yap.
4. Sonuçları JSON formatında döndür.

İçerik formatı:
- title
- severity
- description
- evidence
- recommendation
```

### 7.2 Güvenlik ajanı için örnek prompt

```text
Sen bir güvenlik uzmanısın.
Bu PR diff'inde OWASP Top 10 açısından zafiyet arayacaksın.
Aşağıdaki alanlara odaklan:
- injection
- authz/authn
- SSRF
- XSS
- insecure deserialization
- secrets leakage
- unsafe dependencies

Sonucu JSON ile döndür.
```

### 7.3 Test ajanı için örnek prompt

```text
Sen bir test mühendisliği uzmanısın.
Bu diff için eksik unit test senaryolarını üret.
Dikkat et:
- success case
- failure case
- edge case
- exception case
- boundary condition

Çıktı formatı:
- test_name
- scenario
- expected_behavior
- reason
```

---

## 8) En yaygın zorluklar

- Çok büyük PR'ların token limitini aşması
- Ajanlar arasında sonuç formatı tutarsızlığı
- Güvenlik ajanının false positive üretmesi
- Test ajanın gereksiz test önerileri sunması
- GitHub API rate limitine takılma
- Çoklu ajanın aynı bulguyu birden çok kez raporlaması
- LLM çıktısının deterministik olmaması

Çözüm önerileri:

- diff chunking
- output schema güvence altına alma
- deduplication
- confidence score
- human review fallback

---

## 9) Güzel bir minimum viable product (MVP) tasarımı

MVP için şunları yapın:

1. tek PR URL almak
2. GitHub REST API ile PR bilgilerini çekmek
3. değişen dosyaları ve patch'leri almak
4. bir logic agent çalıştırmak
5. bir security agent çalıştırmak
6. bir test agent çalıştırmak
7. her ajanın çıktısını JSON olarak toplamaktır
8. ana orchestrator ile markdown rapor üretmek
9. GitHub issue comment olarak göndermek

Bu MVP hali ile temel sistemin işleyişi doğrulanabilir. Sonrasında şunlar eklenebilir:

- retry mekanizması
- multi-LLM support
- caching
- repository-specific prompt tuning
- GitHub review status publishing
- Slack/Teams entegrasyonu

---

## 10) Öğrenme kaynakları

### 10.1 Temel kavramlar

- LangGraph dokümantasyonu
- AutoGen dokümantasyonu
- OpenAI function calling ve structured outputs
- GitHub REST API docs
- OWASP Top 10 dokümanları
- pytest, unit test best practices

### 10.2 Uygulama pratiği

- GitHub PR örnekleri üzerinde denemeler yapın
- kendi repo'nuzda küçük diff'ler üretin
- safety prompt ve output schema üzerinde test yapın
- review çıktılarınızı manuel değerlendirin
- hata oranlarını toplayın ve prompt'leri iyileştirin

---

## 11) Son tavsiye

Bu problemi çözmek için en doğru yaklaşım şudur:

- tek bir büyük “AI reviewer” yazmak yerine, uzman ajanlar kurun,
- kontrol akışını orchestrator ile yönetin,
- çıktıları standardize edin,
- güvenlik ve kalite için ayrı state ve değerlendirme mantığı oluşturun,
- GitHub PR yorumlarına markdown formatını düzgün yerleştirin.

Bu sistemin gerçek değeri sadece “bir yorum üretmek” değil, “görüşmeleri ayrı uzmanlık alanlarına ayırarak daha güvenilir ve kullanılabilir PR geri bildirimi üretmek”te yatar.

---

## 12) Hızlı başlangıç checklist

- [ ] Python veya Node.js ortamı kur
- [ ] LangGraph veya AutoGen seç
- [ ] GitHub PAT ve repo erişimi hazırla
- [ ] PR fetch pipeline kur
- [ ] diff parser oluştur
- [ ] logic agent prompt yaz
- [ ] security agent prompt yaz
- [ ] test agent prompt yaz
- [ ] orchestrator tanımla
- [ ] markdown formatter yaz
- [ ] GitHub comment API çağrısı ekle
- [ ] örnek PR üzerinde test et
- [ ] false positive/false negative oranını değerlendir

---

## 13) Kısa sonuç

Bu uygulamayı yapmak için temel olarak şunları öğrenmelisiniz:

- ajan temelli LLM mimarisi,
- GitHub PR API kullanımı,
- diff parsing ve code review mantığı,
- OWASP güvenlik analizi,
- unit test generation,
- orchestrator tasarımı,
- GitHub markdown yorum yayınlama,
- prompt engineering ve output schema üretimi.

Bu alan üç ana bilgi katmanına ayrılır:

1. Mimarisi öğrenmek: LangGraph/AutoGen, tool use, orchestrator
2. Alan bilgisini öğrenmek: güvenlik, test, kod kalitesi
3. Uygulama bağlamını öğrenmek: GitHub PR API, diff parsing, review publishing

Bu üç katmanı birleştirdiğinizde, üretilecek sistem hem teknik hem de operasyonel olarak gerçek bir PR otomasyon çözümü olur.
