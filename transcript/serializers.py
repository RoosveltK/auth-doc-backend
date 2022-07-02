
from dataclasses import field, fields
from rest_framework import serializers

from transcript.models import AcademicYear, Amphi, Etudiant, Evaluation, Examen, Faculty, Filiere, Level, SchoolAt, Semester, Transcript, Ue


class AcademicSerializer(serializers.ModelSerializer):
    # tracks = TrackSerializer(many=True, read_only=True)
    class Meta:
        model = AcademicYear
        fields = '__all__'


class AcademicRelatedField(serializers.RelatedField):
    def to_representation(self, instance):
        return AcademicSerializer(instance).data

    def to_internal_value(self, data):
        return self.queryset.get(pk=data)


class SemesterSerializer(serializers.ModelSerializer):
    academic_year = AcademicRelatedField(
        queryset=AcademicYear.objects.all(), many=False)

    class Meta:
        model = Semester
        fields = '__all__'


class SemesterRelatedField(serializers.RelatedField):
    def to_representation(self, instance):
        return SemesterSerializer(instance).data

    def to_internal_value(self, data):
        return self.queryset.get(pk=data)


class EtudiantSerializer(serializers.ModelSerializer):
    # tracks = TrackSerializer(many=True, read_only=True)
    class Meta:
        model = Etudiant
        fields = '__all__'


class EtudiantRelatedField(serializers.RelatedField):
    def to_representation(self, instance):
        return EtudiantSerializer(instance).data

    def to_internal_value(self, data):
        return self.queryset.get(pk=data)


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = '__all__'


class FacultyRelatedField(serializers.RelatedField):
    def to_representation(self, instance):
        return FacultySerializer(instance).data

    def to_internal_value(self, data):
        return self.queryset.get(pk=data)


class FiliereSerializer(serializers.ModelSerializer):
    faculty = FacultyRelatedField(queryset=Faculty.objects.all(), many=False)

    class Meta:
        model = Filiere
        fields = '__all__'


class FiliereRelatedField(serializers.RelatedField):
    def to_representation(self, instance):
        return FiliereSerializer(instance).data

    def to_internal_value(self, data):
        return self.queryset.get(pk=data)


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'


class LevelRelatedField(serializers.RelatedField):
    def to_representation(self, instance):
        return LevelSerializer(instance).data

    def to_internal_value(self, data):
        return self.queryset.get(pk=data)


class AmphiSerializer(serializers.ModelSerializer):
    filiere = FiliereRelatedField(queryset=Filiere.objects.all())
    level = LevelRelatedField(queryset=Level.objects.all())
    academic_year = AcademicRelatedField(
        queryset=AcademicYear.objects.all(), many=False)

    class Meta:
        model = Amphi
        fields = '__all__'


class AmphiRelatedField(serializers.RelatedField):
    def to_representation(self, instance):
        return AmphiSerializer(instance).data

    def to_internal_value(self, data):
        return self.queryset.get(pk=data)


class UeSerializer(serializers.ModelSerializer):
    semester = SemesterRelatedField(
        queryset=Semester.objects.all(), many=False)

    class Meta:
        model = Ue
        fields = '__all__'


class UeRelatedField(serializers.RelatedField):
    def to_representation(self, instance):
        return UeSerializer(instance).data

    def to_internal_value(self, data):
        return self.queryset.get(pk=data)


class TranscriptSerializer(serializers.ModelSerializer):
    etudiant = EtudiantRelatedField(
        queryset=Etudiant.objects.all(), many=False)
    academic_year = AcademicRelatedField(
        queryset=AcademicYear.objects.all(), many=False)

    class Meta:
        model = Transcript
        fields = '__all__'


class TranscriptNormalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = '__all__'


class ExamenSerializer(serializers.ModelSerializer):
    academic_year = AcademicRelatedField(
        queryset=AcademicYear.objects.all(), many=False)

    class Meta:
        model = Examen
        fields = '__all__'


class ExamenRelatedField(serializers.RelatedField):
    def to_representation(self, instance):
        return ExamenSerializer(instance).data

    def to_internal_value(self, data):
        return self.queryset.get(pk=data)


class EvaluationSerializer(serializers.ModelSerializer):
    ue = UeRelatedField(queryset=Ue.objects.all(), many=False)
    examen = ExamenRelatedField(queryset=Examen.objects.all(), many=False)

    class Meta:
        model = Evaluation
        fields = '__all__'


class SchoolAtSerializer(serializers.ModelSerializer):
    amphi = AmphiRelatedField(queryset=Amphi.objects.all())

    class Meta:
        model = SchoolAt
        fields = '__all__'


class CipherSerializer(serializers.Serializer):
    matricule = serializers.CharField(max_length=10)
    number = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    surname = serializers.CharField(max_length=255)
    mgp = serializers.DecimalField(max_digits=3, decimal_places=2)
    decision = serializers.CharField(max_length=255)
    hash = serializers.CharField(max_length=255)
