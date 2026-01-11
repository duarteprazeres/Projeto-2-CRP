def make_booking(self, room, start_time, end_time, course, activity_type="Lecture", booker_name="Anónimo"):
        priorities = {"Exam": 10, "Lecture": 5, "Study": 1}
        current_prio = priorities.get(activity_type, 1)

        # Verificar conflitos (Lógica igual à anterior...)
        if room.has_booking:
            for existing_booking in list(room.has_booking):
                b_start = existing_booking.start_time[0] if existing_booking.start_time else None
                b_end = existing_booking.end_time[0] if existing_booking.end_time else None
                
                if b_start and b_end:
                    if start_time < b_end and end_time > b_start:
                        # CONFLITO
                        existing_prio = 5 
                        if current_prio > existing_prio:
                            print(f"⚠️ CONFLITO RESOLVIDO: Prioridade superior. Substituindo reserva.")
                            room.has_booking.remove(existing_booking)
                            self.attempt_reallocation(existing_booking, forbidden_room=room)
                        else:
                            print(f"❌ REJEITADO: Prioridade insuficiente.")
                            return None

        # --- CRIAÇÃO DA RESERVA COM OS NOVOS DADOS ---
        new_booking = self.ontology.RoomBooking()
        new_booking.start_time = [start_time]
        new_booking.end_time = [end_time]
        new_booking.booking_for = [course]
        
        # Criar ou recuperar a Pessoa e associar à reserva
        # O owlready2 cria automaticamente se não existir
        person = self.ontology.Person(booker_name.replace(" ", "_"))
        new_booking.booked_by = [person]
        
        room.has_booking.append(new_booking)
        
        return new_booking
        # 3. Criar nova reserva (se sobreviveu às verificações)
        new_booking = self.ontology.RoomBooking()
        new_booking.start_time = [start_time]
        new_booking.end_time = [end_time]
        new_booking.booking_for = [course]

        # Criar ou recuperar a Pessoa e associar à reserva
        # O owlready2 cria automaticamente se não existir
        person = self.ontology.Person(booker_name.replace(" ", "_"))
        new_booking.booked_by = [person]
        
        # Associar à sala
        room.has_booking.append(new_booking)
        
        return new_booking