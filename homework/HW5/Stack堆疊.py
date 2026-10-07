def hanoi_iterative(n, source, target, auxiliary):
    """禁止遞迴，使用 Stack 模擬的河內塔"""
    # stack 儲存狀態：(盤子數量, 來源, 目標, 暫存, 是否已準備好移動最大盤)
    stack = [(n, source, target, auxiliary, False)]
    
    while stack:
        disk, src, tgt, aux, ready_to_move = stack.pop()
        
        if disk == 1:
            print(f"將盤子 1 從 {src} 移動到 {tgt}")
        elif not ready_to_move:
            # 由於 Stack 是後進先出 (LIFO)，我們必須將未來的動作反向推入堆疊：
            # 步驟 3: 將 n-1 盤子從 aux 移到 tgt
            stack.append((disk - 1, aux, tgt, src, False))
            # 步驟 2: 將第 n 盤子從 src 移到 tgt
            stack.append((disk, src, tgt, aux, True))
            # 步驟 1: 將 n-1 盤子從 src 移到 aux
            stack.append((disk - 1, src, aux, tgt, False))
        else:
            print(f"將盤子 {disk} 從 {src} 移動到 {tgt}")

# 測試
# hanoi_iterative(3, 'A', 'C', 'B')
