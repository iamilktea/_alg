經典演算法與函數式程式設計解答
這份文件收錄了三個經典計算機科學問題的 Python 實作，包含「河內塔問題（遞迴與非遞迴）」、「符號數學式微分（遞迴）」以及「無迴圈版本的函數式泡沫排序」。
一、 河內塔問題 (Tower of Hanoi)
河內塔可以利用遞迴（Top-down 思考）與非遞迴（利用 Stack 模擬系統呼叫堆疊）兩種方式來解決。
1. 遞迴解法
這是最直覺的解法。將  個盤子先移到暫存柱，把最底下的最大盤移到目標柱，再將  個盤子移到目標柱。
def hanoi_recursive(n, source, target, auxiliary):
    """遞迴版本的河內塔"""
    if n > 0:
        # 將 n-1 個盤子從 source 移到 auxiliary
        hanoi_recursive(n - 1, source, auxiliary, target)
        print(f"將盤子 {n} 從 {source} 移動到 {target}")
        # 將 n-1 個盤子從 auxiliary 移到 target
        hanoi_recursive(n - 1, auxiliary, target, source)

# 測試範例
# hanoi_recursive(3, 'A', 'C', 'B')


2. 禁止遞迴解法 (使用 Stack 堆疊)
我們可以使用自訂的 Stack (陣列) 來手動模擬遞迴時的系統堆疊狀態，完全避免呼叫自身的遞迴行為。
def hanoi_iterative(n, source, target, auxiliary):
    """禁止遞迴，使用 Stack 模擬的河內塔"""
    # stack 儲存狀態：(盤子數量, 來源, 目標, 暫存, 是否已準備好移動最大盤)
    stack = [(n, source, target, auxiliary, False)]
    
    while stack:
        disk, src, tgt, aux, ready_to_move = stack.pop()
        
        if disk == 1:
            print(f"將盤子 1 從 {src} 移動到 {tgt}")
        elif not ready_to_move:
            # 由於 Stack 是後進先出 (LIFO)，必須將未來的動作反向推入堆疊：
            # 步驟 3: 將 n-1 盤子從 aux 移到 tgt
            stack.append((disk - 1, aux, tgt, src, False))
            # 步驟 2: 將第 n 盤子從 src 移到 tgt
            stack.append((disk, src, tgt, aux, True))
            # 步驟 1: 將 n-1 盤子從 src 移到 aux
            stack.append((disk - 1, src, aux, tgt, False))
        else:
            print(f"將盤子 {disk} 從 {src} 移動到 {tgt}")

# 測試範例
# hanoi_iterative(3, 'A', 'C', 'B')


二、 符號數學式微分 (Symbolic Differentiation)
我們可以使用抽象語法樹 (AST) 的概念，將數學式表示為 Tuple 結構。例如 ('add', ('var', 'x'), ('num', 3)) 代表 。接著運用遞迴實作微積分的基本法則（常數法則、加法法則、乘法法則等）。
def sym_diff(expr, var='x'):
    """
    對符號表達式進行微分
    支援類型: 'num' (常數), 'var' (變數), 'add' (加), 'sub' (減), 'mul' (乘)
    """
    node_type = expr[0]
    
    # 常數的微分為 0
    if node_type == 'num':
        return ('num', 0)
    
    # 變數的微分：對目標變數微分為 1，其餘為 0
    elif node_type == 'var':
        return ('num', 1) if expr[1] == var else ('num', 0)
    
    # 加法/減法法則: (f ± g)' = f' ± g'
    elif node_type in ('add', 'sub'):
        left_diff = sym_diff(expr[1], var)
        right_diff = sym_diff(expr[2], var)
        return (node_type, left_diff, right_diff)
    
    # 乘法法則 (Product Rule): (f * g)' = f'g + fg'
    elif node_type == 'mul':
        f, g = expr[1], expr[2]
        f_prime = sym_diff(f, var)
        g_prime = sym_diff(g, var)
        # f'g
        term1 = ('mul', f_prime, g)
        # fg'
        term2 = ('mul', f, g_prime)
        return ('add', term1, term2)
    
    else:
        raise ValueError(f"未知的運算符號: {node_type}")

# --- 測試與格式化輸出 ---
# 範例函數: f(x) = (x * x) + 5  (也就是 x^2 + 5)
expression = ('add', ('mul', ('var', 'x'), ('var', 'x')), ('num', 5))
derivative = sym_diff(expression, 'x')

print("原始算式 AST:", expression)
print("微分結果 AST:", derivative)
# 輸出結果會是 ('add', ('add', ('mul', ('num', 1), ('var', 'x')), ('mul', ('var', 'x'), ('num', 1))), ('num', 0))
# 也就是 (1*x + x*1) + 0 = 2x


三、 禁止使用迴圈的「函數式泡沫排序」
要完全禁止 for 和 while 迴圈，必須依賴遞迴 (Recursion) 來實作高階函數 map、filter 與 reduce，然後利用自製的 reduce 來完成泡沫排序中的「兩兩交換過程」。
1. 自製無迴圈的 Map, Filter, Reduce
def my_map(func, lst):
    """無迴圈 map"""
    if not lst:
        return []
    return [func(lst[0])] + my_map(func, lst[1:])

def my_filter(func, lst):
    """無迴圈 filter"""
    if not lst:
        return []
    head = [lst[0]] if func(lst[0]) else []
    return head + my_filter(func, lst[1:])

def my_reduce(func, lst, initial=None):
    """無迴圈 reduce"""
    if not lst:
        return initial
    if initial is None:
        return my_reduce(func, lst[1:], lst[0])
    return my_reduce(func, lst[1:], func(initial, lst[0]))


2. 利用 Reduce 實作無迴圈的泡沫排序 (Bubble Sort)
泡沫排序的核心是一次「掃描 (Pass)」，將最大的元素像泡泡一樣推到陣列最末端。我們可以用 my_reduce 完成一次掃描，並用遞迴控制總共需要的掃描次數。
def single_bubble_pass(lst):
    """使用 reduce 完成單次泡沫掃描，將最大值推到最後面"""
    def swap_reducer(acc, curr):
        if not acc:
            return [curr]
        prev = acc[-1]
        
        # 比較當前元素與前一個元素 (累積陣列的最後一項)
        if prev > curr:
            # 發生交換：把 prev 往後擠，curr 塞前面
            return acc[:-1] + [curr, prev]
        else:
            # 順序正確：直接附加
            return acc + [curr]
            
    return my_reduce(swap_reducer, lst, [])

def bubble_sort_functional(lst, n=None):
    """
    無迴圈的泡沫排序 (純函數/遞迴風格)
    每次掃描後，陣列最後一個元素必然是最大值，因此只要遞迴排序前面未完成的部分即可。
    """
    if n is None:
        n = len(lst)
        
    # Base case: 1 個 (或 0 個) 元素不需要排序
    if n <= 1:
        return lst
        
    # 進行一次掃描
    passed = single_bubble_pass(lst)
    
    # 遞迴處理剩餘元素 (最後一項已定位)
    # 這裡可以視為把陣列分割：未完成部分 + 已排序好的最後一項
    return bubble_sort_functional(passed[:-1], n - 1) + [passed[-1]]

# --- 測試範例 ---
# unordered_list = [5, 1, 4, 2, 8]
# sorted_list = bubble_sort_functional(unordered_list)
# print("排序結果:", sorted_list)  # 輸出: [1, 2, 4, 5, 8]



