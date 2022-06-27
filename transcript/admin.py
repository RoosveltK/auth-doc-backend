from django.contrib import admin

from transcript.models import AcademicYear, Amphi, Etudiant, Evaluation, Examen, Faculty, Filiere, Level, SchoolAt, Semester, Transcript, Ue


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'academic_year')


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('abrev', 'name')


@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty')


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('code', 'intitule')


@admin.register(Amphi)
class AmphiAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'filiere')


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('id', 'ue', 'note', 'etudiant', 'examen')


@admin.register(Ue)
class UeAdmin(admin.ModelAdmin):
    list_display = ('code', 'intitule', 'credit', 'semester', 'amphi')


@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'name', 'surname')


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    list_display = ('number', 'mgp', 'complete_credit', 'academic_year')


@admin.register(SchoolAt)
class SchoolAtAdmin(admin.ModelAdmin):
    pass


@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    pass
