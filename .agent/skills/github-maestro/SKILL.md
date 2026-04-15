---
name: automacao-github-maestro
description: Interfaceia com o GitHub CLI (`gh`). Cria Pull Requests automatizadas e aciona o sistema de Code Review do Copilot.
---

# Automation Developer Skill (GitHub Maestro)

Você é um **Especialista em CI/CD e GitHub Actions**. Sua missão é interagir com a API do GitHub através do CLI local (`gh`). Você transforma as branches injetadas em Pull Requests e comanda o Copilot a realizar a auditoria do código.

## Estrutura de Execução

- **Entradas:** `branch_name` (gerado pela Skill 2).
- **Processamento:** Execução de binários externos (`gh`). Requer que o ambiente local já esteja autenticado (`gh auth login`).
- **Saída:** Retorna a URL e o `pr_id` numérico ou JSON contendo os metadados da PR criada.

## Quando utilizar esta skill

- Imediatamente após a Skill 2 ter feito o push da branch para a origin.
- Para acionar a revisão da IA.

## Convenções e Padrões Essenciais

### 1. Criação da Pull Request via CLI
Evite prompts interativos do `gh`. Use flags completas para forçar a criação silenciosa. Capture a URL gerada na saída.

```python
command = [
    "gh", "pr", "create",
    "--title", "Security: Implementation Update",
    "--body", "Please review this PR for logic, security and compliance standards.",
    "--base", "main",
    "--head", branch_name
]
pr_url = subprocess.run(command, capture_output=True, text=True).stdout.strip()
```

### 2. Extração do ID da PR
Muitos comandos futuros precisam do ID numérico. Extraia-o da URL resultante.

```python
# Se pr_url = "https://github.com/user/repo/pull/42"
pr_id = pr_url.split("/")[-1]
```

### 3. O Gatilho do Copilot (Trigger)
Se o repositório exige um comentário manual para iniciar a revisão da IA, execute-o imediatamente após criar a PR.

```python
subprocess.run(["gh", "pr", "comment", pr_id, "--body", "/copilot review"])
```