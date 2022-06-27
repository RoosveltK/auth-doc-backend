from re import search
from sys import hash_info
from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from transcript.models import AcademicYear, Amphi, Etudiant, Evaluation, Examen, SchoolAt, Transcript, Ue
from transcript.serializers import AmphiSerializer, EtudiantSerializer, EvaluationSerializer, ExamenSerializer, SchoolAtSerializer, TranscriptNormalSerializer, TranscriptSerializer, UeSerializer, CipherSerializer
from django.db.models import Q

from rest_framework import status

from base64 import b64encode, b64decode
from binascii import unhexlify
import hashlib
import ast


from .AES.crypto import AESCipher
import os


# Create your views here.
# SECRET_kEY_HASH = os.environ.get("AES_KEY")
SECRET_kEY_HASH = "AUTHEN_SYSTEM_UY1"


class EtudiantViewSet(viewsets.ModelViewSet):
    queryset = Etudiant.objects.all()
    serializer_class = EtudiantSerializer

    def list(self, request):
        serializer = EtudiantSerializer(Etudiant.objects.all(), many=True)
        return Response({
            'data': serializer.data
        })

    def retrieve(self, request, pk=None):
        etudiant = Etudiant.objects.get(id=pk)
        serializer = EtudiantSerializer(etudiant)
        return Response({
            'data': serializer.data
        })

    def create(self, request):
        serializer = EtudiantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        etudiant = Etudiant.objects.get(id=pk)
        serializer = EtudiantSerializer(instance=etudiant, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'data': serializer.data}, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, pk=None):
        etudiant = Etudiant.objects.get(id=pk)
        etudiant.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AmphiViewSet(viewsets.ModelViewSet):
    queryset = Amphi.objects.all()
    serializer_class = AmphiSerializer

    def get(self, request):
        serializer = AmphiSerializer(Amphi.objects.all(), many=True)
        return Response({
            "data": serializer.data
        })


class TranscriptApiViewSet(generics.ListCreateAPIView):
    queryset = Transcript.objects.all()
    search_fields = ['=cipher_info']
    serializer_class = TranscriptNormalSerializer


class TranscriptViewSet(viewsets.ViewSet):
    permissions_classes = [IsAuthenticated]

    def list(self, request):

        serializer = TranscriptSerializer(Transcript.objects.all(), many=True)
        response = serializer.data
        transcripts = Transcript.objects.all()
        custom_response = []

        for item in response:

            evaluations = Evaluation.objects.filter(
                etudiant=item['etudiant']['id'])
            eval_serialize = EvaluationSerializer(evaluations, many=True)
            item['evaluations'] = eval_serialize.data
            custom_response.append(item)

        return Response({
            'data': custom_response
        })


class EvaluationViewSet(viewsets.ModelViewSet):

    def list(self, request):
        serializer = EvaluationSerializer(Evaluation.objects.all(), many=True)
        return Response({
            'data': serializer.data
        })


class SchooAtViewSet(viewsets.ModelViewSet):

    def list(self, request):
        serializer = SchoolAtSerializer(SchoolAt.objects.all(), many=True)
        return Response({
            'data': serializer.data
        })

    def create(self, request):
        serializer = SchoolAtSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):

        school = SchoolAt.objects.filter(etudiant=pk)
        if(len(school) > 0):
            school_at = school[0]
            school_at_serializer = SchoolAtSerializer(school_at)
            return Response({
                'data': school_at_serializer.data
            })


class AddNoteAtViewSet(viewsets.ModelViewSet):

    def create(self, request):
        elements = request.data
        item = elements['data']
        try:
            etudiant = Etudiant.objects.filter(matricule=item['matricule'])
            examen = Examen.objects.filter(id=elements['examen'])
            if(len(etudiant) > 0):
                is_exist = Evaluation.objects.filter(
                    etudiant=etudiant[0].id).filter(examen=examen[0].id)
                if(len(is_exist) == 0):
                    Evaluation.objects.create(
                        etudiant=etudiant[0],
                        ue=Ue.objects.get(id=elements['ue']),
                        note=item['note'],
                        examen=examen[0]
                    )
                    return Response({
                        'detail': 'Note assignée avec succès'
                    }, status=status.HTTP_201_CREATED)

                else:
                    return Response({'detail': "L'étudiant "+item['name']+" de matricule "+item['matricule']+" a déja recu une note pour cet examen, modifié la plutot "}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'detail': 'Aucun étudiant trouvé'
                }, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({
                'detail': 'Une erreur est survenue'
            }, status=status.HTTP_400_BAD_REQUEST)


class StudentSchoolATViewSet(viewsets.ModelViewSet):

    def retrieve(self, request, pk=None):

        school_at = SchoolAt.objects.filter(amphi=pk)
        custom_response = []

        for item in school_at:
            custom_response.append(Etudiant.objects.get(id=item.etudiant.id))

        response_d = EtudiantSerializer(custom_response, many=True)

        return Response({
            'data': response_d.data
        })


class UeAmphiViewSet(viewsets.ModelViewSet):

    def retrieve(self, request, pk=None):

        ue_amphi = Ue.objects.filter(amphi=pk)
        response_d = UeSerializer(ue_amphi, many=True)

        return Response({
            'data': response_d.data
        })


class GetTranscriptInfoView(viewsets.ModelViewSet):

    def retrieve(self, request, pk=None):
        transcript = Transcript.objects.filter(id=pk)

        find_tran_serializer = TranscriptSerializer(transcript, many=True)
        response = find_tran_serializer.data
        custom_response = []

        for item in response:
            evaluations = Evaluation.objects.filter(
                etudiant=item['etudiant']['id'])
            eval_serialize = EvaluationSerializer(evaluations, many=True)
            item['evaluations'] = eval_serialize.data
            custom_response.append(item)
        return Response({
            'data': custom_response
        })


class StudentEvaluationViewSet(viewsets.ModelViewSet):
    def retrieve(self, request, pk=None):
        evaluation = Evaluation.objects.filter(etudiant=pk)
        response_d = EvaluationSerializer(evaluation, many=True)

        return Response({
            'data': response_d.data
        })


class OperationTranscriptViewSet(viewsets.ModelViewSet):

    def generate_name_initial(self, name, surname):
        full_name = name + ' '+surname
        full_name_split = full_name.split()
        name_size = len(full_name_split) - 1
        i = 0
        initial = ''
        while(name_size >= i):
            initial += full_name_split[i][0][:1]
            i += 1
        return initial[:3]

    def determined_intermediare_note(self, notes):
        total = 0
        for item in notes:
            if(item['ue']['has_tp'] == True):
                if(item['examen'] == "CC"):
                    total += float(item['note'])
                if(item['examen'] == "SN"):
                    total += float(item['note'])*2
                if(item['examen'] == "TP"):
                    total += float(item['note'])*2
            else:
                if(item['examen'] == "CC"):
                    total += float(item['note'])*1.5
                if(item['examen'] == "SN"):
                    total += float(item['note'])*3.5
        return total

    def get_letter_grade(self, notefinale):
        decision = {
            "grade": '',
            "mgp": 0.0,
            "decision": ''
        }
        if 80 <= notefinale and notefinale <= 100:
            decision['grade'] = 'A'
            decision['mgp'] = 4.00
            decision['decision'] = "CA"
        elif 75 <= notefinale and notefinale <= 79:
            decision['grade'] = 'A-'
            decision['mgp'] = 3.70
            decision['decision'] = "CA"
        elif 70 <= notefinale and notefinale <= 74:
            decision['grade'] = 'B+'
            decision['mgp'] = 3.30
            decision['decision'] = "CA"
        elif 65 <= notefinale and notefinale <= 69:
            decision['grade'] = 'B'
            decision['mgp'] = 3.00
            decision['decision'] = "CA"
        elif 60 <= notefinale and notefinale <= 64:
            decision['grade'] = 'B-'
            decision['mgp'] = 2.70
            decision['decision'] = "CA"
        elif 55 <= notefinale and notefinale <= 59:
            decision['grade'] = 'C+'
            decision['mgp'] = 2.30
            decision['decision'] = "CA"
        elif 50 <= notefinale and notefinale <= 54:
            decision['grade'] = 'C'
            decision['mgp'] = 2.00
            decision['decision'] = "CA"
        elif 45 <= notefinale and notefinale <= 49:
            decision['grade'] = 'C-'
            decision['mgp'] = 1.70
            decision['decision'] = "CANT"
        elif 40 <= notefinale and notefinale <= 44:
            decision['grade'] = 'D+'
            decision['mgp'] = 1.30
            decision['decision'] = "CANT"
        elif 35 <= notefinale and notefinale <= 39:
            decision['grade'] = 'D'
            decision['mgp'] = 1.00
            decision['decision'] = "CANT"
        elif 30 <= notefinale and notefinale <= 34:
            decision['grade'] = 'E'
            decision['mgp'] = 0.00
            decision['decision'] = "NC"
        else:
            decision['grade'] = 'F'
            decision['mgp'] = 0.00
            decision['decision'] = "NC"
        return decision

    def retrieve(self, request, pk=None):
        search_transcript = Transcript.objects.filter(etudiant=pk)

        if(len(search_transcript) == 0):

            # Get all Note of student
            evaluation = Evaluation.objects.filter(etudiant=pk)
            allEvaluation = EvaluationSerializer(evaluation, many=True)

            # Get all Info of student
            etudiant = Etudiant.objects.get(id=pk)
            etudiant_serializer = EtudiantSerializer(etudiant)

            # Get all Info of Class
            school_info = SchoolAt.objects.get(etudiant=pk)
            school_info_serializer = SchoolAtSerializer(school_info)

            # nbre of transcript print
            nbre_transcript_print = Transcript.objects.all().count()

            # Get all Ue of Class
            ue_amphi = Ue.objects.filter(amphi=school_info.amphi)

            total_credit_amphi = UeSerializer(ue_amphi, many=True)
            credit_sum = 0
            credit_capitalised_sum = 0

            # Calculate the total credit of the class
            for cred in total_credit_amphi.data:
                credit_sum += cred['credit']

            id_used = []
            all_notes_credit = []
            concat_note = ''
            for item in allEvaluation.data:

                if item['ue']['id'] not in id_used:
                    note = Evaluation.objects.filter(
                        etudiant=pk).filter(ue=item['ue']['id'])
                    note_serializers = EvaluationSerializer(note, many=True)
                    notes = note_serializers.data

                    note_ee = self.determined_intermediare_note(notes)
                    decision = self.get_letter_grade(note_ee)

                    Evaluation.objects.create(
                        etudiant=Etudiant.objects.get(id=pk),
                        note=note_ee,
                        examen='EE',
                        ue=Ue.objects.get(id=item['ue']['id']),
                        grade=decision['grade'],
                        decision=decision['decision'],
                    )

                    notes_credit = {
                        "note": decision['mgp'],
                        "credit": item['ue']['credit'],
                        "code": item['ue']['code'],
                    }
                    concat_note += notes_credit['code']+':'+str(note_ee)+'-'
                    if(note_ee >= 35):
                        credit_capitalised_sum += item['ue']['credit']

                    all_notes_credit.append(notes_credit)
                    id_used.append(item['ue']['id'])

            note_with_credit = 0.0

            for note in all_notes_credit:
                note_with_credit += note['note']*note['credit']

            mgp = note_with_credit/credit_sum
            final_decision = 'ECHEC'

            mgp = round(mgp, 2)
            if(mgp >= 2):
                final_decision = 'ADMIS'

        # Generate number of transcript
            name_abrv = self.generate_name_initial(
                etudiant_serializer.data['name'], etudiant_serializer.data['surname'])
            abrev_faculty = school_info_serializer.data['amphi']['filiere']['faculty']['abrev']
            filiere = school_info_serializer.data['amphi']['filiere']['name'][:3]
            code_level = school_info_serializer.data['amphi']['level']['code']
            academic_year = school_info_serializer.data['amphi']['academic_year']
            inter = academic_year['name'].split('/')
            abrev_academic_year = inter[0]+inter[1][2:4]
        # end generate number of transcript

            # hash_note
            hash_info = hashlib.new('sha1')
            hash_info.update(concat_note.encode('utf-8'))
            public_hash = hash_info.hexdigest()

            transcript_number = str(nbre_transcript_print+1) + '/' + name_abrv + \
                '/'+code_level+'/'+abrev_faculty+'/'+filiere+'/'+abrev_academic_year

            msg = transcript_number+'-'+etudiant_serializer.data['matricule']+'-' + etudiant_serializer.data['name'].lower() + \
                '-' + etudiant_serializer.data['surname'].lower() + '-' + \
                str(mgp)+'-'+final_decision+'-' + public_hash
            # msg = SECRET_kEY_HASH+'-'+str(data_transcript)

            aes = AESCipher(SECRET_kEY_HASH)
            cipher = aes.encrypt(msg)

            new_transcript = Transcript.objects.create(
                etudiant=Etudiant.objects.get(id=pk),
                mgp=mgp,
                number=transcript_number,
                complete_credit=credit_capitalised_sum,
                decision=final_decision,
                cipher_info=cipher,
                hash=public_hash,
                academic_year=AcademicYear.objects.get(
                    id=school_info_serializer.data['amphi']['academic_year']['id']),
            )
            new_transcript.save()
            search_transcript_serializer = TranscriptNormalSerializer(
                new_transcript)

            return Response({
                'data': search_transcript_serializer.data,
            }, status=status.HTTP_201_CREATED)

        else:
            search_transcript_serializer = TranscriptNormalSerializer(
                search_transcript[0])
            return Response({
                'data': search_transcript_serializer.data
            })


class DecryptDataViewSet(viewsets.ModelViewSet):

    def create(self, request):
        elements = request.data
        try:
            data = elements['data']
            try:
                aes = AESCipher(SECRET_kEY_HASH)
                plaint_data = aes.decrypt(data)
                transcript_data = plaint_data.split('-')
                number = transcript_data[0]
                matricule = transcript_data[1]
                name = transcript_data[2]
                surname = transcript_data[3]
                mgp = transcript_data[4]
                decision = transcript_data[5]
                hash = transcript_data[6]

                data_transcript = {
                    "number": number,
                    "matricule": matricule,
                    "name": name,
                    "surname": surname,
                    "mgp": mgp,
                    "decision": decision,
                    "hash": hash,
                }

                info_serializers = CipherSerializer(data_transcript)
                return Response({
                    'data': info_serializers.data,
                }, status=status.HTT201_CREATED)
            except:
                return Response({
                    'detail': 'Donnees invalides'
                }, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({
                'detail': 'Donnees invalides'
            }, status=status.HTTP_400_BAD_REQUEST)


class VerifNewTranscriptViewSet(viewsets.ModelViewSet):

    def create(self, request):
        elements = request.data

        data_to_compare = elements['number']+'-'+elements['matricule']+'-' + elements['name'].lower() + \
            '-' + elements['surname'].lower() + '-' + elements['mgp'] + \
            '-'+elements['decision']+'-'+elements['hash']

        # Get student
        matricule = elements['matricule']
        number = elements['number']
        student = Etudiant.objects.filter(matricule=matricule)
        if(len(student) > 0):
            student_info = EtudiantSerializer(student[0]).data
            search = Transcript.objects.filter(
                etudiant=student_info['id']).filter(number=number)
            if(len(search) > 0):
                transcript = TranscriptSerializer(search[0]).data

                data_to_hash = transcript['number']+'-'+transcript['etudiant']['matricule']+'-' + transcript['etudiant']['name'].lower() + '-' + \
                    transcript['etudiant']['surname'].lower() + '-'+str(transcript['mgp']) + \
                    '-'+transcript['decision']+'-'+transcript['hash']
                print(data_to_hash)
                print(data_to_compare)

                # hash_note
                hash_data_to_hash = hashlib.new('sha1')
                hash_data_to_compare = hashlib.new('sha1')

                hash_data_to_hash.update(data_to_hash.encode('utf-8'))
                hash_data_to_compare.update(data_to_compare.encode('utf-8'))

                if(hash_data_to_hash.digest() == hash_data_to_compare.digest()):
                    return Response({
                        'data': transcript['id']
                    })
                else:
                    return Response({
                        'detail': 'Ce relevé n\'existe pas'
                    }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'detail': 'Ce relevé n\'existe pas'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'detail': 'Ce relevé n\'existe pas'
            }, status=status.HTTP_400_BAD_REQUEST)


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Examen.objects.all()
    serializer_class = ExamenSerializer

    def get(self, request):
        serializer = ExamenSerializer(Examen.objects.all(), many=True)
        return Response({
            "data": serializer.data
        })
