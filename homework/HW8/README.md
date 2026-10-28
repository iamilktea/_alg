# 旅行推銷員問題：五種 Python 解法

本專案使用同一組城市資料，分別實作 **改良法、爬山演算法、模擬退火法、梯度下降法、貪婪演算法**。每種方法都有自己的 Python 檔案，也能透過 `run_all.py` 一次執行並比較。

**兩個名詞約定：**「改良法」不是唯一指定的演算法名稱，本範例採用 **首次改良的 2-opt**；TSP 的變數是離散排列，因此「梯度下降」採用 **連續指派鬆弛＋投影梯度下降＋線性指派解碼**。如果課程對「改良法」另有指定，應以課程定義為準。

這五個實作都是尋找可行好解的啟發式方法，不能保證每個輸入都得到全域最佳解。專案另外附上小型資料適用的 Held–Karp 精確基準，用於評估結果，不將它混入五個方法的求解程序。

文件與範例測試日期：2026-10-28。測試環境為 Python 3.12.14、NumPy 2.3.5、SciPy 1.17.0、Matplotlib 3.10.8。

## 1. 快速執行

### 1.1 一般環境

先解壓縮完整專案，進入 `tsp_five_methods` 資料夾。建議使用 Python 3.12，並在虛擬環境安裝套件：

```bash
cd tsp_five_methods
python -m pip install -r requirements.txt
python run_all.py
```

程式會在終端顯示五種方法的路徑、距離與秒數，並在 `results` 目錄產生：

- `summary.json`：完整結果、參數、搜尋歷史、梯度法的收斂資訊。
- `summary.md`：可直接閱讀的結果比較表與路徑。
- `routes.png`：五條路徑與距離比較圖。

### 1.2 Windows 使用方式

若 Windows 已安裝 Python 3.12，可在解壓縮後的專案資料夾執行下列命令。直接使用虛擬環境內的 Python，不需要另行執行啟用腳本：

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe run_all.py
```

後續範例中的 `python`，也可以換成 `.venv\Scripts\python.exe`。所有程式與 Markdown 檔案均使用 UTF-8。

### 1.3 分別執行五種方法

每個方法檔案都可單獨啟動；請將它與 `tsp_common.py` 放在同一個資料夾：

```bash
python 01_improvement_2opt.py
python 02_hill_climbing.py
python 03_simulated_annealing.py
python 04_gradient_descent.py
python 05_greedy.py
```

單獨執行時會產生該方法的 JSON 與 PNG，例如 `results/improvement.json`、`results/improvement.png`。單獨執行不計算精確基準。

## 2. 五種方法的差異

| 編號 | 方法與檔案 | 如何產生下一個解 | 如何決定是否採用 |
| --- | --- | --- | --- |
| 1 | [改良法：01_improvement_2opt.py](01_improvement_2opt.py) | 反轉一段城市順序，即 2-opt | 找到第一個變短的鄰居就採用 |
| 2 | [爬山：02_hill_climbing.py](02_hill_climbing.py) | 交換兩個非起點城市 | 比較當輪全部鄰居，採用最佳改善 |
| 3 | [模擬退火：03_simulated_annealing.py](03_simulated_annealing.py) | 隨機產生 2-opt 鄰居 | 較好者採用；較差者依溫度與機率採用 |
| 4 | [梯度下降：04_gradient_descent.py](04_gradient_descent.py) | 更新連續城市／位置權重矩陣 | 投影梯度下降與回溯步長，再解碼成路徑 |
| 5 | [貪婪：05_greedy.py](05_greedy.py) | 在尚未完成的路線後面加一個城市 | 選擇目前最近的未拜訪城市 |

2-opt 改良法與爬山法都屬於局部改良。本教材為了讓兩者容易比較，刻意採用不同的鄰域及選擇規則。不能將兩個檔名當成完全互斥的理論分類。[1][2]

## 3. 問題定義與共用資料

### 3.1 要解決什麼問題？

給定多個城市，從某城市出發，每個城市恰好拜訪一次，最後回到起點，並讓總距離盡量短。

假設路徑為城市編號的排列：

$$
\pi=(\pi_0,\pi_1,\ldots,\pi_{n-1}),\qquad \pi_0=0.
$$

目標函數為：

$$
L(\pi)=\sum_{k=0}^{n-1}D_{\pi_k,\pi_{(k+1)\bmod n}}.
$$

這個寫法已經包含最後一個城市回到起點的距離。由於此處是封閉巡迴，固定城市 0 為起點只是固定路徑的表示方式。

### 3.2 本專案的假設

- 使用平面座標與歐氏距離：$D_{ij}=\sqrt{(x_i-x_j)^2+(y_i-y_j)^2}$。
- 距離矩陣對稱、有限、非負，對角線為零。
- 任意兩個城市都能直接移動，沒有道路方向、交通時間、容量或時間窗限制。
- 允許不同城市有相同座標；城市名稱必須唯一。
- 座標與距離是示範用的相對單位，並非真實城市經緯度或實際道路里程。

這些假設尤其影響 2-opt 的增量公式；不能直接將目前程式改成非對稱道路距離後，仍沿用同一公式。

### 3.3 內建 12 個城市

| 城市 | x | y | 城市 | x | y |
| --- | ---: | ---: | --- | ---: | ---: |
| A | 8 | 12 | G | 58 | 36 |
| B | 18 | 43 | H | 66 | 6 |
| C | 25 | 8 | I | 72 | 52 |
| D | 33 | 28 | J | 81 | 24 |
| E | 42 | 48 | K | 90 | 41 |
| F | 51 | 13 | L | 95 | 9 |

資料也放在 [cities.json](cities.json)。未指定 `--cities` 時使用 `tsp_common.py` 內的同一份範例常數；若修改 `cities.json`，請用 `--cities cities.json` 明確載入修改後的內容。

## 4. 檔案用途

| 檔案 | 用途 |
| --- | --- |
| `01_improvement_2opt.py`～`05_greedy.py` | 五種方法的獨立實作及命令列入口 |
| `tsp_common.py` | 距離矩陣、路徑計分、資料檢查、繪圖、共同命令列介面、精確基準 |
| `run_all.py` | 統一執行五種方法、比較結果並輸出報告 |
| `cities.json` | 可修改的範例城市資料 |
| `requirements.txt` | 本次測試使用的套件版本 |
| `tests/test_algorithms.py` | 正確性、邊界條件與梯度驗證測試 |
| `results/summary.json` | 附贈的實際執行結果，包含完整搜尋資訊 |
| `results/summary.md` | 附贈的 Markdown 結果表 |
| `results/routes.png` | 附贈的路徑比較圖 |

## 5. 方法一：改良法（首次改良 2-opt）

### 5.1 原理

先建立完整的隨機路徑，再反覆嘗試拆掉兩條邊，反轉它們之間的城市順序，重新接成一個巡迴。2-opt 是經典的路徑局部改良操作，可參考 Croes 的原始研究。[1]

例如將 `A → B → C → D → E → A` 中的 `B → C → D` 反轉，得到 `A → D → C → B → E → A`。只有新路徑比較短，才接受這次修改。

### 5.2 本程式流程

1. 固定起點為城市 0，其餘城市依 `seed` 隨機排列。
2. 依序枚舉兩個位置 `i`、`j`。
3. 計算反轉 `route[i:j+1]` 的距離差。
4. 找到第一個嚴格改善的候選，立即接受，重新開始掃描。
5. 完整掃描仍無改善，或接受改善次數達到上限時停止。

令被拆掉的兩條邊為 $(a,b)$、$(c,d)$，對稱距離下，候選的距離差為：

$$
\Delta=D_{a,c}+D_{b,d}-D_{a,b}-D_{c,d}.
$$

內部路段反向後距離不變，因此可用 $O(1)$ 計算每個候選的增量。程式在真正接受前，仍會重新計算完整路長，減少累積數值誤差。

核心操作：

```python
candidate = route.copy()
candidate[i:j + 1] = reversed(candidate[i:j + 1])
candidate_distance = route_length(candidate, distances)
if candidate_distance < distance - tolerance:
    route, distance = candidate, candidate_distance
```

預設 `max_iterations=1000`、`tolerance=1e-12`。此處的 `max_iterations` 計算接受的改善次數，而非比較過的全部鄰居數量。

### 5.3 限制

停止原因為 `local_optimum` 時，表示在設定容忍值下，沒有可改善的 2-opt 鄰居。這不代表全域最佳。若停止原因為 `iteration_limit`，則尚未證明已經掃描到局部最佳。

## 6. 方法二：爬山演算法

### 6.1 原理

爬山搜尋每輪挑選最好的鄰居，若無法再改善就停止；AIMA 的原作者偽程式描述了這個規則。[2] TSP 是最小化距離，可把評分設為 `-distance`，因此「爬得更高」代表路徑更短。

本實作的鄰居由**交換兩個非起點城市**產生。例如交換 `A → B → C → D → E → A` 中的 B 與 D，得到 `A → D → C → B → E → A`。較長路徑上，交換兩城與反轉整段通常會產生不同的結果。

### 6.2 本程式流程

1. 使用與方法一相同的隨機初始路徑。
2. 列舉所有兩城交換的鄰居。
3. 對每個鄰居計算完整巡迴距離。
4. 找出當輪最短的候選；只有比目前路徑短才採用。
5. 無嚴格改善，或接受改善次數達到上限時停止。

核心操作：

```python
candidate = route.copy()
candidate[i], candidate[j] = candidate[j], candidate[i]
candidate_distance = route_length(candidate, distances)
if candidate_distance < best_distance - tolerance:
    best_route = candidate
    best_distance = candidate_distance
```

預設 `max_iterations=1000`、`tolerance=1e-12`。這個版本只使用一個起始路徑，沒有額外的隨機重啟。

### 6.3 與方法一的實際差異

| 比較項目 | 改良法 | 爬山法 |
| --- | --- | --- |
| 鄰居 | 反轉一段路徑 | 交換兩個城市 |
| 採用時機 | 找到第一個改善就採用 | 比較當輪全部候選後採用最佳改善 |
| 每輪候選計分 | 邊增量計算，接受時重算 | 每個候選都完整重算 |
| `local_optimum` 停止時的局部性 | 對 2-opt 鄰域局部最佳 | 對兩城交換鄰域局部最佳 |

表中的局部最佳均以設定容忍值為準；若停止原因為 `iteration_limit`，則沒有此保證。

不同鄰域會造成不同的局部最佳點；本次範例中爬山法結果比較長，正好展示這個現象。

## 7. 方法三：模擬退火法

### 7.1 原理與接受規則

模擬退火允許搜尋過程暫時接受比較差的解，降低被局部最佳點困住的機會；其溫度與 Metropolis 接受機率的關係，可參考 Kirkpatrick、Gelatt 與 Vecchi 的原始論文。[3]

令新路徑與目前路徑的距離差為 $\Delta=L_{new}-L_{current}$：

$$
P(\text{accept})=
\begin{cases}
1,&\Delta\leq 0,\\
\exp(-\Delta/T),&\Delta>0.
\end{cases}
$$

例如路徑變長 5 個單位，溫度為 10 時，接受機率約為 $e^{-0.5}=0.6065$；溫度降到 1 時，接受機率約為 $e^{-5}=0.0067$。降溫後會越來越不願意接受較差的路徑。

### 7.2 本程式流程

1. 使用與前兩個方法相同的隨機初始路徑。
2. 隨機選擇一個區段，反轉成 2-opt 候選路徑。
3. 套用接受規則，更新目前路徑。
4. 若目前路徑比歷來最佳還短，另外保存最佳路徑。
5. 按預先設定的幾何排程降溫，直到候選次數用完。
6. 回傳整個搜尋過程找到的最佳路徑。

核心操作：

```python
delta = candidate_distance - current_distance
if delta <= 0 or rng.random() < math.exp(-delta / temperature):
    route = candidate
    current_distance = candidate_distance
    if current_distance < best_distance:
        best_route = route.copy()
        best_distance = current_distance
```

### 7.3 預設參數

| 參數 | 預設 | 說明 |
| --- | --- | --- |
| `iterations` | 30000 | 隨機候選的次數 |
| `initial_temperature` | 所有正距離的中位數 | 讓溫度跟隨資料的距離尺度 |
| `final_temperature` | 起始溫度 × 0.0001 | 結束時的目標溫度 |

若候選次數為 $S>1$，第 $k$ 次候選（$k=0,\ldots,S-1$）使用：

$$
T_k=T_0\left(\frac{T_f}{T_0}\right)^{k/(S-1)}.
$$

程式使用對數形式計算此排程。`S=1` 時使用起始溫度；若城市數不超過 3，對稱 TSP 的所有可行巡迴等長，直接回傳即可。全部距離為零時，預設起溫使用 1，避免不存在正距離的情況。

### 7.4 為什麼保存歷來最佳？

退火可能在最後幾步接受較差解。此次範例的歷來最佳距離是 `267.1674908825172`，最後停留位置的距離卻是 `267.34064190392434`。程式正確回傳前者；兩者可分別從 `distance` 與 `metadata.final_distance` 查看。

## 8. 方法四：梯度下降法

### 8.1 為什麼需要轉換問題？

城市路徑像 `[0, 3, 1, 2]`，是一個離散排列。城市編號的數值沒有可微的距離意義，因此不能直接對城市編號做 `route -= learning_rate * gradient`。

本實作建立連續的「城市／位置」矩陣，再對一個可微代理目標做投影梯度下降。最後解碼成城市排列。投影梯度法的一般背景可參考 Parikh 與 Boyd；下述 TSP 懲罰模型及參數，是本教材採用的具體設計，並非宣稱該文提供了這套 TSP 演算法。[4]

### 8.2 連續指派矩陣

令 $P_{i,k}$ 代表「城市 $i$ 放在巡迴第 $k$ 個位置」的連續權重。理想的離散情況是：

- 每個元素為 0 或 1。
- 每個城市對應的橫列和為 1：每城只使用一次。
- 每個位置對應的直欄和為 1：每個位置只放一城。

此時 $P$ 是排列矩陣。例如路徑 `[0, 2, 1]` 對應：

$$
P=\begin{bmatrix}1&0&0\\0&0&1\\0&1&0\end{bmatrix}.
$$

實際下降過程允許 $0\leq P_{i,k}\leq1$。固定 $P_{0,0}=1$，並將第 0 橫列與第 0 直欄其餘元素固定為零，代表城市 0 固定在起點。其餘橫列與直欄的和由懲罰項鼓勵接近 1，並非始終精確等於 1，所以不應將所有元素直接解讀為已正規化的機率。

### 8.3 可微的目標函數

先正規化距離：$\widehat D=D/s$，其中 $s=\max D$；全部距離為零時令 $s=1$。令 $p_k=P[:,k]$ 為第 $k$ 欄：

$$
F(P)=
\underbrace{\sum_{k=0}^{n-1}p_k^T\widehat D p_{(k+1)\bmod n}}_{\text{連續路徑成本}}
+\underbrace{\frac{\lambda}{2}\left(\lVert P\mathbf1-\mathbf1\rVert_2^2+\lVert P^T\mathbf1-\mathbf1\rVert_2^2\right)}_{\text{城市與位置唯一性的懲罰}}
+\underbrace{\mu\sum_{i,k}P_{i,k}(1-P_{i,k})}_{\text{鼓勵接近 0 或 1}}.
$$

當 $P$ 確實是排列矩陣時，兩個懲罰項都是零，第一項剛好是該巡迴的距離除以 $s$。在連續過程中，目標值包含懲罰項，不能拿它直接當成真正的巡迴距離。

### 8.4 解析梯度與更新

令 $r=P\mathbf1-\mathbf1$、$c=P^T\mathbf1-\mathbf1$。令 $P_{next}$ 的第 $k$ 欄為 $p_{k+1}$，$P_{prev}$ 的第 $k$ 欄為 $p_{k-1}$，索引都以模 $n$ 計算：

$$
\nabla F(P)=\widehat D P_{next}+\widehat D^T P_{prev}
+\lambda(r\mathbf1^T+\mathbf1c^T)+\mu(1-2P).
$$

程式對應的核心運算為：

```python
next_p = np.roll(p, -1, axis=1)
previous_p = np.roll(p, 1, axis=1)
row_error = p.sum(axis=1) - 1.0
col_error = p.sum(axis=0) - 1.0
grad = normalized_distance @ next_p + normalized_distance.T @ previous_p
grad += constraint_penalty * (row_error[:, None] + col_error[None, :])
grad += binary_penalty * (1.0 - 2.0 * p)
```

接著執行：

$$
Q=\operatorname{Proj}_{\mathcal C}(P-\eta\nabla F(P)).
$$

$\mathcal C$ 是元素介於 0 與 1、且起點相關元素固定的集合。投影實作為 `np.clip`，再恢復固定的第 0 橫列／直欄。

步長使用 Armijo 回溯：若

$$
F(Q)\leq F(P)+10^{-4}\langle\nabla F(P),Q-P\rangle
$$

不成立，就將步長減半後再試。每次最多嘗試 60 個步長；若仍失敗，停止該次重新初始化並記錄原因。接受後，下次嘗試步長可乘 1.5，但不超過設定的 `learning_rate`。

### 8.5 解碼：確保不漏城、不重複

連續矩陣不一定是排列矩陣。對每欄各取一次最大值，可能重複選到同一個城市，因此不能直接當作合法巡迴。

程式以 `scipy.optimize.linear_sum_assignment(-P[1:, 1:])` 求出城市與位置的一對一指派，再加回起點 0。[5]

```python
city_indices, positions = linear_sum_assignment(-p[1:, 1:])
route = np.empty(len(p), dtype=int)
route[0] = 0
route[positions + 1] = city_indices + 1
```

這一步最大化被選中的連續權重，也等價於在 Frobenius 距離下尋找最接近的排列矩陣。它解決的是指派問題，不是直接求得最佳 TSP 路徑。SciPy 的實作採用修改版 Jonker–Volgenant 演算法，所以本文件稱它為「線性指派解碼」。[5]

### 8.6 初始化、預設參數與回傳值

每次初始化都先產生隨機正值矩陣，交替對橫列與直欄正規化 20 次，讓起始權重比較接近指派限制。這只是建立初始點；後續更新仍是梯度下降，沒有使用其他 TSP 方法先找出路徑，也沒有在解碼後追加 2-opt 改良。

| 參數 | 預設 | 意義 |
| --- | ---: | --- |
| `restarts` | 8 | 隨機連續初始化的次數 |
| `max_iterations` | 1200 | 每次初始化最多更新次數 |
| `constraint_penalty` | 20.0 | 橫列與直欄和偏離 1 的懲罰係數 $\lambda$ |
| `binary_penalty` | 0.25 | 鼓勵接近 0／1 的係數 $\mu$ |
| `learning_rate` | 0.25 | 回溯步長的上限 |
| `tolerance` | 0.000001 | 投影梯度映射殘差的停止容忍值 |
| `decode_every` | 20 | 每隔幾次更新解碼一次；起始與最後也會解碼 |

結果中兩種歷史紀錄各有不同含義：

| 欄位 | 意義 |
| --- | --- |
| `history` | 每次解碼後，截至目前最短的合法巡迴距離 |
| `metadata.objective_traces` | 各次初始化的連續目標值；於起始、每隔 `decode_every` 次更新與結束時取樣 |
| `metadata.best_source` | 最佳離散路徑出現的初始化編號與迭代次數 |
| `metadata.runs` | 每次初始化的迭代數、停止原因、投影梯度殘差及橫列／直欄和誤差 |
| `metadata.converged` | 是否每次初始化都達到投影梯度的停止容忍值 |

### 8.7 必須正確解讀的限制

這個目標函數非凸，而且唯一性限制使用有限懲罰。即使目標值持續下降，也不代表每次解碼路徑都會變短；程式因此另行保存歷來最短的解碼結果。

`converged=True` 僅代表連續盒狀限制問題的投影梯度映射殘差小於容忍值。它不證明連續問題達到全域最小，更不證明離散 TSP 達到全域最佳。凸優化教材中的全域保證，不能直接套用到這個非凸模型。[4]

這個方法適合展示「如何用梯度法處理離散問題的鬆弛形式」。若單純追求此類小型 TSP 的求解效率，從本次結果看，2-opt 的程式更直接、運算也更少。

## 9. 方法五：貪婪演算法

### 9.1 原理

從起點出發，每一步只選擇目前距離最近、尚未拜訪的城市，直到所有城市都被加入路線，最後回到起點。這是最近鄰貪婪法；NetworkX 官方文件也描述了相同的建構規則與其未必最優的限制。[6]

### 9.2 本程式流程

1. 路徑先放入城市 0。
2. 建立尚未拜訪的城市集合。
3. 從集合中找出離目前城市最近的城市。
4. 將它加入路徑、移出集合。
5. 集合為空後計算包含回程的完整距離。

核心操作：

```python
next_city = min(unvisited, key=lambda city: (distances[current, city], city))
route.append(next_city)
unvisited.remove(next_city)
```

距離相同時選擇城市編號較小者，因此結果穩定。此方法不使用隨機數；`seed` 只是為了維持五種方法相同的呼叫介面。

### 9.3 限制

每次選擇眼前最近的城市，可能把很長的連接留到最後，尤其是回到起點的邊。本範例固定從城市 A 開始，不額外嘗試每個可能起點，也不追加其他改良法。

## 10. 同一資料集的實際結果

以下為內建 12 個城市、`seed=42`、各方法預設參數的實測。前三種方法的共同初始距離為 **560.624824**。Held–Karp 精確基準的最短距離為 **267.167491**，此值以目前浮點距離矩陣計算。

| 方法 | 實際巡迴距離 | 與精確解的差距 | 此次觀察 |
| --- | ---: | ---: | --- |
| 改良法（2-opt） | 267.167491 | 0.0000% | 16 次改善後，找到與精確基準相同的距離 |
| 爬山演算法 | 310.803289 | 16.3328% | 7 次改善後停在兩城交換的局部最佳 |
| 模擬退火法 | 267.167491 | 0.0000% | 30000 個候選中找到與精確基準相同的距離 |
| 梯度下降法 | 267.475253 | 0.1152% | 最佳解出現在第 5 次初始化、第 440 次更新後 |
| 貪婪演算法 | 275.561728 | 3.1419% | 快速建構完成，沒有後續局部改良 |

差距計算：$100\times(L-L^*)/L^*$。程式將浮點誤差造成的微小負差距截為零；全零距離案例的差距定義為零。

### 10.1 各方法路徑

- **改良法**：A → C → F → H → L → J → K → I → G → E → B → D → A。
- **爬山法**：A → I → K → J → L → H → F → G → E → B → D → C → A。
- **模擬退火**：A → D → B → E → G → I → K → J → L → H → F → C → A。
- **梯度下降**：A → C → F → H → L → J → K → I → G → E → D → B → A。
- **貪婪法**：A → C → D → B → E → G → I → K → J → L → H → F → A。

改良法與退火法的巡迴方向相反，但在對稱距離下它們是同一組巡迴邊，因此總距離相同。

![五種方法的巡迴路徑與距離](results/routes.png)

圖中的紅色星號標示起點 A，長條圖的紅色虛線標示精確基準。圖名使用英文，以降低作業系統缺少中文字型造成的顯示問題。

### 10.2 如何公平解讀？

這個比較使用相同資料、相同距離函數與固定種子。方法一至三從同一路徑開始；貪婪法本來就是從空路徑建構，梯度法則從連續矩陣開始。各方法的運算預算不同，梯度法還包含 8 次初始化，因此此表是教學示範，不能當成所有資料或同時間預算下的普遍排名。

`summary.json` 與 `summary.md` 保留一次實測的秒數。計時只包含 `solve()`，不包含載入模組、讀檔、建立距離矩陣、精確基準或繪圖。極短的毫秒級測量容易受系統排程影響；不應從單次結果判定兩個很快的方法誰永遠比較快。

固定種子便於重現，但不同 Python、套件版本、浮點運算環境或接近同分的候選，仍可能產生不同路徑。以距離、合法性及多次實驗一起比較會更可靠。

## 11. 修改資料、種子與輸出

### 11.1 自訂城市

建立 UTF-8 的 `my_cities.json`：

```json
[
  {"name": "A", "x": 0, "y": 0},
  {"name": "B", "x": 0, "y": 10},
  {"name": "C", "x": 10, "y": 10},
  {"name": "D", "x": 10, "y": 0}
]
```

這個正方形的最短封閉巡迴距離為 40。執行方式：

```bash
python run_all.py --cities my_cities.json --seed 42 --output my_results
python 03_simulated_annealing.py --cities my_cities.json --seed 7 --output sa_results
```

第一個城市固定作為起點。空資料、重複名稱、NaN 與無限大座標會被拒絕。座標單位應一致；若輸入真實經緯度，必須另行建立適當的地理距離，不能直接套用此平面範例。

### 11.2 其他命令列選項

```bash
# 固定不同亂數種子；seed 必須是非負整數。
python run_all.py --seed 7

# 只輸出文字與 JSON，不繪圖。
python run_all.py --no-plot

# 停用精確基準。
python run_all.py --exact-limit 0

# 只在城市數不超過 12 時計算精確基準。
python run_all.py --exact-limit 12

# 顯示選項。
python run_all.py --help
python 04_gradient_descent.py --help
```

`--exact-limit` 預設為 15，上限為 16；超過設定城市數時自動略過精確基準，仍執行五種方法。所有命令會更新指定輸出目錄內同名結果檔；若要保留不同實驗，請各自指定不同 `--output`。

## 12. 在其他 Python 程式中使用

因為五個方法的檔名以數字開頭，本專案提供 `load_solver()`，避免直接寫不合法的 `import 01_improvement_2opt`。

在專案目錄建立並執行下列程式：

```python
from tsp_common import load_cities, distance_matrix, load_solver

cities = load_cities("cities.json")
d = distance_matrix(cities)

solve = load_solver("simulated_annealing")
result = solve(
    d,
    seed=42,
    iterations=50000,
    initial_temperature=50.0,
    final_temperature=0.01,
)

route = result["route"]
closed_route = route + [route[0]]
print(" → ".join(cities[i]["name"] for i in closed_route))
print("總距離：", result["distance"])
```

可用的識別名稱：`improvement`、`hill_climbing`、`simulated_annealing`、`gradient_descent`、`greedy`。

梯度法調整參數的範例：

```python
solve = load_solver("gradient_descent")
result = solve(d, seed=42, restarts=12, max_iterations=1600,
               constraint_penalty=20.0, binary_penalty=0.25,
               learning_rate=0.25, decode_every=20)
```

命令列只提供共同選項；方法特有參數透過上述 Python 函式參數設定，或修改各方法 `solve()` 的預設值。

### 12.1 共用回傳格式

```python
{
    "route": [0, 2, 1],  # 這裡只是三城格式示例，尾端不重複起點
    "distance": ...,     # 含最後回到起點的距離
    "history": [...],    # 完整有效巡迴的距離紀錄
    "metadata": {...},   # 各方法的參數、次數、停止原因等
}
```

前三種方法的 `history` 只新增改善後的完整距離；梯度法每次解碼記錄歷來最佳；貪婪法只存最後完整巡迴。這些歷史陣列的索引意義不同，不能直接把同一索引當成相同的工作量。

命令列包裝另外加入 `closed_route`、`route_names`、`elapsed_seconds` 等欄位。`closed_route` 才會在尾端重複加入起點。

### 12.2 調整參數的取捨

- **2-opt／爬山**：若停止原因是 `iteration_limit`，增加上限才有機會繼續改善；若已是 `local_optimum`，單純增加上限不會改變結果，需換起始種子或鄰域。
- **退火**：增加候選次數可讓降溫更緩慢；溫度太低會很快失去探索能力，太高則容易接近隨機遊走。增加次數不保證單次結果一定更好。
- **梯度**：增加初始化次數會增加探索機會與運算時間；懲罰太小可能造成較大的指派限制誤差，太大則可能壓過距離目標、使可用步長變小。應同時檢查實際距離與 `metadata.runs`。
- **貪婪**：本版本只有固定起點的最近鄰規則，沒有迭代參數。

## 13. 時間與記憶體成本

以下按目前程式實作估算，不將所有演算法籠統視為相同成本。令 $n$ 為城市數、$I$ 為局部搜尋輪數、$S$ 為退火候選數、$R$ 為梯度初始化次數、$G$ 為每次梯度更新數、$B$ 為每次更新的回溯評估次數。

| 方法 | 主要時間成本 | 原因 |
| --- | --- | --- |
| 建立共用距離矩陣 | $O(n^2)$ | 計算所有城市對的距離 |
| 改良法 2-opt | 通常以 $O(I n^2)$ 估算 | 每輪掃描 $O(n^2)$ 個邊增量；接受後才複製、反轉與重算路長 |
| 爬山法 | $O(I n^3)$ | $O(n^2)$ 個交換候選，各自以 $O(n)$ 計算完整路長 |
| 模擬退火 | $O(Sn)$ | 每次建立候選、反轉與重算路長 |
| 梯度法 | 稠密運算約 $O(RGBn^3)$，另含解碼 | 每個目標／梯度評估含矩陣乘法；定期進行線性指派 |
| 貪婪法 | $O(n^2)$ | 每步掃描尚未拜訪的城市 |
| Held–Karp 精確基準 | $O(n^2 2^n)$ | 以城市子集合與最後城市作為動態規劃狀態 |

2-opt 的上述估算以邊增量與完整重算在數值精度內一致為前提；程式遇到通過增量檢查卻未通過完整距離檢查的極小浮點差時，可能有額外重算。所有方法共用的距離矩陣需要 $O(n^2)$ 記憶體；梯度法也使用 $O(n^2)$ 的連續矩陣。另有搜尋歷史的儲存成本。精確基準額外需要 $O(n2^n)$ 狀態與回溯資訊，這也是設定小型城市數上限的原因。

Held–Karp 的基本遞迴是：從起點出發，恰好拜訪集合 $S$ 並停在城市 $j$ 的最小成本，等於所有可能前一城市 $k$ 的成本加上 $D_{k,j}$ 的最小值；最後再加回起點的邊。[7] 精確基準只用來檢查結果，沒有回饋到五種方法內。

## 14. 正確性驗證

執行：

```bash
python -m unittest discover -s tests -v
```

本次 **14 項測試全部通過**。重點包含：

- 五種方法的結果都是從城市 0 開始的合法排列，各城市恰好出現一次。
- 獨立逐邊重算路長，確認包含最後回到起點的邊。
- 一城、兩城、全零距離與正方形案例。
- 固定種子可重現路徑與搜尋歷史。
- 前三種方法使用同一初始路徑，且回傳結果不比初始解差。
- 枚舉停止後的鄰域，確認 2-opt 與爬山法的局部停止條件。
- 退火確實接受較差移動，也確實保留歷來最佳解。
- 六城精確基準與獨立全排列枚舉結果一致。
- 梯度公式與中央有限差分相符，且每次初始化的取樣代理目標不增加。
- 拒絕不合法的距離矩陣與演算法參數。

自動測試對退火與梯度法使用較小的運算預算，以快速檢查正確性；它們沒有假設所有啟發式都必須找到全域最短路徑。前述結果表則來自完整預設參數的實際執行。

## 15. 常見問題

**為什麼有些方法沒有找出最短路徑？** 這些方法是啟發式。局部搜尋會受鄰域及起點影響；退火受種子、溫度及次數影響；梯度法還有鬆弛與解碼誤差。有效路徑與全域最佳是兩個不同的要求。

**「收斂」等於求到精確解嗎？** 不等於。局部搜尋僅在 `stop_reason="local_optimum"` 時，表示設定鄰域與容忍值下沒有嚴格改善；若因 `iteration_limit` 停止則無此保證。梯度法的停止條件只檢查連續模型的一階殘差。只有與精確基準比較後，才能對此小型範例確認距離是否一致。

**修改 `cities.json` 為什麼沒有影響？** 請使用 `--cities cities.json`。省略參數時，程式讀取內建範例常數。

**只想看數值，不想產生圖片？** 加上 `--no-plot`；仍建議依 `requirements.txt` 安裝完整套件，因為梯度法需要 SciPy。

**圖中的中文城市名稱顯示方框？** 示範城市使用 A～L，內建圖名使用英文。若自訂中文名稱，需在 `plot_routes()` 設定系統已安裝的中文字型，例如 Windows 的 Microsoft JhengHei。

**能直接輸入距離矩陣嗎？** 五個 `solve()` 都接受 NumPy 距離矩陣，經 `load_solver()` 呼叫即可；命令列入口目前接受座標 JSON。此教材的矩陣必須符合對稱、非負、有限、對角為零的條件。

## 16. 參考資料

以下資料用於演算法概念與 API 核對。範例資料、Python 實作、懲罰模型的具體設計及實測結果以本專案檔案為準；參考資料不代表為本次啟發式結果提供全域最佳保證。

1. Croes, G. A. (1958). *A Method for Solving Traveling-Salesman Problems*. Operations Research, 6(6), 791–812. [論文 DOI](https://doi.org/10.1287/opre.6.6.791)。
2. AIMA 原作者程式庫。*Hill-Climbing pseudocode*. [原始偽程式](https://github.com/aimacode/aima-pseudocode/blob/master/md/Hill-Climbing.md)。
3. Kirkpatrick, S., Gelatt, C. D., Jr., & Vecchi, M. P. (1983). *Optimization by Simulated Annealing*. Science, 220(4598), 671–680. [論文 DOI](https://doi.org/10.1126/science.220.4598.671)、[原始論文 PDF](https://mk.bcgsc.ca/papers/kirkpatrick-simulatedannealing.pdf)。
4. Parikh, N., & Boyd, S. *Proximal Algorithms*, 第 4.2 節，投影梯度法與近端梯度法的關係。[作者提供的 PDF](https://web.stanford.edu/~boyd/papers/pdf/prox_algs.pdf)。
5. SciPy 官方文件。*scipy.optimize.linear_sum_assignment*. [API 說明](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html)。
6. NetworkX 官方文件。*greedy_tsp*. [最近鄰建構規則與限制](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.approximation.traveling_salesman.greedy_tsp.html)。本程式自行實作，沒有依賴 NetworkX。
7. Held, M., & Karp, R. M. (1962). *A Dynamic Programming Approach to Sequencing Problems*. Journal of the Society for Industrial and Applied Mathematics, 10(1), 196–210. [論文 DOI](https://doi.org/10.1137/0110015)。


