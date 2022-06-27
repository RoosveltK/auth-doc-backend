
# from rest_framework import routers
from django import views
from django.urls import path
from transcript.views import AddNoteAtViewSet, AmphiViewSet, DecryptDataViewSet, EtudiantViewSet, EvaluationViewSet, ExamViewSet, GetTranscriptInfoView, OperationTranscriptViewSet, StudentEvaluationViewSet, StudentSchoolATViewSet, TranscriptApiViewSet, SchooAtViewSet, TranscriptViewSet, UeAmphiViewSet, VerifNewTranscriptViewSet

# router = routers.DefaultRouter()
# router.register('etudiants',EtudiantViewSet)
# router.register('amphis',AmphiViewSet)
# router.register('transcripts',TranscriptViewSet)
# router.register('evaluations',EvaluationViewSet)

urlpatterns = [
    path('transcripts', TranscriptViewSet.as_view({
        "get": "list"
    })),
    path('etudiants', EtudiantViewSet.as_view({
         "get": "list",
         "post": "create"
         })),
    path('etudiant/<str:pk>', EtudiantViewSet.as_view({
        'get': "retrieve",
        'put': 'update',
        'delete': 'destroy'
    })),
    path('assign_amphi', SchooAtViewSet.as_view({
        "get": "list",
        "post": "create"
    })),
    path('assign_note', AddNoteAtViewSet.as_view({
        "post": "create"
    })),
    path('school_at/<int:pk>', SchooAtViewSet.as_view({
        'get': 'retrieve'
    })),
    path('check_existing/<int:pk>', GetTranscriptInfoView.as_view({
        'get': 'retrieve'
    })),
    path('student_by_amphis/<int:pk>', StudentSchoolATViewSet.as_view({
        'get': 'retrieve'
    })),
    path('amphi_ues/<int:pk>', UeAmphiViewSet.as_view({
        'get': 'retrieve'
    })),
    path('amphis', AmphiViewSet.as_view({
         "get": "list"
         })),
    path('examens', ExamViewSet.as_view({
         "get": "list"
         })),
    path('student_note/<int:pk>', StudentEvaluationViewSet.as_view({
         "get": "retrieve"
         })),
    path('can_u_print/<int:pk>', OperationTranscriptViewSet.as_view({
         "get": "retrieve"
         })),
    path('decrypt_data', DecryptDataViewSet.as_view({
         "post": "create"
         })),
    path('authenticate_new_transcript', VerifNewTranscriptViewSet.as_view({
         "post": "create"
         })),
]
