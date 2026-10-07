def hanoi_recursive(n, source, target, auxiliary):
    """遞迴版本的河內塔"""
    if n > 0:
        # 將 n-1 個盤子從 source 移到 auxiliary
        hanoi_recursive(n - 1, source, auxiliary, target)
        print(f"將盤子 {n} 從 {source} 移動到 {target}")
        # 將 n-1 個盤子從 auxiliary 移到 target
        hanoi_recursive(n - 1, auxiliary, target, source)

# 測試
# hanoi_recursive(3, 'A', 'C', 'B')
