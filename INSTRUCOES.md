# Guia de Utilização - Sistema de Gestão de Salas

Este guia explica como utilizar o script `main.py` para testar as funcionalidades do projeto (Ontologia, Agentes e Planeamento).

## 1. Como Iniciar
No terminal, certifique-se que o ambiente virtual está ativo e execute:
```bash
python main.py
```

## 2. Roteiro de Teste Sugerido

Siga estes passos para ver todas as funcionalidades em ação:

### Passo 1: Adicionar Sala (Opção 1)
O sistema começa vazio (ou apenas com o que está no código base). Vamos adicionar uma sala real.
1. No menu, digite `1` e Enter.
2. **Nome da sala**: Digite `Anfiteatro_A`.
3. **Capacidade**: Digite `100`.
4. **Tem projetor?**: Digite `s`.
   * *O que acontece nos bastidores*: O sistema cria a sala na ontologia. O *Reasoner* corre e classifica-a automaticamente como `LargeVenue` (porque >80 lugares) e `MultimediaRoom` (porque tem projetor).

### Passo 2: Fazer uma Reserva com Sucesso (Opção 2)
Vamos usar o Agente de Reservas.
1. Escolha `2`.
2. **Nome do Curso**: `Inteligência Artificial`.
3. **Número de alunos**: `90`.
4. **Precisa de projetor?**: `s`.
   * O Agente procura na ontologia salas com capacidade >= 90 e com projetor.
   * Deve aparecer uma lista com as salas encontradas. Exemplo: `1. Anfiteatro_A (Cap: 100, ...)`.
5. **Escolha o número da sala**: Digite o número que aparece no início da linha da sala desejada (neste caso, `1`) e Enter.
6. **Data e Hora**: Digite `2025-01-20 09:00` (Respeite o formato AAAA-MM-DD HH:MM).
7. **Duração**: `2`.
   * *Resultado*: Reserva efetuada com sucesso.

### Passo 3: Testar Conflitos (Opção 2)
Vamos tentar criar um conflito na mesma sala.
1. Escolha `2` novamente.
2. **Curso**: `Bases de Dados`.
3. **Alunos**: `85`.
4. **Projetor**: `s`.
5. Escolha a mesma sala (`Anfiteatro_A`).
6. **Data e Hora**: `2025-01-20 10:00` (Repare que se sobrepõe à anterior que era das 09:00 às 11:00).
7. **Duração**: `1`.
   * *Resultado*: O Agente deteta que `10:00` está ocupado (já que a anterior acaba às 11:00) e **recusa** a reserva.

### Passo 4: Detetar Desperdício (Opção 3)
Vamos criar uma situação de má gestão.
1. Adicione uma nova sala (Opção 1) chamada `Sala_Pequena`, capacidade `120`, sem projetor.
2. Faça uma reserva (Opção 2) nesta `Sala_Pequena` para um curso com apenas `10` alunos.
3. Agora, escolha a **Opção 3** (Correr Otimizador).
   * *Resultado*: O `ResourceOptimizer` vai auditar todas as reservas e imprimir um **ALERTA** dizendo que há desperdício na `Sala_Pequena` (Capacidade 120 vs 10 alunos = 110 lugares vazios).

### Passo 5: Planeamento Automático (Opção 4)
Esta opção corre o script `planning_task.py` que usa PDDL.
1. Escolha `4`.
   * *Resultado*: O sistema usa a biblioteca `unified-planning` para gerar um plano lógico de alocação de exames a salas e dias. Verá um output como `plan found: [assign_exam(e1, r1, d1), ...]`.
