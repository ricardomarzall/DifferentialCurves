import os
import glob
import numpy as np
from astropy.io import fits
from photutils.detection import DAOStarFinder
from photutils.aperture import CircularAperture, aperture_photometry
from astropy.stats import sigma_clipped_stats
from astropy.table import Table
import matplotlib.pyplot as plt
import traceback

###########################################################################################################

# Para Alterar
# Diretório de entrada
input_directory = "/net/ASTRO/ricardomarzall/Documentos/Tecnicas_observacionais/24nov20/imagens_alinhadas"  # Diretório das imagens alinhadas

# Número de estrelas de comparação (modifique este valor conforme necessário)
num_stars = 5  # Altere para o número desejado de estrelas


# Listar arquivos FITS
data_files = glob.glob(os.path.join(input_directory, "*alinhada*fits")) # pode alterar conforme o nome dos arquivos
data_files.sort()
#####################################################################################################

# Não precisa necessariamente Alterar

# Arquivo de log
log_file = os.path.join(input_directory, "process_log.txt")

# Função para registrar logs
def log_message(message):
    with open(log_file, "a") as log:
        log.write(message + "\n")

# Função para encontrar as N estrelas mais brilhantes na primeira imagem
def find_brightest_stars(image_data, num_stars=3):
    mean, median, std = sigma_clipped_stats(image_data, sigma=3.0)
    daofind = DAOStarFinder(threshold=500 * std, fwhm=5)  # Caso não esteja achando as estrelas corretamente pode alterar os parâmetros da função
    stars = daofind(image_data - median)

    brightest_stars = stars[:num_stars] if stars else None  # Pega as " n " estrelas mais brilhantes
    if brightest_stars is None or len(brightest_stars) < num_stars:
        raise ValueError(f"Número insuficiente de estrelas detectadas na imagem. Encontrado: {len(stars)}")
    return brightest_stars

# Função para realizar a fotometria de abertura
def photometry(image_data, positions, aperture_radius=5):
    apertures = CircularAperture(positions, r=aperture_radius)
    phot_table = aperture_photometry(image_data, apertures)
    return phot_table

# Função para salvar as aberturas no formato .reg para DS9
def save_apertures_to_reg(positions, aperture_radius, output_file):
    with open(output_file, "w") as f:
        f.write("# Region file format: DS9 version 4.1\n")
        for pos in positions:
            # Salvar como círculo, com a coordenada x, y e o raio da abertura
            f.write(f"circle({pos[0]}, {pos[1]}, {aperture_radius}) # color=red\n")
    log_message(f"Aberturas salvas em: {output_file}")
    print(f"Aberturas salvas em: {output_file}")

# Função para plotar a imagem de referência com as aberturas e os números das estrelas
def plot_image_with_apertures(image_data, positions, output_file):
    plt.figure(figsize=(10, 10))
    plt.imshow(image_data, cmap='gray', origin='lower', vmin=np.percentile(image_data, 5), vmax=np.percentile(image_data, 95))
    apertures = CircularAperture(positions, r=6)
    apertures.plot(color='red', lw=1.5)
    for i, pos in enumerate(positions, start=1):
        plt.text(pos[0], pos[1], str(i), color='yellow', fontsize=12, ha='center', va='center', weight='bold')
    plt.colorbar(label='Pixel Intensity')
    plt.title("Estrelas Mais Brilhantes e Aberturas")
    plt.xlabel("Pixels X")
    plt.ylabel("Pixels Y")
    plt.savefig(output_file)
    plt.close()
    log_message(f"Gráfico salvo em: {output_file}")
    print(f"Gráfico salvo em: {output_file}")

# Processo principal
def main():
    if not data_files:
        log_message("Nenhum arquivo FITS encontrado no diretório.")
        print("Nenhum arquivo FITS encontrado no diretório.")
        return

    # Inicializar arquivo de log
    with open(log_file, "w") as log:
        log.write("Log de processamento de fotometria\n")
        log.write("=" * 40 + "\n")

    # Abrir a primeira imagem para encontrar as estrelas mais brilhantes
    try:
        image_data = fits.getdata(data_files[0])
        stars = find_brightest_stars(image_data, num_stars=num_stars)
        positions = np.transpose((stars['xcentroid'], stars['ycentroid']))
        log_message(f"Estrelas mais brilhantes encontradas na primeira imagem: {positions}")
        print("Posições das estrelas mais brilhantes:", positions)
    except Exception as e:
        log_message(f"Erro ao processar a primeira imagem {data_files[0]}: {e}")
        log_message(traceback.format_exc())
        print(f"Erro ao processar a primeira imagem: {e}")
        return

    # Salvar as aberturas em um arquivo .reg para DS9
    reg_file = os.path.join(input_directory, "apertures.reg")
    save_apertures_to_reg(positions, aperture_radius=6, output_file=reg_file)

    # Plotar e salvar o gráfico da imagem de referência com as aberturas
    plot_file = os.path.join(input_directory, "reference_image_with_apertures.png")
    plot_image_with_apertures(image_data, positions, output_file=plot_file)

    # Inicializar fluxos com listas vazias
    star_fluxes = {i: [] for i in range(num_stars)}

    for file in data_files:
        try:
            image_data = fits.getdata(file)
            phot_table = photometry(image_data, positions)

            # Salvar fluxos das estrelas
            for i in range(num_stars):
                star_fluxes[i].append(phot_table['aperture_sum'][i])
            log_message(f"SUCESSO: Processamento concluído para {file}")
        except Exception as e:
            # Adicionar marcador para fluxos ausentes
            for i in range(num_stars):
                star_fluxes[i].append(np.nan)
            log_message(f"FALHA: Erro ao processar {file}: {e}")
            log_message(traceback.format_exc())
            print(f"Erro ao processar o arquivo {file}: {e}")

    # Salvar tabelas de fluxos para cada estrela
    for i in range(num_stars):
        try:
            table = Table()
            table['image'] = data_files
            table['flux'] = star_fluxes[i]
            output_file = os.path.join(input_directory, f"star_{i+1}_fluxes.csv")
            table.write(output_file, format='csv', overwrite=True)
            log_message(f"Fluxos da estrela {i+1} salvos em: {output_file}")
            print(f"Fluxos da estrela {i+1} salvos em: {output_file}")
        except Exception as e:
            log_message(f"Erro ao salvar fluxos da estrela {i+1}: {e}")
            log_message(traceback.format_exc())
            print(f"Erro ao salvar fluxos da estrela {i+1}: {e}")

if __name__ == "__main__":
    main()
