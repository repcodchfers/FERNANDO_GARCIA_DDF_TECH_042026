



import pandas as pd
import io
from google.colab import files

# Solicita o upload do arquivo
print("Selecione o arquivo swiggy.csv original:")
uploaded = files.upload()

# Carrega o DataFrame
file_name = list(uploaded.keys())[0]
df1 = pd.read_excel(io.BytesIO(uploaded[file_name]))

print(f"\n✅ Arquivo '{file_name}' carregado com sucesso!")
print(f"Total de registros: {len(df1)}")

import re

def clean_canonical_dish(text):
    text = str(text).lower()
    # 1. Remove pesos e medidas (gm, kg, ml, l, pcs)
    text = re.sub(r'\d+\s*(gm|g|kg|ml|l|pcs|pieces|per|serves|slice)', '', text)
    # 2. Remove o que estiver dentro de parênteses (comentários do restaurante)
    text = re.sub(r'\(.*\)', '', text)
    # 3. Remove caracteres especiais e números soltos
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    # 4. Remove espaços duplos
    text = " ".join(text.split())
    return text.title() # Deixa Bonitinho: "Chicken Biryani"

df1['Dish_Clean'] = df1['Dish Name'].apply(clean_canonical_dish)

import re

def reclassificar_pelo_nome(row):
    # Transformamos tudo em texto único para busca
    # Damos peso 2x ao nome do prato concatenando-o primeiro
    texto = str(row['Dish_Clean']).lower() + " " + str(row['Category']).lower()

    # 1. Definição de Dicionário com Palavras-Chave de ALTO IMPACTO
    regras = {
        'Refeições': r'rice|biryani|pulao|curry|dal|gravy|noodle|pasta|pizza|thali|paneer|chicken|mutton|fish|beef|steak|burger|whopper|meal|combo|platter|main|chinese|indian|bath|kadai|masala|hyderabadhi|patiala|mutter|gobi|kofta',
        'Lanches/Entradas': r'roll|soup|snack|starter|appetizer|kebab|tikka|tandoori|chaat|samosa|momos|manchurian|nugget|wings|fries|taco|nachos|sandwich|wrap|hotdog',
        'Sobremesas': r'ice cream|dessert|sweet|cake|bakery|pastry|kulfi|chocolate|scoop|tub|shake|pudding|halwa|gulab|jamun|donut|waffle|brownie',
        'Bebidas': r'drink|beverage|juice|tea|coffee|soda|water|lassi|cooler|mocktail|soft|beer|wine|coke|pepsi|sprite|milk',
        'Pães e Acompanhamentos': r'bread|roti|nan|naan|kulcha|paratha|phulka|poori|papad|chutney|raita|salad|sauce|dip|fry|raitha'
    }

    # 2. Varredura de Regras
    for label, pattern in regras.items():
        if re.search(pattern, texto):
            return label

    return 'Outros/Especialidades'

# Aplicar a nova lógica
df1['Macro_Category'] = df1.apply(reclassificar_pelo_nome, axis=1)

# Ver o novo ranking
print(df1['Macro_Category'].value_counts(normalize=True) * 100)

# Identifica o que ainda é "Outros"
df1_outros = df1[df1['Macro_Category'] == 'Outros/Especialidades']

    # Pega apenas os nomes ÚNICOS (para economizar tokens e tempo)
itens_unicos = df1_outros['Dish_Clean'].unique().tolist()

print(f"Total de itens únicos em 'Outros' para processar: {len(itens_unicos)}")

import google.generativeai as genai
from google.colab import userdata
import json
import time
# Configuramos nuestra instancia del modelo con nuestra API key
GEMINI_API_KEY = userdata.get('GEMINI_API_KEY')

genai.configure(api_key = GEMINI_API_KEY)
# Configure sua API Key (Pegue em aistudio.google.com)
#genai.configure(api_key="SUA_CHAVE_AQUI")

model = genai.GenerativeModel('gemini-flash-latest')

df_outros = df1[df1['Macro_Category'] == 'Outros/Especialidades']
top_100_outros = df_outros['Dish_Clean'].value_counts().head(100).index.tolist()

# --- 4. FUNÇÃO DE CHAMADA À IA ---
def processar_cauda_longa_ia(lista_itens):
    mapeamento_ia = {}
    lote_tamanho = 10 # Lotes pequenos para estabilidade

    print(f"Enviando {len(lista_itens)} itens para IA...")

    for i in range(0, len(lista_itens), lote_tamanho):
        lote = lista_itens[i:i+lote_tamanho]
        prompt = f"""
        Classifique estes pratos indianos nas categorias: Refeições, Sobremesas, Lanches/Entradas, Bebidas, Pães e Acompanhamentos.
        Retorne APENAS um JSON: {{"nome_do_prato": "categoria"}}
        Itens: {lote}
        """
        try:
            response = model.generate_content(prompt)
            res_limpa = response.text.replace('```json', '').replace('```', '').strip()
            mapeamento_ia.update(json.loads(res_limpa))
            time.sleep(10) # Rate limit protection
        except Exception as e:
            print(f"Erro no lote começando em {i}: {e}")
            print("Aguardando 30 segundos para tentar o próximo lote...")
            time.sleep(30) # Pausa longa para 'limpar' o erro 429/503
            continue
    return mapeamento_ia

# Executando a IA para os Top 500
dicionario_ia = processar_cauda_longa_ia(top_100_outros)

dicionario_ia

# --- 5. INTEGRAÇÃO FINAL NO DATAFRAME ---
def integracao_final(row):
    if row['Macro_Category'] == 'Outros/Especialidades':
        # Se a IA classificou, usamos a resposta dela
        return dicionario_ia.get(row['Dish_Clean'], 'Outros/Especialidades')
    return row['Macro_Category']

df1['Macro_Category'] = df1.apply(integracao_final, axis=1)

# --- 6. EXPORTAÇÃO E RESULTADOS ---
print(df1['Macro_Category'].value_counts(normalize=True) * 100)
#df1.to_csv('dataset_final_dadosfera.csv', index=False)

# Unificando as variações de nome que a IA criou
df1['Macro_Category'] = df1['Macro_Category'].replace({
    'Pães': 'Pães e Acompanhamentos',
    'Acompanhamentos': 'Pães e Acompanhamentos'
})

# conferir
print(df1['Macro_Category'].value_counts(normalize=True) * 100)