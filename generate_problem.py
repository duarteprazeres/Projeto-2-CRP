import math

def gerar_ficheiro_problema():
    print("--- A gerar PDDL Otimizado para Pyperplan (Regras Estritas) ---")
    
    cursos = ["LEI", "LIACD", "LDM"]
    anos = [1, 2, 3]
    disciplinas = ["ExameA", "ExameB", "ExameC", "ExameD", "ExameE"]
    
    # Definição das salas e seus tipos
    salas_tipo = {
        "Auditorio1": "grande", "Auditorio2": "grande", "Auditorio3": "grande",
        "Sala_B1": "media", "Sala_B2": "media", "Sala_B3": "media",
        "Sala_C1": "pequena", "Sala_C2": "pequena", "Sala_C3": "pequena"
    }
    
    # 10 Slots
    slots = ["seg_m", "seg_t", "ter_m", "ter_t", 
             "qua_m", "qua_t", "qui_m", "qui_t", "sex_m", "sex_t"]
    
    # Para otimizar o nosso planeamento tivemos de obrigar cada curso a ficar no seu tipo de sala. 
    # (O objetivo inicial era um curso poder ficar numa sala com capacidade igual ou superior mas o Pyperplan não lida bem com muitas opções)
    # O Pyperplan deixa de perder tempo a tentar pôr LDM (curso com menos alunos) num Auditório (sala com mais alunos).
    def verifica_cabe(curso, tipo_sala):
        if curso == "LEI": 
            return tipo_sala == "grande"    # LEI (200) só cabe em Grandes
        elif curso == "LIACD": 
            return tipo_sala == "media"     # LIACD forçamos a ir para Médias
        else: # LDM
            return tipo_sala == "pequena"   # LDM forçamos a ir para Pequenas

    with open("problem.pddl", "w") as f:
        f.write("(define (problem agendamento-otimizado)\n")
        f.write("    (:domain agendamento-universitario-simples)\n")
        f.write("    (:objects\n")
        f.write("        lei liacd ldm - curso\n")
        f.write("        ano1 ano2 ano3 - ano\n")
        f.write(f"        {' '.join(slots)} - slot\n")
        f.write(f"        {' '.join(salas_tipo.keys())} - sala\n")
        
        lista_exames = []
        for c in cursos:
            for a in anos:
                for disc in disciplinas:
                    lista_exames.append(f"{c}_{a}_{disc}")
        f.write(f"        {' '.join(lista_exames)} - exame\n")
        f.write("    )\n")

        
        f.write("    (:init\n")
        
        for exame in lista_exames:
            parts = exame.split('_')
            curso_atual = parts[0]
            ano_num = parts[1]
            
            f.write(f"        (do_curso {exame} {curso_atual.lower()}) (do_ano {exame} ano{ano_num})\n")
            f.write(f"        (exame_pendente {exame})\n") # Token positivo
            
            # Escreve apenas as salas onde o exame cabe estritamente
            for sala, tipo in salas_tipo.items():
                if verifica_cabe(curso_atual, tipo):
                    f.write(f"        (cabe_na_sala {exame} {sala})\n")

        # Salas livres
        for s in salas_tipo.keys():
            for t in slots:
                f.write(f"        (sala_livre {s} {t})\n")

        # Sem conflitos
        for c in cursos:
            for a in anos:
                for t in slots:
                    f.write(f"        (curso_ano_sem_conflito {c.lower()} ano{a} {t})\n")
        f.write("    )\n")

        
        f.write("    (:goal (and\n")
        for exame in lista_exames:
            f.write(f"        (agendado {exame})\n")
        f.write("    ))\n")
        f.write(")\n")
        
    print("✅ PDDL Otimizado Gerado (Regras estritas para performance rápida).")