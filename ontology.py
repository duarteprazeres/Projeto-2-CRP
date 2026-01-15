from owlready2 import *

# Cria uma nova ontologia
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
    class Study(Activity): pass
    
    class Course(Thing): pass
    class Equipment(Thing): pass
    class Projector(Equipment): pass

    class has_capacity(DataProperty):
        domain = [Room]
        range = [int]

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

    class EquippedRoom(Room):
        equivalent_to = [Room & has_equipment.some(Equipment)]


    class is_taught_by(ObjectProperty):
        domain = [Course]
        range = [Teacher]

    class has_activity(ObjectProperty):
        domain = [Course]
        range = [Activity]
    
    #O curso a que a disciplina pertence
    class part_of_degree(DataProperty):
        domain = [Course]
        range = [str]

    # Quem fez a reserva
    class booked_by(ObjectProperty):
        domain = [RoomBooking]
        range = [Person]

    class has_activity_type(ObjectProperty):
        domain = [RoomBooking]
        range = [Activity]

    # 5 classes inferidas (requisito 2)
    # Estas classes classificam-se sozinhas quando corremos o reasoner

    # 1. LargeRoom: Qualquer sala com capacidade >= 100
    class LargeRoom(Room):
        equivalent_to = [Room & (has_capacity >= 100)]
    
    class SmallRoom(Room):
        equivalent_to = [Room & Not(LargeRoom)]

    # 2. MultimediaRoom: Qualquer sala que tenha pelo menos um Projetor
    class MultimediaRoom(Room):
        equivalent_to = [Room & has_equipment.some(Projector)]

    # 3. BusyRoom: Uma sala que já tenha alguma reserva associada
    class BusyRoom(Room):
        equivalent_to = [Room & has_booking.some(RoomBooking)]
    
    # 4. ExamBooking: Uma reserva cuja atividade seja um Exame
    class ExamBooking(RoomBooking):
        equivalent_to = [RoomBooking & has_activity_type.some(Exam)]

    # 5. CrowdedCourse (Curso Numeroso): Curso com mais de 100 alunos
    # Útil para: Saber quais cursos PRECISAM de salas grandes.
    class CrowdedCourse(Course):
        # Nota: Precisas de garantir que a prop enrolled_students está definida no ontology.py
        equivalent_to = [Course & (enrolled_students >= 100)]
    
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

if onto.LargeRoom in r1.is_a:
    print("Sucesso: SalaGrande classificada como LargeRoom")
else:
    print("Falha: SalaGrande NÃO foi classificada como LargeRoom")

