"""
Gera um dataset sintético com variáveis de saúde cardiovascular
e exporta para CSV usando pandas.
"""

import random
import pandas as pd

# Sementes para reprodutibilidade
random.seed(42)

# Opções para as variáveis categóricas
sexos = ["Masculino", "Feminino"]
historico_cardiaco = ["Sim", "Não"]
sintomas_opcoes = [
    "Nenhum",
    "Dor no peito",
    "Falta de ar",
    "Fadiga",
    "Dor no peito e falta de ar",
    "Tontura",
    "Palpitações",
    "Dor no peito e fadiga",
    "Falta de ar e tontura",
    "Múltiplos sintomas",
]

# Pesos para tornar os dados mais realistas
pesos_historico_nao = [0.85, 0.15]  # 85% sem histórico, 15% com
pesos_sintomas = [0.4, 0.15, 0.12, 0.1, 0.08, 0.05, 0.04, 0.03, 0.02, 0.01]

n_linhas = 120  # Mais de 100 linhas

dados = []

for _ in range(n_linhas):
    idade = random.randint(25, 85)
    sexo = random.choice(sexos)
    
    # Pressão arterial (sistólica/diastólica em mmHg) - valores realistas
    pressao_sistolica = random.randint(100, 180)
    pressao_diastolica = random.randint(60, 110)
    pressao_arterial = f"{pressao_sistolica}/{pressao_diastolica}"
    
    # Colesterol total em mg/dL (120-280)
    colesterol = random.randint(120, 280)
    
    # Histórico de doenças cardíacas
    historico = random.choices(historico_cardiaco, weights=pesos_historico_nao)[0]
    
    # Sintomas
    sintomas = random.choices(sintomas_opcoes, weights=pesos_sintomas)[0]
    
    # Frequência cardíaca em bpm (50-120)
    frequencia_cardiaca = random.randint(55, 115)
    
    dados.append({
        "idade": idade,
        "sexo": sexo,
        "pressao_arterial": pressao_arterial,
        "colesterol": colesterol,
        "historico_doencas_cardiacas": historico,
        "sintomas": sintomas,
        "frequencia_cardiaca": frequencia_cardiaca,
    })

def main():
    # Criar DataFrame
    df = pd.DataFrame(dados)

    # Exportar para CSV
    arquivo_csv = "dataset_cardiovascular.csv"
    df.to_csv(arquivo_csv, index=False, encoding="utf-8-sig")

    print(f"Dataset criado com sucesso!")
    print(f"Total de linhas: {len(df)}")
    print(f"Arquivo salvo: {arquivo_csv}")
    print("\nPrimeiras linhas do dataset:")
    print(df.head(10))

if __name__ == "__main__":
    main()
    