gcloud auth login
gcloud config set project YOUR_PROJECT_ID

gcloud artifacts repositories create monday \
  --repository-format=docker \
  --location=us-central1 \
  --description="Repositório Docker"

gcloud auth configure-docker us-central1-docker.pkg.dev



docker build -t us-central1-docker.pkg.dev/lookerstudylab/monday/export-monday:v1 .
docker push us-central1-docker.pkg.dev/lookerstudylab/monday/export-monday:v1

gcloud run deploy export-app \
  --image us-central1-docker.pkg.dev/lookerstudylab/monday/export-monday:v1 \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
