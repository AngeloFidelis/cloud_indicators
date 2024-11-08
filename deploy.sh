gcloud auth login
gcloud projects list 
gcloud config get-value project
gcloud config set project YOUR_PROJECT_ID

gcloud artifacts repositories create repo-monday \
  --repository-format=docker \
  --location=us-central1 \
  --description="Repositório Docker"

gcloud auth configure-docker us-central1-docker.pkg.dev


docker build -t us-central1-docker.pkg.dev/lookerstudylab/repo-monday/etl-monday:v1 .
docker push us-central1-docker.pkg.dev/lookerstudylab/repo-monday/etl-monday:v1

gcloud run deploy etl-app \
  --image us-central1-docker.pkg.dev/lookerstudylab/repo-monday/etl-monday:v1 \
  --region=us-central1 \
  --service-account=access-cloud-run@lookerstudylab.iam.gserviceaccount.com \
  --platform managed \
  --allow-unauthenticated