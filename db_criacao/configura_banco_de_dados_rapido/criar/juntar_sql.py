import os

# Diretório onde os arquivos SQL estão localizados
diretorio = "scripts/"

# Nome do arquivo de saída que conterá todo o conteúdo combinado
arquivo_saida = "init.sql"
arquivos_sql = os.listdir(diretorio)
arquivos_sql.sort()

# Abre o arquivo de saída em modo de escrita
with open(arquivo_saida, "w") as output_file:
    # Loop através dos arquivos no diretório
    for arquivo in arquivos_sql:
        if arquivo.endswith(".sql"):
            caminho_completo = os.path.join(diretorio, arquivo)

            # Abre cada arquivo SQL e lê o conteúdo
            with open(caminho_completo, "r") as input_file:
                conteudo_sql = input_file.read()

                # Escreve o conteúdo no arquivo de saída
                output_file.write(conteudo_sql)

                # Adiciona uma quebra de linha entre os scripts SQL
                output_file.write("\n---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n\n")

print(f"Arquivos SQL combinados com sucesso em '{arquivo_saida}'.")
