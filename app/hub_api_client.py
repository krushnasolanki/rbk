import json
import ssl
from http import HTTPStatus
from typing import *


from app import app_logger, msteams_client
from models.APIClient import APIClient
from util import constants

logger = app_logger.get_logger()


class HubApiAuth:
    def __init__(self):
        self.hub_api_cert_path = constants.HUB_API.get("CERT_PATH")
        self.target_env = constants.HUB_API.get("TARGET_ENV")
        self.client_crt = f"{self.hub_api_cert_path}/api-ibm-com-chain.pem"
        self.client_key = f"{self.hub_api_cert_path}/client.key"
        self.host_name = constants.HUB_API.get("HOST_NAME")
        self.host_port = constants.HUB_API.get("HOST_PORT")
        self.auth_uri = constants.HUB_API.get("AUTH_URI")
        self.ibm_client_id = constants.HUB_API.get("IBM_CLIENT_ID")
        self.ibm_client_secret = constants.HUB_API.get("IBM_CLIENT_SECRET")
        self.use_stg: bool = constants.HUB_API.get("USE_STG")
        self.use_dev: bool = constants.HUB_API.get("USE_DEV")
        self.user_id = constants.HUB_API.get("USER_ID")
        self.password = constants.HUB_API.get("PASSWORD")
        self.client_app_id = constants.HUB_API.get("CLIENT_APP_ID")

    def get_host_name(self) -> str:
        return self.host_name

    def get_host_port(self) -> str:
        return self.host_port

    def get_auth_uri(self) -> str:
        return self.auth_uri

    def get_client_crt(self) -> str:
        return self.client_crt

    def get_client_key(self) -> str:
        return self.client_key

    def get_auth_headers(self) -> Dict[str, str]:
        headers = {"content-type": "application/x-www-form-urlencoded",
                   "X-IBM-Client-Id": f"{self.ibm_client_id}",
                   "X-IBM-Client-Secret": f"{self.ibm_client_secret}"}
        if self.use_stg is True:
            headers["usestg"] = "true"
            app_logger.get_logger().debug(f"Environment for run is STG")
        elif self.use_dev is True:
            headers["useodi"] = "true"
            app_logger.get_logger().debug(f"Environment for run is DEV")

        return headers

    def get_auth_body(self) -> str:
        auth_form = {"userId": self.user_id,
                     "password": constants.HUB_API.get('PASSWORD'),
                     "clientApplicationId": f"{constants.HUB_API.get('CLIENT_APP_ID')}"}
        return auth_form


# initialize token for hub api services
__HUB_API_TOKEN: str = None
# __CONNECTION = None
hub_api_auth: HubApiAuth = HubApiAuth()


@logger.catch
def init_connection():
    # global __CONNECTION

    # see: https://docs.python.org/3.7/library/ssl.html#ssl.SSLContext
    # see: https://docs.python.org/3.7/library/ssl.html#ssl.create_default_context
    if not ssl.HAS_TLSv1_3:
        logger.error(f"{ssl.OPENSSL_VERSION} DOES NOT HAVE support for TLS 1.3")

    # see: https://docs.python.org/3/library/ssl.html#ssl.OP_NO_TLSv1
    # see: https://docs.python.org/3/library/ssl.html#ssl.SSLContext.maximum_version
    # see: https://docs.python.org/3.7/library/ssl.html#context-creation
    ssl.SSLContext.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl.SSLContext.maximum_version = ssl.TLSVersion.TLSv1_3
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_default_certs()
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True
    # try:
    #     context.load_verify_locations(cafile=hub_api_auth.get_client_crt())
    # except Exception as ex:
    #     logger.exception(ex)

    #   ssl.OP_NO_TLSv1_2
    context.options |= (
            ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    )
    return APIClient(host=hub_api_auth.get_host_name(), port=hub_api_auth.get_host_port(), context=context,
                     timeout=constants.API_TIMEOUT_SECONDS)

@logger.catch
def get_connection() -> APIClient:
    return init_connection()


def get_auth_token() -> str:
    global __HUB_API_TOKEN
    if __HUB_API_TOKEN is None:
        connection = get_connection()
        connection.request(method="POST",
                           url=hub_api_auth.get_auth_uri(),
                           headers=hub_api_auth.get_auth_headers(),
                           body=hub_api_auth.get_auth_body())
        response = connection.getresponse()
        data = response.read().decode(constants.DEFAULT_CHARACTER_ENCODING)
        json_data = json.loads(data)
        if response.code == HTTPStatus.OK.value:
            __HUB_API_TOKEN = json_data['bearerTokenDetails']['bearerToken']
            connection.close()
        else:
            err_code = response.code
            err_reason = f"{json_data.get('httpMessage', json_data.get('message'))} - {json_data.get('moreInformation', json_data.get('details'))}"
            connection.close()
            app_logger.get_logger().critical(f"HUB API Token ERROR returned: {response.code} {response.reason}")
            msteams_client.post_to_msteams(f"****HUB API TOKEN****\n"
                                       f"API: AUTH_USER\n"
                                       f"URI: {constants.HUB_API.get('AUTH_URI')}\n"
                                       f"CODE : {err_code} \n"
                                       f"REASON: {err_reason}!")
            exit(1)

    return f"Bearer {__HUB_API_TOKEN}"
