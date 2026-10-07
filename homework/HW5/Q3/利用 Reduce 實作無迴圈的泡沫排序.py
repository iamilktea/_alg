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
        
    # Base case: 1 個元素不需要排序
    if n <= 1:
        return lst
        
    # 進行一次掃描
    passed = single_bubble_pass(lst)
    
    # 遞迴處理剩餘元素 (最後一項已定位)
    # 這裡可以視為把陣列分割：未完成部分 + 已排序好的最後一項
    return bubble_sort_functional(passed[:-1], n - 1) + [passed[-1]]

# --- 測試 ---
# unordered_list = [5, 1, 4, 2, 8]
# sorted_list = bubble_sort_functional(unordered_list)
# print("排序結果:", sorted_list)  # [1, 2, 4, 5, 8]
