# Configuraçoes iniciais
gcloud auth login

YOUR_PROJECT_ID=lookerstudylab
gcloud config set project YOUR_PROJECT_ID

#Criando container local
docker build -t us-central1-docker.pkg.dev/lookerstudylab/monday/export-monday:v1 .

# Criando o repositorio para o container
gcloud artifacts repositories create monday \
  --repository-format=docker \
  --location=us-central1 \
  --description="Repositório Docker"

gcloud auth configure-docker us-central1-docker.pkg.dev

# Realizando um upload do container para o repositorio
docker push us-central1-docker.pkg.dev/lookerstudylab/monday/export-monday:v1

gcloud run deploy export-app \
  --image us-central1-docker.pkg.dev/lookerstudylab/monday/export-monday:v1 \
  --region us-central1 \
  --service-account=access-cloud-run@lookerstudylab.iam.gserviceaccount.com \
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
  