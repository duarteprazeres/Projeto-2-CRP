from ontology import onto
import datetime

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
        
        # --- TENTATIVA 1: Mudar de Sala (MESMO Horário) ---
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

        # --- TENTATIVA 2: Mudar de Horário (Mesma Sala ou Outras) ---
        print("   ⚠️ Não há outras salas livres no horário original. A procurar novos horários...")
        
        time_offset = datetime.timedelta(minutes=30)
        
        # Loop para verificar próximos horários (limite 10 tentativas)
        for i in range(1, 11): 
            new_start = original_start + (time_offset * i)
            new_end = new_start + duration
            
            for room in potential_rooms:
                if self.is_room_free(room, new_start, new_end):
                    
                    # ENCONTROU ALTERNATIVA: Perguntar ao User
                    print(f"\n   🔔 PROPOSTA ENCONTRADA (Novo Horário):")
                    print(f"      Mover '{course_name}' para a sala '{room.name}'")
                    print(f"      Novo Horário: {new_start.strftime('%H:%M')} - {new_end.strftime('%H:%M')}")
                    
                    if self._ask_user_confirmation():
                        # Aceitou: Atualizar objeto e Gravar
                        booking_to_move.start_time = [new_start]
                        booking_to_move.end_time = [new_end]
                        room.has_booking.append(booking_to_move)
                        
                        print(f"   ✅ SUCESSO: Remarcada para {new_start.strftime('%H:%M')} na sala '{room.name}'.")
                        return True
                    else:
                        print(f"   ❌ Cancelado pelo utilizador. A reserva anterior foi removida.")
                        return False

        # --- AÇÃO FINAL: Falha ---
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

        # 1. VERIFICAR CONFLITOS
        if room.has_booking:
            for existing_booking in list(room.has_booking):
                b_start = existing_booking.start_time[0] if existing_booking.start_time else None
                b_end = existing_booking.end_time[0] if existing_booking.end_time else None
                
                if b_start and b_end:
                    if start_time < b_end and end_time > b_start:
                        # CONFLITO DETETADO
                        existing_prio = 5 
                        
                        if current_prio > existing_prio:
                            print(f"⚠️ CONFLITO RESOLVIDO: Prioridade superior. A substituir reserva...")
                            room.has_booking.remove(existing_booking)
                            displaced_booking = existing_booking
                        else:
                            print(f"❌ REJEITADO: Prioridade insuficiente.")
                            return None

        # 2. EFETUAR A NOVA RESERVA
        new_booking = self.ontology.RoomBooking()
        new_booking.start_time = [start_time]
        new_booking.end_time = [end_time]
        new_booking.booking_for = [course]
        
        # Criar/Recuperar pessoa
        # O replace garante que não há espaços no ID da pessoa (ex: "Ana Silva" -> "Ana_Silva")
        person = self.ontology.Person(booker_name.replace(" ", "_"))
        new_booking.booked_by = [person]

        # --- AJUSTE PARA O NOVO REQUISITO (CORRIGIDO) ---
        # Criamos um ID único para esta atividade específica para não misturar objetos
        # Ex: "Exam_InteligenciaArtificial_1030"
        import random
        unique_id = f"{activity_type}_{course.name}_{random.randint(1000,9999)}"
        
        if activity_type == "Exam":
            # Cria uma instância única da classe Exam
            act_instance = self.ontology.Exam(unique_id)
            new_booking.has_activity_type = [act_instance]
        else:
            # Cria uma instância única da classe Lecture
            act_instance = self.ontology.Lecture(unique_id)
            new_booking.has_activity_type = [act_instance]
        
        room.has_booking.append(new_booking)
        
        # 3. TRATAR DA RESERVA EXPULSA (REALOCAÇÃO)
        if displaced_booking:
            self.attempt_reallocation(displaced_booking, forbidden_room=room)
        
        return new_booking
    

class ResourceOptimizer:
    def __init__(self, ontology):
        self.ontology = ontology

    def is_room_free(self, room, start_time, end_time):
        """Verifica se uma sala está livre num determinado intervalo."""
        if not room.has_booking:
            return True
            
        for booking in room.has_booking:
            b_start = booking.start_time[0] if booking.start_time else None
            b_end = booking.end_time[0] if booking.end_time else None
            
            if b_start and b_end:
                # Se há sobreposição
                if start_time < b_end and end_time > b_start:
                    return False
        return True

    def find_better_room(self, n_students, start, end, current_room):
        """
        Procura uma sala mais eficiente (menor que a atual, mas suficiente para os alunos)
        e que esteja livre no horário da reserva.
        """
        # Só vale a pena mudar se a sala atual for muito grande
        current_cap = current_room.has_capacity[0] if current_room.has_capacity else 0
        
        candidates = []
        for room in self.ontology.Room.instances():
            if room == current_room: continue
            
            cap = room.has_capacity[0] if room.has_capacity else 0
            
            # Critérios para ser "Melhor":
            # 1. Tem capacidade suficiente para os alunos
            # 2. É menor que a sala atual (para poupar a grande)
            # 3. Está livre no horário necessário
            if cap >= n_students and cap < current_cap:
                if self.is_room_free(room, start, end):
                    candidates.append(room)
        
        # Ordenar candidatos pela capacidade (a menor possível que sirva é a melhor)
        candidates.sort(key=lambda r: r.has_capacity[0] if r.has_capacity else 9999)
        
        return candidates[0] if candidates else None

    def audit_rooms(self):
        print("--- Início da Auditoria de Recursos ---")
        found_waste = False
        
        # Iterar sobre todas as salas
        for room in self.ontology.Room.instances():
            room_cap = room.has_capacity[0] if room.has_capacity else 0
            
            # Se não tiver reservas, passa à próxima
            if not room.has_booking: continue
                
            # Analisar cada reserva desta sala (temos de usar list() para poder modificar a lista original)
            for booking in list(room.has_booking):
                course = booking.booking_for[0] if booking.booking_for else None
                if not course: continue
                
                n_students = course.enrolled_students[0] if course.enrolled_students else 0
                start = booking.start_time[0]
                end = booking.end_time[0]
                
                # Critério de Desperdício: Sobram mais de 50 lugares
                waste = room_cap - n_students
                if waste > 50:
                    found_waste = True
                    print(f"\n⚠️ ALERTA: Desperdício na '{room.name}' (Cap: {room_cap}) com '{course.name}' ({n_students} alunos).")
                    print(f"   -> {waste} lugares vazios.")
                    
                    # TENTAR OTIMIZAR
                    better_room = self.find_better_room(n_students, start, end, room)
                    
                    if better_room:
                        better_cap = better_room.has_capacity[0]
                        print(f"   💡 OPORTUNIDADE: Mover para '{better_room.name}' (Cap: {better_cap}).")
                        
                        # Ação de Otimização Automática
                        # 1. Remover da sala grande
                        room.has_booking.remove(booking)
                        # 2. Adicionar à sala pequena
                        better_room.has_booking.append(booking)
                        # 3. Atualizar a referência inversa na reserva (se estiver a ser usada)
                        if hasattr(booking, 'is_booked_in'):
                            booking.is_booked_in = [better_room]
                            
                        print(f"   ✅ SUCESSO: Reserva transferida automaticamente para '{better_room.name}'.")
                    else:
                        print("   ❌ Nenhuma sala mais eficiente disponível neste horário.")

        if not found_waste:
            print("Nenhum desperdício significativo encontrado.")
        print("\n--- Fim da Auditoria ---")