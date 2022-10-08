import json
import traceback
from http import HTTPStatus
from typing import Dict, Tuple


from app import app_logger
from app import hub_api_client
from util import constants

logger = app_logger.get_logger()
class HubApiDealDna:
    def __init__(self):
        self.ddna_uri = constants.HUB_API.get("TXN_URI")
        self.ibm_client_id = constants.HUB_API.get("IBM_CLIENT_ID")
        self.ibm_client_secret = constants.HUB_API.get("IBM_CLIENT_SECRET")
        self.client_app_id = constants.HUB_API.get("CLIENT_APP_ID")
        self.use_stg: bool = constants.HUB_API.get("USE_STG")
        self.use_dev: bool = constants.HUB_API.get("USE_DEV")

    def get_ddna_uri(self) -> str:
        return self.ddna_uri

    def get_client_app_id(self) -> str:
        return str(self.client_app_id)

    def get_ddna_headers(self) -> Dict[str, str]:
        dna_tx_header = {"content-type": "application/x-www-form-urlencoded",
                         "X-IBM-Client-Id": f"{self.ibm_client_id}",
                         "X-IBM-Client-Secret": f"{self.ibm_client_secret}",
                         "Authorization": f"{hub_api_client.get_auth_token()}"}
        if self.use_stg is True:
            dna_tx_header["usestg"] = "true"
        elif self.use_dev is True:
            dna_tx_header["useodi"] = "true"

        return dna_tx_header


# Create Deal Dna function
def create_deal_transaction(root_oppty_num: str) -> Tuple:
    try:
        hub_api_deal_dna: HubApiDealDna = HubApiDealDna()
        root_oppty_num = root_oppty_num.strip()

        # checks if the C-Scores are being Recalculated; Adds additional field for Recalc validation
        deal_dna_body: dict = {"referenceTxId": root_oppty_num,
                               "txTypeCd": "DEAL",
                               "txNm": "Deal Workflow Customer Buying Event Deal",
                               "opptyNum": root_oppty_num,
                               "workstreamCd": "BEWF",
                               "workflowTypeCd": "BESTD",
                               "applicationId": {hub_api_deal_dna.get_client_app_id()},
                               }
        connection = hub_api_client.get_connection()
        connection.request(method="POST",
                           url=hub_api_deal_dna.get_ddna_uri(),
                           headers=hub_api_deal_dna.get_ddna_headers(),
                           body=deal_dna_body)
        if constants.EXTRA_LOGGING is True:
            logger.debug(f"DEAL TX Body: {deal_dna_body}")
            logger.debug(f"DEAL TX headers: {hub_api_deal_dna.get_ddna_headers()}")
        response = connection.getresponse()
        data = response.read().decode(constants.DEFAULT_CHARACTER_ENCODING)
        json_data: Dict[str:str] = json.loads(data)

        if response.code == HTTPStatus.CREATED.value:
            connection.close()

            if constants.EXTRA_LOGGING is True:
                logger.debug(f"DEAL TX success Response: {json_data}")

            status = response.code
            resp = (json_data.get('txUid'), json_data.get('dealDnaUid'))
            return status, resp
        else:
            err_code = response.code
            err_reason = f"{json_data.get('httpMessage', json_data.get('message'))} - {json_data.get('moreInformation', json_data.get('details'))}"
            if err_reason.strip() == "":
                err_reason = "No error reason returned"
            app_logger.get_logger().error(f"ERROR returned: {err_code} {err_reason}")
            connection.close()
            return err_code, err_reason
    except Exception as e:
        if "request-sent" in e.__str__().casefold():
            raise
        app_logger.get_logger().error(f"Failed when calling HUB Deal Dna service: {traceback.format_exc()}")
