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
                # se há sobreposição
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
            # 1 - Ter capacidade suficiente para os alunos
            # 2 - Ser menor que a sala atual (para poupar a grande)
            # 3 - Estar livre no horário necessário
            if cap >= n_students and cap < current_cap:
                if self.is_room_free(room, start, end):
                    candidates.append(room)
        
        # ordenar candidatos pela capacidade (a menor possível que sirva é a melhor)
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
                
            # Analisar cada reserva desta sala 
            for booking in list(room.has_booking):
                course = booking.booking_for[0] if booking.booking_for else None
                if not course: continue
                
                n_students = course.enrolled_students[0] if course.enrolled_students else 0
                start = booking.start_time[0]
                end = booking.end_time[0]
                
                # critério de desperdício: sobram mais de 50 lugares
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