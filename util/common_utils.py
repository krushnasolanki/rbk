import os
from pathlib import Path

from app import hub_api_client
from util import constants


# ================= FUNCTIONS ================= #

def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent


def get_environment() -> str:
    env = os.environ.get("ENVIRONMENT")
    switcher = {
        "dev": "development",
        "sit": "sit",
        "prod": "production",
        "staging": "staging",
        "uat": "uat",
        "local": "local",
    }
    return switcher.get(env, switcher.get("local"))


def string_empty_or_null(input_str: str) -> bool:
    return input_str is None or input_str.strip() == ""


CBE_ATTACHMENT_HEADERS = {
    'Authorization': hub_api_client.get_auth_token(),
    'htx-fileNm': 'CBEDeal.json',
    'htx-fileVersionNum': '1',
    'htx-fileDesc': 'CBEDeal json',
    'htx-hubTxAttachTypeCd': 'CBEDEAL',
    'htx-metaConfigId': '1021',
    'htx-metaConfigVersionNum': '1',
    'htx-appVersionBuildTxt': '1',
    'Content-Type': 'application/json',
    'X-IBM-Client-Id': constants.HUB_API.get("IBM_CLIENT_ID"),
    'X-IBM-Client-Secret': constants.HUB_API.get("IBM_CLIENT_SECRET"),
}

CSCORE_ATTACHMENT_HEADERS = {
    'Authorization': hub_api_client.get_auth_token(),
    'htx-fileNm': 'CSCORE.json',
    'htx-fileVersionNum': '1',
    'htx-fileDesc': 'CSCORE json',
    'htx-hubTxAttachTypeCd': 'CSCORE',
    'htx-metaConfigId': '1020',
    'htx-metaConfigVersionNum': '1',
    'htx-appVersionBuildTxt': '1',
    'Content-Type': 'application/json',
    'X-IBM-Client-Id': constants.HUB_API.get("IBM_CLIENT_ID"),
    'X-IBM-Client-Secret': constants.HUB_API.get("IBM_CLIENT_SECRET"),
}

CSCORE_TX_AND_ATTACHMENT_HEADERS = {
    'Authorization': hub_api_client.get_auth_token(),
    'Content-Type': 'application/json',
    'X-IBM-Client-Id': constants.HUB_API.get("IBM_CLIENT_ID"),
    'X-IBM-Client-Secret': constants.HUB_API.get("IBM_CLIENT_SECRET"),
    'htx-txNm': 'Deal Workflow C-Score Transaction for Buying Event',
    'htx-opptyNum': None,
    'htx-workstreamCd': "BEWF",
    'htx-workflowTypeCd': "BESTD",
    'htx-fileNm': 'CSCORE.json',
    'htx-fileDesc': 'CSCORE json',
}
