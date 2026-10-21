def combination_recursive(n, k):
    # 邊界條件
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    
    # 遞迴呼叫
    return combination_recursive(n - 1, k - 1) + combination_recursive(n - 1, k)
