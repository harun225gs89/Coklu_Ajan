# GitHub REST API — Detaylı Araştırma

## 1. GitHub REST API Nedir?

**GitHub REST API**, GitHub'ın tüm platform özelliklerine programlı olarak erişim sağlayan HTTP-based API'sidir.

### Base URL
```
https://api.github.com/
```

### Örnek: Pull Request Bilgisi Almak
```bash
curl https://api.github.com/repos/owner/repo/pulls/123
```

---

## 2. Authentication (Kimlik Doğrulama)

### 2.1 Unauthenticated Requests
```bash
# Rate limit: 60 requests/hour
curl https://api.github.com/repos/nodejs/node/pulls/1

# Dezavantaj: Düşük rate limit
```

### 2.2 Personal Access Token (PAT)
```bash
# Rate limit: 5,000 requests/hour
curl -H "Authorization: token ghp_xxxxxxxxxxxxx" \
     https://api.github.com/repos/nodejs/node/pulls/1
```

### 2.3 Bearer Token (Apps)
```bash
curl -H "Authorization: Bearer ghu_xxxxxxxxxxxxx" \
     https://api.github.com/repos/nodejs/node/pulls/1
```

### PAT Oluşturma Adımları
1. GitHub.com → Settings → Developer settings → Personal access tokens
2. "Generate new token" → Scopes seç
3. Token'ı kopyala ve kaydet (tekrar göremezsin!)

### Gereken Scopes (PR Review için)
```
repo              # Full control of private repositories
repo:status       # Access commit status
public_repo       # Access public repositories
read:user         # User profile data
```

---

## 3. PR API Endpoints

### 3.1 Pull Request Detayları Almak

```bash
GET /repos/{owner}/{repo}/pulls/{pull_number}
```

**Response:**
```json
{
  "id": 1,
  "number": 1347,
  "state": "open",
  "title": "Amazing new feature",
  "user": {
    "login": "octocat",
    "type": "User"
  },
  "body": "Please pull these awesome changes in!",
  "created_at": "2011-01-26T19:01:12Z",
  "updated_at": "2011-01-26T19:01:12Z",
  "head": {
    "label": "octocat:new-topic",
    "ref": "new-topic",
    "sha": "6dcb09b5b57875f2f69c6e1ce857dfe72f"
  },
  "base": {
    "label": "octocat:master",
    "ref": "master",
    "sha": "d85f76b01"
  },
  "changed_files": 104,
  "additions": 4336,
  "deletions": 3467
}
```

### 3.2 PR'deki Değişen Dosyaları Almak

```bash
GET /repos/{owner}/{repo}/pulls/{pull_number}/files
```

**Response (paginated, max 100 per page):**
```json
[
  {
    "sha": "bbcd538c8e72b8c175046e27cc627ce3738d9a55",
    "filename": "file1.txt",
    "status": "added",
    "additions": 104,
    "deletions": 21,
    "changes": 125,
    "blob_url": "https://github.com/octocat/Hello-World/blob/6dcb09b5b57875f2f69c6e1ce857dfe72f/file1.txt",
    "raw_url": "https://github.com/octocat/Hello-World/raw/6dcb09b5b57875f2f69c6e1ce857dfe72f/file1.txt",
    "patch": "@@ -132,7 +132,7 @@ module Test\n...\n"
  },
  ...
]
```

### 3.3 Tek Dosya Inline Comment Eklemek

```bash
POST /repos/{owner}/{repo}/pulls/{pull_number}/comments
```

**Request Body:**
```json
{
  "body": "Great work on this change!",
  "commit_id": "6dcb09b5b57875f2f69c6e1ce857dfe72f",
  "path": "file1.txt",
  "line": 1
}
```

### 3.4 PR'ye General Comment Eklemek

```bash
POST /repos/{owner}/{repo}/issues/{issue_number}/comments
```

**Request Body:**
```json
{
  "body": "# Code Review Results\n\n## Security Issues: 3\n..."
}
```

### 3.5 Commit Detayları

```bash
GET /repos/{owner}/{repo}/commits/{commit_sha}
```

### 3.6 File Diff

```bash
GET /repos/{owner}/{repo}/pulls/{pull_number}/files/{file_index}
```

---

## 4. Rate Limiting

### Rate Limit Information
```bash
curl -i https://api.github.com/repos/octocat/Hello-World
```

Response headers:
```
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4999
X-RateLimit-Reset: 1234567890
```

### Rate Limit Status
```bash
GET /rate_limit
```

**Response:**
```json
{
  "resources": {
    "core": {
      "limit": 5000,
      "remaining": 4999,
      "reset": 1234567890
    },
    "search": {
      "limit": 30,
      "remaining": 30,
      "reset": 1234567890
    }
  },
  "rate": {
    "limit": 5000,
    "remaining": 4999,
    "reset": 1234567890
  }
}
```

### Rate Limit Handling Strategy

```python
import time
import requests

def safe_github_request(url, headers):
    response = requests.get(url, headers=headers)
    
    if response.status_code == 403:
        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        reset_time = int(response.headers.get('X-RateLimit-Reset', time.time()))
        
        if remaining == 0:
            sleep_duration = reset_time - time.time() + 10
            print(f"Rate limited! Waiting {sleep_duration}s...")
            time.sleep(max(0, sleep_duration))
            return safe_github_request(url, headers)
    
    return response
```

---

## 5. Pagination

GitHub API birçok endpoint'te max 100 item dönüyor.

### Link Header (Recommended)

```bash
curl -i https://api.github.com/repos/octocat/Hello-World/pulls/1/files
```

Response header:
```
Link: <https://api.github.com/repos/octocat/Hello-World/pulls/1/files?page=2>; rel="next",
      <https://api.github.com/repos/octocat/Hello-World/pulls/1/files?page=3>; rel="last"
```

### Manual Pagination

```bash
# First page (default per_page=30)
GET /repos/{owner}/{repo}/pulls/1/files?page=1&per_page=100

# Next pages
GET /repos/{owner}/{repo}/pulls/1/files?page=2&per_page=100
GET /repos/{owner}/{repo}/pulls/1/files?page=3&per_page=100
```

### Python Implementation

```python
def fetch_all_pr_files(owner, repo, pr_number, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    headers = {"Authorization": f"token {token}"}
    all_files = []
    page = 1
    
    while True:
        response = requests.get(url, headers=headers, params={"page": page, "per_page": 100})
        response.raise_for_status()
        
        files = response.json()
        if not files:  # Empty page = no more data
            break
        
        all_files.extend(files)
        page += 1
    
    return all_files
```

---

## 6. PR URL Parsing

### GitHub PR URL Formatları

```
https://github.com/owner/repo/pull/123
https://github.com/owner/repo/pulls/123
https://github.com/owner/repo/pull/123/
```

### Python Parsing

```python
import re
from urllib.parse import urlparse

def parse_pr_url(url):
    url = url.strip().rstrip('/')
    
    # Regex: https://github.com/{owner}/{repo}/pull(s)?/{number}
    pattern = r'https://github\.com/([^/]+)/([^/]+)/pulls?/(\d+)'
    match = re.match(pattern, url)
    
    if not match:
        raise ValueError(f"Invalid GitHub PR URL: {url}")
    
    owner, repo, pr_number = match.groups()
    return {
        "owner": owner,
        "repo": repo,
        "pr_number": int(pr_number)
    }

# Test
result = parse_pr_url("https://github.com/nodejs/node/pull/12345")
# {'owner': 'nodejs', 'repo': 'node', 'pr_number': 12345}
```

---

## 7. Gitmek İçin Best Practices

### 7.1 Conditional Requests (Caching)

```bash
# First request
curl -i https://api.github.com/repos/octocat/Hello-World

# Response includes ETag
ETag: "644b5b0155e6404a33152e27f085136f"

# Second request (conditional)
curl -i -H 'If-None-Match: "644b5b0155e6404a33152e27f085136f"' \
     https://api.github.com/repos/octocat/Hello-World

# Response: 304 Not Modified (doesn't count towards rate limit!)
```

### 7.2 Field Filtering

Sadece ihtiyacın alanları iste (bandwidth tasarrufu):

```bash
# Tüm alanları al (6.2 KB)
GET /repos/{owner}/{repo}/pulls/1

# Sadece title ve state (0.5 KB)
GET /repos/{owner}/{repo}/pulls/1?fields=title,state
```

### 7.3 Batch Processing

Birden fazla PR'yi işlerken:

```python
# Paralel istekler (rate limit'e dikkat!)
import concurrent.futures

pr_numbers = [1, 2, 3, 4, 5]

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(fetch_pr_details, owner, repo, pr_num, token)
        for pr_num in pr_numbers
    ]
    results = [f.result() for f in futures]
```

---

## 8. GraphQL API (Alternative)

GitHub'ın GraphQL API'si de vardır (daha esnek):

```graphql
query {
  repository(owner: "octocat", name: "Hello-World") {
    pullRequest(number: 1) {
      title
      body
      files(first: 100) {
        edges {
          node {
            path
            patch
          }
        }
      }
    }
  }
}
```

### REST vs GraphQL

| Özellik | REST | GraphQL |
|---------|------|---------|
| Simplicity | Kolay öğrenilir | Kompleks |
| Over-fetching | Var (extra fields) | Yok (tam kontrol) |
| Under-fetching | Var (multiple calls) | Yok (single call) |
| Rate Limit | Per endpoint | Per query (node-based) |
| Learning Curve | Düşük | Yüksek |

---

## 9. Projede GitHub API Kullanımı

### File: pr_review_agent/github_client.py

```python
class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def fetch_pr(self, owner: str, repo: str, pr_number: int) -> dict:
        """Fetch PR details"""
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def fetch_pr_files(self, owner: str, repo: str, pr_number: int) -> list:
        """Fetch all changed files with pagination"""
        files = []
        page = 1
        
        while True:
            url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
            response = requests.get(
                url,
                headers=self.headers,
                params={"page": page, "per_page": 100}
            )
            response.raise_for_status()
            
            data = response.json()
            if not data:
                break
            
            files.extend(data)
            page += 1
        
        return files
    
    def post_comment(self, owner: str, repo: str, issue_number: int, body: str):
        """Post comment on PR"""
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
        response = requests.post(
            url,
            headers=self.headers,
            json={"body": body}
        )
        response.raise_for_status()
        return response.json()
```

---

## 10. Error Handling

### Common HTTP Status Codes

| Code | Anlamı | Örnek |
|------|--------|-------|
| 200 | OK | Request başarılı |
| 301 | Moved Permanently | Repo taşındı |
| 304 | Not Modified | Cached data hala geçerli |
| 400 | Bad Request | Invalid parameter |
| 401 | Unauthorized | Token gerekli |
| 403 | Forbidden | Rate limit veya permission |
| 404 | Not Found | PR yok |
| 422 | Validation Failed | Invalid data submitted |
| 500 | Server Error | GitHub server hatası |

### Python Error Handling

```python
import requests
from requests.exceptions import RequestException

def safe_fetch_pr(owner, repo, pr_number, token):
    try:
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}",
            headers={"Authorization": f"token {token}"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError(f"PR not found: {owner}/{repo}#{pr_number}")
        elif e.response.status_code == 403:
            raise RuntimeError("Rate limited. Wait and retry.")
        else:
            raise
    
    except requests.exceptions.Timeout:
        raise RuntimeError("GitHub API timeout")
    
    except RequestException as e:
        raise RuntimeError(f"Network error: {e}")
```

---

## 11. Sonuç

GitHub REST API ile:

- PR detayları programlı olarak alabilirsiniz
- Dosya diff'lerini çekebilirsiniz
- PR'ye comment ekleyebilirsiniz
- Rate limiting'i yönetebilirsiniz

Projemizde, PR code review'ın başındaki ilk adım GitHub'tan veri çekmek olmuştur. Bu veri, ajanların analiz etmesi için pipeline'ın ilk düğümüdür (fetch_pr node).

**Key Takeaway:** Rate limiting'e dikkat edin! Büyük PR'ler (100+ dosya) unauthenticated requests'le hızlı rate limit'e çarpabilir.
