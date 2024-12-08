import numpy as np
import matplotlib.pyplot as plt
import glob
from astropy.io import fits
from astropy.modeling import models, fitting
from matplotlib.patches import Rectangle
from matplotlib.colors import LogNorm
import os
from photutils.detection import DAOStarFinder
from photutils.background import MedianBackground



# Diretório de saída para as imagens calibradas

output_dir = "/net/ASTRO/ricardomarzall/Documentos/Tecnicas_observacionais/24nov20/imagens_reduzidas"
os.makedirs(output_dir, exist_ok=True)  # Cria o diretório, se não existir

# Carregando Imagens

flats = glob.glob("/net/ASTRO/ricardomarzall/Documentos/Tecnicas_observacionais/24nov20/flat*.fits") # caminho para os flats
flats.sort()
zero = glob.glob("/net/ASTRO/ricardomarzall/Documentos/Tecnicas_observacionais/24nov20/bias*.fits") # caminho para os bias
zero.sort()
data = glob.glob("/net/ASTRO/ricardomarzall/Documentos/Tecnicas_observacionais/24nov20/*ap*.fits") # caminho para as imagens
data.sort()


# Bias ############################################################################################

bias = np.stack([fits.getdata(_).astype("float") for _ in zero])
print(bias.shape)

# Calcular o bias mestre (média dos frames)
master_bias = np.mean(bias, axis=0)


#Flat #############################################################################################

# não normalizado

flat = np.stack([fits.getdata(_).astype("float") for _ in flats])
print(flat.shape)
master_flats = (np.mean(flat,axis=0)-master_bias)

# Normalizado
master_flats_normalizado = master_flats/(np.mean(master_flats))


# Redução de cada imagem ###########################################################################

# Loop para processar cada arquivo
for file_path in data:
    # Carregar a imagem bruta
    with fits.open(file_path) as hdul:
        raw_image = hdul[0].data.astype("float")  # Convertendo para float se necessário
        header = hdul[0].header  # Copiar o cabeçalho para o arquivo de saída
    
    # Reduzir a imagem (calibrar)
    reduced_image = (raw_image - master_bias) / master_flats_normalizado
    
    # Gerar o nome para o arquivo de saída
    base_name = os.path.basename(file_path).replace(".fits", "_clear.fits")
    output_path = os.path.join(output_dir, base_name)
    
    # Salvar a imagem reduzida
    fits.writeto(output_path, reduced_image, header, overwrite=True)
    print(f"Imagem reduzida salva: {output_path}")
