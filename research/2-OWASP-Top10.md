# OWASP Top 10 — Detaylı Araştırma

## 1. OWASP Nedir?

**OWASP** (Open Web Application Security Project), web uygulamalarının güvenliğini iyileştirmek için bağımsız, açık kaynak bir organizasyondur.

Her 3 yılda bir "OWASP Top 10" yayınlanır — en kritik web güvenliği risklerinin sıralaması.

**Son Versiyon:** OWASP Top 10 2021

---

## 2. OWASP Top 10 2021

### 1️⃣ A01: Broken Access Control (Kırılmış Erişim Kontrolü)

**Tanım:** Kullanıcıların yetkisi olmadığı kaynaklara erişebilmesi.

**Örnekler:**
```python
# ❌ KÖTÜ: Hiçbir yetki kontrolü yok
@app.route('/user/<int:user_id>')
def get_user(user_id):
    return User.query.get(user_id).to_json()

# ✅ İYİ: Yetki kontrolü var
@app.route('/user/<int:user_id>')
@login_required
def get_user(user_id):
    current_user = get_current_user()
    if current_user.id != user_id and not current_user.is_admin:
        abort(403)
    return User.query.get(user_id).to_json()
```

**Risk Seviyesi:** 🔴 KRITIK  
**Etki:** Unauthorized veri okuma, yazma, silme veya modifikasyon.

---

### 2️⃣ A02: Cryptographic Failures (Kriptografi Arızaları)

**Tanım:** Hassas verilerin şifrelenmeksizin veya zayıf şifrelemeyle depolanması.

**Örnekler:**
```python
# ❌ KÖTÜ: Şifresiz password depolama
user.password = request.data['password']

# ❌ KÖTÜ: Zayıf hashing
import hashlib
hashed = hashlib.md5(password).hexdigest()

# ✅ İYİ: bcrypt ile hashing
from werkzeug.security import generate_password_hash
hashed = generate_password_hash(password, method='pbkdf2:sha256')
```

**Risk Seviyesi:** 🔴 KRITIK  
**Etki:** Hassas veri sızıntısı, GDPR ihlali, finansal zarar.

---

### 3️⃣ A03: Injection (Enjeksiyon)

**Tanım:** Güvenilmez verilerin interpreter'a gönderilerek kod yürütülmesi.

**Türleri:**
- **SQL Injection**
- **Command Injection**
- **LDAP Injection**
- **OS Command Injection**

**Örnekler:**

#### SQL Injection
```python
# ❌ KÖTÜ: String concatenation
query = "SELECT * FROM users WHERE email = '" + email + "'"
db.execute(query)

# ✅ İYİ: Parameterized query
query = "SELECT * FROM users WHERE email = ?"
db.execute(query, [email])
```

#### Command Injection
```python
# ❌ KÖTÜ: Shell string concatenation
os.system("rm -rf " + user_input)

# ✅ İYİ: Safe subprocess API
subprocess.run(["rm", "-rf", user_input], check=True)
```

**Risk Seviyesi:** 🔴 KRITIK  
**Etki:** Tam sistem kontrolü, veri çalınması, veri bozulması.

---

### 4️⃣ A04: Insecure Design (Güvensiz Tasarım)

**Tanım:** Uygulamanın tasarım aşamasında güvenlik göz ardı edilmesi.

**Örnekler:**
- Threat modeling yapılmamış
- Rate limiting yok
- Password policy zayıf
- Account recovery process güvensiz

**Risk Seviyesi:** 🟠 YÜKSEK  
**Etki:** Brute force, account takeover.

---

### 5️⃣ A05: Security Misconfiguration (Güvenlik Yanlış Konfigürasyonu)

**Tanım:** Uygulamayı çalıştıran sistemin yanlış konfigürasyonu.

**Örnekler:**
- Debug mode production'da açık
- Default credentials kullanılmış
- Gereksiz HTTP headers açık
- Bilinmeyen software versiyonları
- Security headers ekli değil

**Kontrol Listesi:**
```
- [ ] Debug mode disabled
- [ ] Default credentials changed
- [ ] Unnecessary features disabled
- [ ] Security headers set (CSP, X-Frame-Options, etc.)
- [ ] CORS properly configured
- [ ] HTTPS enforced
- [ ] Sensitive endpoints rate limited
```

**Risk Seviyesi:** 🟠 YÜKSEK

---

### 6️⃣ A06: Vulnerable and Outdated Components (Zayıf ve Eski Bileşenler)

**Tanım:** Known vulnerabilities'i olan kütüphaneler veya framework'lerin kullanılması.

**Örnekler:**
```bash
# Bağımlılıkları kontrol et
pip install safety
safety check

# npm'de
npm audit
npm audit fix

# GitHub bağımlılık taraması
dependabot scan
```

**Ortak Kütüphane Zafiyetleri:**
- OpenSSL 1.0.2 (heartbleed)
- Log4j 2 (CVE-2021-44228)
- Apache Struts 2 (RCE)

**Risk Seviyesi:** 🟠 YÜKSEK

---

### 7️⃣ A07: Identification and Authentication Failures (Kimlik ve Kimlik Doğrulama Arızaları)

**Tanım:** Weak authentication mekanizmaları.

**Örnekler:**
```python
# ❌ KÖTÜ: Weak password
if password == "123456":
    login()

# ❌ KÖTÜ: Session timeout yok
session['user_id'] = user.id
# Never expires!

# ✅ İYİ: Multi-factor authentication
import pyotp
secret = pyotp.random_base32()
totp = pyotp.TOTP(secret)
if totp.verify(user_code):
    login()

# ✅ İYİ: Session timeout
@app.before_request
def check_session_timeout():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)
```

**Risk Seviyesi:** 🔴 KRITIK

---

### 8️⃣ A08: Software and Data Integrity Failures (Yazılım ve Veri Bütünlüğü Arızaları)

**Tanım:** Güncellemeler veya kritik verinin kaynağının doğrulanmaması.

**Örnekler:**
- Signed updates olmadan build ve deployment
- Package manager poisoning
- Unsigned dependencies

**Kontrol:**
```bash
# Cryptographic signature verification
gpg --verify package.tar.gz.asc package.tar.gz

# npm package integrity
npm install --audit-level=critical

# Checksum verification
sha256sum -c checksums.txt
```

**Risk Seviyesi:** 🟠 YÜKSEK

---

### 9️⃣ A09: Security Logging and Monitoring Failures (Güvenlik Logging ve Monitoring Arızaları)

**Tanım:** Güvenlik olaylarının kaydedilmemesi veya izlenmemesi.

**Örnekler:**
```python
# ✅ İYİ: Security events logging
import logging

security_logger = logging.getLogger('security')

def login(email, password):
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.verify_password(password):
        security_logger.warning(f"Failed login attempt: {email}")
        return False
    
    security_logger.info(f"Successful login: {email} from {request.remote_addr}")
    return True

def unauthorized_access(user_id):
    security_logger.error(f"Unauthorized access attempt by {user_id}")
    alert_admin()
```

**Monitoring Konuları:**
- Failed login attempts
- Unauthorized access attempts
- Privilege escalation
- Data access patterns
- Configuration changes

**Risk Seviyesi:** 🟠 YÜKSEK

---

### 🔟 A10: Server-Side Request Forgery (SSRF)

**Tanım:** Uygulama, kullanıcının kontrol ettiği bir URL'ye istek yapması.

**Örnekler:**
```python
# ❌ KÖTÜ: Unvalidated URL
@app.route('/fetch')
def fetch_data():
    url = request.args.get('url')
    response = requests.get(url)  # Attacker can fetch internal resources!
    return response.text

# ✅ İYİ: URL whitelisting
ALLOWED_DOMAINS = ['api.example.com', 'data.example.com']

def is_safe_url(url):
    parsed = urllib.parse.urlparse(url)
    return parsed.netloc in ALLOWED_DOMAINS

@app.route('/fetch')
def fetch_data():
    url = request.args.get('url')
    if not is_safe_url(url):
        abort(400)
    response = requests.get(url)
    return response.text

# ✅ İYİ: Disallowing internal networks
BLOCKED_SUBNETS = [
    '192.168.0.0/16',
    '10.0.0.0/8',
    '127.0.0.0/8',
    '169.254.0.0/16'
]

def is_internal_ip(ip_str):
    ip = ipaddress.ip_address(ip_str)
    for subnet in BLOCKED_SUBNETS:
        if ip in ipaddress.ip_network(subnet):
            return True
    return False
```

**Yaygın SSRF Hedefleri:**
- Internal APIs
- Cloud metadata servers (AWS, GCP, Azure)
- Database servers
- Admin panels

**Risk Seviyesi:** 🟠 YÜKSEK

---

## 3. Risk Severity Matrix

| ID | Zafiyet | Prevalence | Detectability | Impact | Severity |
|-----|---------|-----------|---------------|--------|----------|
| A01 | Broken Access Control | Widespread | Easy | Severe | 🔴 CRITICAL |
| A02 | Cryptographic Failures | Widespread | Average | Severe | 🔴 CRITICAL |
| A03 | Injection | Common | Easy | Severe | 🔴 CRITICAL |
| A04 | Insecure Design | Widespread | Difficult | Severe | 🟠 HIGH |
| A05 | Security Misconfiguration | Common | Easy | Severe | 🟠 HIGH |
| A06 | Vulnerable Components | Common | Easy | Severe | 🟠 HIGH |
| A07 | Auth Failures | Widespread | Easy | Severe | 🔴 CRITICAL |
| A08 | Integrity Failures | Uncommon | Difficult | Severe | 🟠 HIGH |
| A09 | Logging Failures | Widespread | Difficult | Moderate | 🟡 MEDIUM |
| A10 | SSRF | Common | Average | Severe | 🟠 HIGH |

---

## 4. PR Code Review Checklist (OWASP Uyarı)

Bu listeyi PR analiz ederken kullanabilirsin:

```markdown
## OWASP Top 10 Security Check

- [ ] **A01:** Yetki kontrolü var mı? (isAdmin, owner check, etc.)
- [ ] **A02:** Sensitive data (password, key, token) doğru şifrelenmiş mi?
- [ ] **A03:** Kullanıcı input'u safe şekilde kullanılmış mı? (Parameterized queries, escaped output)
- [ ] **A04:** Threat model yazılmış mı? Rate limiting, account recovery secure mi?
- [ ] **A05:** Debug mode, default credentials, security headers kontrol edilmiş mi?
- [ ] **A06:** Yeni dependency'ler güvenli versiyonda mı?
- [ ] **A07:** Session/JWT timeout var mı? MFA gerekli mi?
- [ ] **A08:** Dependency updates signed ve verified mi?
- [ ] **A09:** Security events logged mi? (failed auth, unauthorized access)
- [ ] **A10:** External URL requests validated mi? SSRF riski var mı?
```

---

## 5. Praktik Güvenlik Araçları

### Static Analysis Tools
- **SonarQube:** Code quality ve security taraması
- **Bandit (Python):** Python güvenlik analiziyor
- **ESLint (JS):** JavaScript linter'ı ve security rules
- **Semgrep:** Multi-language static analyzer

### Dependency Scanning
- **npm audit:** Node.js bağımlılık taraması
- **safety:** Python bağımlılık taraması
- **OWASP Dependency-Check:** Multi-language
- **Snyk:** Continuous vulnerability monitoring

### Dynamic Testing
- **OWASP ZAP:** Web application security scanner
- **Burp Suite:** Penetration testing suite

---

## 6. Sonuç

OWASP Top 10, web uygulamalarının en yaygın ve tehlikeli zafiyetlerini listeler. PR analiz ederken bu listevi göz önünde bulundurarak:

1. Input validation kontrol et
2. Authentication/authorization mekanizmasını doğrula
3. Cryptography doğru kullanılmış mı bak
4. Sensitive data'nın güvenliğini kontrol et
5. External resource access'i sınırla
6. Error handling ve logging düzgün mü kontrol et
7. Dependencies güncel ve güvenli mi bak

...yapılmalıdır. Bu proje tam da bunu otomatize etmek için tasarlandı!
