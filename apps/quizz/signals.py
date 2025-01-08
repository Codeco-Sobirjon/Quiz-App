from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.quizz.models import UploadTests, QuizQuestion, QuestionOption


@receiver(post_save, sender=UploadTests)
def process_uploaded_file(sender, instance, created, **kwargs):
    if created and instance.file:
        file_path = instance.file.path
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='ISO-8859-1') as file:
                lines = file.readlines()

        current_question = None

        for line in lines:
            line = line.strip()

            if line.startswith("#"):
                current_question = QuizQuestion.objects.create(
                    title=line[1:].strip(),
                    quiz=instance.quiz,
                )
            elif line.startswith("+"):
                if current_question:
                    QuestionOption.objects.create(
                        question=current_question,
                        text=line[1:].strip(),
                        is_correct=True,
                    )
            elif line.startswith("-"):
                if current_question:
                    QuestionOption.objects.create(
                        question=current_question,
                        text=line[1:].strip(),
                        is_correct=False,
                    )
