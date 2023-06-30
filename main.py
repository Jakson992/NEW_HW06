import sqlite3
from datetime import datetime, date, timedelta
from random import randint, choice
from typing import List

from faker import Faker

fake = Faker('uk-UA')

subjects = [
    "Основи програмування",
    "Математичний аналіз",
    "Численні методи",
    "Культурологія",
    "Філософія",
    "Теорія ймовірності",
    "Web програмування",
    "Механіка рідини і газу",
    "Фізика"
]

groups = ["ФФ-11", "GoIt-12", "ЕМ-10"]

NUMBERS_TEACHERS = 5
NUMBERS_STUDENTS = 60

connect = sqlite3.connect('new_hw06.sqlite')
cursor = connect.cursor()


def seed_teacher():
    teachers = [fake.name() for _ in range(NUMBERS_TEACHERS)]
    sql = "INSERT INTO teachers(fullname) VALUES (?);"
    cursor.executemany(sql, zip(teachers, ))


def seed_groups():
    sql = "INSERT INTO groups(name) VALUES (?);"
    cursor.executemany(sql, zip(groups, ))


def seed_students():
    students = [fake.name() for _ in range(NUMBERS_STUDENTS)]
    list_group_id = [randint(1, len(groups)) for _ in range(NUMBERS_STUDENTS)]
    sql = "INSERT INTO students(fullname, group_id) VALUES (?, ?);"
    cursor.executemany(sql, zip(students, list_group_id))


def seed_subjects():
    list_teacher_id = [randint(1, NUMBERS_TEACHERS) for _ in range(len(subjects))]
    sql = "INSERT INTO subjects(name, teacher_id) VALUES (?, ?);"
    cursor.executemany(sql, zip(subjects, list_teacher_id))


def seed_grades():
    start_date = datetime.strptime("2022-09-01", "%Y-%m-%d")
    finish_date = datetime.strptime("2023-05-31", "%Y-%m-%d")
    sql = "INSERT INTO grades(student_id, subject_id, grade, date_of) VALUES (?, ?, ?, ?);"

    def get_list_date(start_date, finish_date) -> List[date]:
        result = []
        current_day: date = start_date
        while current_day < finish_date:
            if current_day.isoweekday() < 6:
                result.append(current_day)
            current_day += timedelta(1)
        return result

    list_date = get_list_date(start_date, finish_date)

    grades = []
    for day in list_date:
        random_subject = randint(1, len(subjects))
        random_students = [randint(1, NUMBERS_STUDENTS) for _ in range(7)]
        for student in random_students:
            grades.append((student, random_subject, randint(1, 12), day.date()))

    cursor.executemany(sql, grades)


if __name__ == '__main__':
    seed_teacher()
    seed_groups()
    seed_students()
    seed_subjects()
    seed_grades()
    connect.commit()
    connect.close()

    while True:
        choice = input("Введите номер запроса (1-10) или 'exit' для выхода: ")

        if choice == 'exit':
            break

        try:
            choice = int(choice)

            if choice == 1:
                query = """
                SELECT s.fullname, ROUND(AVG(g.grade), 2) as avg_grade
                FROM grades g
                LEFT JOIN students s ON s.id = g.student_id
                GROUP BY s.id
                ORDER BY avg_grade DESC
                LIMIT 5;
                """
                execute_query(query)

            elif choice == 2:
                query = """
                SELECT sbj.name, s.fullname, ROUND(AVG(g.grade), 2) as avg_grade
                FROM grades g
                LEFT JOIN students s ON s.id = g.student_id
                LEFT JOIN subjects sbj ON sbj.id = g.subject_id
                WHERE sbj.id = 4
                GROUP BY s.id
                ORDER BY avg_grade DESC
                LIMIT 1;
                """
                execute_query(query)


            elif choice == 3:
                query = """
                SELECT sbj.name, gr.name, ROUND(AVG(g.grade), 2) AS avg_grade
                FROM grades g
                LEFT JOIN students s ON s.id = g.student_id
                LEFT JOIN groups gr ON gr.id = s.group_id
                LEFT JOIN subjects sbj ON sbj.id = g.subject_id
                WHERE sbj.id = 4 AND gr.id IN (1, 2, 3)
                GROUP BY gr.name, sbj.name;
                """
                execute_query(query)

            elif choice == 4:
                query = """
                SELECT ROUND(AVG(grade), 2) AS avg_grade
                FROM grades;
                """
                execute_query(query)

            elif choice == 5:
                query = """
                SELECT sbj.name , t.fullname 
                FROM subjects sbj
                LEFT JOIN teachers t ON t.id = sbj.teacher_id
                WHERE t.id IN (1, 2, 3, 4, 5);
                """
                execute_query(query)

            elif choice == 6:
                query = """
                SELECT g.name , g.name , s.name
                FROM students s
                INNER JOIN groups g ON g.id = s.group_id
                WHERE g.id = 1;
                """
                execute_query(query)

            elif choice == 7:
                query = """
                SELECT gr.name AS group_name, sbj.name AS subject_name, g.grade
                FROM groups gr
                LEFT JOIN grades g ON g.student_id = gr.id
                LEFT JOIN subjects sbj ON sbj.id = g.subject_id
                WHERE sbj.id = 1 AND gr.id = 1;
                """
                execute_query(query)

            elif choice == 8:
                query = """
                SELECT ROUND(AVG(g.grade),2) AS average_grade, t.fullname
                FROM grades g
                LEFT JOIN subjects sbj ON sbj.id = g.subject_id
                LEFT JOIN teachers t ON t.id = sbj.teacher_id
                WHERE t.id = 2;
                """
                execute_query(query)

            elif choice == 9:
                query = """
                SELECT s.fullname, sbj.name
                FROM students s
                JOIN grades g ON g.student_id = s.id
                JOIN subjects sbj ON sbj.id = g.subject_id
                JOIN groups gr ON gr.id = s.group_id
                WHERE s.id = 2
                GROUP BY s.fullname, sbj.name;
                           """
                execute_query(query)


            elif choice == 10:
                query = """
                SELECT s.fullname, t.fullname, sbj.name
                FROM students s
                JOIN groups g ON g.id = s.group_id
                JOIN 
                (SELECT DISTINCT gr.student_id, gr.subject_id
                 FROM grades gr
                 JOIN subjects sbj ON sbj.id = gr.subject_id
                 JOIN teachers t ON t.id = sbj.teacher_id
                 WHERE gr.student_id = 56 AND t.id = 1) sub ON sub.student_id = s.id
                JOIN subjects sbj ON sbj.id = sub.subject_id
                JOIN teachers t ON t.id = sbj.teacher_id;
                """
                execute_query(query)

            else:
                print("Некорректный номер запроса. Попробуйте снова.")

        except ValueError:
            print("Некорректный ввод. Введите число от 1 до 10 или 'exit' для выхода.")

    connect.close()
