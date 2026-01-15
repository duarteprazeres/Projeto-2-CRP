(define (domain agendamento-universitario-simples)
    (:requirements :strips :typing) 

    (:types
        exame sala slot curso ano - object
    )

    (:predicates
        ;; Atributos estáticos
        (do_curso ?e - exame ?c - curso)
        (do_ano ?e - exame ?a - ano)
        (cabe_na_sala ?e - exame ?s - sala)
        
        ;; ESTADOS DE CONTROLO
        (agendado ?e - exame)          ;; Objetivo final: o exame está marcado
        (exame_pendente ?e - exame)    ;; Novo: O exame ainda falta marcar (Token Positivo)
        
        (sala_livre ?s - sala ?t - slot)
        
        ;; Token de disponibilidade para evitar conflitos de horário
        (curso_ano_sem_conflito ?c - curso ?a - ano ?t - slot)
    )

    (:action alocar_exame
        :parameters (?e - exame ?s - sala ?t - slot ?c - curso ?a - ano)
        :precondition (and 
            ;; Verificamos se está pendente
            (exame_pendente ?e)
            
            (do_curso ?e ?c)
            (do_ano ?e ?a)
            (sala_livre ?s ?t)
            (cabe_na_sala ?e ?s)
            (curso_ano_sem_conflito ?c ?a ?t)
        )
        :effect (and 
            (agendado ?e)
            
            ;; Consumimos o facto "pendente", logo a ação não se repete
            (not (exame_pendente ?e))
            
            (not (sala_livre ?s ?t))
            (not (curso_ano_sem_conflito ?c ?a ?t))
        )
    )
)