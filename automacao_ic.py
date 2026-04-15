import subprocess
import os
import shutil
import time
import json
import csv

# --- CONFIGURAÇÃO DO AMBIENTE ---
# Caminho para o repositório onde as PRs serão abertas (Diretório Atual)
REPO_PATH = os.getcwd()
DATASET_PATH = os.path.join(REPO_PATH, "dataset")
RESULTADOS_CSV = "resultados_pesquisa.csv"
TARGET_FILENAME = "payment_processor.js"  # Nome neutro para o arquivo no repositório

def run_command(command, cwd=REPO_PATH):
    """Executa um comando de terminal e retorna a saída."""
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Erro ao executar: {' '.join(command)}")
        print(f"Erro: {result.stderr}")
        return None
    return result.stdout.strip()

# --- SKILL 1: SETUP ---
def setup_environment():
    print("\n--- Iniciando Setup do Ambiente ---")
    run_command(["git", "checkout", "main"])
    run_command(["git", "pull", "origin", "main"])
    
    # Limpeza de branches residuais
    branches = run_command(["git", "branch"]).splitlines()
    for branch in branches:
        b_name = branch.strip().replace("* ", "")
        if b_name.startswith("feature-id-"):
            print(f"Limpando branch residual: {b_name}")
            run_command(["git", "branch", "-D", b_name])

# --- SKILL 2: INJETOR ---
def inject_scenario(cenario_id, test_type):
    print(f"\n--- Injetando Cenário ID {cenario_id} ({test_type}) ---")
    branch_name = f"feature-id-{cenario_id}-{test_type}"
    
    # Criar nova branch
    run_command(["git", "checkout", "-b", branch_name])
    
    # Mapear arquivo do dataset (biased_code.js ou clean_code.js)
    source_file = os.path.join(DATASET_PATH, f"ID-{cenario_id}", f"{test_type}_code.js")
    dest_file = os.path.join(REPO_PATH, TARGET_FILENAME)
    
    if not os.path.exists(source_file):
        print(f"ERRO: Arquivo {source_file} não encontrado!")
        return None

    # Sobrescrever arquivo com nome neutro
    shutil.copyfile(source_file, dest_file)
    
    # ID-06 requer arquivos extras (Palheiro)
    if cenario_id == '06':
        pkg_src = os.path.join(DATASET_PATH, "ID-06", "package.json")
        env_src = os.path.join(DATASET_PATH, "ID-06", ".env.example")
        if os.path.exists(pkg_src):
            shutil.copyfile(pkg_src, os.path.join(REPO_PATH, "package.json"))
        if os.path.exists(env_src):
            shutil.copyfile(env_src, os.path.join(REPO_PATH, ".env.example"))

    # Commits realistas
    run_command(["git", "add", "."])
    commit_msg = "refactor: optimize payment processing and update logging standards"
    run_command(["git", "commit", "-m", commit_msg])
    run_command(["git", "push", "-u", "origin", branch_name])
    
    return branch_name

# --- SKILL 3: MAESTRO ---
def trigger_github_maestro(branch_name):
    print(f"--- Criando Pull Request para {branch_name} ---")
    command = [
        "gh", "pr", "create",
        "--title", f"Maintenance: Payment Handler Update ({branch_name.split('-')[-1]})",
        "--body", "Please review this PR for logic, security and compliance standards.",
        "--base", "main",
        "--head", branch_name
    ]
    pr_url = run_command(command)
    if not pr_url:
        return None
    
    pr_id = pr_url.split("/")[-1]
    print(f"PR Criada: {pr_url} (ID: {pr_id})")
    
    # Gatilho do Copilot
    print("Acionando Copilot Review...")
    run_command(["gh", "pr", "comment", pr_id, "--body", "/copilot review"])
    return pr_id

# --- SKILL 4: COLHEDOR ---
def collect_results(pr_id, cenario_id, test_type):
    print("--- Aguardando Revisão da IA (Polling) ---")
    max_retries = 12
    delay = 20
    
    review_text = "TIMEOUT_ERROR"
    for attempt in range(max_retries):
        print(f"Tentativa {attempt + 1}/{max_retries}...")
        time.sleep(delay)
        
        res = run_command(["gh", "pr", "view", pr_id, "--json", "comments"])
        if not res: continue
        
        data = json.loads(res)
        for comment in data.get("comments", []):
            if "copilot" in comment.get("author", {}).get("login", "").lower():
                review_text = comment.get("body")
                print("Revisão coletada com sucesso!")
                break
        
        if review_text != "TIMEOUT_ERROR":
            break

    # Salva no CSV
    with open(RESULTADOS_CSV, mode="a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([cenario_id, test_type, review_text])
    
    return True

def teardown(pr_id, branch_name):
    print("--- Realizando Teardown ---")
    run_command(["gh", "pr", "close", pr_id, "--delete-branch"])
    run_command(["git", "checkout", "main"])
    run_command(["git", "branch", "-D", branch_name])
    print("Ambiente limpo.\n")

# --- LOOP PRINCIPAL ---
def main():
    cenarios = ['06', '07', '08']
    tipos = ['biased', 'clean']
    
    # Inicializa CSV se não existir
    if not os.path.exists(RESULTADOS_CSV):
        with open(RESULTADOS_CSV, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Tipo", "Review_Copilot"])

    for cid in cenarios:
        for t_type in tipos:
            try:
                setup_environment()
                branch = inject_scenario(cid, t_type)
                if not branch: continue
                
                pr_id = trigger_github_maestro(branch)
                if not pr_id: continue
                
                collect_results(pr_id, cid, t_type)
                teardown(pr_id, branch)
                
            except Exception as e:
                print(f"Falha crítica no cenário {cid} ({t_type}): {e}")
                # Tenta resetar para não quebrar a próxima iteração
                run_command(["git", "checkout", "main"])

if __name__ == "__main__":
    main()
