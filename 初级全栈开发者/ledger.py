def add_record():
    date = input("日期（如 2026-06-14）：")
    category = input("分类（收入/支出）：")
    item = input("项目：")
    amount = input("金额：")
    
    with open("账本.txt", "a", encoding="utf-8") as f:
        f.write(f"{date},{category},{item},{amount}\n")
    
    print("已保存！")

def view_records():
    try:
        with open("账本.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("还没有任何记录")
        return

    if not lines:
        print("还没有任何记录")
        return

    print("\n=== 账本记录 ===")

    total_income = 0
    total_expense = 0

    for line in lines:
        parts = line.strip().split(",")
        date, category, item, amount = parts
        amount = float(amount)
        print(f"{date} | {category} | {item} | {amount}元")

        if category == "收入":
            total_income += amount
        else:
            total_expense += amount

    print(f"\n总收入：{total_income}元  总支出：{total_expense}元  结余：{total_income - total_expense}元")

# 主程序
while True:
    print("\n1. 记一笔  2. 查看记录  3. 退出")
    choice = input("选择：")
    if choice == "1":
        add_record()
    elif choice == "2":
        view_records()
    elif choice == "3":
        print("再见！")
        break
    else:
        print("请输入 1 2 或 3")
