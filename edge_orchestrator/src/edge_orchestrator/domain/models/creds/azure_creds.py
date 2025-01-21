from pydantic import BaseModel


class AzureCreds(BaseModel):
    azure_storage_connection_string: str
    container_name: str
