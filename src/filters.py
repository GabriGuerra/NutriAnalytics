import pandas as pd
from pathlib import Path


def load_data():
    base_dir = Path(__file__).resolve().parent.parent
    file_path = base_dir / "data" / "nutri_data.csv"
    if not file_path.exists(): return pd.DataFrame()

    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()

        # Taxonomia de Sistemas
        mapeamento = {
            'Cognição': ['cognição', 'foco', 'memória', 'mental', 'neuro', 'raciocínio'],
            'Metabolismo': ['metabolismo', 'glicêmico', 'peso', 'insulina', 'tireoide'],
            'Longevidade': ['longevidade', 'celular', 'reparo', 'autofagia', 'antioxidante'],
            'Performance': ['performance', 'vo2', 'vascular', 'oxigênio', 'muscular'],
            'Recuperação': ['sono', 'relaxamento', 'estresse', 'recuperação', 'inflamação'],
            'Imunidade': ['imunidade', 'proteção', 'detox', 'microbiota']
        }

        def categorizar(obj):
            obj = str(obj).lower()
            for pilar, keywords in mapeamento.items():
                if any(k in obj for k in keywords): return pilar
            return 'Outros'

        df['Sistema_Biologico'] = df['Objetivo_Primario'].apply(categorizar)

        # Valor estético para os gráficos de tamanho (peso visual)
        df['Peso_Visual'] = 1

        # Ordenação Cronológica para navegação
        ordem_tempo = {
            'Pré-exercício': 0, 'Manhã': 1, 'Almoço': 2,
            'Pós-exercício': 2.5, 'Tarde': 3, 'Noite': 4, 'Qualquer Horário': 5
        }
        df['Ordem_Cronos'] = df['Cronobiologia_Periodo'].map(ordem_tempo).fillna(6)

        return df.sort_values('Ordem_Cronos')
    except:
        return pd.DataFrame()