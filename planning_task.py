z< import unified_planning
from unified_planning.shortcuts import UserType, Fluent, InstantaneousAction, BoolType, Problem, Object, Or

# Define UserTypes
Exam = UserType('Exam')
Room = UserType('Room')
Day = UserType('Day')

# Define Fluents
exam_at = Fluent('exam_at', BoolType(), exam=Exam, room=Room, day=Day)
room_free = Fluent('room_free', BoolType(), room=Room, day=Day)
is_allocated = Fluent('is_allocated', BoolType(), exam=Exam)

# Define Action
assign_exam = InstantaneousAction('assign_exam', exam=Exam, room=Room, day=Day)
assign_exam.add_precondition(room_free(assign_exam.room, assign_exam.day))
assign_exam.add_effect(exam_at(assign_exam.exam, assign_exam.room, assign_exam.day), True)
assign_exam.add_effect(room_free(assign_exam.room, assign_exam.day), False)
assign_exam.add_effect(is_allocated(assign_exam.exam), True)

# Define Problem
problem = Problem('exam_scheduling')
problem.add_fluent(exam_at, default_initial_value=False)
problem.add_fluent(room_free, default_initial_value=False)
problem.add_fluent(is_allocated, default_initial_value=False)
problem.add_action(assign_exam)

# Objects
e1 = Object('e1', Exam)
e2 = Object('e2', Exam)
e3 = Object('e3', Exam)
r1 = Object('r1', Room)
r2 = Object('r2', Room)
d1 = Object('d1', Day)
d2 = Object('d2', Day)

problem.add_objects([e1, e2, e3, r1, r2, d1, d2])

# Initial State
for r in [r1, r2]:
    for d in [d1, d2]:
         problem.set_initial_value(room_free(r, d), True)

# Goals
for e in [e1, e2, e3]:
    problem.add_goal(is_allocated(e))

# Solve
from unified_planning.shortcuts import OneshotPlanner

with OneshotPlanner(name='pyperplan') as planner:
    result = planner.solve(problem)
    if result.status == unified_planning.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
        print("Plan found:")
        for action in result.plan.actions:
            print(action)
    else:
        print("No plan found.")

