import Convert_input as ci
from slover import solve, format_clause

def test_graduate():
    raw_kb = [
        "GradStudent(sue)",
        "(~GradStudent(x), Student(x))",
        "(~Student(x), HardWorker(x))",
        "~HardWorker(sue)"
    ]
    kb_list = [ci.parse_clause(c) for c in raw_kb]
    print("--- 开始测试 Graduate Student 问题 ---")
    success = solve(kb_list)
    if success:
        print("\nSuccess!")
    else:
        print("\nFail.")

if __name__ == "__main__":
    test_graduate()