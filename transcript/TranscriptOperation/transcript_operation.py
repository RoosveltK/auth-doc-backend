from django.db import connection


class TranscriptOperation:

    @staticmethod
    def generate_name_initial(name, surname):
        full_name = name + ' '+surname
        full_name_split = full_name.split()
        name_size = len(full_name_split) - 1
        i = 0
        initial = ''
        while(name_size >= i):
            initial += full_name_split[i][0][:1]
            i += 1
        return initial[:3]

    @staticmethod
    def determined_intermediare_note(notes):
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

    @staticmethod
    def get_letter_grade(notefinale):
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

    @staticmethod
    def get_next_id(model_class):
        cursor = connection.cursor()
        cursor.execute("select nextval('%s_id_seq')" %
                       model_class._meta.db_table)
        row = cursor.fetchone()
        cursor.close()
        return row[0]
