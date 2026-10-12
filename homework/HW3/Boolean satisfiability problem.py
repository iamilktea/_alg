import itertools

def solve_sat_by_truth_table(variables, formula_func):
    """
    使用真值表窮舉法解決 SAT 問題
    :param variables: 變數名稱列表，例如 ['A', 'B', 'C']
    :param formula_func: 接受變數字典並回傳布林值的邏輯函式
    """
    n = len(variables)
    satisfiable = False
    solutions = []

    print(f"正在分析 {n} 個變數的所有真值表組合 (共 {2**n} 種可能)...\n")
    print("-" * 45)
    
    # 印出真值表表頭 (將 True/False 簡化為 1/0 方便閱讀)
    header = " | ".join(f"{v:>5}" for v in variables) + " | 結果"
    print(header)
    print("-" * len(header))

    # 使用 itertools.product 生成所有 True/False 的笛卡兒積組合
    for values in itertools.product([False, True], repeat=n):
        # 建立變數與布林值的對應字典
        assignment = dict(zip(variables, values))
        
        # 評估邏輯公式
        result = formula_func(assignment)
        
        # 格式化輸出每一列的 1/0
        row_str = " | ".join(f"{str(int(v)):>5}" for v in values) + f" | {int(result)}"
        print(row_str)

        if result:
            satisfiable = True
            solutions.append(assignment)

    print("-" * 45)
    if satisfiable:
        print("\n【結果】本問題具有可滿足性 (SAT)")
        print("所有滿足條件的變數指派 (Models)：")
        for idx, sol in enumerate(solutions, 1):
            formatted_sol = ", ".join(f"{k}={v}" for k, v in sol.items())
            print(f"  解 {idx}: {{{formatted_sol}}}")
    else:
        print("\n【結果】本問題不可滿足 (UNSAT)")

    return satisfiable, solutions

# === 範例測試 ===
if __name__ == "__main__":
    # 1. 定義變數
    vars_list = ['A', 'B', 'C']
    
    # 2. 定義邏輯公式: (A or B) and (not A or C)
    def my_formula(assign):
        A = assign['A']
        B = assign['B']
        C = assign['C']
        return (A or B) and (not A or C)

    print("正在求解邏輯公式: (A or B) and (not A or C)\n")
    solve_sat_by_truth_table(vars_list, my_formula)
