import Convert_input as ci
from slover import solve # 注意你的文件名可能是 slover.py (拼写)

def test_color_logic():
    raw_kb = [
        "On(tony,mike)",                       # 1. Tony 在 Mike 上面
        "On(mike,john)",                       # 2. Mike 在 John 上面
        "Green(tony)",                         # 3. Tony 是绿色的
        "~Green(john)",                        # 4. John 不是绿色的 (这是结论取反后的矛盾点)
        "(~On(xx,yy), ~Green(xx), Green(yy))"  # 5. 规则：上绿则下绿
    ]

    kb_list = []
    for c_str in raw_kb:
        parsed = ci.parse_clause(c_str)
        kb_list.append(parsed)
    
    print("--- 开始测试作业 2: 颜色传递问题 ---")
    success = solve(kb_list)
    
    if success:
        print("\nSuccess!")
    else:
        print("\nFail.")

if __name__ == "__main__":
    test_color_logic()