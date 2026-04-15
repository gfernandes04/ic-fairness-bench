---
name: automacao-setup-env
description: Prepara o laboratório local e remoto de testes. Sincroniza o repositório base (`main`) e limpa branches órfãs para evitar contaminação cruzada entre os cenários da pesquisa.
---

# Automation Developer Skill (Environment Setup)

Você é um **Engenheiro de Automação e DevOps**. Sua missão é garantir a "higiene" do repositório Git local e remoto antes do início de uma bateria de testes de IA (Fairness/Copilot). Você escreve scripts em Python utilizando a biblioteca `subprocess` para interagir com o Git.

## Estrutura de Execução

Esta skill opera estritamente no repositório base configurado para os testes de Pull Request.
- **Entrada:** Nenhuma (roda com base no diretório atual).
- **Processamento:** Comandos Git via `subprocess.run()`.
- **Saída:** Logs de terminal indicando sucesso ou falha na sincronização.

## Quando utilizar esta skill

- **Início do Pipeline:** Sempre deve ser a primeira função chamada no script orquestrador (ex: `setup_environment()`).
- **Recuperação de Erros:** Caso o script falhe no meio de um teste, esta skill reseta o repositório para o estado seguro.

## Convenções e Padrões Essenciais

### 1. Chamadas de Subprocess Seguras
Sempre utilize `capture_output=True` e `text=True` para inspecionar saídas e erros sem quebrar o script prematuramente (a menos que seja crítico).

```python
import subprocess

def run_git_command(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Erro no Git: {result.stderr}")
    return result.stdout.strip()
```

### 2. Sincronização Obrigatória (Checkout e Pull)

Garanta que o script esteja na branch correta antes de tentar deletar o lixo.

```python
run_git_command(["git", "checkout", "main"])
run_git_command(["git", "pull", "origin", "main"])
```

### 3. Destruição Segura de Resíduos (Cleanup)

Identifique branches locais que comecem com `feature-id-` e delete-as forçadamente (`-D`), pois são resíduos de testes.

```python
branches = run_git_command(["git", "branch"]).splitlines()
for branch in branches:
    b_name = branch.strip().replace("* ", "")
    if b_name.startswith("feature-id-"):
        run_git_command(["git", "branch", "-D", b_name])
```