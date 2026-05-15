# K3s ArgoCD Setup

Deploy a Streamlit JSON Updater app on a K3s node managed by ArgoCD.

## Current Repository Layout

```text
.
├── ansible/
│   ├── ansible.cfg
│   ├── inventory.ini.example
│   ├── group_vars/
│   │   └── all.yml.example
│   ├── roles/
│   │   ├── argocd/
│   │   ├── common/
│   │   ├── helm/
│   │   └── k3s/
│   └── site.yml
├── app/
│   ├── requirements.txt
│   ├── streamlit_app.py
│   └── update_jsons.py
├── terraform/
│   ├── main.tf
│   ├── outputs.tf
│   ├── providers.tf
│   ├── terraform.tfvars.example
│   ├── variables.tf
│   └── versions.tf
├── Dockerfile
├── README.md
├── .dockerignore
└── .gitignore
```

The `Dockerfile` stays at the repository root. Application code lives under `app/`.

Local files such as `terraform/terraform.tfvars`, Terraform state, Ansible inventory, and Ansible local group variables are ignored by Git.

## Build Order

1. Provision one VM with Terraform.
2. Configure K3s on the VM with Ansible.
3. Install ArgoCD on K3s with Helm.
4. Install platform components through ArgoCD.
5. Deploy the JSON Updater app through ArgoCD.

Validate each phase before starting the next one.

## Local App Run

```bash
cd app
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Docker Run

```bash
docker build -t json-updater-tool:local .
docker run --rm -p 8501:8501 json-updater-tool:local
```

Open:

```text
http://localhost:8501
```

## Remaining Planned Directory

```text
kubernetes/  # ArgoCD applications and app manifests
```

