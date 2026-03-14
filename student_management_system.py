# -*- coding: utf-8 -*-
"""
学生信息管理系统 (Student Information Management System)
功能: 学生信息的增删改查操作
作者: Python-Edu-Developer
版本: 1.0
"""

class Student:
    """
    学生类 - 封装学生的基本信息
    属性:
        stu_id (str): 学号
        name (str): 姓名
        age (int): 年龄
        score (float): 成绩
    """
    def __init__(self, stu_id, name, age, score):
        """
        构造方法 - 初始化学生对象
        参数:
            stu_id: 学号
            name: 姓名
            age: 年龄
            score: 成绩
        """
        self.stu_id = stu_id
        self.name = name
        self.age = age
        self.score = score

    def __str__(self):
        """
        返回学生信息的字符串表示
        返回: 格式化的学生信息字符串
        """
        return f"学号: {self.stu_id}, 姓名: {self.name}, 年龄: {self.age}, 成绩: {self.score}"

student_list = []

def display_menu():
    """显示主菜单"""
    print("\n" + "="*50)
    print(" " * 15 + "学生信息管理系统")
    print("="*50)
    print("1. 添加学生信息")
    print("2. 删除学生信息")
    print("3. 修改学生信息")
    print("4. 查询所有学生信息")
    print("5. 按姓名模糊查询")
    print("6. 退出系统")
    print("="*50)

def get_valid_input(prompt, input_type, allow_empty=False):
    """
    获取并验证用户输入
    参数:
        prompt: 提示信息
        input_type: 期望的输入类型 ('int', 'float', 'str')
        allow_empty: 是否允许空输入
    返回: 验证后的输入值
    """
    while True:
        user_input = input(prompt).strip()
        
        if allow_empty and user_input == "":
            return None
        
        if user_input == "" and not allow_empty:
            print("输入不能为空，请重新输入！")
            continue
        
        if input_type == 'int':
            try:
                value = int(user_input)
                return value
            except ValueError:
                print("请输入有效的整数！")
        elif input_type == 'float':
            try:
                value = float(user_input)
                return value
            except ValueError:
                print("请输入有效的数字！")
        else:
            return user_input

def is_student_exist(stu_id):
    """
    检查学号是否已存在
    参数:
        stu_id: 要检查的学号
    返回: True表示存在，False表示不存在
    """
    for student in student_list:
        if student.stu_id == stu_id:
            return True
    return False

def add_student():
    """添加学生信息"""
    print("\n--- 添加学生信息 ---")
    
    while True:
        stu_id = get_valid_input("请输入学号: ", 'str')
        if is_student_exist(stu_id):
            print(f"学号 {stu_id} 已存在，请使用其他学号！")
        else:
            break
    
    name = get_valid_input("请输入姓名: ", 'str')
    
    while True:
        age = get_valid_input("请输入年龄: ", 'int')
        if age <= 0 or age > 120:
            print("年龄必须在1-120之间！")
        else:
            break
    
    while True:
        score = get_valid_input("请输入成绩(0-100): ", 'float')
        if score < 0 or score > 100:
            print("成绩必须在0-100之间！")
        else:
            break
    
    new_student = Student(stu_id, name, age, score)
    student_list.append(new_student)
    print(f"学生 {name} 信息添加成功！")

def delete_student():
    """按学号删除学生信息"""
    print("\n--- 删除学生信息 ---")
    stu_id = get_valid_input("请输入要删除的学生学号: ", 'str')
    
    for i, student in enumerate(student_list):
        if student.stu_id == stu_id:
            del student_list[i]
            print(f"学号为 {stu_id} 的学生信息已删除！")
            return
    
    print(f"未找到学号为 {stu_id} 的学生！")

def update_student():
    """按学号修改学生信息"""
    print("\n--- 修改学生信息 ---")
    stu_id = get_valid_input("请输入要修改的学生学号: ", 'str')
    
    for student in student_list:
        if student.stu_id == stu_id:
            print(f"当前学生信息: {student}")
            print("(直接按回车保留原值)")
            
            new_name = get_valid_input(f"请输入新姓名 [{student.name}]: ", 'str', allow_empty=True)
            if new_name is not None:
                student.name = new_name
            
            while True:
                new_age = get_valid_input(f"请输入新年龄 [{student.age}]: ", 'str', allow_empty=True)
                if new_age is None:
                    break
                try:
                    new_age = int(new_age)
                    if new_age <= 0 or new_age > 120:
                        print("年龄必须在1-120之间！")
                        continue
                    student.age = new_age
                    break
                except ValueError:
                    print("请输入有效的整数！")
            
            while True:
                new_score = get_valid_input(f"请输入新成绩 [{student.score}]: ", 'str', allow_empty=True)
                if new_score is None:
                    break
                try:
                    new_score = float(new_score)
                    if new_score < 0 or new_score > 100:
                        print("成绩必须在0-100之间！")
                        continue
                    student.score = new_score
                    break
                except ValueError:
                    print("请输入有效的数字！")
            
            print("学生信息修改成功！")
            return
    
    print(f"未找到学号为 {stu_id} 的学生！")

def show_all_students():
    """显示所有学生信息"""
    print("\n--- 所有学生信息 ---")
    
    if not student_list:
        print("当前没有学生信息！")
        return
    
    print(f"{'学号':<10} {'姓名':<10} {'年龄':<6} {'成绩':<6}")
    print("-" * 35)
    for student in student_list:
        print(f"{student.stu_id:<10} {student.name:<10} {student.age:<6} {student.score:<6}")
    print(f"\n共 {len(student_list)} 名学生")

def search_student_by_name():
    """按姓名模糊查询学生信息"""
    print("\n--- 按姓名模糊查询 ---")
    keyword = get_valid_input("请输入要查询的姓名关键词: ", 'str')
    
    results = []
    for student in student_list:
        if keyword.lower() in student.name.lower():
            results.append(student)
    
    if not results:
        print(f"未找到姓名包含 '{keyword}' 的学生！")
        return
    
    print(f"找到 {len(results)} 名匹配的学生:")
    print(f"{'学号':<10} {'姓名':<10} {'年龄':<6} {'成绩':<6}")
    print("-" * 35)
    for student in results:
        print(f"{student.stu_id:<10} {student.name:<10} {student.age:<6} {student.score:<6}")

def main():
    """主函数 - 程序入口"""
    print("欢迎使用学生信息管理系统！")
    
    while True:
        display_menu()
        choice = input("请选择操作(1-6): ").strip()
        
        if choice == '1':
            add_student()
        elif choice == '2':
            delete_student()
        elif choice == '3':
            update_student()
        elif choice == '4':
            show_all_students()
        elif choice == '5':
            search_student_by_name()
        elif choice == '6':
            print("感谢使用学生信息管理系统，再见！")
            break
        else:
            print("无效的选择，请输入1-6之间的数字！")

if __name__ == "__main__":
    main()
