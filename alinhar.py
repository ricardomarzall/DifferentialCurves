import astroalign as aa
import numpy as np
from astropy.io import fits
import glob
import os

np.random.seed(seed=12)


'''

Output information - As imagens alinhadas, assim como, o log estão no output_directory

'''

################################################################################

# Para Alterar

# Caminhos e diretórios
input_directory = "/net/ASTRO/ricardomarzall/Documentos/Tecnicas_observacionais/24nov20/imagens_reduzidas" # Caminho das imagens reduzidas
output_directory = "/net/ASTRO/ricardomarzall/Documentos/Tecnicas_observacionais/24nov20/imagens_alinhadas" # Output directory - Irá criar a pasta imagens_alinhadas caso não tenha

################################################################################

# Não precisa necessariamente Alterar

log_file = os.path.join(output_directory, "processamento.log")

# Garantir que o diretório de saída existe
os.makedirs(output_directory, exist_ok=True)

# Abrir imagem base
hdu_base = fits.open(os.path.join(input_directory, "ap_dor_0006_clear.fits"))
imagem_base = hdu_base[0].data.astype(np.float32)

# Obter lista de arquivos FITS
data = glob.glob(os.path.join(input_directory, "ap_dor_*_clear.fits"))
data.sort()

# Inicializar listas para registrar status
imagens_sucesso = []
imagens_falha = []

# Processar as imagens
with open(log_file, "w") as log:
    log.write("Log de processamento:\n")
    log.write("=====================\n\n")
    
    for path_image in data:
        try:
            # Abrir imagem a ser alinhada
            hdu = fits.open(path_image)
            imagem_alinhar = hdu[0].data.astype(np.float32)
            
            # Alinhar a imagem
            aligned_image, _ = aa.register(imagem_alinhar, imagem_base)
            
            # Obter o nome do arquivo original
            original_name = os.path.basename(path_image)
            new_name = original_name.replace(".fits", "_alinhada.fits")
            
            # Caminho completo para salvar o arquivo alinhado
            fits_filename = os.path.join(output_directory, new_name)
            
            # Salvar a imagem alinhada
            hdu[0].data = aligned_image
            hdu.writeto(fits_filename, overwrite=True)
            
            # Registrar sucesso
            imagens_sucesso.append(original_name)
            log.write(f"SUCESSO: {original_name} alinhada e salva como {new_name}\n")
        
        except Exception as e:
            # Registrar falha
            original_name = os.path.basename(path_image)
            imagens_falha.append(original_name)
            log.write(f"ERRO: Falha ao processar {original_name} - {str(e)}\n")
    
    # Resumo do processamento
    log.write("\nResumo do processamento:\n")
    log.write(f"Total processado: {len(data)}\n")
    log.write(f"Sucessos: {len(imagens_sucesso)}\n")
    log.write(f"Falhas: {len(imagens_falha)}\n")

# Exibir resumo no console
print("Processamento concluído!")
print(f"Imagens alinhadas com sucesso: {len(imagens_sucesso)}")
print(f"Imagens com falha: {len(imagens_falha)}")
print(f"Log salvo em: {log_file}")
