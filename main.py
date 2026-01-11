import sys
import subprocess
import datetime
from ontology import onto, Room, Course, Projector, sync_reasoner
from agents import BookingAgent, ResourceOptimizer
from owlready2 import sync_reasoner_pellet, sync_reasoner

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
    print("\n--- Fazer Reserva Detalhada ---")
    
    # 1. Pedir Informações Detalhadas
    booker_name = input("Nome da Pessoa (Quem reserva): ")
    degree_name = input("Nome do Curso (ex: LEI, MEI, LCD): ")
    subject_name = input("Nome da Disciplina (ex: CRP, IA, SD): ")
    
    if not booker_name or not subject_name: return
        
    try:
        n_input = input("Número de participantes: ")
        n_students = int(n_input)
    except ValueError: 
        print("Número inválido.")
        return

    print("\nTipo de Atividade:")
    print("1. Lecture (Aula)")
    print("2. Exam (Exame)")
    print("3. Study (Estudo)")
    type_map = {'1': 'Lecture', '2': 'Exam', '3': 'Study'}
    type_choice = input("Escolha (1-3): ")
    activity_type = type_map.get(type_choice, 'Lecture')

    # Criar a Disciplina e associar ao Curso (Grau)
    with onto:
        # Usamos o nome da disciplina como identificador do objeto Course
        # Substituímos espaços por underscores para evitar problemas no ID
        c_id = subject_name.replace(" ", "_")
        c = Course(c_id)
        c.label = [subject_name] # Guardar nome bonito no label se quiseres
        c.enrolled_students = [n_students]
        c.part_of_degree = [degree_name] # <--- Guardar o Curso Superior

    agent = BookingAgent(onto)
    
    # ... (Procura de sala igual ao anterior) ...
    needs_proj = input("\nPrecisa de projetor? (s/n): ").lower() == 's'
    eq_list = [onto.Projector] if needs_proj else []
    
    suitable = agent.find_suitable_room(n_students, eq_list)
    if not suitable:
        print("Não foram encontradas salas adequadas.")
        return
        
    print(f"\nSalas adequadas encontradas ({len(suitable)}):")
    for i, r in enumerate(suitable):
        cap = r.has_capacity[0] if r.has_capacity else 0
        eq_names = [type(eq).name for eq in r.has_equipment]
        print(f"{i+1}. {r.name} (Cap: {cap}, Equip: {eq_names})")
        
    choice = input("\nEscolha sala (0 cancelar): ")
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(suitable): return
        chosen_room = suitable[idx]
    except ValueError: return

    # Datas e Horas
    date_str = input("Data Início (AAAA-MM-DD HH:MM): ")
    if not date_str: return
    dur_str = input("Duração (HH:MM): ")
    
    try:
        start_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        if ':' in dur_str:
            h, m = map(int, dur_str.split(':'))
        else:
            h, m = int(dur_str), 0
        end_dt = start_dt + datetime.timedelta(hours=h, minutes=m)
    except ValueError:
        print("Formato inválido.")
        return

    # Chamar o agente com o novo parâmetro booker_name
    booking = agent.make_booking(
        chosen_room, start_dt, end_dt, c, 
        activity_type=activity_type, 
        booker_name=booker_name
    )
    
    if booking:
        print(f"\n✅ Reserva Confirmada!")
        print(f"   👤 {booker_name}")
        print(f"   📚 {subject_name} ({degree_name})")
        print(f"   📍 {chosen_room.name} | {start_dt} -> {end_dt}")
    else:
        print("❌ Falha: Conflito de prioridade.")

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

def list_reservations():
    print("\n--- Estado Atual das Salas ---")
    rooms = list(onto.Room.instances())
    
    if not rooms:
        print("Aviso: Não existem salas.")
        return

    for room in rooms:
        cap = room.has_capacity[0] if room.has_capacity else "N/A"
        print(f"\n📍 SALA: {room.name} (Lotação: {cap})")
        
        if not room.has_booking:
            print("   ✅ Livre")
        else:
            bookings = sorted(
                room.has_booking, 
                key=lambda x: x.start_time[0] if x.start_time else datetime.datetime.min
            )
            
            for b in bookings:
                # Recuperar dados com segurança (caso algum esteja vazio)
                start = b.start_time[0].strftime('%d/%m %H:%M') if b.start_time else "?"
                end = b.end_time[0].strftime('%H:%M') if b.end_time else "?"
                
                # Dados do Curso e Disciplina
                course_obj = b.booking_for[0] if b.booking_for else None
                subject = course_obj.name if course_obj else "S/Nome"
                # O nome do curso superior (Degree)
                degree = course_obj.part_of_degree[0] if course_obj and course_obj.part_of_degree else "Geral"
                
                # Quem reservou
                booker = b.booked_by[0].name if b.booked_by else "Sistema"
                
                print(f"   🔴 [{start}-{end}] {subject} ({degree})")
                print(f"      ↳ Reservado por: {booker}")

def check_inferences():
    print("--- A executar o Reasoner (Raciocínio Automático) ---")
    with onto:
        # Sincroniza e aplica as regras lógicas
        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
        
    print("Inferências concluídas!")
    
    # Exemplo: Listar todas as salas que o sistema descobriu serem "LargeRoom"
    print("\n Salas Grandes (Detetadas automaticamente):")
    for r in onto.LargeRoom.instances():
        print(f" -> {r.name} (Capacidade: {r.has_capacity})")

    # Exemplo: Listar salas ocupadas
    print("\n Salas Ocupadas (BusyRoom):")
    for r in onto.BusyRoom.instances():
        print(f" -> {r.name}")

def main():
    while True:
        print("\n=============================")
        print("=  SISTEMA DE GESTÃO - DEI  =")
        print("= - - - - - - - - - - - - - =")
        print("=  by Duarte Prazeres       =")
        print("=  e Marília Brito          =")
        print("=============================")
        print("1. Adicionar Sala")
        print("2. Fazer uma reserva")
        print("3. Correr o Otimizador")
        print("4. Correr o Planeamento PDDL")
        print("5. Carregar Dados de Demo (Se tiveres adicionado)")
        print("6. Consultar Reservas das Salas")
        print("7. Verificar Inferências (Reasoner)")
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
        elif op == '5':
            # populate_demo_data() # Se tiveres esta função
            pass 
        elif op == '6':
            list_reservations() # <--- CHAMADA NOVA
        elif op == '7':
            check_inferences()
        elif op == '0':
            print("A sair...")
            break
        else:
            print("Opção inválida, tente novamente.")



if __name__ == "__main__":
    main()
