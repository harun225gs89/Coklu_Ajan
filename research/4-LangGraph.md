# LangGraph Nedir? — Detaylı Araştırma

## 1. LangGraph Tanımı

**LangGraph**, LLM'leri programlı workflow'lar içinde kullanmak için tasarlanmış bir Python framework'üdür. Graph (DAG - Directed Acyclic Graph) yapısında ajanlar, state'ler ve transitions'ı tanımlayarak kompleks multi-step işlemleri modellemenizi sağlar.

**Temel İdea:** Ajan mantığını linear kod yerine state machine'e dönüştürme.

### LangGraph Kimden?
LangChain ekibi tarafından geliştirilen bir framework.

---

## 2. Neden LangGraph Gerekli?

### Problem: Sıradan LLM Çağrısı

```python
# Simple LLM call — problem!
response = llm.call("Analyze this code for security issues")

# Sorunlar:
# 1. Hiçbir kontrol akışı yok
# 2. Error handling zor
# 3. Parallelization imkansız
# 4. State management yok
# 5. Debugging zorluyuk
```

### Çözüm: LangGraph

```python
# LangGraph — structured workflow
graph = StateGraph(ReviewState)
graph.add_node("fetch_pr", fetch_pr_function)
graph.add_node("analyze_security", security_agent)
graph.add_node("analyze_logic", logic_agent)
graph.add_edge("fetch_pr", "analyze_security")
graph.add_edge("fetch_pr", "analyze_logic")
# ...
compiled_graph = graph.compile()
result = compiled_graph.invoke({"pr_url": url})
```

---

## 3. LangGraph'ın Temel Kavramları

### 3.1 State

State, workflow'un her adımında geçiş yapan veridir.

```python
from typing import TypedDict
from typing import Annotated

class ReviewState(TypedDict):
    pr_url: str                      # Input
    pr_context: dict                 # Fetched PR data
    logic_findings: list[Finding]    # Logic agent output
    security_findings: list[Finding] # Security agent output
    final_report: str                # Final output
```

### 3.2 Nodes

Node'lar, her state geçişinde çalıştırılan fonksiyonlardır.

```python
def fetch_pr_node(state: ReviewState) -> dict:
    """Fetch PR from GitHub"""
    pr_data = github_client.fetch(state["pr_url"])
    return {"pr_context": pr_data}

def analyze_security_node(state: ReviewState) -> dict:
    """Run security agent"""
    findings = security_agent.analyze(state["pr_context"])
    return {"security_findings": findings}

def aggregate_node(state: ReviewState) -> dict:
    """Combine all findings"""
    all_findings = (
        state["logic_findings"] + 
        state["security_findings"]
    )
    report = render_markdown(all_findings)
    return {"final_report": report}
```

### 3.3 Edges

Edge'ler, node'lar arasındaki geçişleri tanımlar.

```python
# Basit edge (unconditional)
graph.add_edge("fetch_pr", "analyze_security")
graph.add_edge("analyze_security", "aggregate")

# Conditional edge (if-else)
def route_by_size(state: ReviewState) -> str:
    if state["pr_context"]["changed_files"] > 100:
        return "handle_large_pr"
    else:
        return "handle_normal_pr"

graph.add_conditional_edges(
    "fetch_pr",
    route_by_size,
    {
        "handle_large_pr": "split_analysis",
        "handle_normal_pr": "full_analysis"
    }
)
```

---

## 4. LangGraph Workflow Örneği: PR Review

### Basit Akış

```
START
  │
  ▼
fetch_pr_node (GitHub API çağrısı)
  │
  ├──────────────────────────────┐
  │                              │
  ▼                              ▼
logic_node              security_node    (paralel çalışır)
  │                              │
  │                              ▼
  │                        test_node
  │                              │
  └──────────────────┬───────────┘
                     ▼
              aggregate_node (sonuçları birleştir)
                     │
                     ▼
               END (markdown output)
```

### Kod Implementasyonu

```python
from langgraph.graph import StateGraph, END, START

def build_review_graph():
    graph = StateGraph(ReviewState)
    
    # Node'ları ekle
    graph.add_node("fetch", fetch_pr_node)
    graph.add_node("logic", logic_analysis_node)
    graph.add_node("security", security_analysis_node)
    graph.add_node("tests", test_analysis_node)
    graph.add_node("aggregate", aggregate_findings_node)
    
    # Edge'leri ekle
    graph.add_edge(START, "fetch")
    graph.add_edge("fetch", "logic")
    graph.add_edge("fetch", "security")
    graph.add_edge("logic", "tests")
    graph.add_edge("security", "tests")
    graph.add_edge("tests", "aggregate")
    graph.add_edge("aggregate", END)
    
    # Compile et
    return graph.compile()

# Çalıştır
graph = build_review_graph()
result = graph.invoke({"pr_url": "https://github.com/..."})
print(result["final_report"])
```

---

## 5. LangGraph'ın Avantajları

### 5.1 State Management
```python
# State tutarlı şekilde workflow'un tamamında taşınır
state = {
    "pr_url": "...",
    "pr_context": {...},
    "findings": [],
    "errors": []
}

# Her node state'i güncelleyebilir
def new_node(state):
    state["findings"].append(new_finding)
    return {"findings": state["findings"]}
```

### 5.2 Conditional Routing
```python
# Dinamik karar verme
def should_continue(state):
    if len(state["findings"]) > 10:
        return "alert_admin"
    else:
        return "finalize"

graph.add_conditional_edges("analyze", should_continue, {...})
```

### 5.3 Error Handling
```python
# Try-except ve fallback mekanizmaları
def safe_fetch_pr(state):
    try:
        return {"pr_context": github_client.fetch(...)}
    except Exception as e:
        return {"error": str(e), "fallback_mode": True}

# Sonra error'u handle et
def handle_error(state):
    if "error" in state:
        return "use_cache"
    else:
        return "normal_flow"
```

### 5.4 Parallelization
```python
# Aynı anda birden fazla node çalıştırılabilir
graph.add_edge("fetch", "logic")
graph.add_edge("fetch", "security")
graph.add_edge("fetch", "tests")

# Bunların hepsi paralel olarak çalışır
```

### 5.5 Debugging & Monitoring
```python
# Execution trace
for step in graph.stream(state):
    print(f"Node: {step}")
    # Hangi node çalışıyor, ne input aldı, ne output verdi biliriz
```

---

## 6. State Annotators (Advanced)

State'i güncellerken değişiklikleri özelleştirmek.

```python
from typing import Annotated
from operator import add

def add_list(existing: list, new: list) -> list:
    """Custom reducer for list fields"""
    return existing + new  # Append instead of replace

class ReviewState(TypedDict):
    pr_url: str
    findings: Annotated[list[Finding], add_list]  # Add to list, don't replace
    errors: Annotated[list[str], add_list]
```

---

## 7. Memory / Persistence

Workflow'un durumunu kaydetme ve geri yükleme.

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph = build_review_graph()
compiled = graph.compile(checkpointer=memory)

# Workflow'u çalıştır ve checkpoint'ler kaydedilir
result = compiled.invoke({"pr_url": "..."}, config={"configurable": {"thread_id": "pr_123"}})

# Aynı workflow'u devam ettir (resumable workflows)
result = compiled.invoke({"continue": True}, config={"configurable": {"thread_id": "pr_123"}})
```

---

## 8. LangGraph vs Alternatifler

| Framework | Use Case | Avantaj | Dezavantaj |
|-----------|----------|---------|-----------|
| **LangGraph** | Kompleks multi-step workflows | State management, Conditional routing | LLM-specific |
| **Prefect / Airflow** | Data pipelines | Scaling, Monitoring | Complex setup |
| **Pydantic** | Data validation | Simple, Fast | No workflow control |
| **asyncio** | Async tasks | Native Python | Manual orchestration |

---

## 9. Proje'de LangGraph Kullanımı

Projemizde şu şekilde kullanılmıştır:

```python
# File: pr_review_agent/pr_review_agent/graph.py

from langgraph.graph import StateGraph, END, START

class ReviewState(TypedDict):
    pr_url: str
    pr_context: PRContext
    logic_findings: list[Finding]
    security_findings: list[Finding]
    test_findings: list[Finding]
    review: ReviewResult
    markdown: str

def build_review_graph(github_client: GitHubClient):
    workflow = StateGraph(ReviewState)
    
    # Node'ları ekle
    workflow.add_node("fetch_pr", lambda s: _fetch_pr_context(s, github_client))
    workflow.add_node("logic_review", _collect_logic)
    workflow.add_node("security_review", _collect_security)
    workflow.add_node("test_review", _collect_tests)
    workflow.add_node("aggregate", _aggregate_results)
    
    # Edge'leri ekle (sequential)
    workflow.add_edge(START, "fetch_pr")
    workflow.add_edge("fetch_pr", "logic_review")
    workflow.add_edge("logic_review", "security_review")
    workflow.add_edge("security_review", "test_review")
    workflow.add_edge("test_review", "aggregate")
    workflow.add_edge("aggregate", END)
    
    return workflow.compile()

# Çalıştırma
graph = build_review_graph(github_client)
result = graph.invoke({"pr_url": pr_url})
```

---

## 10. Gerçek Hayat Örneği: Multi-PR Review

```python
# Paralel PR review için optimize edilmiş workflow

class MultiPRState(TypedDict):
    pr_urls: list[str]
    current_pr_index: int
    results: Annotated[dict[str, ReviewResult], lambda x, y: {**x, **y}]

def select_next_pr(state: MultiPRState) -> str:
    if state["current_pr_index"] < len(state["pr_urls"]):
        return "process_pr"
    else:
        return "finalize"

graph = StateGraph(MultiPRState)
graph.add_node("process_pr", process_single_pr_node)
graph.add_node("finalize", finalize_results_node)
graph.add_conditional_edges("process_pr", select_next_pr, {
    "process_pr": "process_pr",
    "finalize": "finalize"
})
```

---

## 11. LangGraph Installation ve Usage

### Installation
```bash
pip install langgraph
```

### Minimal Example
```python
from langgraph.graph import StateGraph, END, START
from typing import TypedDict

class State(TypedDict):
    message: str

def node_1(state: State) -> dict:
    return {"message": state["message"] + " processed by node1"}

def node_2(state: State) -> dict:
    return {"message": state["message"] + " processed by node2"}

graph = StateGraph(State)
graph.add_node("n1", node_1)
graph.add_node("n2", node_2)
graph.add_edge(START, "n1")
graph.add_edge("n1", "n2")
graph.add_edge("n2", END)

compiled = graph.compile()
result = compiled.invoke({"message": "Hello"})
print(result["message"])
# Output: Hello processed by node1 processed by node2
```

---

## 12. Sonuç

LangGraph, LLM-based ajanları production'da çalıştırmak için güçlü bir framework'tür. Bununla:

- Kompleks workflows basitçe modellenir
- State management otomatik olur
- Error handling ve debugging kolay hale gelir
- Parallelization'u hemen kullana bilirsiniz
- Production-ready checkpoint/memory desteği vardır

Projemizde, PR code review'ı sıralı olarak 4 node'da yapmak için kullanılmıştır:
1. fetch_pr (GitHub'tan PR al)
2. logic_review (Logic Agent çalıştır)
3. security_review (Security Agent çalıştır)
4. test_review (Test Agent çalıştır)
5. aggregate (Sonuçları birleştir)

Bu, state management'ı ve kontrol akışını temiz ve anlaşılır hale getirir.
