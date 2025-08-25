
from engrate_sdk.utils import log
from engrate_sdk.http.client import AsyncClient
from engrate_sdk.types.plugins import BasePluginSpec
from src.exceptions import UnexpectedValue

logger = log.get_logger(__name__)




class PluginManager:
    REGISTER_URI= "/plugins"

    def __init__(self, mgmt_url:str):
        self.mgmt_url = mgmt_url

    def __repr__(self):
        return f"<PluginManagementClient(url={self.mgmt_url}>"


    async def register_plugin(self, spec:BasePluginSpec):

        async with AsyncClient() as client:
            data = spec.model_dump()
            response = await client.request(
                method="POST",
                json=data,
                url=f"{self.mgmt_url.rstrip('/')}{self.REGISTER_URI}")

            if response.status_code == 409:
                logger.warning(f"Plugin {spec.name} is already registered, skipping registration.")
                return
            if response.status_code != 201:
                logger.error(f"Failed to register plugin {spec.name} with status code {response.status_code}")
                raise UnexpectedValue(f"Failed to register plugin: {response.status_code}")
            
            

