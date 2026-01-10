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

# Teste rápido
with onto:
    r1 = Room("SalaGrande", has_capacity=[100])

sync_reasoner()

if onto.LargeVenue in r1.is_a:
    print("Sucesso: SalaGrande classificada como LargeVenue")
else:
    print("Falha: SalaGrande NÃO foi classificada como LargeVenue")

