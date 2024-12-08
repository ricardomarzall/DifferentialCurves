import pandas as pd
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt



##################################################################

# Para Alterar


######## Caminhos das tabelas CSV 

# Estrela principal
paths_star_1 = "/net/ASTRO/ricardomarzall/Documentos/Tecnicas_observacionais/24nov20/imagens_alinhadas/star_5_fluxes.csv" 

# Estrelas de Comparação
paths_comparison_stars = [
    "/net/ASTRO/ricardomarzall/Documentos/Tecnicas_observacionais/24nov20/imagens_alinhadas/star_1_fluxes.csv",
    "/net/ASTRO/ricardomarzall/Documentos/Tecnicas_observacionais/24nov20/imagens_alinhadas/star_2_fluxes.csv",
    "/net/ASTRO/ricardomarzall/Documentos/Tecnicas_observacionais/24nov20/imagens_alinhadas/star_3_fluxes.csv",
    "/net/ASTRO/ricardomarzall/Documentos/Tecnicas_observacionais/24nov20/imagens_alinhadas/star_4_fluxes.csv",
    #"/net/ASTRO/ricardomarzall/Documentos/Tecnicas_observacionais/24nov20/imagens_alinhadas/star_5_fluxes.csv"
    # Adicione mais caminhos de comparação conforme necessário
]


####################################################################

# Não precisa necessariamente Alterar

# Função para carregar a tabela e remover NaN
def load_table(path):
    df = pd.read_csv(path)
    df.dropna(inplace=True)  # Remove NaN
    return df

# Função para extrair o tempo a partir dos arquivos FITS
def get_jd_from_fits(fits_path):
    with fits.open(fits_path) as hdul:
        header = hdul[0].header
        return header.get("JD", np.nan)

# Carregar a tabela da estrela alvo
star_1 = load_table(paths_star_1)

# Carregar as tabelas das estrelas de comparação
comparison_stars = [load_table(path) for path in paths_comparison_stars]

# Adicionar colunas de tempo (JD) às tabelas
star_1["JD"] = star_1["image"].apply(get_jd_from_fits)  # Mudança para "image"
for star in comparison_stars:
    star["JD"] = star["image"].apply(get_jd_from_fits)  # Mudança para "image"

# Remover possíveis NaN introduzidos pela falta de JD no header
star_1.dropna(subset=["JD"], inplace=True)
for star in comparison_stars:
    star.dropna(subset=["JD"], inplace=True)

# Ordenar as tabelas por JD
star_1.sort_values("JD", inplace=True)
for star in comparison_stars:
    star.sort_values("JD", inplace=True)

# Calcular o fluxo médio das estrelas de comparação
# Aqui estamos somando o fluxo de todas as estrelas de comparação e dividindo pelo número de estrelas de comparação
comparison_flux = np.mean([star["flux"].values for star in comparison_stars], axis=0)

# Calcular a curva de luz diferencial
light_curve = star_1["flux"].values / comparison_flux


eixo_x =[]

for i in star_1["JD"]:
    eixo_x.append(float(i))

# Plotar a curva de luz
# Plotar a curva de luz
plt.figure(figsize=(10, 6))
plt.plot(eixo_x, light_curve, 'o', label="Curva de Luz Diferencial")  # Alteração aqui
plt.xlabel("Tempo (JD)")
plt.ylabel("Fluxo Relativo")
plt.title("Curva de Luz Diferencial")
plt.legend()
plt.grid()
plt.show()

