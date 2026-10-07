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
# 輸出結果會是 (x' * x + x * x') + 0 ，也就是 (1*x + x*1) + 0 = 2x
