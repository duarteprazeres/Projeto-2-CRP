import sys
import subprocess
import datetime
from ontology import onto, Room, Course, Projector, sync_reasoner
from agents import BookingAgent, ResourceOptimizer

def add_room():
    print("\n--- Adicionar Sala ---")
    name = input("Nome da sala: ")
    if not name:
        return
        
    try:
        cap_input = input("Capacidade: ")
        cap = int(cap_input)
    except ValueError:
        print("Capacidade inválida.")
        return

    has_proj = input("Tem projetor? (s/n): ").lower() == 's'

    with onto:
        # Verifica se já existe
        existing = onto.search(iri=f"*{name}")
        if existing and any(isinstance(x, Room) for x in existing):
             print(f"Aviso: Já existe algo com nome '{name}'. Criando mesmo assim...")

        r = Room(name)
        r.has_capacity = [cap]
        
        if has_proj:
            # Cria uma instância de projetor para esta sala
            proj = Projector(f"Projector_{name}")
            r.has_equipment.append(proj)

    # Tenta sincronizar o reasoner para classificar (LargeVenue, etc.)
    try:
        print("Sincronizando Reasoner...")
        sync_reasoner()
    except Exception as e:
        print(f"Aviso: Reasoner falhou ou não configurado corretamente: {e}")

    print(f"Sala '{name}' criada com sucesso.")

def make_reservation():
    print("\n--- Fazer Reserva ---")
    course_name = input("Nome do Curso: ")
    if not course_name:
        return
        
    try:
        n_input = input("Número de alunos inscritos: ")
        n_students = int(n_input)
    except ValueError: 
        print("Número inválido.")
        return

    # Criar instância de curso na ontologia
    with onto:
        c = Course(course_name)
        c.enrolled_students = [n_students]
    
    agent = BookingAgent(onto)
    
    # Perguntar requisitos
    needs_proj = input("Precisa de projetor? (s/n): ").lower() == 's'
    eq_list = [onto.Projector] if needs_proj else []
    
    # Encontrar salas adequadas
    suitable = agent.find_suitable_room(n_students, eq_list)
    
    if not suitable:
        print("Não foram encontradas salas adequadas.")
        return
        
    print(f"\nSalas adequadas encontradas ({len(suitable)}):")
    for i, r in enumerate(suitable):
        cap = r.has_capacity[0] if r.has_capacity else 0
        
        # Listar equipamentos de forma legível
        eq_names = []
        for eq in r.has_equipment:
            # Pega o nome da classe do equipamento (ex: Projector)
            eq_names.append(type(eq).name)
            
        print(f"{i+1}. {r.name} (Cap: {cap}, Equip: {eq_names})")
        
    choice = input("\nEscolha o número da sala para reservar (0 para cancelar): ")
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(suitable):
            print("Cancelado.")
            return
        chosen_room = suitable[idx]
    except ValueError:
        print("Inválido.")
        return

    # Pedir datas
    # Formato sugerido: AAAA-MM-DD HH:MM
    date_str = input("Data e Hora de Início (AAAA-MM-DD HH:MM): ")
    duration_input = input("Duração em horas (ex: 1.5): ")
    
    try:
        start_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        duration = float(duration_input)
        end_dt = start_dt + datetime.timedelta(hours=duration)
    except ValueError:
        print("Formato de data ou duração inválido.")
        return
        
    booking = agent.make_booking(chosen_room, start_dt, end_dt, c)
    if booking:
        print(f"Reserva efetuada com sucesso para sala '{chosen_room.name}'.")
    else:
        print("Não foi possível efetuar a reserva (conflito de horário).")

def run_optimizer():
    print("\n--- Correr Otimizador ---")
    opt = ResourceOptimizer(onto)
    opt.audit_rooms()

def run_pddl():
    print("\n--- Correr Planeamento PDDL ---")
    print("Executando 'planning_task.py'...")
    try:
        # Executa o script existente num sub-processo
        subprocess.run([sys.executable, "planning_task.py"], check=True)
    except Exception as e:
        print(f"Erro ao executar script PDDL: {e}")

def main():
    while True:
        print("\n===========================")
        print("   SISTEMA DE GESTÃO - G4   ")
        print("===========================")
        print("1. Adicionar Sala")
        print("2. O Agente fazer uma reserva")
        print("3. Correr o Otimizador")
        print("4. Correr o Planeamento PDDL")
        print("0. Sair")
        
        op = input("\nOpção: ")
        
        if op == '1':
            add_room()
        elif op == '2':
            make_reservation()
        elif op == '3':
            run_optimizer()
        elif op == '4':
            run_pddl()
        elif op == '0':
            print("A sair...")
            break
        else:
            print("Opção inválida, tente novamente.")

if __name__ == "__main__":
    main()
