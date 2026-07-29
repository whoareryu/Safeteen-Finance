from admin.adapter.outbound.client.n8n_client import N8nClient
from core.matrix.secret_manager import secret_manager


N8N_WEBHOOK_URL = secret_manager.get_secret("N8N_WEBHOOK_URL", "https://your-n8n-instance.com/webhook/...")


def get_n8n_client() -> N8nClient:
    return N8nClient(webhook_url=N8N_WEBHOOK_URL)
