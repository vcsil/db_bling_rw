# 08 - RW

### Executar programa
1. Git clone

    ```bash
    git clone https://github.com/vcsil/db_bling_rw.git
    ```
    
2. Renomeia o arquivo do projeto para padronizar
    
    ```bash
    mv db_bling_rw/ 01-BancoDeDados && cd 01-BancoDeDados
    ```
    
3. Copia o arquivo .env.example e cria o .env. **Não se esquela de preenche-lo**
    
    ```bash
    cp .env.example .env
    # edita com nano .env
    ```
    
4. Baixe o sub módulo
    
    ```bash
    git submodule update --init --recursive
    ```
    
5. Ative o screen para conseguir acompanhar o andamento do script sem ficar com o computador ligado, só o servidor.
    
    ```bash
    screen
    ```
    
6. Rode o container Docker para iniciar o script
    
    ```bash
    # Verifique se esta no diretório correto
    sudo docker compose -f Docker-compose.development.yml up --build
    ```

7. Caso queira verifica o consumo do servidor, abra outro terminal conectado com ssh e digite:
    
    ```bash
    htop
    ```
### A Fazer:
* Utilizar ORM para o banco de dados
* configurar ferramentas mais avançadas e centralizadas, como Prometheus e Grafana, para monitoramento de longo prazo e visualizações gráficas mais detalhadas.
