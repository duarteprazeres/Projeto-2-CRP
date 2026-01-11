from unified_planning.shortcuts import *
from unified_planning.io import PDDLReader
# Import necessário para o status
from unified_planning.engines.results import PlanGenerationResultStatus

# Se tiveres a função de gerar o problema neste ficheiro ou importada, chama-a aqui.
# from generate_problem import gerar_ficheiro_problema_otimizado

def run_planning():
    # Descomenta a linha abaixo se quiseres gerar o ficheiro sempre que corres
    # gerar_ficheiro_problema_otimizado()
    
    print("--- A carregar ficheiros PDDL... ---")
    reader = PDDLReader()
    try:
        pddl_problem = reader.parse_problem('./domain.pddl', './problem.pddl')
    except Exception as e:
        print(f"Erro ao ler ficheiros PDDL: {e}")
        return

    print("--- A resolver o problema de agendamento... ---")
    
    with OneshotPlanner(name='pyperplan') as planner:
        result = planner.solve(pddl_problem)
        
        # CORREÇÃO 1: Usa diretamente a classe importada
        if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
            print("✅ Plano Encontrado com Sucesso!")
            print("-------------------------------------------------")
            
            for action in result.plan.actions:
                # Converter parâmetros para string
                params = [str(arg) for arg in action.actual_parameters]
                
                # CORREÇÃO 2: Mapeamento correto dos 5 parâmetros do PDDL
                # A ordem no domain.pddl é: (?e ?s ?t ?c ?a)
                exame = params[0]
                sala = params[1]
                slot = params[2]
                curso = params[3]
                ano = params[4]
                
                print(f"📅 {slot} | {exame} ({curso} {ano}) -> 📍 {sala}")
            
            print("-------------------------------------------------")
        else:
            print("❌ Não foi possível encontrar um plano.")

if __name__ == "__main__":
    run_planning()