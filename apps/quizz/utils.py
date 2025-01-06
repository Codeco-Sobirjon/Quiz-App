import re
from apps.quizz.models import Quiz, Question

def import_tests_from_file(file_path, category):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            content = file.read()

    tests = content.strip().split('#')[1:]
    print(category,4)
    for test in tests:
        lines = test.strip().split('\n')
        title = lines[0].strip()
        answers = lines[1:]

        quiz = Quiz.objects.create(
            title=title,
            category=category,
            description="Imported from file"
        )

        for answer in answers:
            text = answer[1:].strip()
            is_correct = answer.startswith('+')
            Question.objects.create(
                quiz=quiz,
                text=text,
                is_correct=is_correct
            )
