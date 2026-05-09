



import pandas as pd
import io
from google.colab import files

# Solicita o upload do arquivo
print("Selecione o arquivo swiggy.csv original:")
uploaded = files.upload()

# Carrega o DataFrame
file_name = list(uploaded.keys())[0]
#df = pd.read_csv(io.BytesIO(uploaded[file_name]))
df = pd.read_excel(io.BytesIO(uploaded[file_name]))

print(f"\n✅ Arquivo '{file_name}' carregado com sucesso!")
print(f"Total de registros: {len(df)}")


display(df.head())

# 2. Verificar tipos de dados e valores nulos
print("\n--- Informações do Dataset ---")
df.info()

# 3. Estatística Descritiva (O coração da sua análise)
print("\n--- Resumo Estatístico ---")
display(df.describe())

# 4. Verificar se há linhas duplicadas
print(f"\nLinhas duplicadas encontradas: {df.duplicated().sum()}")

"""limpeza & data quality
*texto en cursiva*
"""

# 1. Limpeza de Duplicatas
df = df.drop_duplicates()
print(f"✅ Duplicatas removidas. Novo total: {len(df)}")

import great_expectations as ge
import pandas as pd

# 1. Configurar o contexto
context = ge.get_context()

# 2. Configurar o Datasource e o Batch Definition
datasource = context.data_sources.add_pandas(name="swiggy_datasource")
data_asset = datasource.add_dataframe_asset(name="swiggy_asset")
batch_definition = data_asset.add_batch_definition_whole_dataframe("all_data")

# 3. Criar a Suite de Expectativas
suite = context.suites.add(ge.ExpectationSuite(name="swiggy_report"))

# 4. Adicionar as regras (Expectations)
suite.add_expectation(ge.expectations.ExpectColumnValuesToBeBetween(
    column="Price (INR)", min_value=0.1, max_value=10000
))
suite.add_expectation(ge.expectations.ExpectColumnValuesToBeBetween(
    column="Rating", min_value=1.0, max_value=5.0
))
suite.add_expectation(ge.expectations.ExpectColumnValuesToNotBeNull(column="Restaurant Name"))
suite.add_expectation(ge.expectations.ExpectColumnValuesToNotBeNull(column="Order Date"))

# 5. Criar a Validação vinculando o Batch Definition
definition = ge.ValidationDefinition(
    name="swiggy_validation",
    data=batch_definition,
    suite=suite
)

# 6. Rodar a validação
result = definition.run(batch_parameters={"dataframe": df})

print("\n" + "="*40)
print("RELATÓRIO DE QUALIDADE (GREAT EXPECTATIONS)")
print("="*40)
print(f"Sucesso Geral: {result.success}")

stats = getattr(result, 'statistics', getattr(result, 'result_statistics', None))

if stats:
    # Se stats for um objeto Pydantic, convertemos para dict, se já for dict, usamos direto
    stats_dict = stats.dict() if hasattr(stats, 'dict') else stats

    print(f"Total de Testes: {stats_dict.get('evaluated_expectations')}")
    print(f"Sucessos: {stats_dict.get('successful_expectations')}")
    print(f"Percentual: {stats_dict.get('success_percent'):.2f}%")

    import json
    print("\n--- JSON  ---")
    print(json.dumps(stats_dict, indent=2))
else:
    print("\n--- RESULTADO DETALHADO ---")
    print(result)

!pip install -q -U google-genai





#!pip install -q -U google-generativeai


import google.generativeai as genai

# Esto es para usar secrets, la nueva opción de Google Colab, para almacenar la API key
from google.colab import userdata

import textwrap
from IPython.display import display
from IPython.display import Markdown

# Esta función se usa para dejar el formato Markdown que devuelve Gemini en formato compatible con Colab
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))





# Configuramos nuestra instancia del modelo con nuestra API key
GEMINI_API_KEY = userdata.get('GEMINI_API_KEY')

genai.configure(api_key = GEMINI_API_KEY)

# 2. Descobrir qual modelo está ativo 
available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

print("Modelos disponíveis na sua conta:")
for name in available_models:
    print(f"- {name}")

# Selecionar o 1.5-flash se disponível, senão pega o primeiro da lista
target_model = next((m for m in available_models if '1.5-flash' in m), available_models[0])

print(f"\n🚀 Usando o modelo: {target_model}")
model = genai.GenerativeModel(target_model)

#3. Teste rápido com 2 pratos
test_dishes = ['Butter Murukku-200gm', 'Badam Milk']
prompt = f"Retorne um JSON com ingrediente principal e se é veg (true/false) para: {test_dishes}"

try:
    response = model.generate_content(prompt)
    print("\n--- RESPOSTA DA IA ---")
    print(response.text)
except Exception as e:
    print(f"Erro ao gerar conteúdo: {e}")





df

"""###Abordagem"""

import re

def limpeza_express(texto):
    texto = str(texto).lower()
    # Remove tudo entre parênteses e colchetes (ex: (serves 1), [new])
    texto = re.sub(r'[\(\[].*?[\)\]]', '', texto)
    # Remove números e unidades (ex: 500ml, 2pcs, 10.50)
    texto = re.sub(r'\d+\s*(ml|gm|kg|pcs|pc|oz|g|l|ml)?', '', texto)
    # Remove símbolos estranhos
    texto = re.sub(r'[^a-zA-Z\s]', '', texto)
    return texto.strip()

df['dish_clean'] = df['Dish Name'].apply(limpeza_express)

df

# Criamos um dicionário de prioridades
mapeamento = {
    'Sobremesas': [
        'ice cream', 'dessert', 'cake', 'kulfi', 'waffle', 'donut', 'brownie', 'sweet', 'falooda',
        'gulab', 'halwa', 'pastry', 'choco', 'pie', 'lava', 'sundae', 'brow-wow-nie',
        'mcflurry', 'rasmalai', 'shahi tukda', 'kaju katli', 'pudding', 'gelato', 'rasgulla',
        'kalakand', 'cookie', 'nutella', 'kitkat'
    ],
    'Bebidas': [
        'tea', 'coffee', 'juice', 'shake', 'drink', 'beverage', 'milk', 'soda', 'lassi', 'water',
        'mojito', 'cooler', 'coke', 'cola', 'pepsi', '7up', '7 up', 'mirinda', 'dew', 'thums up',
        'cappuccino', 'aam panna', 'sprite', 'coolberg', 'fizz', 'bottle', 'can ', 'fanta',
        'smoothie', 'latte', 'frappuccino', 'americano', 'cold brew', 'blonde', 'mocha',
        'lemonade', 'espresso', 'orange', 'b natural'
    ],
    'Pratos Principais': [
        'curry', 'gravy', 'paneer', 'chicken', 'mutton', 'dal', 'sabji', 'kadai', 'main course',
        'masala', 'kofta', 'fish', 'egg', 'veg', 'keema', 'pav bhaji', 'murg', 'makhni', 'chole',
        'lamb', 'aloo matar', 'do pyaza', 'mushroom', 'rajma', 'dum aloo'
    ],
    'Arroz & Biryani': ['biryani', 'rice', 'pulao', 'jeera', 'khichdi'],
    'South Indian': ['dosa', 'idli', 'vada', 'bath', 'pongal', 'upma', 'sambar', 'uttapam'],
    'Refeições & Combos': ['meal', 'combo', 'bucket', 'lunchbox', 'binge', 'squad', 'party', 'saving', 'duo', 'thali', 'box', 'make at home'],
    'Lanches': [
        'burger', 'sandwich', 'pizza', 'roll', 'wrap', 'fries', 'nuggets', 'momo', 'noodle',
        'pasta', 'chowmein', 'margherita', 'feast', 'mexican', 'crispy', 'zinger', 'whopper',
        'pepperoni', 'croissant', 'loaf', 'sourdough', 'baguette', 'cheesiken', 'delight'
    ],
    'Entradas & Petiscos': [
        'kebab', 'tikka', 'chaat', 'starter', 'appetizer', 'snack', 'manchurian', 'chilly',
        'wedges', 'shots', 'potato', 'garlic bread', 'stix', 'poppers', 'strips', 'popcorn',
        'wings', 'soup', 'chilli', 'samosa', 'kachori', 'bhalla'
    ],
    'Pães & Acompanhamentos': [
        'roti', 'naan', 'paratha', 'kulcha', 'phulka', 'chapati', 'raita', 'papad', 'chutney',
        'pickle', 'salad', 'dip', 'ketchup', 'mayo', 'onion', 'corn', 'cheese', 'curd', 'spice mix', 'sauce'
    ]
}

def classificar_final(texto):
    # Converte o nome do prato para minúsculo e remove espaços nas pontas
    t = str(texto).lower().strip()

    # Percorre o dicionário
    for categoria, palavras in mapeamento.items():
        # Verifica se alguma palavra-chave está CONTIDA no texto
        if any(p.lower() in t for p in palavras):
            return categoria

    return 'Outros'

# 3. Aplicando na coluna que você já limpou anteriormente
df['super_category'] = df['dish_clean'].apply(classificar_final)



mapeamento = {
    'Sobremesas': ['ice cream', 'dessert', 'cake', 'kulfi', 'waffle', 'donut', 'brownie', 'sweet', 'falooda', 'gulab', 'halwa', 'pastry', 'choco', 'pie', 'lava', 'sundae', 'brow-wow-nie', 'mcflurry', 'rasmalai', 'shahi tukda', 'kaju katli', 'pudding', 'gelato', 'rasgulla', 'kalakand', 'cookie', 'nutella', 'kitkat','jalebi', 'laddu', 'sorbet', 'popsicle', 'fruit bowl', 'mini sticks','modak', 'peda', 'imarti', 'kheer', 'tiramisu', 'ice pops', 'almond rocks', 'jar'],
    'Bebidas': ['tea', 'coffee', 'juice', 'shake', 'drink', 'beverage', 'milk', 'soda', 'lassi', 'water', 'mojito', 'cooler', 'coke', 'cola', 'pepsi', '7up', '7 up', 'mirinda', 'dew', 'thums up', 'cappuccino', 'aam panna', 'sprite', 'coolberg', 'fizz', 'bottle', 'can ', 'fanta', 'smoothie', 'latte', 'frappuccino', 'americano', 'cold brew', 'blonde', 'mocha', 'lemonade', 'espresso', 'orange', 'b natural','frappe', 'blue lagoon', 'devils own', 'dark frappe', 'alphonso', 'green apple', 'mango ras','macchiato', 'go green'],
    'Pratos Principais': ['curry', 'gravy', 'paneer', 'chicken', 'mutton', 'dal', 'sabji', 'kadai', 'main course', 'masala', 'kofta', 'fish', 'egg', 'veg', 'keema', 'pav bhaji', 'murg', 'makhni', 'chole', 'lamb', 'aloo matar', 'do pyaza', 'mushroom', 'rajma', 'dum aloo', 'aloo gobi', 'aloo palak','aloo dum', 'aloo mattar', 'navratan korma', 'omelette','kadhi pakoda', 'ghee roast', 'pao bhaji', 'maggi', 'korma'],
    'Arroz & Biryani': ['biryani', 'rice', 'pulao', 'jeera', 'khichdi'],
    'South Indian': ['dosa', 'idli', 'vada', 'bath', 'pongal', 'upma', 'sambar', 'uttapam'],
    'Refeições & Combos': ['meal', 'combo', 'bucket', 'lunchbox', 'binge', 'squad', 'party', 'saving', 'duo', 'thali', 'box', 'make at home', 'hamper', 'basket', 'gift'],
    'Lanches': ['burger', 'sandwich', 'pizza', 'roll', 'wrap', 'fries', 'nuggets', 'momo', 'noodle', 'pasta', 'chowmein', 'margherita', 'feast', 'mexican', 'crispy', 'zinger', 'whopper', 'pepperoni', 'croissant', 'loaf', 'sourdough', 'baguette', 'cheesiken', 'delight', 'mcaloo', 'mcsaver','falafel', 'sausages', 'multipack', 'mini treats','spaghetti', 'aglio', 'fry', 'toasty'],
    'Entradas & Petiscos': ['kebab', 'tikka', 'chaat', 'starter', 'appetizer', 'snack', 'manchurian', 'chilly', 'wedges', 'shots', 'potato', 'garlic bread', 'stix', 'poppers', 'strips', 'popcorn', 'wings', 'soup', 'chilli', 'samosa', 'kachori', 'bhalla', 'murukku', 'puri', 'bhel','tikki', 'gobi 65', 'dhokla', 'chaap, poha','drums of heaven', 'tangdi', 'peri peri', 'chaap'],
    'Pães & Acompanhamentos': ['roti', 'naan', 'paratha', 'kulcha', 'phulka', 'chapati', 'raita', 'papad', 'chutney', 'pickle', 'salad', 'dip', 'ketchup', 'mayo', 'onion', 'corn', 'cheese', 'curd', 'spice mix', 'sauce', 'butter','seasoning', 'dahi, variety pack','dahi', 'marinara']
}

def classificar_melhor(texto):
    # Força minúsculo, transforma em string e limpa espaços nas pontas
    t = str(texto).lower().strip()

    # Percorremos o dicionário
    for categoria, palavras in mapeamento.items():
        # Verificamos se alguma das palavras-chave está CONTIDA no texto
        # Isso resolve o 'butter murukku-200gm' porque ele acha a palavra 'butter' lá dentro
        if any(p.lower() in t for p in palavras):
            return categoria

    return 'Outros'

# 3. Aplicamos na coluna que você preferir (recomendo usar a 'Dish Name' original ou 'dish_clean')
df['super_category'] = df['Dish Name'].apply(classificar_melhor)

df

# Contagem absoluta
contagem = df['super_category'].value_counts()
print(contagem)

print(df[df['super_category'] == 'Outros']['Dish Name'].value_counts().head(30))

df

"""###até aqui"""



print(df['super_category'].nunique())

from google.colab import files

# Salva temporariamente no servidor do Colab
#df.to_csv('swiggy_sc.csv', sep=';', encoding='utf-8-sig', index=False)

# Dispara o download automático para o seu navegador
#files.download('swiggy_sc.csv')

df1 = df[~df['dish_clean'].astype(str).isin(['0', 'nan', ''])]
df_final2=df1




"""###Modelo Star Schema"""


# --- PREPARAÇÃO ---
# Garante que a data 
df_final2['Order Date'] = pd.to_datetime(df_final2['Order Date'], format='%d/%m/%Y', errors='coerce')
df_final2 = df_final2.dropna(subset=['Order Date'])

# --- 1. DIM_RESTAURANT ---
dim_restaurant = df_final2[['Restaurant Name']].drop_duplicates().reset_index(drop=True)
dim_restaurant['restaurant_key'] = dim_restaurant.index + 1 # Começar em 1 é melhor prática

# --- 2. DIM_LOCATION ---
dim_location = df_final2[['State', 'City', 'Location']].drop_duplicates().reset_index(drop=True)
dim_location['location_key'] = dim_location.index + 1

# --- 3. DIM_DISH ---
dim_dish = df_final2[['Dish Name', 'dish_clean', 'Category', 'super_category']].drop_duplicates().reset_index(drop=True)
dim_dish['dish_key'] = dim_dish.index + 1

# --- 4. DIM_DATE (O ajuste fino) ---
# Pegamos os únicos, removemos nulos e garantimos que é datetime
unique_dates = df_final2['Order Date'].dropna().unique()
dim_date = pd.DataFrame({'full_date': unique_dates})
dim_date['full_date'] = pd.to_datetime(dim_date['full_date'])

# Agora o .dt funciona seguro
dim_date['date_key'] = dim_date['full_date'].dt.strftime('%Y%m%d').astype(int)
dim_date['day'] = dim_date['full_date'].dt.day
dim_date['month'] = dim_date['full_date'].dt.month
dim_date['year'] = dim_date['full_date'].dt.year

# --- 5. MAPEAMENTO (Criação da Fato) ---
# Usamos um DF temporário para não sujar o original
fact_orders = df_final2.merge(dim_restaurant, on='Restaurant Name') \
                       .merge(dim_location, on=['State', 'City', 'Location']) \
                       .merge(dim_dish, on=['Dish Name', 'dish_clean', 'Category', 'super_category'])

# Criar a chave de data na fato de forma segura
fact_orders['date_key'] = fact_orders['Order Date'].dt.strftime('%Y%m%d').astype(int)

# Seleção final das colunas da Fato
fact_orders = fact_orders[['date_key', 'restaurant_key', 'dish_key', 'location_key', 'Price', 'Rating', 'Rating Count']]

dim_restaurant

dim_date

fact_orders

"""###Verif"""

original_rows = len(df_final2)
fact_rows = len(fact_orders)

if original_rows == fact_rows:
    print(f"✅ Sucesso! Volume preservado: {fact_rows} linhas.")
else:
    print(f"❌ Erro! Diferença de {original_rows - fact_rows} linhas. Verifique seus merges!")




#from google.colab import files

# --- 1. CONFIGURAÇÃO DO DICIONÁRIO DE TABELAS ---
model_tables = {
    "fact_orders": fact_orders,
    "dim_dish": dim_dish,
    "dim_restaurant": dim_restaurant,
    "dim_location": dim_location,
    "dim_date": dim_date
}

# --- 2. EXPORTAÇÃO PARA CSV NO AMBIENTE VIRTUAL ---
print("🚀 Iniciando exportação para CSV...")

exported_files = []
for table_name, df in model_tables.items():
    file_path = f"{table_name}.csv"

    # index=False: não salva a coluna de números do Pandas
    # sep=',': separador padrão por vírgula
    # encoding='utf-8-sig': garante que acentos fiquem corretos no Excel/Dadosfera
    df.to_csv(file_path, index=False, sep=',', encoding='utf-8-sig')

    exported_files.append(file_path)
    print(f"✅ Tabela '{table_name}' salva no Colab.")

print("\n--- Exportação Concluída ---\n")

# --- 3. DOWNLOAD PARA O COMPUTADOR LOCAL ---
print("📥 Iniciando downloads... .")

for file in exported_files:
    files.download(file)