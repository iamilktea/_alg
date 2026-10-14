# Lambda Calculus 解譯器與說明

本專案是一個用 Python 實作的 **Lambda Calculus 解譯器**。該解譯器具備完整的 **Lexer（詞法分析）**、**Parser（語法解析）** 與 **Evaluator（求值引擎）**，支援自訂名稱綁定（`let` 語法），並能**一步步印出完整的 $\beta$-歸約（$\beta$-reduction）計算過程**。

---

## 核心功能與特色

1. **語法糖支援（`let` 綁定）**：允許定義如 `let true = \x. \y. x` 等有名稱的表達式，降低閱讀難度。
2. **單步 $\beta$-歸約追蹤**：採用**正規序（Normal Order Evaluation）**，逐步印出代換細節，適合教學與除錯。
3. **自動 $\alpha$-轉換（$\alpha$-conversion）**：具備變數捕捉檢查機制，自動解決同名變數衝突問題（如重命名為 $x'$）。
4. **註解支援**：支援使用 `--` 撰寫單行註解。

---

## 系統架構與模組說明

整個解譯器分為三個主要部分：

```
[原始程式碼] ──> 1. AST & Lexer & Parser ──> 2. Substitutor & Alpha-Conv ──> 3. Evaluator ──> [逐步輸出結果]

```

### 1. 抽象語法樹 (AST, Abstract Syntax Tree)

Lambda Calculus 的世界僅由以下三種基本結構組成，我們在 Python 中定義為三個類別：

* **`Var(name)`**：變數節點，代表一個標識符（例如 $x$）。
* **`Abs(param, body)`**：抽象節点（Abstraction），代表函數定義 $\lambda \text{param}. \text{body}$。
* **`App(fn, arg)`**：應用節點（Application），代表函數呼叫 $(M \; N)$。

---

### 2. 詞法分析器 (Lexer) 與語法解析器 (Parser)

* **`tokenize(code)`**：使用正規表達式將原始字串切分為 Token 標記（如 `LAMBDA`、`DOT`、`LET`、`ID` 等），並自動過濾掉 `--` 開頭的註解。
* **`Parser`**：採用遞迴下降解析法（Recursive Descent Parser）：
* `parse_program()`：處理頂層的 `let` 宣告，建立變數環境表（Environment）。
* `parse_expr()` / `parse_app()` / `parse_atom()`：處理左結合的函數呼叫（Application）與括號優先權。



---

### 3. 求值與代換引擎 (Evaluator & Substitutor)

這是解譯器最核心的計算邏輯：

* **`free_vars(node)`**：計算目前語法樹中所有的自由變數（Free Variables）。
* **`substitute(node, target, replacement)`**：**代換演算法**。
* 當將 `replacement` 代入 `node` 時，若發現內部參數名存在於 `replacement` 的自由變數中（可能造成變數捕捉），會自動觸發 **$\alpha$-轉換**，將內部參數重新命名為 `param'`。


* **`expand_env(node, env)`**：在計算開始前，將程式中使用的 `let` 定義名稱展開替換為對應的 Lambda Term。
* **`eval_step(node)`**：執行單步的 $\beta$-歸約。採用**正規序（Normal Order，最外層優先化簡）**，若找到 $(\lambda x. M) \; N$ 形式，則將其替換為 $M[x := N]$ 並回傳 `True` 表示已發生改變。

---

## 測試與輸出範例

以下示範兩個代表性的測試案例及其執行結果：

### 測試案例一：Church Booleans 與邏輯閘 (AND)

#### 測試輸入

```python
program_1 = """
let true = \\x. \\y. x
let false = \\x. \\y. y
let and = \\p. \\q. p q false

-- 計算: AND true false
and true false
"""

run_interpreter(program_1)

```

#### 測試輸出

```text
============================================================
【原始輸入程式】
let true = \x. \y. x
let false = \x. \y. y
let and = \p. \q. p q false

-- 計算: AND true false
and true false
============================================================
【1. 名稱展開後 AST】
(((\p. (\q. ((p q) (\x. (\y. y))))) (\x. (\y. x))) (\x. (\y. y)))

【2. 開始計算過程 (β-reduction)】
Step  0: (((\p. (\q. ((p q) (\x. (\y. y))))) (\x. (\y. x))) (\x. (\y. y)))
Step  1: ((\q. (((\x. (\y. x)) q) (\x. (\y. y)))) (\x. (\y. y)))
Step  2: (((\x. (\y. x)) (\x. (\y. y))) (\x. (\y. y)))
Step  3: ((\y. (\x. (\y. y))) (\x. (\y. y)))
Step  4: (\x. (\y. y))

【3. 計算結束 (已到達 Normal Form)】
最終結果: (\x. (\y. y))

```

> **結果解析**：`(\x. (\y. y))` 正是 `FALSE` 的定義，證明 $\text{AND} \; \text{TRUE} \; \text{FALSE} \to \text{FALSE}$ 推導正確。

---

### 測試案例二：Church Numerals 自然數加法 ($1 + 2 = 3$)

#### 測試輸入

```python
program_2 = """
let zero = \\f. \\x. x
let one  = \\f. \\x. f x
let two  = \\f. \\x. f (f x)

let succ = \\n. \\f. \\x. f (n f x)
let plus = \\m. \\n. m succ n

-- 計算: 1 + 2
plus one two
"""

run_interpreter(program_2)

```

#### 測試輸出

```text
============================================================
【原始輸入程式】
let zero = \f. \x. x
let one  = \f. \x. f x
let two  = \f. \x. f (f x)

let succ = \n. \f. \x. f (n f x)
let plus = \m. \n. m succ n

-- 計算: 1 + 2
plus one two
============================================================
【1. 名稱展開後 AST】
(((\m. (\n. ((m (\n. (\f. (\x. (f (((n f) x))))))) n))) (\f. (\x. (f x)))) (\f. (\x. (f (f x)))))

【2. 開始計算過程 (β-reduction)】
Step  0: (((\m. (\n. ((m (\n. (\f. (\x. (f (((n f) x))))))) n))) (\f. (\x. (f x)))) (\f. (\x. (f (f x)))))
Step  1: ((\n. (((\f. (\x. (f x))) (\n. (\f. (\x. (f (((n f) x))))))) n)) (\f. (\x. (f (f x)))))
Step  2: (((\f. (\x. (f x))) (\n. (\f. (\x. (f (((n f) x))))))) (\f. (\x. (f (f x)))))
Step  3: ((\x. ((\n. (\f. (\x. (f (((n f) x)))))) x)) (\f. (\x. (f (f x)))))
Step  4: (\n. (\f. (\x. (f (((n f) x)))))) (\f. (\x. (f (f x))))
Step  5: (\f. (\x. (f ((((\f. (\x. (f (f x)))) f) x)))))
Step  6: (\f. (\x. (f (((\x. (f (f x))) x)))))
Step  7: (\f. (\x. (f (f (f x)))))

【3. 計算結束 (已到達 Normal Form)】
最終結果: (\f. (\x. (f (f (f x)))))

```

> **結果解析**：最終結果 `(\f. (\x. (f (f (f x)))))` 中，函數 $f$ 被連續套用了 3 次，精確代表了 Church Numeral 中的自然數 **3**。
