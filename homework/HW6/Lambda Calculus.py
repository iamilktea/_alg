import re

# ==========================================
# 1. AST (抽象語法樹節點)
# ==========================================
class Var:
    """變數：x"""
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name

class Abs:
    """抽象：\x. M"""
    def __init__(self, param, body):
        self.param = param
        self.body = body
    def __repr__(self):
        return f"(\\{self.param}. {self.body})"

class App:
    """應用：M N"""
    def __init__(self, fn, arg):
        self.fn = fn
        self.arg = arg
    def __repr__(self):
        return f"({self.fn} {self.arg})"


# ==========================================
# 2. Lexer (詞法分析) & Parser (語法解析)
# ==========================================
def tokenize(code):
    # 將註解過濾掉
    code = re.sub(r'--.*', '', code)
    token_spec = [
        ('LAMBDA', r'\\|λ'),
        ('DOT',    r'\.'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('ASSIGN', r'='),
        ('LET',    r'\blet\b'),
        ('ID',     r'[a-zA-Z0-9_]+'),
        ('SKIP',   r'[ \t\n]+'),
    ]
    tokens = []
    for mo in re.finditer('|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_spec), code):
        kind = mo.lastgroup
        value = mo.group()
        if kind != 'SKIP':
            tokens.append((kind, value))
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def consume(self, expected_kind=None):
        kind, val = self.peek()
        if expected_kind and kind != expected_kind:
            raise SyntaxError(f"Expected {expected_kind}, got {kind} ('{val}')")
        self.pos += 1
        return val

    def parse_program(self):
        """解析多行程式（包含 let 綁定與最後的主運算式）"""
        env = {}
        while self.pos < len(self.tokens):
            kind, _ = self.peek()
            if kind == 'LET':
                self.consume('LET')
                var_name = self.consume('ID')
                self.consume('ASSIGN')
                expr = self.parse_expr()
                env[var_name] = expr
            else:
                expr = self.parse_expr()
                return env, expr
        return env, None

    def parse_expr(self):
        """Expr ::= Abs | AppExpr"""
        kind, _ = self.peek()
        if kind == 'LAMBDA':
            self.consume('LAMBDA')
            param = self.consume('ID')
            self.consume('DOT')
            body = self.parse_expr()
            return Abs(param, body)
        return self.parse_app()

    def parse_app(self):
        """AppExpr ::= Atom+ (左結合應用)"""
        expr = self.parse_atom()
        while True:
            kind, _ = self.peek()
            if kind in ('VAR', 'ID', 'LPAREN', 'LAMBDA'):
                arg = self.parse_atom()
                expr = App(expr, arg)
            else:
                break
        return expr

    def parse_atom(self):
        """Atom ::= ID | ( Expr )"""
        kind, val = self.peek()
        if kind == 'ID':
            self.consume('ID')
            return Var(val)
        elif kind == 'LPAREN':
            self.consume('LPAREN')
            expr = self.parse_expr()
            self.consume('RPAREN')
            return expr
        elif kind == 'LAMBDA':
            return self.parse_expr()
        else:
            raise SyntaxError(f"Unexpected token: {kind} ('{val}')")


# ==========================================
# 3. 求值引擎 (Alpha-Conversion & Beta-Reduction)
# ==========================================
def free_vars(node):
    """取得 AST 中所有的自由變數集合"""
    if isinstance(node, Var):
        return {node.name}
    elif isinstance(node, Abs):
        return free_vars(node.body) - {node.param}
    elif isinstance(node, App):
        return free_vars(node.fn) | free_vars(node.arg)
    return set()

def substitute(node, target, replacement):
    """代換演算法（包含自動 α-轉換防堵變數捕捉）"""
    if isinstance(node, Var):
        return replacement if node.name == target else node

    elif isinstance(node, Abs):
        if node.param == target:
            return node  # 被遮蔽，停止代換

        # 避免自由變數捕捉：若參數名出現在 replacement 的自由變數中，進行 α-轉換 (重命名)
        repl_free = free_vars(replacement)
        if node.param in repl_free:
            new_param = node.param + "'"
            while new_param in repl_free or new_param in free_vars(node.body):
                new_param += "'"
            # 重新命名內部參數
            renamed_body = substitute(node.body, node.param, Var(new_param))
            return Abs(new_param, substitute(renamed_body, target, replacement))
        else:
            return Abs(node.param, substitute(node.body, target, replacement))

    elif isinstance(node, App):
        return App(substitute(node.fn, target, replacement),
                   substitute(node.arg, target, replacement))

def expand_env(node, env):
    """將環境中的名稱（let 定義）展開至 AST 中"""
    if isinstance(node, Var):
        if node.name in env:
            return expand_env(env[node.name], env)
        return node
    elif isinstance(node, Abs):
        return Abs(node.param, expand_env(node.body, env))
    elif isinstance(node, App):
        return App(expand_env(node.fn, env), expand_env(node.arg, env))
    return node

def eval_step(node):
    """執行單步 β-歸約（Normal Order 正規序，最外層優先）"""
    if isinstance(node, App):
        # 核心：(\x. M) N  ==> 代換 M[x := N]
        if isinstance(node.fn, Abs):
            reduced = substitute(node.fn.body, node.fn.param, node.arg)
            return reduced, True

        # 若左邊還沒變成 Abs，先化簡左邊
        new_fn, reduced = eval_step(node.fn)
        if reduced:
            return App(new_fn, node.arg), True

        # 再化簡右邊
        new_arg, reduced = eval_step(node.arg)
        if reduced:
            return App(node.fn, new_arg), True

    elif isinstance(node, Abs):
        new_body, reduced = eval_step(node.body)
        if reduced:
            return Abs(node.param, new_body), True

    return node, False

# 1. 定義預設函式庫
STANDARD_LIBRARY = """
-- Church Booleans
let true  = \\x. \\y. x
let false = \\x. \\y. y
let if    = \\p. \\a. \\b. p a b
let and   = \\p. \\q. p q false
let or    = \\p. \\q. p true q
let not   = \\p. p false true

-- Church Numerals
let zero  = \\f. \\x. x
let one   = \\f. \\x. f x
let two   = \\f. \\x. f (f x)
let three = \\f. \\x. f (f (f x))

-- Arithmetic
let succ  = \\n. \\f. \\x. f (n f x)
let plus  = \\m. \\n. m succ n
let mult  = \\m. \\n. \\f. m (n f)
let iszero = \\n. n (\\x. false) true

-- Recursion
let z     = \\f. (\\x. f (\\v. x x v)) (\\x. f (\\v. x x v))
"""

def run_interpreter_with_stdlib(user_code, max_steps=100):
    # 將預設函式庫與使用者的程式碼拼接
    full_code = STANDARD_LIBRARY + "\n" + user_code
    
    # 呼叫原本的解譯器執行
    run_interpreter(full_code, max_steps)

def run_interpreter(code, max_steps=100):
    """解譯器執行入口，印出步驟"""
    print("=" * 60)
    print("【原始輸入程式】")
    print(code.strip())
    print("=" * 60)

    tokens = tokenize(code)
    parser = Parser(tokens)
    env, expr = parser.parse_program()

    if not expr:
        print("未找到可執行的表達式。")
        return

    # 1. 展開 let 語法糖名稱
    ast = expand_env(expr, env)
    print("【1. 名稱展開後 AST】")
    print(ast)
    print("\n【2. 開始計算過程 (β-reduction)】")

    step = 0
    curr = ast
    print(f"Step {step:2d}: {curr}")

    while step < max_steps:
        next_ast, reduced = eval_step(curr)
        if not reduced:
            print("\n【3. 計算結束 (已到達 Normal Form)】")
            print(f"最終結果: {curr}")
            return
        step += 1
        curr = next_ast
        print(f"Step {step:2d}: {curr}")

    print("\n[警告] 已達到最大步驟上限，計算可能陷入無限迴圈！")
