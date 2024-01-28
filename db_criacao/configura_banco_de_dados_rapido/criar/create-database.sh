#!/bin/bash

# Pedir ao usuário o nome do arquivo a ser buscado
nome_arquivo=create-database.sh

# Diretório onde a busca será realizada
diretorio=$(pwd)

# Verificar se o diretório existe
if [ ! -d "$diretorio" ]; then
    echo "Diretório não encontrado: $diretorio"
    exit 1
fi

# Realizar a busca pelo arquivo
caminho_arquivo=$(find "$diretorio" -type f -name "$nome_arquivo" -exec dirname {} \;)

# Verificar se o arquivo foi encontrado
if [ -z "$caminho_arquivo" ]; then
    echo "Arquivo não encontrado: $nome_arquivo"
fi

dir_functions="${caminho_arquivo}"/src/functions.sh
dir_database="${caminho_arquivo}"/src/database.sh

source "$dir_functions";

DATABASE=$(cat "$dir_database");

echo "Checando status do postgres..." &&
checkPostgres &&

echo "Criando banco de dados..." &&
createDatabase $DATABASE &&

echo "Executando scripts..." &&
runScripts $DATABASE;
