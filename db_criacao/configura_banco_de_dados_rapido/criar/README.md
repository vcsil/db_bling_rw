# Manipula Banco de Dados Rápido
[![wakatime](https://wakatime.com/badge/user/04459a42-f0a6-4019-ad90-9558a7c04b39/project/018c3a26-8f43-4a6b-bf8b-0c596112d7c9.svg)](https://wakatime.com/badge/user/04459a42-f0a6-4019-ad90-9558a7c04b39/project/018c3a26-8f43-4a6b-bf8b-0c596112d7c9)

Código `bash` para **criar**, **conectar** e **deletar** banco de dados do tipo PostgreSQL.

É necessário ter o Postgres instalado na sua máquina.

Caso não tenha, veja como instalar na sua máquina:

- [Linux](https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart-pt)
- [Windows](https://learn.microsoft.com/pt-br/windows/wsl/tutorials/wsl-database#install-postgresql)

# Como configurar o banco

1. Clone o projeto
2. Extraia o conteúdo e abra um terminal na pasta extraída
3. Execute o seguinte comando para **criar** o banco de dados
    
    ```bash
    bash create-database
    ```
    
4. Por fim, execute o seguinte comando para se **conectar** ao banco de dados
    
    ```bash
    bash connect-database
    ```
    
5. Para finalizar, quando quiser **deletar** o banco de dados, basta executar o seguinte comando:
    
    ```bash
    bash destroy-database
    ```
    

## Exemplo criado

![drawSQL-ver-export-2023-12-05.png](images/drawSQL-ver-export-2023-12-05.png)

## Outro banco de dados

Para criar o seu próprio banco de dados, com suas tabelas:
1. Ir no arquivo `./src/database`, apagar e colocar o nome da DATABASE que você deseja criar.
2. Apagar os arquivos do `./scripts` e colocar o Schema (.sql) neste mesmo diretório. 
3. Posteriormente basta seguir os mesmo passos.
