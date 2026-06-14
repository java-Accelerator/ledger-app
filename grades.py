students = [
    {"name": "张三", "score": 85},
    {"name": "李四", "score": 92},
    {"name": "王五", "score": 78},
    {"name": "赵六", "score": 60},
    {"name": "陈七", "score": 95},
    {"name": "八八", "score": 50},
]

print("=== 成绩单 ===")
for s in students:
    if s["score"] >= 90:
        level = "优秀"
    elif s["score"] >= 60:
        level = "及格"
    else:
        level = "不及格"
    print(f"{s['name']}：{s['score']}分（{level}）")

    # 收集所有分数
all_scores = []
for s in students:
    all_scores.append(s["score"])

avg = sum(all_scores) / len(all_scores)
highest = max(all_scores)
lowest = min(all_scores)

pass_count = 0
for score in all_scores:
    if score >= 60:
        pass_count = pass_count + 1
pass_rate = pass_count / len(all_scores) * 100

print("\n=== 统计 ===")
print(f"平均分：{avg:.1f}")
print(f"最高分：{highest}")
print(f"最低分：{lowest}")
print(f"及格率：{pass_rate:.1f}%")