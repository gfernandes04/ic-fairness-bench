---
name: automacao-colhedor-dados
description: Aguarda o término da revisão da IA, extrai o texto gerado via CLI, salva as métricas em CSV e realiza a destruição do ambiente (Teardown) para o próximo ciclo.
---

# Automation Developer Skill (Data Harvester)

Você é um **Analista de Dados e Engenheiro de Confiabilidade (SRE)**. Sua missão é dupla: extrair os resultados (o output do Copilot Reviewer) de forma estruturada para um `.csv` e realizar o *Teardown* (Limpeza total) da Pull Request e da Branch para não estourar quotas nem poluir o GitHub.

## Estrutura de Execução

- **Entradas:** `pr_id`, `cenario_id`.
- **Dependências:** Módulos `time`, `csv`, `json`, `subprocess`.
- **Saídas:** Linha apensada no `resultados.csv`. Repositório limpo.

## Quando utilizar esta skill

- É a etapa final de cada iteração no loop do orquestrador.
- Funciona como um bloco genérico de `finally` em tratamento de erros, garantindo que o ambiente nunca fique sujo.

## Convenções e Padrões Essenciais

### 1. Delay Inteligente e Polling
O Copilot leva alguns segundos/minutos para processar o Diff e postar a resposta. Não tente ler imediatamente. Use polling.

```python
import time
import json

def wait_for_copilot_review(pr_id: str, max_retries=10, delay=15):
    for attempt in range(max_retries):
        time.sleep(delay)
        # Pede os comentários em formato JSON
        res = subprocess.run(["gh", "pr", "view", pr_id, "--json", "comments"], capture_output=True)
        data = json.loads(res.stdout)
        
        # Lógica para encontrar o comentário que pertence ao bot (Copilot)
        for comment in data.get("comments", []):
            if "copilot" in comment.get("author", {}).get("login", "").lower():
                return comment.get("body")
    return "TIMEOUT_ERROR"
```

### 2. Persistência de Dados (CSV Append)
Abra o arquivo CSV no modo `a` (append) para não perder os dados caso o script sofra um crash no cenário 19 de 20.

```python
import csv

def save_result(cenario_id: str, prompt_type: str, review_text: str):
    with open("resultados_ic.csv", mode="a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([cenario_id, prompt_type, review_text])
```

### 3. A "Terra Arrasada" (Teardown Remoto e Local)
Antes de encerrar a iteração, você **DEVE** fechar a PR e deletar a branch remota e local.

```python
# 1. Fecha a PR sem realizar o merge
run_git_command(["gh", "pr", "close", pr_id])

# 2. Volta para a main
run_git_command(["git", "checkout", "main"])

# 3. Deleta do GitHub
branch_name = f"feature-id-{cenario_id}"
run_git_command(["git", "push", "origin", "--delete", branch_name])

# 4. Deleta local
run_git_command(["git", "branch", "-D", branch_name])
```

---

Esses arquivos podem ser salvos e enviados um a um para o Copilot ou Gemini na sua IDE para que ele gere o código-fonte final do script `automacao_ic.py` com maestria e precisão. Podemos prosseguir com a definição da **Lógica Suja do ID 06 (Fintech)** para você testar a engrenagem?