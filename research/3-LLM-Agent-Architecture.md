# LLM Tabanlı Ajan Mimarisi — Detaylı Araştırma

## 1. LLM Nedir?

**LLM** (Large Language Model), transformer mimarisi üzerine kurulu ve milyarlarca parametre ile eğitilmiş, doğal dil anlayan ve üretebilen derin öğrenme modelidir.

**Örnekler:**
- GPT-4, GPT-4o (OpenAI)
- Claude 3 (Anthropic)
- Gemini (Google)
- LLaMA (Meta)

---

## 2. Ajan Nedir?

Bir **ajan**, belirli bir görevi yerine getirmek için bağımsız kararlar alabilen, önceki adımların sonuçlarına dayanarak ilerleyebilen yazılım bileşenidir.

### Ajan Özelliği
- **Autonomy:** Kendi kararlarını alabilir
- **Reactivity:** Çevreye tepki verebilir
- **Proactivity:** Kendi amaçlarına doğru hareket edebilir
- **Social:** Diğer ajanlar/insanlar ile iletişim kurabilir

---

## 3. LLM Tabanlı Ajan Mimarisi Nedir?

LLM'i, görev çözmek için aracı (tool) kullanan, sıralı adımlar izleyen bir "zeka" olarak kullanan sistemdir.

### Basit Akış Diyagramı

```
┌─────────────────┐
│   User Query    │
│  (Giriş Sorunu) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   LLM Analysis                          │
│   (Soruyu Anlama, Plan Yapma)           │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Tool Selection & Execution            │
│   (Hangi Tool Kullanacak?)              │
│   - Search                              │
│   - Code Analysis                       │
│   - API Calls                           │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Reflection & Iteration                │
│   (Sonuç Doğru mu? Devam Et mi?)        │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Final Response                        │
│   (Çıkış, Sonuç, Rapor)                 │
└─────────────────────────────────────────┘
```

---

## 4. Multi-Agent Mimarisi

Tek bir LLM yerine, farklı uzmanlık alanlarında birden fazla LLM ajanının koordine edilmesi.

### Örnek: PR Code Review için Multi-Agent

```
GitHub PR
    │
    ├─▶ Logic Agent
    │   ├─ Kontrol: Null handling, error handling, complexity
    │   └─ Çıktı: Logic findings, recommendations
    │
    ├─▶ Security Agent
    │   ├─ Kontrol: OWASP risks, injection, auth/authz
    │   └─ Çıktı: Security findings, risk level
    │
    └─▶ Test Agent
        ├─ Kontrol: Test coverage, missing scenarios
        └─ Çıktı: Test recommendations
            │
            └─▶ Orchestrator
                ├─ Deduplicate
                ├─ Prioritize by severity
                └─ Generate Markdown Report
                    │
                    └─▶ GitHub PR Comment
```

### Avantajları
- **Specialization:** Her ajan kendi alanında uzman
- **Parallelization:** Aynı anda birden fazla analiz
- **Resilience:** Bir ajan hata verirse, diğerleri devam edebilir
- **Accuracy:** Belirli task için daha doğru ve tutarlı sonuçlar

---

## 5. LLM Ajan Bileşenleri

### 5.1 System Prompt
Ajanın rolü ve davranışını tanımlayan talimatlar.

```python
system_prompt = """
You are a senior code reviewer specialized in security analysis.
Your task is to analyze GitHub PR diffs and identify OWASP Top 10 vulnerabilities.

Output format: Return JSON with an array of findings.
Each finding must have:
- title: str
- severity: "info" | "low" | "medium" | "high" | "critical"
- description: str
- evidence: str (relevant code snippet)
- file_path: str
- recommendation: str

Be thorough but avoid false positives. Focus on actual security risks.
"""
```

### 5.2 User Input / Context
Ajanın çalışması için verilen veri.

```python
user_input = f"""
Analyze this GitHub PR for security issues:

Title: {pr_title}
Description: {pr_description}

Changed Files:
{patch_content}

Focus on:
1. Input validation issues
2. Authentication/Authorization flaws
3. Cryptographic weaknesses
4. Command/SQL injection risks
5. SSRF vulnerabilities
"""
```

### 5.3 Tool Use (Function Calling)
Ajan, LLM'in çağırabileceği fonksiyonları tanımlar.

```python
tools = [
    {
        "name": "search_code_pattern",
        "description": "Search for specific security patterns in code",
        "parameters": {
            "pattern": "regex pattern to search",
            "file_path": "optional file to search in"
        }
    },
    {
        "name": "check_dependency",
        "description": "Check if a dependency has known vulnerabilities",
        "parameters": {
            "package": "package name",
            "version": "version number"
        }
    },
    {
        "name": "verify_authentication",
        "description": "Verify if a route has proper auth checks",
        "parameters": {
            "code_snippet": "the code to check"
        }
    }
]
```

### 5.4 Structured Output Schema
LLM'in JSON formatında döndürdüğü yapılandırılmış çıktı.

```json
{
  "findings": [
    {
      "title": "SQL Injection Risk",
      "severity": "critical",
      "description": "User input is concatenated directly into SQL query",
      "evidence": "query = \"SELECT * FROM users WHERE id = \" + user_id",
      "file_path": "src/auth.py",
      "line_hint": "42",
      "recommendation": "Use parameterized queries: db.query('SELECT * FROM users WHERE id = ?', [user_id])"
    }
  ]
}
```

### 5.5 Reflection & Iteration
Ajan, aldığı sonucu kontrol eder ve gerekirse tekrar deneyebilir.

```python
def review_pr_with_reflection(pr_context):
    findings = get_initial_review(pr_context)
    
    # Deduplicate
    findings = deduplicate_findings(findings)
    
    # Check for false positives
    findings = filter_false_positives(findings)
    
    # Prioritize by severity
    findings = sort_by_severity(findings)
    
    return findings
```

---

## 6. Ajan Mimarisinin Tasarım Desenleri

### 6.1 Sequential Agent Pattern
Ajanlar sırasıyla çalışır.

```
Agent1 → Agent2 → Agent3 → Aggregator → Output
```

### 6.2 Parallel Agent Pattern
Ajanlar aynı anda çalışır.

```
          ┌─ Agent1 ─┐
Input ─┬─┤ Agent2 ─┤─ Aggregator ─ Output
       └─ Agent3 ─┘
```

### 6.3 Hierarchical Agent Pattern
Bir master ajan, worker ajanları koordine eder.

```
Master Agent
    ├─ Assign: Analyze security
    │   └─ Worker: Security Agent
    │
    ├─ Assign: Check logic
    │   └─ Worker: Logic Agent
    │
    └─ Collect & Synthesize
        └─ Output
```

### 6.4 Collaborative Agent Pattern
Ajanlar birbirlerine mesaj gönderebilir.

```
Agent1 ◄─→ Agent2 ◄─→ Agent3
  │         │         │
  └─────────┴─────────┘
        Shared Memory
```

---

## 7. Ajan Kontrol Akışı (ReAct Pattern)

**ReAct** = **Reasoning** + **Acting**

```
1. THINK (Düşün)
   └─ Ajan: "Bu PR'da SQL injection riski olabilir. Şu kod bölümünü kontrol etmeliyim."

2. ACT (Harekete Geç)
   └─ Ajan: search_code_pattern(pattern="SELECT.*\+") çağır
   └─ Sonuç: 3 satırda SQL concatenation bulundu

3. OBSERVE (Gözlemle)
   └─ Ajan: Sonuçları analiz et

4. REASON (Mantıkla Yürü)
   └─ Ajan: "Bu gerçekten bir zafiyet, severity=HIGH"

5. OUTPUT (Sonuç Ver)
   └─ Ajan: Finding oluştur
```

---

## 8. LLM Ajan Implementasyonunda Zorluklar

| Zorluk | Açıklama | Çözüm |
|--------|----------|-------|
| Hallucination | LLM var olmayan şeyler üretebilir | Output validation, fact-checking |
| Context Length | Çok uzun input LLM'in anlamasını güçleştir | Chunking, summarization |
| Cost | Her API çağrısı para çıkar | Caching, prioritization |
| Latency | LLM çağrısı zaman alır | Async/parallel processing |
| Consistency | Aynı input farklı output verebilir | Seed setting, temperature tuning |
| False Positives | Zafiyet yok ama zafiyet bulunuyor | Manual review, pattern refinement |

---

## 9. Ajan Tasarımında En İyi Uygulamalar

### 9.1 Clear Role Definition
```python
system_prompt = """
You are SECURITY_REVIEWER_AGENT.
Your ONLY responsibility is to find security vulnerabilities.
Do NOT focus on code style, performance, or logic errors.
Focus ONLY on OWASP Top 10 and CWE-25 issues.
"""
```

### 9.2 Structured Input/Output
```python
# Input'u yapılandır
input_format = {
    "pr_title": str,
    "pr_description": str,
    "files": [{
        "path": str,
        "status": str,  # added/modified/deleted
        "patch": str
    }]
}

# Output'u yapılandır
output_format = {
    "findings": [{
        "title": str,
        "severity": str,  # "critical" | "high" | "medium" | "low" | "info"
        "description": str,
        "evidence": str,
        "recommendation": str
    }]
}
```

### 9.3 Tool Definitions
```python
# Tool'ları net şekilde tanımla
tools = [
    {
        "name": "search_pattern",
        "description": "Search for specific security patterns in code",
        "parameters": {...},
        "return_type": "list[str]"
    }
]
```

### 9.4 Error Handling
```python
try:
    findings = agent.analyze(pr_context)
except LLMError:
    # Fallback to heuristic analysis
    findings = fallback_heuristic_analyzer(pr_context)
except ValueError:
    # Invalid output format
    log_and_alert()
```

### 9.5 Monitoring & Logging
```python
logger.info(f"Starting review for {pr_url}")
logger.debug(f"Agent: {agent.name}, Input tokens: {input_tokens}")
logger.warning(f"Confidence low for finding: {finding.title}")
logger.error(f"Agent failed: {error}")
```

---

## 10. Proje Bağlamında Ajan Mimarisi

Projemizde:

```
GitHub PR URL
    │
    ▼
┌──────────────────────────────────────┐
│ ReviewOrchestrator                   │
│ ├─ Fetches PR via GitHub Client     │
│ ├─ Delegates to agents              │
│ └─ Aggregates results               │
└─────┬────┬────┬────────────────────┘
      │    │    │
      ▼    ▼    ▼
  Logic  Security  Test
  Agent  Agent     Agent
    │      │        │
    └──────┴────────┘
         │
         ▼
  DeduplicateFindings()
         │
         ▼
  SortBySeverity()
         │
         ▼
  RenderMarkdown()
         │
         ▼
  GitHub PR Comment
```

---

## 11. Sonuç

LLM tabanlı multi-agent mimarisi, karmaşık görevleri uzman ajanlarına bölmek ve koordine etmek için güçlü bir yapıdır. Bununla:

- PR code review otomatize edilebilir
- Güvenlik analizi daha kapsamlı hale gelir
- İnsan review'erın iş yükü azalır
- Tutarlı ve tekrarlanabilir sonuçlar elde edilir

Ama şu noktalara dikkat etmek gerekir:
- **Accuracy:** False positive/negative'leri minimize et
- **Cost:** API çağrılarını optimize et
- **Latency:** Kullanıcı beklemede kalsın istemiyor
- **Human Loop:** Nihai karar her zaman insan tarafından yapılsın
