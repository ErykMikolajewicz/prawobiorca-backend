gcloud container clusters create-auto prawobiorca --region=europe-central2

gcloud services enable artifactregistry.googleapis.com

gcloud artifacts repositories create prawobiorca-repo \
  --repository-format=docker \
  --location=europe-central2


gcloud services enable container.googleapis.com

gcloud iam service-accounts create prawobiorca-deployer \
  --project=prawobiorca \
  --display-name="Prawobiorca app deployer"


gcloud artifacts repositories add-iam-policy-binding "prawobiorca-repo" \
  --location=europe-central2 \
  --member="serviceAccount:prawobiorca-deployer@prawobiorca.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"


gcloud services enable iamcredentials.googleapis.com
gcloud iam service-accounts add-iam-policy-binding "prawobiorca-deployer@prawobiorca.iam.gserviceaccount.com" \
  --member="user:eryk.mikolajewicz@gmail.com" \
  --role="roles/iam.serviceAccountTokenCreator"


gcloud projects add-iam-policy-binding prawobiorca \
  --member="serviceAccount:296630821006-compute@developer.gserviceaccount.com" \
  --role="roles/artifactregistry.reader"

