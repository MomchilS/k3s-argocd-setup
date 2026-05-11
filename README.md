# K3s ArgoCD Setup

Deploy a Streamlit JSON Updater app on a K3s cluster managed by ArgoCD.

## Repository Layout

```text
.
├── app/
│   ├── requirements.txt
│   ├── streamlit_app.py
│   └── update_jsons.py
├── Dockerfile
├── README.md
├── .dockerignore
└── .gitignore
```

The `Dockerfile` stays at the repository root. Application code lives under `app/`.

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

## Planned Directories

```text
terraform/   # VM provisioning
ansible/     # K3s and host configuration
kubernetes/  # ArgoCD applications and app manifests
```

