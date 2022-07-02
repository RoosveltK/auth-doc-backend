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
from .TranscriptOperation.transcript_operation import TranscriptOperation
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
                    return Response({'detail':  "Note de l'étudiant "+item['name']+" de matricule "+item['matricule']+" assignée avec succès "}, status=status.HTTP_201_CREATED)

                else:
                    return Response({'detail': "L'étudiant "+item['name']+" de matricule "+item['matricule']+" a déja reçu une note pour cette évaluation"}, status=status.HTTP_400_BAD_REQUEST)
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
            concat_infos = ''

            # Calcul finals notes of student
            for item in allEvaluation.data:

                if item['ue']['id'] not in id_used:
                    note = Evaluation.objects.filter(
                        etudiant=pk).filter(ue=item['ue']['id'])
                    note_serializers = EvaluationSerializer(note, many=True)
                    notes = note_serializers.data

                    note_ee = TranscriptOperation.determined_intermediare_note(
                        notes)
                    decision = TranscriptOperation.get_letter_grade(note_ee)

                    Evaluation.objects.create(
                        etudiant=Etudiant.objects.get(id=pk),
                        note=note_ee,
                        examen=Examen.objects.get(code='EE'),
                        ue=Ue.objects.get(id=item['ue']['id']),
                        grade=decision['grade'],
                        decision=decision['decision'],
                    )

                    notes_credit = {
                        "note": decision['mgp'],
                        "credit": item['ue']['credit'],
                        "code": item['ue']['code'],
                    }

                    # 1 . We add Notes
                    format_note = "{:.2f}".format(note_ee)
                    concat_infos += notes_credit['code']+':' + \
                        str(format_note)+':'+str(notes_credit['credit'])+'|'

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

            # 2. add mgp and decision  to hasher info
            s = "{:.2f}".format(mgp)
            print(mgp, s)
            concat_infos += '-'+str(s)+'|'+final_decision.lower()

        # Generate number of transcript
            name_abrv = TranscriptOperation.generate_name_initial(
                etudiant_serializer.data['name'], etudiant_serializer.data['surname'])

            # 3. personnal etudiant info to hasher info
            concat_infos += '-'+etudiant_serializer.data['name'].lower() + '|'+etudiant_serializer.data['surname'].lower() + \
                '|'+etudiant_serializer.data['matricule'].lower() + \
                '|'+etudiant_serializer.data['gender'].lower() + '|' + \
                etudiant_serializer.data['born_on'] + \
                '|'+etudiant_serializer.data['born_at'].lower()

            abrev_faculty = school_info_serializer.data['amphi']['filiere']['faculty']['abrev']
            filiere = school_info_serializer.data['amphi']['filiere']['name'][:3]
            code_level = school_info_serializer.data['amphi']['level']['code']
            academic_year = school_info_serializer.data['amphi']['academic_year']
            inter = academic_year['name'].split('/')
            abrev_academic_year = inter[0]+inter[1][2:4]

            # 4. add Class info
            concat_infos += '-'+school_info_serializer.data['amphi']['filiere']['faculty']['abrev'].lower()+'|'+school_info_serializer.data['amphi']['filiere']['name'].lower(
            ) + '|'+school_info_serializer.data['amphi']['level']['intitule'].lower()+'|'+academic_year['name']

        # end generate number of transcript
            next_id = TranscriptOperation.get_next_id(Transcript)
            transcript_number = str(next_id) + '/' + name_abrv + \
                '/'+code_level+'/'+abrev_faculty+'/'+filiere+'/'+abrev_academic_year
            # 5. add transcript number
            concat_infos += '-'+transcript_number.lower()

            print(concat_infos)
            # hash_info
            hash_info = hashlib.new('sha1')
            hash_info.update(concat_infos.encode('utf-8'))
            statement_footprint = hash_info.hexdigest()
            hash_save = statement_footprint
            statement_footprint += 'ID'+str(next_id)
            aes = AESCipher(SECRET_kEY_HASH)
            cipher = aes.encrypt(statement_footprint)

            new_transcript = Transcript.objects.create(
                id=next_id,
                etudiant=Etudiant.objects.get(id=pk),
                mgp=mgp,
                number=transcript_number,
                complete_credit=credit_capitalised_sum,
                decision=final_decision,
                cipher_info=cipher,
                statement_footprint=hash_save,
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
                transcript_data = plaint_data.split('ID')
                id = transcript_data[1]
                hash = transcript_data[0]

                transcript = Transcript.objects.get(id=id)
                serial_transcript = TranscriptSerializer(transcript)

                number = serial_transcript.data['number']
                matricule = serial_transcript.data['etudiant']['matricule']
                name = serial_transcript.data['etudiant']['name']
                surname = serial_transcript.data['etudiant']['surname']
                mgp = serial_transcript.data['mgp']
                decision = serial_transcript.data['decision']

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
                }, status=status.HTTP_201_CREATED)

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
            concat_infos = ""
            student_info = EtudiantSerializer(student[0]).data
            search = Transcript.objects.filter(
                etudiant=student_info['id']).filter(number=number)
            if(len(search) > 0):
                transcript = TranscriptSerializer(search[0]).data
                get_id_exam_ee = Examen.objects.get(code='EE')
                data_to_hash = transcript['number']+'-'+transcript['etudiant']['matricule']+'-' + transcript['etudiant']['name'].lower() + '-' + \
                    transcript['etudiant']['surname'].lower() + '-'+str(transcript['mgp']) + \
                    '-'+transcript['decision']+'-' + \
                    transcript['statement_footprint']

                note = Evaluation.objects.filter(
                    etudiant=student_info['id']).filter(examen=get_id_exam_ee)

                # Concat noteabrev_academic_yeaacademic_yearrabrev_academic_yeaacademic_yearr
                if(len(note) > 0):
                    note_serializer = EvaluationSerializer(
                        note, many=True)
                    for item in note_serializer.data:
                        concat_infos += item['ue']['code']+':' + \
                            str(item['note'])+':'+str(item['ue']['credit'])+'|'
                concat_infos += '-' + \
                    str(elements['mgp'])+'|'+elements['decision'].lower()
                # add personnal info
                concat_infos += '-'+elements['name'].lower() + '|'+elements['surname'].lower() + \
                    '|'+elements['matricule'].lower().lower() + \
                    '|'+student_info['gender'].lower() + '|' + \
                    student_info['born_on'] + \
                    '|'+student_info['born_at'].lower()
                school = SchoolAt.objects.filter(etudiant=student_info['id'])
                if(len(school) > 0):
                    school_seralizer = SchoolAtSerializer(school[0])
                    concat_infos += '-'+school_seralizer.data['amphi']['filiere']['faculty']['abrev'].lower()+'|'+school_seralizer.data['amphi']['filiere']['name'].lower(
                    ) + '|'+school_seralizer.data['amphi']['level']['intitule'].lower()+'|'+school_seralizer.data['amphi']['academic_year']['name']
                concat_infos += '-'+number.lower()
                print(concat_infos)

                # hash_noteevaluations
                hash_data_to_hash = hashlib.new('sha1')
                hash_data_to_hash.update(concat_infos.encode('utf-8'))
                statement_footprint = hash_data_to_hash.hexdigest()
                print(statement_footprint)
                print(transcript['statement_footprint'])

                if(statement_footprint == transcript['statement_footprint']):
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
