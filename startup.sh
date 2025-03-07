# -------------------------------------------------- Variáveis -----------------------------------------
PROJECT_ID=lookerstudylab
SERVICE_ACOUNT_NAME=etl-monday-to-bq
SERVICE_ACOUNT_VIEWER='extract-data-api-sheet'
CONTAINER_NAME=export-monday
CONTAINER_VERSION=v1
REPOSITORY_NAME=monday-repository
REGION=us-central1
CONTAINER_NAME=export-monday
CONTAINER_VERSION=v1
REPOSITORY_NAME=monday-repository
REGION=us-central1

# -------------------------------------------- Configuraçoes iniciais -----------------------------------------
gcloud auth login
gcloud config set project $PROJECT_ID
gcloud config set project $PROJECT_ID

# -------------------------------------------- Criando container local -------------------------------------------- 
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$CONTAINER_NAME:$CONTAINER_VERSION .
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$CONTAINER_NAME:$CONTAINER_VERSION .

# -------------------------------------- Criando o repositorio para o container -------------------------------------------- 
gcloud artifacts repositories create $REPOSITORY_NAME \
gcloud artifacts repositories create $REPOSITORY_NAME \
  --repository-format=docker \
  --location=$REGION \
  --location=$REGION \
  --description="Repositório Docker"

gcloud auth configure-docker us-central1-docker.pkg.dev

# -------------------------------- Realizando um upload do container para o repositorio -------------------------------------------- 
docker push us-central1-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$CONTAINER_NAME:$CONTAINER_VERSION
docker push us-central1-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$CONTAINER_NAME:$CONTAINER_VERSION

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
  --image us-central1-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$CONTAINER_NAME:$CONTAINER_VERSION \
  --region us-central1 \
  --service-account=$SERVICE_ACOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com \
  --platform managed \
  --allow-unauthenticated \
  --env-vars-file=./env.yaml