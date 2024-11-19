# Indicadores de Cloud: Migração e Visualização de Dados

Este projeto tem como objetivo migrar dados do <a href="https://monday.com">Monday</a> para o BigQuery utilizando um processo de ETL (Extract, Transform e Load) implementado em Python. Após a migração, serão desenvolvidos gráficos e visualizações no <a href="https://lookerstudio.google.com/navigation/reporting">Looker Studio</a> para facilitar o monitoramento e a análise desses indicadores.

Atualmente, o ETL realiza a migração dos seguintes painéis do Monday:
- **GCP Squad - Old Projects**: referente a projetos dos anos passados
- **GCP Squad - OPTs&Projects**: referente a projetos do ano atual
- **Alocação Consultor**: referente a dados dos consultores, assim como suas alocações

## Arquitetura de solução

## Mapeamento

O **monday** é uma plataforma de gestão de trabalho e colaboração que ajuda equipes a planejar, organizar e acompanhar projetos. Ele oferece ferramentas para criar fluxos de trabalho personalizados, como quadros, listas de tarefas e painéis, onde você pode visualizar o progresso de atividades, delegar responsabilidades e monitorar prazos.

Para este projeto, os dados foram extraídos através da API do monday, que utiliza o **GraphQL** como linguagem de consulta. O processo de extração dos dados envolve:
- **Autenticação**: primeiro, é necessário obter o token de API do monday. Para isso, acesse a aba de <span style="color: #FFB800;">Developer</span> e depois em <span style="color: #FFB800;">My Access Token</span>.
  - <span style="color: #E74C3C;">IMPORTANTE</span>: o Token de API é um dado <span style="color: #FFB800;">extremamente sensível</span>, e deve ser manuseado com cuidado. 
- **Requisição**: a API do monday utiliza o GraphQL, o que exige a definição de uma Query GraphQL, especificando exatamente os dados que deseja obter (como painéis, colunas, itens, etc.).
- **Chamada à API**: com a Query e o Token, você pode realizar a chamada <span style="color: #FFB800;">HTTP POST</span> para o endpoint da API "https://api.monday.com/v2" (consultar a documentação da API para maiores especificações de versão).
  - É necessário enviar o token da API no cabeçalho da requisição, utilizando, por exemplo: <span style="color: #FFB800;">Authorization: Bearer SEU_TOKEN</span>.
- **Manipulação de Respostas**: a resposta vem em JSON, com a estrutura exata que você solicitou na Query GraphQL. Em Python, por exemplo, foi utilizada a biblioteca <span style="color: #FFB800;">requests</span> para fazer a requisição e manipular o JSON com facilidade.

> 💡 Para o mapeamento inicial, foi utiliado o software **Postman** para as requisições via Query GraphQL

### Requisição dos IDs dos Boards

Primeiramente, é necessário ter acesso aos boards e seus respectivos IDs. Para isso, vamos executar a seguinte Query dentro do Postman:

```sh
query { boards { id, name } }
```

Para que este código funcione, siga as seguintes etapas dentro do Postman:
- Dentro do Postman, vá até a aba **Authorization**
- Em Auth Token, selecione **Bearer Token**
- No campo Token, insira o Token da API do monday.
- Em seguida, vá até a aba **Body**, selecione **GraphQL** e insira a query acima.
- Execute a query para obter os IDs e nomes dos boards.

O retorno será no formato json, trazendo os nomes dos Boards e os IDs. Os nomes serão apenas para sabermos quais os boards queremos usar, mas o importante será guardar os IDs.

### Requisição dos Boards

Os boards dentro do monday seguem uma estrutura similar, então utilizaremos a mesma Query para obter dados dos seguintes boards:
- **GCP Squad - Old Projects**: projetos dos anos anteriores
- **GCP Squad - OPTs&Projects**: projetos do ano atual
- **Alocação Consultor**: dados dos consultores e suas alocações

Com os respectivos IDs em mãos, siga estes passos no Postman:
- Primeiro, insira no campo **QUERY** na Aba Body (com o GraphQL selecionado) a Query mostrada abaixo
  - Note que a variável **$boardId: [ID!]** permite enviar o ID do board de forma dinâmica, em vez de fixá-lo no código (hard-coded). Isso facilita o uso da mesma Query para diferentes boards.
- Em **GRAPHQL VARIABLES** (ao lado do campo da query), insira o seguinte trecho: <span style="color: #FFB800;">{"boardId": [id_board]}</span>. Substitua **id_board** pelo ID do board de interesse.
- Execute a query para obter os dados do Board

> A Query retornará dados das colunas (como id, name da coluna e tipo), além de todos os itens por página (até 300, permitindo obter os dados sem paginação adicional). Para cada item, também serão incluídos os subitens principais.

```sh
query GetBoardItems($boardId: [ID!]){  
  boards(ids: $boardId) {  
    columns {
      id
      title
      type
    }
    items_page(limit: 300) {  
      items {  
        id  
        name
        column_values {  
          id  
          text
          column {
            id
            title
          }
        }  
        subitems {
            id
            name
            column_values {
                id
                text
                column {
                    id
                    title
                }
            }
        }
      }  
    }  
  }  
}
```

O resultado virá em um formato JSON extenso, com várias linhas de dados, começando pelos nomes das colunas, e após os dados referente a cada coluna

### Dados nulos na resposta da requisição
A API não retorna dados de **colunas dinâmicas**, como aquelas que contêm fórmulas ou medidores de progresso, pois esses valores não são calculados diretamente pela API. Como resultado, esses campos podem aparecer como null, mesmo que exibam dados no monday.

> Para calcular valores ausentes, você pode recriar as fórmulas localmente usando uma linguagem de programação (como Python), baseando-se nos dados obtidos pela API. Abordaremos como fazer isso mais adiante.

## Etapas de desenvolvimento

Após concluir o mapeamento e entender como a API funciona para obter os dados necessários, iniciaremos agora o processo de desenvolvimento do ETL para a extração e transformação desses dados.

### Ambiente virtual

Primeiro, vamos criar um ambiente virtual para trabalhar em um ambiente isolado. No terminal, execute o seguinte comando:

```sh
python3 -m venv etl_process
```

Esse comando cria um ambiente virtual chamado etl_process. Para ativá-lo, execute o comando abaixo no terminal (no mesmo local onde o ambiente foi criado):

```sh
source etl_process/bin/activate
```

### Dependências
Com o ambiente virtual ativo, vamos instalar as seguintes bibliotecas:
- **Pandas**: para manipulação de datasets.
- **pandas-gbq**: extensão do Pandas para salvar datasets no BigQuery.
- **Flask**: para criar uma interface web amigável.
- **Requests**: para fazer requisições à API e manipular o JSON.
- **dotenv**: para trabalhar com variáveis de ambiente.
- **Google Cloud Secret Manager**: para acessar segredos no Secret Manager da GCP.

Vamos executar o seguinte comando:

```sh
pip3 install pandas pandas-gbq Flask requests python-dotenv google-cloud-secret-manager
```

Para salvar essas dependências (principalmente para quando a aplicação for ser executada em um container docker), execute o seguinte comando:
```sh
pip3 freeze > requirements.txt
```

Esse comando vai criar um arquivo chamado **requirements.txt** com os nomes e suas respectivas versões de cada dependência instalada

### Criação da Service Account

Como o desenvolvimento será feito inicialmente de forma local, precisamos configurar uma Service Account para acessar o Google BigQuery e o Google Secret Manager, onde o token da API será armazenado.

- Para isso, acesse o Console do Google Cloud, procure por IAM, e na aba a esquerda clique em <a href="https://console.cloud.google.com/iam-admin/serviceaccounts">Service Account</a>
- Clique em **CREATE SERVICE ACCOUNT**
- Atribua o nome "cloud-indicators-cloud-run" (pois usaremos essa Service Account em um serviço do Cloud Run).
- Clique em **CREATE AND CONTINUE**
- Em "Grant this service account access to project", selecione as seguintes roles:
  - Bigquery Data Owner
  - Secret Manager Secret Acessor
- Clique em "CONTINUE" e depois em "DONE"

Para acessar o BigQuery e o Secret Manager localmente, será necessário uma chave JSON associada à Service Account:

- Clique na service account criada
- Clique na aba "KEYS"
- Clique em **ADD KEY** e depois em **Create New Key**
- Selecione o formato JSON e clique em CREATE
- A cheve automaticamente será baixada na sua máquina local

> Em seguida, mova o arquivo de chave para o diretório do projeto e renomeie-o para cloud-indicators-key.json.

### Salvando o Token de API no Secret Manager

Para garantir maior segurança, vamos salvar o token da API como um segredo no Secret Manager:
- Dentro da console GCP, pesquise por <a href="https://console.cloud.google.com/security/secret-manager">Secret Manager</a>
- Clique em **+ CREATE SECRET**
- em "Name" atribua o valor **api_key**, e em "Secret Value", insira o Token de API
- Clique em "CREATE SECRET"

> Se o token for atualizado, você pode adicionar uma nova versão no segredo existente. Basta clicar no segredo criado, acessar a aba Versions e selecionar NEW VERSION. Nessa aba, também é possível visualizar as versões anteriores do segredo.

### Estrutura e Desenvolvimento do Código
Dentro da Pasta 'Code', teremos os seguintes arquivos:
- **board.py**: este arquivo será responsável por realizar programaticamente a requisição dos IDs dos boards.
- **config.py**: este arquivo centraliza todas as principais configurações do projeto, incluindo:
  - **self.project_id**: o id do projeto dentro do Google Cloud
  - **self.key**: o nome do segredo criado
  - **self.version**: a versão do segredo que estamos utilizando (nesse caso, a latest)
  - **self.api_url**: a URL da API do monday
  - **self.data_set**: O nome do dataset em que salvaremos os dados
  - **self.table_name_old_projects, self.table_name_actual_projects e self.table_name_consultants_allocation**: os nomes das tabelas
    - Para cada board, criaremos duas tabelas, organizadas da seguinte maneira:
      - Nos boards de "Projetos Antigos" e "Projetos Novos", teremos um dataset para projetos e outro para consultores.
      - No board de "Alocação de Consultores", criaremos tabelas para dados dos consultores e para informações detalhadas das suas alocações.
  - **self.board**: os IDs de cada board definidos em um objeto para facilitar o acesso.
- **consultor_allocation.py, projects_old_opts.py e projects_opt**: arquivos contendo o processo de ETL (extração, transformação e carregamento) dos dados de cada board para o BigQuery.
- **request_api.py**: responsável por fazer as requisições para a API do Monday, utilizando a query descrita na seção de [Requisição dos Boards](#requisição-dos-boards)
- **secret.py**: arquivo contendo a função que faz a requisição ao Secret Manager para recuperar o token da API.
- **main.py**: arquivo que define as rotas no Flask para renderizar a interface web e chamar as funções responsáveis pelo ETL dos dados

O processo de execução segue as etapas abaixo:
1. O usuário acessa a interface web e seleciona qual dos boards deseja migrar para o BigQuery.
2. O arquivo main.py aciona o arquivo correspondente **(consultor_allocation.py, projects_old_opts.py ou projects_opt.py)**, com base na escolha do usuário.
3. Os arquivos de ETL chamam o **request_api.py**, que realiza a requisição para a API do Monday.
4. Antes de fazer a requisição, request_api.py utiliza **secret.py** para obter o token de API do Secret Manager.
5. Todos os arquivos fazem uso das configurações definidas em **config.py**.

### Processo de autenticação entre o ambiente local e o ambiente GCP

Para a fase de desenvolvimento, foi utilizado a Service Account Key criada na etapa [Criação da Service Account](#criação-da-service-account) para permitir que, localmente, seja possível acessar serviços da nuvem GCP, tais como o Google Cloud BigQuery para armazenamento, e Google Cloud Secret Manager para o gerenciamento de segredos. 

Para criar essa ponte entre o ambiente local e o ambiente GCP, é necessário que a Service Account Key esteja no mesmo diretório dos arquivos contendo o código, e, dentro do arquivo 'main.py', vamos atribuir a seguinte linha de código:

```py
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./cloud-indicators-key.json"
```

Isso vai permitir que toda a estrutura de arquivos acesse os serviços do Google Cloud Platform (com as devidas permissões) localmente

> IMPORTANTE: a Service Account Key não é recomendada para o uso de forma descentralizada. Usaremos apenas para o ambiente de desenvolvimento. Jamais compartilhar ou salvar a Service Account Key em repositórios públicos

## Etapas de implementação na nuvem

### Autenticação

Para os próximos passos, usaremos a linha de comando (CLI) para provisionar o ambiente, e, para isso, é necessário realizar a **Autenticação** com a sua conta na GCP. Para isso, vamos instalar o Gcloud CLI, a ferramenta de linha de comando que nos permite interagir com o ambiente do Google Cloud Platform. 

O processo de instalação está descrito <a href="https://cloud.google.com/sdk/docs/install?hl=pt-br">nesta documentação</a> para os sistemas Linux, Windows e Mac

Após a instalação correta da ferramenta de linha de comando Gcloud, vamos executar os seguintes comandos:
```sh
gcloud auth login
gcloud projects list
gcloud config set project YOUR_PROJECT_ID
```

### Preparando o ambiente
Para a próxima etapa, onde iremos "Dockerizar" nossa aplicação, é necessário fazermos alguns ajustes em nossa estrutura de código
1. O primeiro ajuste, é remover qualquer chave ou informação confidencial de dentro do nosso código, como é o caso da service account key que criamos anteriormente
2. Dentro do arquivo **main.py**, vamos remover o bloco de código ```os.environ["GOOGLE_APPLICATION_CREDENTIALS"]```
3. Para os testes, os dados retornados e transformados foram salvos em arquivos CSV localmente. Agora, vamos remover ou comentar o trecho de código responsável por esse carregamento local, mantendo apenas o processo de load para o BigQuery.

### "Dockerizando" a aplicação

Para a implementação do nosso código no ambiente GCP, usaremos o serviço de Cloud Run. E, para isso, é necessário criar um Contêiner Docker para encapsular nossa aplicação Python.

Basicamente, vamos criar uma instância isolada com um sistema operacional linux, permitindo executar o código python criado em qualquer ambiente que suporte o Docker.

Para encapsular uma aplicação Python em um container Docker, você precisará definir um arquivo chamado **Dockerfile** no diretório da sua aplicação. Esse arquivo especificará as instruções para construir o ambiente Docker, tal como mostrado abaixo:

```sh
# Use uma imagem base oficial do Python
FROM python:3.12-slim

# Defina o diretório de trabalho dentro do Contêiner
WORKDIR /app

# Copie os arquivos de dependência para o Contêiner e instale as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código-fonte para o Contêiner
COPY . .

# Mapeie a porta 8080 para o acesso a aplicação dentro do Contêiner
EXPOSE 8080

# Defina o comando para rodar o serviço quando o Contêiner iniciar
CMD ["python3", "main.py"]
```

> IMPORTANTE: é necessário que a porta exposta seja a 8080, padrão utilizado pelo Cloud Run. E é necessário também que a aplicação Flask esteja sendo executada na porta 8080, como configurada dentro do arquivo **main.py**

Após a criação do arquivo de **Dockerfile**, iremos criar o Contêiner. Para esse projeto, iremos utilizar o **Artifacts Registry**, um Hub de repositório de artefatos, incluindo images docker. Para criar o repositório dentro do Artifacts Registry, e configurar o Docker para autenticar com o Artifact Registry, permitindo que você faça pull (download) ou push (upload) de imagens de contêiner armazenadas nesses repositórios, execute os seguinte comandos no terminal:

```sh
# Cria o repositório docker
gcloud artifacts repositories create monday \
  --repository-format=docker \
  --location=us-central1 \
  --description="Repositório Docker"

# Permite a autenticacão
gcloud auth configure-docker us-central1-docker.pkg.dev
```

Nesse caso, vamos criar um repositório chamado 'monday', na região **us-central1**, com o formato para aceitar containers dockers.

Após criar o repositório, é necessário criar o container docker localmente, e armazená-lo no repositório criado. E, para isso, precisamos criar nosso Contêiner Docker com a seguinte nomenclatura:

```sh
LOCATION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE_NAME:TAG
```

Portanto, vamos criar nosso container docker e realizar um push para o repositório criado (lembrando que o primeiro comando no terminal precisa ser executado no mesmo diretório em que o arquivo **Dockerfile** se encontra)
```sh
# Cria a imagem docker seguindo a nomenclatura do Artifacts Registry
docker build -t us-central1-docker.pkg.dev/lookerstudylab/monday/export-monday:v1 .

# Executa um push da imagem para dentro do repositório
docker push us-central1-docker.pkg.dev/lookerstudylab/monday/export-monday:v1
```

### Cloud run

Após a criação do container e do upload do mesmo para dentro do repositório na GCP, agora é possível executar nossa aplicação dentro de um aplicativo no Cloud RUN. Para isso, execute o seguinte comando no terminal:
```sh
gcloud run deploy export-app \
  --image us-central1-docker.pkg.dev/lookerstudylab/monday/export-monday:v1 \
  --region us-central1 \
  --service-account=access-cloud-run@lookerstudylab.iam.gserviceaccount.com \
  --platform managed \
  --allow-unauthenticated
```

Esse comando vai criar um aplicativo chamado **export-app**, usando a imagem docker que criamos na etapa anterior, na região us-central1, com a service account criada na etapa [Criação da Service Account](#criação-da-service-account) e permitindo a execução sem uma autenticação (o que não é recomendado).

Agora, para executar nossa aplicação, vá para o serviço de <a href="https://console.cloud.google.com/run?">Cloud Run</a> na Console da GCP, clique no app criado, e copie sua URL. Em uma aba do navegador (ou até mesmo no terminal usando a ferramenta **curl** ou no postman), cole a URL e execute.
