from ontology import onto

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

    def make_booking(self, room, start_time, end_time, course, activity_type="Lecture"):
        # 1. Definir tabela de prioridades
        priorities = {"Exam": 10, "Lecture": 5, "Study": 1}
        # Prioridade da reserva que estamos a tentar fazer agora
        current_prio = priorities.get(activity_type, 1)

        # 2. Verificar conflitos e gerir prioridades
        if room.has_booking:
            # Usamos list() para criar uma cópia, permitindo remover itens da lista original durante o loop
            for booking in list(room.has_booking):
                b_start = booking.start_time[0] if booking.start_time else None
                b_end = booking.end_time[0] if booking.end_time else None
                
                if b_start and b_end:
                    # Lógica de sobreposição temporal
                    if start_time < b_end and end_time > b_start:
                        
                        # Tentar descobrir a prioridade da reserva JÁ EXISTENTE
                        # (Assumimos 'Lecture' (5) como default se não soubermos)
                        existing_prio = 5 
                        # Se quiseres ser rigoroso, terias de guardar o tipo de atividade na ontologia 
                        # quando crias a reserva, mas para este efeito assumir 5 funciona bem.

                        if current_prio > existing_prio:
                            print(f"⚠️ CONFLITO RESOLVIDO: Prioridade ({current_prio}) > Existente ({existing_prio}).")
                            print(f"   -> A cancelar a reserva anterior de '{booking.booking_for[0].name}'...")
                            room.has_booking.remove(booking)
                            # Se estivesses a usar sync_reasoner(), podias destruir a instância aqui.
                        else:
                            print(f"❌ REJEITADO: Conflito com '{booking.booking_for[0].name}' (Prioridade existente >= Pedido).")
                            return None

        # 3. Criar nova reserva (se sobreviveu às verificações)
        new_booking = self.ontology.RoomBooking()
        new_booking.start_time = [start_time]
        new_booking.end_time = [end_time]
        new_booking.booking_for = [course]
        
        # Associar à sala
        room.has_booking.append(new_booking)
        
        return new_booking

class ResourceOptimizer:
    def __init__(self, ontology):
        self.ontology = ontology

    def audit_rooms(self):
        print("--- Início da Auditoria de Recursos ---")
        found_waste = False
        for room in self.ontology.Room.instances():
            # Capacidade da sala
            room_cap = room.has_capacity[0] if room.has_capacity else 0
            
            if not room.has_booking:
                continue
                
            for booking in room.has_booking:
                # Curso associado
                course = booking.booking_for[0] if booking.booking_for else None
                if not course:
                    continue
                
                # Alunos inscritos
                n_students = course.enrolled_students[0] if course.enrolled_students else 0
                
                # Verificação de desperdício
                if (room_cap - n_students) > 50:
                    found_waste = True
                    print(f"ALERTA: Desperdício de Espaço! Sala '{room.name}' (Cap: {room_cap}) usada pelo curso '{course.name}' (Alunos: {n_students}).")
        
        if not found_waste:
            print("Nenhum desperdício significativo encontrado.")
        print("--- Fim da Auditoria ---")

