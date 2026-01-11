from ontology import onto
import datetime
import random



# Agent 1: Agente de Reservas
class BookingAgent:
    def __init__(self, ontology):
        self.ontology = ontology

    def find_suitable_room(self, capacity_needed, equipment_list):
        suitable_rooms = []
        # Iterar sobre todas as instâncias de Room na ontologia
        for room in self.ontology.Room.instances():
            # Verificar capacidade (has_capacity é uma lista)
            # Assumimos 0 se não estiver definida
            room_cap = room.has_capacity[0] if room.has_capacity else 0
            
            if room_cap < capacity_needed:
                continue

            # Verificar equipamentos
            # equipment_list deve conter classes da ontologia (ex: onto.Projector)
            missing_equipment = False
            for req_eq_class in equipment_list:
                # Verificar se a sala tem alguma instância desse tipo de equipamento
                found = False
                for eq in room.has_equipment:
                    if isinstance(eq, req_eq_class):
                        found = True
                        break
                if not found:
                    missing_equipment = True
                    break
            
            if not missing_equipment:
                suitable_rooms.append(room)
                
        return suitable_rooms
    
    def is_room_free(self, room, start_time, end_time, ignore_booking=None):
        """Verifica se a sala está livre, ignorando uma reserva específica se necessário."""
        if not room.has_booking:
            return True
            
        for booking in room.has_booking:
            if booking == ignore_booking:
                continue # Ignorar a reserva que estamos a tentar mover

            b_start = booking.start_time[0] if booking.start_time else None
            b_end = booking.end_time[0] if booking.end_time else None
            
            if b_start and b_end:
                # Se há sobreposição
                if start_time < b_end and end_time > b_start:
                    return False
        return True
    
    def attempt_reallocation(self, booking_to_move, forbidden_room=None):
        """
        Procura alternativas e propõe ao utilizador (Interativo).
        O utilizador decide se aceita a sugestão ou se deixa a reserva ser cancelada.
        """
        # Proteção para obter o nome do curso
        course_name = booking_to_move.booking_for[0].name if booking_to_move.booking_for else "Desconhecido"
        print(f"   🔄 A procurar alternativas para a reserva de '{course_name}'...")
        
        # 1. Recuperar dados Originais
        course = booking_to_move.booking_for[0]
        n_students = course.enrolled_students[0] if course.enrolled_students else 0
        original_start = booking_to_move.start_time[0]
        original_end = booking_to_move.end_time[0]
        duration = original_end - original_start
        
        # 2. Identificar sala original/proibida
        current_room = forbidden_room
        if not current_room and booking_to_move.is_booked_in:
             current_room = booking_to_move.is_booked_in[0]

        # 3. Encontrar salas com capacidade suficiente
        potential_rooms = self.find_suitable_room(n_students, []) 
        
        #1a tentativa: mudar de sala (mesmo horário) 
        for room in potential_rooms:
            if room != current_room and self.is_room_free(room, original_start, original_end):
                
                # ENCONTROU ALTERNATIVA: Perguntar ao User
                print(f"\n   🔔 PROPOSTA ENCONTRADA (Mesmo Horário):")
                print(f"      Mover '{course_name}' para a sala '{room.name}' das {original_start.strftime('%H:%M')} às {original_end.strftime('%H:%M')}.")
                
                if self._ask_user_confirmation():
                    # Aceitou: Gravar
                    room.has_booking.append(booking_to_move)
                    print(f"   ✅ SUCESSO: Reserva realocada para '{room.name}'.")
                    return True
                else:
                    # Rejeitou: Sair logo (Cancela)
                    print(f"   ❌ Cancelado pelo utilizador. A reserva anterior foi removida.")
                    return False

        #2a tentativa: mudar de horário (mesma sala ou outras)
        print("   ⚠️ Não há outras salas livres no horário original. A procurar novos horários...")
        
        time_offset = datetime.timedelta(minutes=30)
        
        # Loop para verificar próximos horários (limite 10 tentativas)
        for i in range(1, 11): 
            new_start = original_start + (time_offset * i)
            new_end = new_start + duration
            
            for room in potential_rooms:
                if self.is_room_free(room, new_start, new_end):
                    
                    # alternativa encontrada- perguntar ao user
                    print(f"\n   🔔 PROPOSTA ENCONTRADA (Novo Horário):")
                    print(f"      Mover '{course_name}' para a sala '{room.name}'")
                    print(f"      Novo Horário: {new_start.strftime('%H:%M')} - {new_end.strftime('%H:%M')}")
                    
                    if self._ask_user_confirmation():
                        # aceitou: atualizar objeto e dar save
                        booking_to_move.start_time = [new_start]
                        booking_to_move.end_time = [new_end]
                        room.has_booking.append(booking_to_move)
                        
                        print(f"   ✅ SUCESSO: Remarcada para {new_start.strftime('%H:%M')} na sala '{room.name}'.")
                        return True
                    else:
                        print(f"   ❌ Cancelado pelo utilizador. A reserva anterior foi removida.")
                        return False

        print(f"   ❌ FALHA: Não foram encontradas alternativas viáveis. A reserva foi cancelada.")
        return False

    def _ask_user_confirmation(self):
        """Função auxiliar para o menu interativo (Sim/Não)"""
        while True:
            choice = input("      >> Aceita esta alteração? (s/n): ").lower().strip()
            if choice == 's':
                return True
            elif choice == 'n':
                return False
            else:
                print("      Por favor responda 's' para sim ou 'n' para não.")

    # Nota: Adicionámos o argumento 'booker_name'
    def make_booking(self, room, start_time, end_time, course, activity_type="Lecture", booker_name="Anónimo"):
        priorities = {"Exam": 10, "Lecture": 5, "Study": 1}
        current_prio = priorities.get(activity_type, 1)
        
        # Variável para guardar a reserva "expulsa", se houver
        displaced_booking = None

        # 1. verificar conflitos
        if room.has_booking:
            for existing_booking in list(room.has_booking):
                b_start = existing_booking.start_time[0] if existing_booking.start_time else None
                b_end = existing_booking.end_time[0] if existing_booking.end_time else None
                
                if b_start and b_end:
                    if start_time < b_end and end_time > b_start:
                        # conflito detetado
                        existing_prio = 5 
                        
                        if current_prio > existing_prio:
                            print(f"⚠️ CONFLITO RESOLVIDO: Prioridade superior. A substituir reserva...")
                            room.has_booking.remove(existing_booking)
                            displaced_booking = existing_booking
                        else:
                            print(f"❌ REJEITADO: Prioridade insuficiente.")
                            return None

        # 2. efetuar a nova reserva
        new_booking = self.ontology.RoomBooking()
        new_booking.start_time = [start_time]
        new_booking.end_time = [end_time]
        new_booking.booking_for = [course]
        
        # criar/recuperar pessoa
        # O replace garante que não há espaços no ID da pessoa (ex: "Duarte Prazeres" - "Duarte_Prazeres")
        person = self.ontology.Person(booker_name.replace(" ", "_"))
        new_booking.booked_by = [person]

        # Criamos um ID único para esta atividade específica para não misturar objetos
        # Ex: "Exam_InteligenciaArtificial_1030"
        
        unique_id = f"{activity_type}_{course.name}_{random.randint(1000,9999)}"
        
        if activity_type == "Exam":
            # cria uma instância única da classe Exam
            act_instance = self.ontology.Exam(unique_id)
            new_booking.has_activity_type = [act_instance]
        else:
            # cria uma instância única da classe Lecture
            act_instance = self.ontology.Lecture(unique_id)
            new_booking.has_activity_type = [act_instance]
        
        room.has_booking.append(new_booking)
        
        # 3. tentar realocar reserva expulsa, se houver
        if displaced_booking:
            self.attempt_reallocation(displaced_booking, forbidden_room=room)
        
        return new_booking
    



# Agent 2: Controlo Pedagógico
class PedagogicalControlAgent:
    def __init__(self, ontology):
        self.ontology = ontology


    def check_anti_copy(self, room, n_students, activity_type):
        """
        Regra 1: Anti-Cópia.
        Se for Exame, a capacidade efetiva é 50% (lugares intercalados).
        """
        if activity_type == "Exam":
            # Assume 0 se capacidade não definida
            cap = room.has_capacity[0] if room.has_capacity else 0
            effective_cap = cap // 2  # dividir por 2 (50%)
            
            if n_students > effective_cap:
                return False, f"Violação Anti-Cópia: Sala '{room.name}' (Cap: {cap}) só suporta {effective_cap} alunos em exame (50%). Pedido: {n_students}."
        
        return True, "OK"

    def check_daily_load(self, degree_name, date_check, additional_minutes=0):
        """
        Regra 2: Prevenção de Burnout (Com Debug e Normalização).
        """
        # Normalizar o nome do curso alvo (maiúsculas e sem espaços)
        target_degree = str(degree_name).strip().upper()
        
        print(f"\n--- Auditoria Pedagógica sobre a carga diária para {target_degree} em {date_check} ---")
        print(f"   > Carga da nova reserva: {additional_minutes} minutos")

        total_minutes = additional_minutes
        
        # Iterar sobre todas as reservas do sistema
        for booking in self.ontology.RoomBooking.instances():
            # Seguranças para dados incompletos
            if not booking.booking_for: 
                continue
            
            course = booking.booking_for[0]
            if not course.part_of_degree: 
                continue
                
            # 2. Normalizar o nome do curso da reserva existente
            existing_degree = str(course.part_of_degree[0]).strip().upper()
            
            # Se não for o curso que estamos a analisar, passa à frente
            if existing_degree != target_degree:
                continue
            
            # Verificar datas e tempos
            if booking.start_time and booking.end_time:
                b_start = booking.start_time[0]
                
                # Se for no mesmo dia
                if b_start.date() == date_check:
                    b_end = booking.end_time[0]
                    duration = (b_end - b_start).total_seconds() / 60
                    total_minutes += duration
                    
                    # Print para veres o que está a ser somado
                    start_str = b_start.strftime("%H:%M")
                    end_str = b_end.strftime("%H:%M")
                    print(f"   > Somada reserva existente: {start_str}-{end_str} ({int(duration)} min)")

        print(f"   > TOTAL ACUMULADO: {total_minutes} minutos (Máximo: 420)")
        print("------------------------------------------------")

        if total_minutes > 420: # 7h * 60 min
            hours = total_minutes / 60
            return False, f"Violação Burnout: O curso {degree_name} ficaria com {hours:.1f}h de carga (Máx: 7h)."
            
        return True, "OK"

    def check_exam_spacing(self, degree_name, date_check, new_activity_type):
        """
        Regra 3: Espaçamento de Exames.
        Não pode haver 2 exames no mesmo dia, nem em dias consecutivos.
        """
        if new_activity_type != "Exam":
            return True, "OK"
            
        # Datas proibidas: O próprio dia, o dia anterior e o dia seguinte
        forbidden_dates = [
            date_check,
            date_check - datetime.timedelta(days=1),
            date_check + datetime.timedelta(days=1)
        ]
        
        for booking in self.ontology.RoomBooking.instances():
            if not self._is_booking_for_degree(booking, degree_name):
                continue
            
            # Verificar se a reserva existente é um exame
            is_exam_existing = False
            if booking.has_activity_type:
                act = booking.has_activity_type[0]
                if isinstance(act, self.ontology.Exam):
                    is_exam_existing = True
            
            if is_exam_existing:
                if booking.start_time:
                    b_date = booking.start_time[0].date()
                    if b_date in forbidden_dates:
                        return False, f"Violação Espaçamento: Já existe um exame para {degree_name} em {b_date} (Conflito com {date_check})."

        return True, "OK"

    def check_lunch_break(self, degree_name, date_check, new_booking_start=None, new_booking_end=None):
        """
        Regra 4: Direito ao Almoço.
        Tem de haver 1h livre contínua entre 12:00 e 14:00.
        """
        lunch_start = datetime.datetime.combine(date_check, datetime.time(12, 0))
        lunch_end = datetime.datetime.combine(date_check, datetime.time(14, 0))
        
        occupied_intervals = []
        
        # 1. Adicionar reserva proposta (se houver)
        if new_booking_start and new_booking_end:
            start = max(new_booking_start, lunch_start)
            end = min(new_booking_end, lunch_end)
            if start < end:
                occupied_intervals.append((start, end))
                
        # 2. Adicionar reservas existentes
        for booking in self.ontology.RoomBooking.instances():
            if not self._is_booking_for_degree(booking, degree_name):
                continue
            
            if booking.start_time and booking.end_time:
                b_start = booking.start_time[0]
                b_end = booking.end_time[0]
                
                start = max(b_start, lunch_start)
                end = min(b_end, lunch_end)
                if start < end:
                    occupied_intervals.append((start, end))
        
        if not occupied_intervals:
            return True, "OK"
            
        # Ordenar e fundir intervalos
        occupied_intervals.sort(key=lambda x: x[0])
        merged = []
        if occupied_intervals:
            curr_start, curr_end = occupied_intervals[0]
            for next_start, next_end in occupied_intervals[1:]:
                if next_start < curr_end:
                    curr_end = max(curr_end, next_end)
                else:
                    merged.append((curr_start, curr_end))
                    curr_start, curr_end = next_start, next_end
            merged.append((curr_start, curr_end))
            
        # Verificar Gaps de 1 hora (3600 segundos)
        # Gap inicial (12h -> primeiro bloco)
        if (merged[0][0] - lunch_start).total_seconds() >= 3600: return True, "OK"
            
        # Gaps intermédios
        for i in range(len(merged) - 1):
            if (merged[i+1][0] - merged[i][1]).total_seconds() >= 3600: return True, "OK"
                
        # Gap final (último bloco -> 14h)
        if (lunch_end - merged[-1][1]).total_seconds() >= 3600: return True, "OK"
            
        return False, f"Violação Almoço: O curso {degree_name} não tem 1h contínua livre entre 12h-14h em {date_check}."

    
    def _is_booking_for_degree(self, booking, degree_name):
        if not booking.booking_for: return False
        course = booking.booking_for[0]
        if not course.part_of_degree: return False
        return course.part_of_degree[0] == degree_name

    def validate_new_booking(self, room, start_dt, end_dt, course, activity_type):
        """Valida uma nova reserva ANTES de ser criada."""
        degree = course.part_of_degree[0] if course.part_of_degree else "Geral"
        date_check = start_dt.date()
        n_students = course.enrolled_students[0] if course.enrolled_students else 0
        duration_minutes = (end_dt - start_dt).total_seconds() / 60
        
        # 1. Anti-Cópia
        ok, msg = self.check_anti_copy(room, n_students, activity_type)
        if not ok: return False, msg
        
        # 2. Burnout
        ok, msg = self.check_daily_load(degree, date_check, additional_minutes=duration_minutes)
        if not ok: return False, msg
        
        # 3. Espaçamento
        ok, msg = self.check_exam_spacing(degree, date_check, activity_type)
        if not ok: return False, msg
        
        # 4. Almoço
        ok, msg = self.check_lunch_break(degree, date_check, start_dt, end_dt)
        if not ok: return False, msg
        
        return True, "Aprovado"

    def audit_schedule(self):
        """Auditoria global para o menu principal."""
        print("\n--- 🎓 PEDAGOGICAL CONTROL AGENT: Auditoria em Curso ---")
        violations_count = 0
        checked_days_degrees = set()
        
        bookings = list(self.ontology.RoomBooking.instances())
        if not bookings:
            print("Nenhuma reserva para auditar.")
            return

        for booking in bookings:
            if not booking.booking_for: continue
            course = booking.booking_for[0]
            degree = course.part_of_degree[0] if course.part_of_degree else "N/A"
            if not booking.start_time: continue
            date_check = booking.start_time[0].date()
            
            activity_type = "Lecture"
            if booking.has_activity_type:
                if isinstance(booking.has_activity_type[0], self.ontology.Exam):
                    activity_type = "Exam"

            # Validação Individual (Anti-Cópia)
            if booking.is_booked_in:
                room = booking.is_booked_in[0]
                n_students = course.enrolled_students[0] if course.enrolled_students else 0
                ok, msg = self.check_anti_copy(room, n_students, activity_type)
                if not ok:
                    print(f"❌ {msg}")
                    violations_count += 1

            # Validações de Contexto (Uma vez por Curso/Dia)
            key = (degree, date_check)
            if key not in checked_days_degrees:
                checked_days_degrees.add(key)
                
                # Almoço
                ok, msg = self.check_lunch_break(degree, date_check)
                if not ok: print(f"❌ {msg}"); violations_count += 1
                
                # Burnout
                ok, msg = self.check_daily_load(degree, date_check)
                if not ok: print(f"❌ {msg}"); violations_count += 1

        if violations_count == 0:
            print("✅ Tudo em conformidade com as regras pedagógicas.")
        else:
            print(f"\n⚠️ Total de violações: {violations_count}")