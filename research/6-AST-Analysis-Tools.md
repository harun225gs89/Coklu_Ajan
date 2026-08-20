# AST Analiz Araçları — Detaylı Araştırma

## 1. AST Nedir?

**AST** = **Abstract Syntax Tree** (Soyut Söz Dizimi Ağacı)

Kaynak kodun yapısını hiyerarşik bir ağaç yapısına dönüştüren, semantik detayları (değişken adları gibi) saklayan, syntax detaylarını (whitespace, comments) atlayan veri yapısıdır.

### Örnek: Python Kodu → AST

```python
x = 5 + 3
```

**AST Representation:**
```
Module(
  body=[
    Assign(
      targets=[Name(id='x')],
      value=BinOp(
        left=Constant(value=5),
        op=Add(),
        right=Constant(value=3)
      )
    )
  ]
)
```

### Görsel Ağaç
```
        Module
          │
        Assign
         │   │
      targets value
         │      │
       Name  BinOp
        │    │   │
        x  left  op  right
           │     │    │
          Const Add  Const
           5         3
```

---

## 2. Neden AST?

### Problem: Regex Ile Kod Analizi
```python
# Güvenlik açığı arandı (SQL injection)
import re

def find_sql_injection(code):
    # Regex: çok basit, çok hatalı!
    pattern = r'SELECT.*\+.*FROM'
    return re.findall(pattern, code)
```

**Sorunlar:**
- String'ler içindeki "SELECT" de bulur (yanlış alarm)
- Comment'ler içindeki "SELECT"i bulur
- Whitespace değişikliklerine duyarlı
- False positive çok

### Çözüm: AST

```python
import ast

class SqlInjectionChecker(ast.NodeVisitor):
    def visit_Call(self, node):
        # SQL query function çağrılarını bul
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ('execute', 'executemany'):
                # SQL string'in nasıl oluşturulduğunu kontrol et
                if isinstance(node.args[0], ast.BinOp):
                    # String concatenation: risky!
                    self.report_issue("SQL injection risk")
        self.generic_visit(node)

tree = ast.parse(code)
checker = SqlInjectionChecker()
checker.visit(tree)
```

**Avantajlar:**
- Semantic olarak doğru analiz
- String vs. code ayrımı yapabilir
- Komplex pattern matching
- False positive çok az

---

## 3. Python AST

### 3.1 Basic Usage

```python
import ast

code = """
def add(a, b):
    return a + b
"""

tree = ast.parse(code)
print(ast.dump(tree, indent=2))
```

**Output:**
```
Module(
  body=[
    FunctionDef(
      name='add',
      args=arguments(
        posonlyargs=[],
        args=[arg(arg='a'), arg(arg='b')],
        kwonlyargs=[],
        kw_defaults=[],
        defaults=[]
      ),
      body=[
        Return(
          value=BinOp(
            left=Name(id='a'),
            op=Add(),
            right=Name(id='b')
          )
        )
      ]
    )
  ]
)
```

### 3.2 NodeVisitor Pattern

```python
import ast

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.variables = []
    
    def visit_FunctionDef(self, node):
        self.functions.append({
            "name": node.name,
            "args": [arg.arg for arg in node.args.args],
            "line": node.lineno
        })
        self.generic_visit(node)  # Continue visiting child nodes
    
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.append(target.id)
        self.generic_visit(node)

code = """
def calculate(x, y):
    result = x + y
    return result
"""

tree = ast.parse(code)
analyzer = CodeAnalyzer()
analyzer.visit(tree)

print("Functions:", analyzer.functions)
print("Variables:", analyzer.variables)
```

### 3.3 Güvenlik Analizi Örneği

```python
import ast

class SecurityChecker(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
    
    def visit_Call(self, node):
        # eval() kullanımını kontrol et (RCE risk!)
        if isinstance(node.func, ast.Name):
            if node.func.id in ('eval', 'exec', '__import__'):
                self.issues.append({
                    "type": "CODE_EXECUTION",
                    "function": node.func.id,
                    "severity": "CRITICAL",
                    "line": node.lineno
                })
        
        # os.system() kullanımını kontrol et
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'system':
                self.issues.append({
                    "type": "COMMAND_INJECTION",
                    "function": "os.system",
                    "severity": "HIGH",
                    "line": node.lineno
                })
        
        self.generic_visit(node)

code = """
user_input = input("Enter code: ")
eval(user_input)  # DANGER!

import os
os.system(f"rm -rf {directory}")  # DANGER!
"""

tree = ast.parse(code)
checker = SecurityChecker()
checker.visit(tree)

for issue in checker.issues:
    print(f"[{issue['severity']}] {issue['type']} at line {issue['line']}")
```

---

## 4. JavaScript/TypeScript AST

### 4.1 @babel/parser

```javascript
const parser = require("@babel/parser");

const code = `
function add(a, b) {
  return a + b;
}
`;

const ast = parser.parse(code, {
  sourceType: 'module'
});

console.log(JSON.stringify(ast, null, 2));
```

### 4.2 AST Traversal (babel-traverse)

```javascript
const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;

const code = `
function fetchData(url) {
  fetch(url);  // Security risk: untrusted URL
}
`;

const ast = parser.parse(code);

traverse(ast, {
  CallExpression(path) {
    const callee = path.node.callee;
    if (callee.name === 'fetch') {
      console.log("SECURITY: fetch() called at line", path.node.loc.start.line);
    }
  }
});
```

### 4.3 Security Pattern: SQL Injection in SQL Tag Template

```javascript
const traverse = require("@babel/traverse").default;
const parser = require("@babel/parser");

const code = `
const query = sql\`SELECT * FROM users WHERE id = \${userId}\`;
`;

const ast = parser.parse(code, { sourceType: "module" });

traverse(ast, {
  TemplateLiteral(path) {
    // Check if it's SQL-like template
    const expressions = path.node.expressions;
    if (expressions.length > 0) {
      console.log("WARNING: Template interpolation at line", path.node.loc.start.line);
    }
  }
});
```

---

## 5. Tree-Sitter (Multi-Language)

**Tree-Sitter**, multiple dilleri destekleyen, incremental parsing yapan, hızlı AST parser'ıdır.

### Installation

```bash
# Python bindings
pip install tree-sitter

# Clone language parsers
git clone https://github.com/tree-sitter/tree-sitter-python
cd tree-sitter-python && bash script/build-wasm
```

### Usage (Python)

```python
from tree_sitter import Language, Parser

# Language yükle
PYTHON_LANGUAGE = Language("path/to/tree-sitter-python.so")
parser = Parser()
parser.set_language(PYTHON_LANGUAGE)

code = b"""
def fetch_user(user_id):
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    db.execute(query)
"""

tree = parser.parse(code)

def find_string_concatenations(node, depth=0):
    if node.type == 'binary_operation':
        left = node.child_by_field_name('left')
        right = node.child_by_field_name('right')
        operator = node.child_by_field_name('operator')
        
        if operator and operator.text == b'+':
            print(f"String concatenation at line {node.start_point[0]}")
    
    for child in node.children:
        find_string_concatenations(child, depth + 1)

find_string_concatenations(tree.root_node)
```

### Supported Languages (Tree-Sitter)
- Python
- JavaScript/TypeScript
- Go
- Ruby
- Java
- C/C++
- Rust
- PHP
- ... ve 50+ daha

---

## 6. AST Kullanım Alanları

### 6.1 Security Analysis (Güvenlik Analizi)
```python
# Vulnerable function calls detect
# SQL/Command injection patterns
# Cryptography weakness
# Authentication bypass
```

### 6.2 Code Quality
```python
# Complexity analysis
# Dead code detection
# Unused variables
# Copy-paste detection
```

### 6.3 Refactoring
```python
# Automated code transformations
# Variable renaming
# Function extraction
# Pattern replacement
```

### 6.4 Linting
```python
# ESLint, pylint, flake8 hepsi AST kullanır
# Code style violations
# Best practice checks
```

### 6.5 Type Analysis
```python
# Static type checking (MyPy, TypeScript)
# Type inference
# Type mismatch detection
```

---

## 7. Proje İçin AST Uygulaması

### Use Case: Python Dosyasında Güvenlik Açıkları Bulmak

```python
import ast
from typing import List

class SecurityVulnerabilityFinder(ast.NodeVisitor):
    def __init__(self):
        self.vulnerabilities = []
    
    def visit_Call(self, node):
        # eval(), exec() kullanımı
        if isinstance(node.func, ast.Name):
            if node.func.id in ('eval', 'exec'):
                self.vulnerabilities.append({
                    'type': 'CODE_EXECUTION',
                    'severity': 'CRITICAL',
                    'line': node.lineno,
                    'col': node.col_offset,
                    'function': node.func.id
                })
        
        # SQL concatenation pattern
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ('execute', 'executemany'):
                # Check if argument is string concatenation
                if node.args and isinstance(node.args[0], ast.BinOp):
                    if isinstance(node.args[0].op, ast.Add):
                        # Likely SQL injection
                        self.vulnerabilities.append({
                            'type': 'SQL_INJECTION',
                            'severity': 'HIGH',
                            'line': node.lineno,
                            'col': node.col_offset
                        })
        
        self.generic_visit(node)

def analyze_python_file(file_path: str) -> List[dict]:
    with open(file_path, 'r') as f:
        code = f.read()
    
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [{'error': f'Syntax error: {e}', 'line': e.lineno}]
    
    finder = SecurityVulnerabilityFinder()
    finder.visit(tree)
    
    return finder.vulnerabilities
```

### JavaScript Dosyasında XSS Bulma

```javascript
const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;

function findXSSVulnerabilities(code) {
  const ast = parser.parse(code, {
    sourceType: "module",
    plugins: ["jsx"]
  });
  
  const vulnerabilities = [];
  
  traverse(ast, {
    JSXExpressionContainer(path) {
      // Check for unescaped innerHTML assignment
      const expression = path.node.expression;
      if (expression.type === 'Identifier') {
        // Potential XSS: <div>{userInput}</div>
        vulnerabilities.push({
          type: 'XSS_RISK',
          severity: 'MEDIUM',
          line: path.node.loc.start.line,
          message: 'Potentially unescaped user input in JSX'
        });
      }
    },
    
    MemberExpression(path) {
      // Check for innerHTML assignments
      if (path.node.property.name === 'innerHTML') {
        vulnerabilities.push({
          type: 'XSS_CRITICAL',
          severity: 'HIGH',
          line: path.node.loc.start.line,
          message: 'innerHTML should not be set with user input'
        });
      }
    }
  });
  
  return vulnerabilities;
}
```

---

## 8. AST Tools Comparison

| Tool | Language | Use Case | Advantages | Disadvantages |
|------|----------|----------|------------|-----------------|
| **ast (Python)** | Python | Education, Simple analysis | Built-in, Easy to use | Python only |
| **Babel Parser** | JavaScript/TS | Web dev analysis | Modern syntax, Plugin system | Node.js required |
| **Tree-Sitter** | Multi | Production use | Fast, Incremental, Multi-lang | Steeper learning curve |
| **Roslyn (.NET)** | C# | .NET analysis | Integrated with compiler | C# specific |
| **LLVM** | LLVM IR | Low-level analysis | Powerful | Complex |

---

## 9. AST Analiz Best Practices

### 9.1 Visitor Pattern (Recommended)
```python
class MyAnalyzer(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        # Process function
        self.generic_visit(node)
    
    def visit_If(self, node):
        # Process if statement
        self.generic_visit(node)
```

### 9.2 Error Handling
```python
try:
    tree = ast.parse(code)
except SyntaxError as e:
    report_error(f"Syntax error at line {e.lineno}: {e.msg}")
except Exception as e:
    report_error(f"Parse error: {e}")
```

### 9.3 Caching
```python
# Cache AST'ler büyük codebase'ler için
import hashlib

def get_or_parse(file_path):
    cache_key = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
    if cache_key in ast_cache:
        return ast_cache[cache_key]
    
    tree = ast.parse(open(file_path).read())
    ast_cache[cache_key] = tree
    return tree
```

### 9.4 Performance Considerations
```python
# Large files için incremental parsing
if file_size > 1MB:
    # Split file into chunks
    # Parse chunks separately
    # Combine results
    pass
```

---

## 10. Proje'de AST Uygulaması

Projede şu şekilde kullanılabilir:

```python
# File: pr_review_agent/agents/logic_agent.py

from pr_review_agent.ast_analyzer import SecurityVulnerabilityFinder

class LogicAgent:
    def analyze_python_file(self, file_path, file_content):
        findings = []
        
        # AST-based security analysis
        finder = SecurityVulnerabilityFinder()
        try:
            tree = ast.parse(file_content)
            finder.visit(tree)
            findings.extend(finder.vulnerabilities)
        except SyntaxError:
            pass  # Not Python or syntax error
        
        return findings
```

---

## 11. Sonuç

AST analizi:

- **Regex'ten daha güçlü** – Semantic understanding
- **Production-ready** – Linters, formatters, Type checkers
- **Multi-language** – Tree-Sitter ile hepsi aynı şekilde analiz edilebilir
- **Hızlı** – Özellikle Tree-Sitter
- **Accurate** – False positive'ler minimum

PR code review ajanlarında AST kullanarak:
- Gerçek SQL injection'ları bulabilirsiniz (false positive az)
- XSS açıklarını semantik olarak tespit edebilirsiniz
- Code complexity'yi hassas şekilde ölçebilirsiniz
- Refactoring önerileri yapabilirsiniz

**Key Takeaway:** AST, regex ve string matching'den çok daha doğru ve tutarlı kod analizi sağlar.
