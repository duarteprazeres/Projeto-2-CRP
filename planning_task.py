from unified_planning.shortcuts import *
from unified_planning.io import PDDLReader

def run_planning():
    print("--- A carregar ficheiros PDDL... ---")
    reader = PDDLReader()
    try:
        # Tenta carregar: 1º Domínio, 2º Problema
        pddl_problem = reader.parse_problem('./domain.pddl', './problem.pddl')
    except Exception as e:
        print(f"Erro ao ler ficheiros PDDL: {e}")
        print("Verifica se os ficheiros 'domain.pddl' e 'problem.pddl' estão na pasta correta.")
        return

    print("--- A resolver o problema de agendamento... ---")
    # Usamos o 'pyperplan' que já tens instalado
    with OneshotPlanner(name='pyperplan') as planner:
        result = planner.solve(pddl_problem)
        
        if result.status == unified_planning.engines.PlanGenerationResultStatus.SOLVED_SATISFICING:
            print("✅ Plano Encontrado com Sucesso!")
            print("-------------------------------------------------")
            for action in result.plan.actions:
                # Limpar a formatação para leitura fácil
                # Exemplo original: assign-exam(exam-ai, auditorium, monday, am)
                params = [str(arg) for arg in action.actual_parameters]
                exame, sala, dia, hora = params
                print(f"📅 {dia} {hora}: {exame} -> {sala}")
            print("-------------------------------------------------")
        else:
            print("❌ Não foi possível encontrar um plano.")

if __name__ == "__main__":
    run_planning()