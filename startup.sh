# -------------------------------------------------- Variáveis -----------------------------------------
PROJECT_ID=lookerstudylab
SERVICE_ACOUNT_NAME=etl-monday-to-bq
SERVICE_ACOUNT_VIEWER='extract-data-api-sheet'

# -------------------------------------------- Configuraçoes iniciais -----------------------------------------
gcloud auth login
gcloud config set project PROJECT_ID

# -------------------------------------------- Criando container local -------------------------------------------- 
docker build -t us-central1-docker.pkg.dev/lookerstudylab/monday/export-monday:v1 .

# -------------------------------------- Criando o repositorio para o container -------------------------------------------- 
gcloud artifacts repositories create monday \
  --repository-format=docker \
  --location=us-central1 \
  --description="Repositório Docker"

gcloud auth configure-docker us-central1-docker.pkg.dev

# -------------------------------- Realizando um upload do container para o repositorio -------------------------------------------- 
docker push us-central1-docker.pkg.dev/lookerstudylab/monday/export-monday:v1

# --------------------------------------- Criando as service Accounts -------------------------------------------- 

gcloud iam service-accounts create $SERVICE_ACOUNT_NAME \
  --display-name="'${SERVICE_ACOUNT_NAME}'" \
  --project=$PROJECT_ID

gcloud iam service-accounts create $SERVICE_ACOUNT_VIEWER \
  --display-name="'${SERVICE_ACOUNT_VIEWER}'" \
  --project=$PROJECT_ID

# ------------------------------- Atribuindo permissoes as services accounts -------------------------------------------- 

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACOUNT_VIEWER@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/viewer"

# ---------------------------------------- Criando o Cloud Run -------------------------------------------- 

https://cloud.google.com/iam/docs/service-accounts-create?hl=pt-br

gcloud run deploy export-app \
  --image us-central1-docker.pkg.dev/lookerstudylab/monday/export-monday:v1 \
  --region us-central1 \
  --service-account=$SERVICE_ACOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars \
    PROJECT_ID=lookerstudylab, \
    KEY=api_key, \
    SERVICE_ACOUNT=key-api-sheet, \
    VERSION=latest, \
    API_URL=https://api.monday.com/v2, \
    DATA_SET=cloud_indicators, \
    REGEX_OLD_BOARD='old', \
    REGEX_CURRENT_BOARD='opt', \
    REGEX_CONSULTANT='consultor', \
    REGEX_NOT_IN_BOARD='sub', \
    SAMPLE_SPREADSHEET_ID='1Ad3OMrTJnkoulvRORS2yFNEBzPeUUjpTXGkXGSaiaOU', \
    SAMPLE_RANGE_NAME='alocação consultor!A2:O300'
  --cpu=2 \
  --memory=2Gi
  