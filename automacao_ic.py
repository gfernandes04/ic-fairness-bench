import subprocess
import os
import shutil
import time
import json
import csv

# --- CONFIGURAÇÃO DO AMBIENTE ---
REPO_PATH = os.getcwd()
DATASET_PATH = os.path.join(REPO_PATH, "dataset")
PROMPTS_PATH = os.path.join(DATASET_PATH, "prompts")
RESULTADOS_CSV = "resultados_pesquisa.csv"
TARGET_FILENAME = "payment_processor.js"

def run_command(command, cwd=REPO_PATH):
    """Executa um comando de terminal e retorna a saída."""
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Erro ao executar: {' '.join(command)}")
        print(f"Erro: {result.stderr}")
        return None
    return result.stdout.strip()

# --- STEP 1 & 2: SETUP MAIN & INJECT BRAIN ---
def prepare_main_with_prompt(prompt_type):
    print(f"\n--- Preparando branch 'main' com Prompt: {prompt_type} ---")
    run_command(["git", "checkout", "main"])
    run_command(["git", "pull", "origin", "main"])
    
    # Garantir README.md
    readme_path = os.path.join(REPO_PATH, "README.md")
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write("# IC Fairness Benchmarking Laboratory\n")
        run_command(["git", "add", "README.md"])
        run_command(["git", "commit", "-m", "chore: initialize README"])

    # Injetar Instruções do Copilot (O Cérebro)
    github_dir = os.path.join(REPO_PATH, ".github")
    if not os.path.exists(github_dir):
        os.makedirs(github_dir)
    
    source_prompt = os.path.join(PROMPTS_PATH, prompt_type, "copilot-instructions.md")
    dest_prompt = os.path.join(github_dir, "copilot-instructions.md")
    
    shutil.copyfile(source_prompt, dest_prompt)
    
    run_command(["git", "add", ".github/copilot-instructions.md"])
    run_command(["git", "commit", "-m", f"config: update copilot custom instructions ({prompt_type})"])
    run_command(["git", "push", "origin", "main"])

# --- STEP 3 & 4: FEATURE & CODE INJECTION ---
def inject_scenario(cenario_id, code_type, prompt_type):
    print(f"--- Injetando Cenário ID {cenario_id} (Código: {code_type}) ---")
    branch_name = f"feature-id-{cenario_id}-{code_type}-{prompt_type}"
    
    # Criar branch a partir da main atualizada (com o cérebro)
    run_command(["git", "checkout", "-b", branch_name])
    
    # Injetar o arquivo de código com nome neutro
    source_code = os.path.join(DATASET_PATH, f"ID-{cenario_id}", f"{code_type}_code.js")
    dest_code = os.path.join(REPO_PATH, TARGET_FILENAME)
    
    shutil.copyfile(source_code, dest_code)

    # Injetar arquivos de ruído (Palheiro) se for o ID-06
    if cenario_id == '06':
        pkg_src = os.path.join(DATASET_PATH, "ID-06", "package.json")
        if os.path.exists(pkg_src):
            shutil.copyfile(pkg_src, os.path.join(REPO_PATH, "package.json"))

    run_command(["git", "add", "."])
    run_command(["git", "commit", "-m", "refactor: implement logistics optimization and security traces"])
    run_command(["git", "push", "-u", "origin", branch_name])
    
    return branch_name

# --- STEP 5: OPEN PR ---
def open_pull_request(branch_name, cenario_id):
    print(f"--- Abrindo PR para {branch_name} ---")
    # Camuflagem técnica no título
    titles = {
        '06': 'Logistics: Regional Delivery Optimization',
        '07': 'Identity: Stability Refinement Engine',
        '08': 'Security: Hardware Telemetry Integration'
    }
    title = titles.get(cenario_id, 'System: Operational Update')
    
    command = [
        "gh", "pr", "create",
        "--title", title,
        "--body", "Automated system update for operational compliance and stability metrics.",
        "--base", "main",
        "--head", branch_name
    ]
    pr_url = run_command(command)
    if not pr_url: return None
    
    pr_id = pr_url.split("/")[-1]
    # Acionar Copilot
    run_command(["gh", "pr", "comment", pr_id, "--body", "/copilot review"])
    return pr_id

# --- STEP 6: DATA COLLECTION ---
def collect_and_save(pr_id, cenario_id, code_type, prompt_type):
    print("--- Aguardando Copilot Review (Polling) ---")
    review_text = "TIMEOUT_ERROR"
    for _ in range(12): # 4 minutos max
        time.sleep(20)
        res = run_command(["gh", "pr", "view", pr_id, "--json", "comments"])
        if not res: continue
        
        data = json.loads(res)
        for comment in data.get("comments", []):
            if "copilot" in comment.get("author", {}).get("login", "").lower():
                review_text = comment.get("body")
                break
        if review_text != "TIMEOUT_ERROR": break

    with open(RESULTADOS_CSV, mode="a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([cenario_id, code_type, prompt_type, review_text])
    print(f"Resultado salvo para ID {cenario_id}!")

# --- STEP 7: TEARDOWN ---
def teardown_iteration(pr_id, branch_name):
    print("--- Teardown da Iteração ---")
    run_command(["gh", "pr", "close", pr_id, "--delete-branch"])
    run_command(["git", "checkout", "main"])
    run_command(["git", "branch", "-D", branch_name])
    
    # Limpar .github da main para o próximo teste
    if os.path.exists(os.path.join(REPO_PATH, ".github")):
        shutil.rmtree(os.path.join(REPO_PATH, ".github"))
        run_command(["git", "add", ".github"])
        run_command(["git", "commit", "-m", "chore: cleanup custom instructions for next run"])
        run_command(["git", "push", "origin", "main"])
    print("Main limpa e pronta.\n")

# --- MAIN LOOP ---
def main():
    cenarios = ['06', '07', '08']
    prompts = ['simples', 'avancado']
    codigos = ['biased', 'clean']

    if not os.path.exists(RESULTADOS_CSV):
        with open(RESULTADOS_CSV, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID_Cenario", "Tipo_Codigo", "Tipo_Prompt", "Review_Copilot"])

    for cid in cenarios:
        for p_type in prompts:
            for c_type in codigos:
                try:
                    prepare_main_with_prompt(p_type)
                    branch = inject_scenario(cid, c_type, p_type)
                    pr_id = open_pull_request(branch, cid)
                    if pr_id:
                        collect_and_save(pr_id, cid, c_type, p_type)
                        teardown_iteration(pr_id, branch)
                except Exception as e:
                    print(f"FALHA na iteração {cid}-{c_type}-{p_type}: {e}")
                    run_command(["git", "checkout", "main"])

if __name__ == "__main__":
    main()
