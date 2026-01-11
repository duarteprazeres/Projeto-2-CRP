from owlready2 import *

# Cria uma nova ontologia com o IRI especificado
onto = get_ontology("http://dei.uc.pt/management.owl")

with onto:
    class Room(Thing): pass
    class RoomBooking(Thing): pass

    class ConflictingBooking(RoomBooking): pass
    class AvailableRoom(Room): pass
    
    class Person(Thing): pass
    class Teacher(Person): pass
    class Student(Person): pass
    
    class Activity(Thing): pass
    class Lecture(Activity): pass
    class Exam(Activity): pass
    
    class Course(Thing): pass
    class Equipment(Thing): pass
    class Projector(Equipment): pass

    class has_capacity(DataProperty):
        domain = [Room]
        range = [int]

    class LargeVenue(Room):
        equivalent_to = [Room & (has_capacity >= 80)]

    class start_time(DataProperty):
        domain = [RoomBooking]
        range = [datetime.datetime]

    class end_time(DataProperty):
        domain = [RoomBooking]
        range = [datetime.datetime]

    class enrolled_students(DataProperty):
        domain = [Course]
        range = [int]

    class has_booking(ObjectProperty):
        domain = [Room]
        range = [RoomBooking]

    class is_booked_in(ObjectProperty):
        domain = [RoomBooking]
        range = [Room]
        inverse_property = has_booking

    class booking_for(ObjectProperty):
        domain = [RoomBooking]
        range = [Course]

    class requires_equipment(ObjectProperty):
        domain = [Activity]
        range = [Equipment]

    class has_equipment(ObjectProperty):
        domain = [Room]
        range = [Equipment]

    class MultimediaRoom(Room):
        equivalent_to = [Room & has_equipment.some(Projector)]

    class SmallRoom(Room):
        equivalent_to = [Room & Not(LargeVenue)]

    class BusyRoom(Room):
        equivalent_to = [Room & has_booking.min(1, RoomBooking)]

    class EquippedRoom(Room):
        equivalent_to = [Room & has_equipment.some(Equipment)]

    class OverBookedRoom(Room):
        pass

    # Regra SWRL para definir OverBookedRoom: enrolled_students > has_capacity
    # NOTA: O reasoner HermiT incluído no Owlready2 pode não suportar 'greaterThan'.
    # Se falhar, teremos de validar isto em Python.
    # rule = Imp()
    # rule.set_as_rule("Room(?r), has_capacity(?r, ?cap), has_booking(?r, ?b), booking_for(?b, ?c), enrolled_students(?c, ?stud), greaterThan(?stud, ?cap) -> OverBookedRoom(?r)")

    class is_taught_by(ObjectProperty):
        domain = [Course]
        range = [Teacher]

    class has_activity(ObjectProperty):
        domain = [Course]
        range = [Activity]
    
    # NOVA PROPRIEDADE: O Curso (ex: LEI, MEI) a que a disciplina pertence
    class part_of_degree(DataProperty):
        domain = [Course]
        range = [str]

    # NOVA PROPRIEDADE: Quem fez a reserva
    class booked_by(ObjectProperty):
        domain = [RoomBooking]
        range = [Person]

    class has_activity_type(ObjectProperty):
        domain = [RoomBooking]
        range = [Activity]

    # --- 5 CLASSES INFERIDAS (Requisito 2) ---
    # Estas classes classificam-se sozinhas quando corres o reasoner!

    # 1. LargeRoom: Qualquer sala com capacidade >= 100
    class LargeRoom(Room):
        equivalent_to = [Room & (has_capacity >= 100)]

    # 2. MultimediaRoom: Qualquer sala que tenha pelo menos um Projetor
    class MultimediaRoom(Room):
        equivalent_to = [Room & has_equipment.some(Projector)]

    # 3. BusyRoom: Uma sala que já tenha alguma reserva associada
    class BusyRoom(Room):
        equivalent_to = [Room & has_booking.some(RoomBooking)]

    # 4. ExamBooking: Uma reserva cuja atividade seja um Exame
    class ExamBooking(RoomBooking):
        equivalent_to = [RoomBooking & has_activity_type.some(Exam)]

    # 5. CS_Course (Curso de Informática): Cursos que pertençam ao departamento de informática (Exemplo)
    # Para simplificar, vamos criar uma inferência baseada no nome ou propriedade
    # Ou, em alternativa, uma "SmallClass" (Turma pequena)
    class SmallClass(Course):
        # Assumindo que criamos uma propriedade 'enrolled_students' no Course
        equivalent_to = [Course] 
        # Nota: Data properties em inferências complexas podem requerer o reasoner Pellet,
        # mas para o básico isto serve de placeholder.
        
    # Vamos adicionar a propriedade para o Course para suportar a inferência
    class enrolled_students(DataProperty):
        domain = [Course]
        range = [int]
        
    class CrowdedCourse(Course):
        equivalent_to = [Course & (enrolled_students >= 100)]

# Teste rápido
with onto:
    r1 = Room("SalaGrande", has_capacity=[100])

sync_reasoner()

if onto.LargeVenue in r1.is_a:
    print("Sucesso: SalaGrande classificada como LargeVenue")
else:
    print("Falha: SalaGrande NÃO foi classificada como LargeVenue")

