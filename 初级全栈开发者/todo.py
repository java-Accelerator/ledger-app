import os

TODO_FILE = "todo_data.txt"

def load_todos():
    """从文件读取待办列表，返回 list[dict]"""
    todos = []
    if not os.path.exists(TODO_FILE):
        return todos

    with open(TODO_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",,,")
            if len(parts) == 2:
                todos.append({"task": parts[0], "done": parts[1] == "True"})
    return todos

def save_todos(todos):
    """把待办列表写回文件"""
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        for t in todos:
            f.write(f"{t['task']},,,{t['done']}\n")

def add_todo(todos):
    task = input("待办事项：")
    todos.append({"task": task, "done": False})
    save_todos(todos)
    print("已添加！")

def show_todos(todos):
    if not todos:
        print("暂无待办")
        return

    print("\n=== 待办列表 ===")
    for i, t in enumerate(todos, 1):
        status = "✓" if t["done"] else " "
        print(f"[{status}] {i}. {t['task']}")

def show_done(todos):
    done_list = []
    for t in todos:
        if t["done"]:
            done_list.append(t)

    if not done_list:
        print("暂无已完成的待办")
        return

    print("\n=== 已完成的待办 ===")
    for i, t in enumerate(done_list, 1):
        print(f"✓ {i}. {t['task']}")

def mark_done(todos):
    show_todos(todos)
    if not todos:
        return

    try:
        num = int(input("输入要完成的序号："))
        if 1 <= num <= len(todos):
            todos[num - 1]["done"] = True
            save_todos(todos)
            print(f"'{todos[num - 1]['task']}' 已完成！")
        else:
            print("序号超出范围")
    except ValueError:
        print("请输入数字")

def delete_todo(todos):
    show_todos(todos)
    if not todos:
        return

    try:
        num = int(input("输入要删除的序号："))
        if 1 <= num <= len(todos):
            removed = todos.pop(num - 1)
            save_todos(todos)
            print(f"'{removed['task']}' 已删除！")
        else:
            print("序号超出范围")
    except ValueError:
        print("请输入数字")

def main():
    todos = load_todos()

    while True:
        print("\n1. 添加  2. 查看  3. 完成  4. 删除  5. 已完成  6. 退出")
        choice = input("选择：")

        if choice == "1":
            add_todo(todos)
        elif choice == "2":
            show_todos(todos)
        elif choice == "3":
            mark_done(todos)
        elif choice == "4":
            delete_todo(todos)
        elif choice == "5":
            show_done(todos)
        elif choice == "6":
            print("再见！")
            break
        else:
            print("输入 1-6")

main()
