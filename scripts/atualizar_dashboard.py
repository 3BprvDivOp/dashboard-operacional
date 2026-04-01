import subprocess
import os

print("\n🔄 Iniciando atualização do dashboard...\n")

base_dir = os.path.dirname(os.path.abspath(__file__))
projeto = os.path.dirname(base_dir)

processar = os.path.join(projeto, "scripts", "processar_eventos.py")
gerar_json = os.path.join(projeto, "scripts", "gerar_json_mapa.py")

print("1️⃣ Processando eventos...")
subprocess.run(["python", processar])

print("2️⃣ Gerando JSON do mapa...")
subprocess.run(["python", gerar_json])

print("\n✅ Dashboard atualizado!\n")
