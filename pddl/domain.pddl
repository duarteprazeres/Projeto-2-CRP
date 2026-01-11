(define (domain exam-scheduling)
  (:requirements :strips :typing :equality)
  (:types
    exam room day slot - object
    small-room large-room - room
    small-exam large-exam - exam
  )

  (:predicates
    (exam-at ?e - exam ?r - room ?d - day ?s - slot)
    (room-free ?r - room ?d - day ?s - slot)
    (allocated ?e - exam)
    (fits-in ?e - exam ?r - room)
    ;; Predicado auxiliar para evitar "not allocated" nas precondições
    (unallocated ?e - exam)
  )

  (:action assign-exam
    :parameters (?e - exam ?r - room ?d - day ?s - slot)
    :precondition (and
        (unallocated ?e)      ;; O exame ainda não tem sala
        (room-free ?r ?d ?s)  ;; A sala está livre
        (fits-in ?e ?r)       ;; O exame cabe na sala
    )
    :effect (and
        (allocated ?e)
        (not (unallocated ?e))
        (not (room-free ?r ?d ?s))
        (exam-at ?e ?r ?d ?s)
    )
  )
)