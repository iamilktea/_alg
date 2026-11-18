# 第 11 週習題：蒙地卡羅隨機法

> **AI 使用聲明（本作業有使用 AI）**
>
> 本作業的 `main.py` 程式、程式內註解、`test_main.py` 測試程式，以及本 `README.md`，皆使用 **OpenAI ChatGPT（GPT-6）協助產生、整理與檢查**。已實際使用 Python 執行所有範例與 17 項自動測試，測試結果均通過。請在繳交前自行閱讀、理解內容，並依課程規定補充實際使用 AI 的情況。

## 一、作業目標

本專案使用 Python 完成題目要求的六項功能，**不需要安裝 NumPy、SciPy 等第三方套件**：

| 題號 | 作業要求 | Python 函數 | 測試例題 |
|---|---|---|---|
| 1 | 數值方法求單變數微分和積分 | `derivative`、`numerical_integral_1d` | \(f(x)=x^2\)，求 \(f'(2)\) 與 \(\int_0^1 x^2 dx\) |
| 2 | 蒙地卡羅法求單變數積分 | `monte_carlo_integral_1d` | \(\int_0^1 x^2 dx\) |
| 3 | 數值方法求 n 變數梯度和積分（超體積） | `gradient`、`riemann_integral_nd`、`hyperrectangle_volume` | \(\nabla(x^2+y^2+z^2)\)、二維積分、三維長方體體積 |
| 4 | 蒙地卡羅法求 n 變數積分（超體積） | `monte_carlo_integral_nd` | 三維平方和積分、三維長方體體積 |
| 5 | 用黎曼積分法寫 `integral(f, low, high)` | `integral` | 1、2、5、100 維，各維範圍 0 到 1 |
| 6 | 用蒙地卡羅法做第 5 題的 n 維積分 | `monte_carlo_integral_nd` | 1、2、5、100 維，各維範圍 0 到 1 |

題目中的 `f(x)=x12+...+xn2` 在本專案解讀為：

\[
f(x_1, x_2, \ldots, x_n) = x_1^2 + x_2^2 + \cdots + x_n^2.
\]

各維區間都是 \([0,1]\)；因此 `low=[0, 0, ..., 0]`、`high=[1, 1, ..., 1]`，陣列長度就是維度 \(n\)。

## 二、檔案結構

```text
week11_monte_carlo/
├── main.py          # 六題所有函數、每一題示範、輸出數值
├── test_main.py     # 17 項 unittest 自動化測試
├── README.md        # 原理、公式、使用說明、測試結果、AI 揭露
├── requirements.txt # 不需第三方套件
├── example_output.txt # 實際執行六題的輸出
└── test_output.txt    # 17 項自動測試的輸出
```

## 三、執行環境與操作方式

- Python 3.10 或更新版本。
- 適用 Windows 11 / Windows 10、macOS、Linux。
- 使用 Python 內建模組：`math`、`random`、`itertools`、`unittest`。

下載並解壓縮整份 ZIP。開啟終端機（Windows 可使用 PowerShell 或 CMD），切換到包含 `main.py` 的資料夾：

```bash
cd week11_monte_carlo
```

先確認版本：

```bash
python --version
```

執行全部六題：

```bash
python main.py
```

執行 17 項自動測試：

```bash
python -m unittest -v
```

Windows 如果找不到 `python`，可試用 `py --version`、`py main.py`、`py -m unittest -v`。不必執行 `pip install`。

## 四、各題數學原理與測試範例

### 第 1 題：數值方法求單變數微分與積分

**1. 中央差分法**

把微分定義近似為：

\[
f'(x) \approx \frac{f(x+h)-f(x-h)}{2h},
\]

本程式使用預設步長 \(h=10^{-5}\)。例如 \(f(x)=x^2\)，在 \(x=2\) 的真實導數是 \(2x=4\)。

```python
from main import derivative

f = lambda x: x**2
print(derivative(f, 2))  # 約 4.0
```

**2. 中點黎曼積分法**

將 \([a,b]\) 等分成 \(m\) 個小區間，寬度 \(\Delta x=(b-a)/m\)，每個區間用中點高度乘上寬度：

\[
\int_a^b f(x)\,dx \approx
\Delta x \sum_{k=0}^{m-1}f\left(a+(k+\tfrac12)\Delta x\right).
\]

```python
from main import numerical_integral_1d

print(numerical_integral_1d(lambda x: x**2, 0, 1, partitions=10_000))
# 約 0.33333333；解析解為 1/3
```

### 第 2 題：蒙地卡羅法求單變數積分

隨機產生 \(N\) 個均勻分布在 \([a,b]\) 的點 \(X_j\)，估計公式為：

\[
\int_a^b f(x)\,dx \approx (b-a)\frac1N\sum_{j=1}^{N}f(X_j).
\]

```python
from main import monte_carlo_integral_1d

result = monte_carlo_integral_1d(
    lambda x: x**2, 0, 1, samples=50_000, seed=42
)
print(result)  # 0.33300525；解析解為 0.33333333
```

隨機樣本不同，估計值會有誤差。本程式固定 `seed` 以利重現。增加 `samples` 通常可以降低估計的隨機誤差，但不保證每次結果都更接近真值；典型誤差量級約為 \(1/\sqrt{N}\)。

### 第 3 題：n 變數梯度與數值積分（超體積）

**1. 梯度**

對 \(f(x_1,\ldots,x_n)\)，梯度是由全部偏導數組成的向量：

\[
\nabla f=\left(\frac{\partial f}{\partial x_1},\ldots,\frac{\partial f}{\partial x_n}\right).
\]

對每一維固定其餘變數，再使用中央差分估計偏導：

\[
\frac{\partial f}{\partial x_i}\approx
\frac{f(\mathbf{x}+h\mathbf{e}_i)-f(\mathbf{x}-h\mathbf{e}_i)}{2h}.
\]

若 \(f(x,y,z)=x^2+y^2+z^2\)，在 \((1,2,3)\) 的梯度應是 \((2,4,6)\)。

```python
from main import gradient, sum_of_squares

print(gradient(sum_of_squares, [1, 2, 3]))
# 約 [2.0, 4.0, 6.0]
```

**2. n 維中點黎曼積分**

每個座標軸都切成 \(m\) 份，形成 \(m^n\) 個小超長方體；各小塊取中心點 \(\mathbf{c}_k\)，以「函數值乘小超體積」相加：

\[
\int_D f(\mathbf{x})\,d\mathbf{x}
\approx \frac{V}{m^n}\sum_{k_1=0}^{m-1}\cdots\sum_{k_n=0}^{m-1}
f(\mathbf{c}_{k_1,\ldots,k_n}),
\quad V=\prod_{i=1}^{n}(b_i-a_i).
\]

```python
from main import riemann_integral_nd, sum_of_squares

print(riemann_integral_nd(sum_of_squares, [0, 0], [1, 1], partitions=100))
# 0.66665000；解析解為 2/3
```

**3. 超長方體體積**

對 \(n\) 維超長方體 \(D=\prod_i[a_i,b_i]\)：

\[
\operatorname{Volume}(D)=\prod_{i=1}^{n}(b_i-a_i)=\int_D 1\,d\mathbf{x}.
\]

```python
from main import hyperrectangle_volume

print(hyperrectangle_volume([0, 0, 0], [2, 3, 4]))  # 24
```

### 第 4 題：n 變數蒙地卡羅積分（超體積）

在每個維度的範圍 \([a_i,b_i]\) 內獨立、均勻取樣，形成 \(N\) 個 n 維亂數點 \(\mathbf{X}_j\)。公式為：

\[
\int_D f(\mathbf{x})\,d\mathbf{x}\approx
V\frac1N\sum_{j=1}^{N} f(\mathbf{X}_j),
\quad V=\prod_{i=1}^{n}(b_i-a_i).
\]

```python
from main import monte_carlo_integral_nd, sum_of_squares

# 測試一：三維積分，解析解是 3/3 = 1
print(monte_carlo_integral_nd(
    sum_of_squares, [0, 0, 0], [1, 1, 1], samples=50_000, seed=42
))
# 1.00000816

# 測試二：以常數函數 1 積分求三維超體積，解析解是 2*3*4=24
print(monte_carlo_integral_nd(
    lambda p: 1.0, [0, 0, 0], [2, 3, 4], samples=50_000, seed=42
))
# 24.0
```

### 第 5 題：`integral(f, low, high)` 求 1、2、5、100 維黎曼積分

本題的函數為 \(f(\mathbf{x})=\sum_{i=1}^{n}x_i^2\)。因為每個變數在 \([0,1]\) 內，解析解為：

\[
\int_{[0,1]^n}\left(\sum_{i=1}^{n}x_i^2\right)d\mathbf{x}
=\sum_{i=1}^{n}\int_0^1 x_i^2\,dx_i
=\frac n3.
\]

`integral(f, low, high)` **會從 `low` 和 `high` 的陣列長度自動取得維度**。可以額外指定 `partitions` 以調整各維切割數。

```python
from main import integral, sum_of_squares

for n in [1, 2, 5, 100]:
    low = [0] * n
    high = [1] * n
    print(n, integral(sum_of_squares, low, high))
```

**100 維為何需要特別處理？**

普通的完整黎曼網格若每維切 100 份，在 100 維會產生 \(100^{100}=10^{200}\) 個點，根本不可能逐點計算。本專案 **沒有省略題目，也沒有把蒙地卡羅法冒充成黎曼法**：利用本題函數的「加法可分離」性質，把完整 n 維的中點黎曼和**等價地化簡**為 n 個一維中點黎曼和。

若 \(f(\mathbf{x})=C+\sum_i g_i(x_i)\)，對各維切成同樣 \(m\) 份的中點黎曼和有**精確代數恆等式**：

\[
R_m(f)=V\left[C+\sum_{i=1}^{n}\left(\frac1m\sum_{k=0}^{m-1}
g_i\left(a_i+(k+\tfrac12)\frac{b_i-a_i}{m}\right)\right)\right].
\]

這裡的「精確」指**與完整離散黎曼網格求和完全相等（不考慮浮點捨入）**，不代表它等於積分的解析真值。對本題 \(g_i(x_i)=x_i^2\)、\(C=0\)，在 \([0,1]^n\) 的中點黎曼結果可寫成：

\[
R_m= n\left(\frac13-\frac{1}{12m^2}\right).
\]

`main.py` 中的 `sum_of_squares` 明確宣告了 `additive_component` 與 `additive_constant`，讓 `integral` 確認這是**已知可加法分離的函數**，在網格過大時使用此恆等式。對普通不可分離函數，若網格超過 `MAX_GRID_POINTS=2_000_000`，程式會**明確報錯**，不會默默使用不正確的近似方法。

例如，這類一般函數可在低維時使用：

```python
from main import integral

f = lambda x: x[0] * x[1]
print(integral(f, [0, 0], [1, 1], partitions=20))
# 0.25；因為 x*y 的二維積分解析解為 1/4
```

### 第 6 題：使用蒙地卡羅法計算相同的 n 維積分

這次不必枚舉 \(m^n\) 個網格，只要從 n 維超長方體均勻隨機抽取 `samples` 個點即可，**即使 n=100，也能在合理的計算量下估計**。不過蒙地卡羅結果仍有抽樣誤差，無法保證與解析解完全相同。

```python
from main import monte_carlo_integral_nd, sum_of_squares

for n in [1, 2, 5, 100]:
    result = monte_carlo_integral_nd(
        sum_of_squares,
        [0] * n,
        [1] * n,
        samples=50_000,
        seed=2026 + n,
    )
    print(n, result)
```

## 五、實際執行結果（第 5、6 題）

以下是執行 `python main.py` 的實測結果。`m` 表示黎曼法每一維的切割數；`N` 表示蒙地卡羅的總抽樣點數：

| 維度 n | 黎曼切割 m | 黎曼積分結果 | MC 抽樣 N | 蒙地卡羅結果 | 解析解 n/3 |
|---:|---:|---:|---:|---:|---:|
| 1 | 1,000 | 0.33333325 | 50,000 | 0.33219327 | 0.33333333 |
| 2 | 100 | 0.66665000 | 50,000 | 0.66692199 | 0.66666667 |
| 5 | 10 | 1.66250000 | 50,000 | 1.66958028 | 1.66666667 |
| 100 | 100 | 33.33250000 | 50,000 | 33.32471121 | 33.33333333 |

觀察結果：

1. 低維的數值黎曼法只要切割足夠細，通常能獲得相當準確的結果；但是直接枚舉網格所需計算量是 \(m^n\)，會隨維度快速增加。
2. 100 維的黎曼結果因為這題函數可加法分離，才可以利用數學恆等式降低運算量。**不能直接推論任意 100 維函數都能這樣計算**。
3. 蒙地卡羅法的計算量約與 `samples × n` 成正比，較容易處理高維問題，但數值存在隨機誤差。
4. 解析解 `n/3` 是驗證數值答案是否合理的標準，而不是演算法直接回傳的答案。

## 六、自動測試結果

在專案資料夾執行：

```bash
python -m unittest -v
```

測試涵蓋以下 **17 項**：

1. 單變數數值微分與解析解比較。
2. 單變數黎曼積分與解析解比較。
3. 單變數蒙地卡羅積分與解析解比較（設容許誤差）。
4. 三變數梯度與解析梯度比較。
5. 二維中點黎曼積分與解析解比較。
6. 三維超長方體體積計算。
7. 三維蒙地卡羅積分與解析解比較。
8. 蒙地卡羅法對常數 1 積分求體積。
9. 1、2、5、100 維黎曼法與中點黎曼理論值比較。
10. 1、2、5、100 維蒙地卡羅與 `n/3` 比較。
11. 驗證加法可分離黎曼和與完整網格結果一致。
12. 驗證一般二維函數 `f(x,y)=xy` 仍可使用 `integral`。
13. 驗證一般 100 維函數網格過大時會明確報錯。
14. 驗證維度不符、上下界錯誤等輸入檢查。
15. 驗證錯誤微分步長、切割數、抽樣數會報錯。
16. 驗證超體積為 0 時積分為 0。
17. 驗證固定蒙地卡羅種子可以重現相同結果。

實際執行摘要：

```text
Ran 17 tests in 0.710s

OK
```

`0.710s` 是本次測試環境的實際耗時，其他電腦可能不同。由於隨機種子固定，蒙地卡羅輸出應可重現相同數值（依 Python 版本及浮點運算環境可能有極小差異）。

## 七、注意事項與結論

- 本專案使用**中央差分**求導數，使用**中點黎曼法**計算數值積分。
- 題目中的「積分（超體積）」是 n 維積分；若被積函數是 `1`，其積分就是 n 維區域本身的超體積。
- 一般的黎曼網格在高維有**維度災難**；100 維示範僅針對**已知可加法分離**的函數使用完全等價的化簡。
- 蒙地卡羅方法可用於一般高維函數，實際準確度仍與樣本數、函數變異程度有關。
- 程式有使用 AI 協助；請依課程規定如實揭露，不應將 AI 協助內容聲稱為完全獨立撰寫。

**結論：** 本作業使用數值方法與蒙地卡羅法完成單變數、多變數微分與積分，並對照解析解與自動測試，理解黎曼法在高維的計算成本，以及蒙地卡羅法在高維積分問題的實用性。
