import random

def generate_pddl_problem(filename="problem.pddl"):
    # --- CONFIGURAÇÃO DO CENÁRIO ---
    # 1. Definição do Tempo (1 semana = 5 dias x 2 slots)
    days = ["mon", "tue", "wed", "thu", "fri"]
    slots = ["am", "pm"]
    
    # 2. Definição das Salas (Total: 6 salas)
    # Tuplas: (Nome, Tipo)
    rooms = [
        ("auditorium-a", "large-room"), 
        ("auditorium-b", "large-room"),
        ("room-101", "small-room"),
        ("room-102", "small-room"),
        ("room-103", "small-room"),
        ("lab-c", "small-room")
    ]
    
    # 3. Definição dos Exames (Total: 15 exames)
    # Vamos gerar nomes genéricos como exam-1, exam-2...
    large_exams = [f"exam-l-{i}" for i in range(1, 6)]   # 5 Exames Grandes
    small_exams = [f"exam-s-{i}" for i in range(1, 11)]  # 10 Exames Pequenos
    
    all_exams = large_exams + small_exams

    # --- ESCRITA DO FICHEIRO ---
    with open(filename, "w") as f:
        f.write("(define (problem semester-exams)\n")
        f.write("  (:domain exam-scheduling)\n")
        
        # 1. OBJECTS
        f.write("  (:objects\n")
        # Escrever Exames
        f.write(f"    {' '.join(large_exams)} - large-exam\n")
        f.write(f"    {' '.join(small_exams)} - small-exam\n")
        # Escrever Salas
        l_rooms = [r[0] for r in rooms if r[1] == "large-room"]
        s_rooms = [r[0] for r in rooms if r[1] == "small-room"]
        f.write(f"    {' '.join(l_rooms)} - large-room\n")
        f.write(f"    {' '.join(s_rooms)} - small-room\n")
        # Escrever Tempo
        f.write(f"    {' '.join(days)} - day\n")
        f.write(f"    {' '.join(slots)} - slot\n")
        f.write("  )\n\n")

        # 2. INIT
        f.write("  (:init\n")
        
        # Estado Inicial: Exames por alocar
        for exam in all_exams:
            f.write(f"    (unallocated {exam})\n")
        
        f.write("\n")

        # Estado Inicial: Salas livres (Todas as salas x Todos os dias x Todos os slots)
        for r_name, _ in rooms:
            for d in days:
                for s in slots:
                    f.write(f"    (room-free {r_name} {d} {s})\n")

        f.write("\n")

        # Capacidades (Quem cabe onde)
        # Regra: Salas Grandes levam TUDO. Salas Pequenas só levam exames pequenos.
        
        # Lógica para Salas Grandes (Aceitam Large e Small exams)
        for r_name in l_rooms:
            for exam in all_exams:
                f.write(f"    (fits-in {exam} {r_name})\n")
        
        # Lógica para Salas Pequenas (Aceitam APENAS Small exams)
        for r_name in s_rooms:
            for exam in small_exams:
                f.write(f"    (fits-in {exam} {r_name})\n")
                
        f.write("  )\n\n")

        # 3. GOAL
        f.write("  (:goal\n")
        f.write("    (and\n")
        for exam in all_exams:
            f.write(f"      (allocated {exam})\n")
        f.write("    )\n")
        f.write("  )\n")
        f.write(")\n")

    print(f"✅ Ficheiro '{filename}' gerado com sucesso!")
    print(f"   - {len(all_exams)} Exames")
    print(f"   - {len(rooms)} Salas")
    print(f"   - {len(days) * len(slots) * len(rooms)} Slots totais disponíveis")

if __name__ == "__main__":
    generate_pddl_problem()