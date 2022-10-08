import os
from pathlib import Path
from typing import *


def str_to_bool(input_bool_str) -> bool:
    input_bool_str = str(eval(input_bool_str))
    return True if input_bool_str is not None and input_bool_str == "True" else False


PROJECT_ROOT = Path(__file__).parent.parent
CHARACTER_ENCODING_UTF8: str = "utf-8"
DEFAULT_CHARACTER_ENCODING: str = CHARACTER_ENCODING_UTF8
EXTRA_LOGGING = str_to_bool(os.environ.get("EXTRA_LOGGING"))
CSCORE_RECALC = str_to_bool(os.environ.get("CSCORE_RECALC"))
RECALC_DATE = os.environ.get("RECALC_DATE")

# Database SSL Cert Manager Credentials
CERT_MANAGER: Dict[str, str] = {
    "API_ENDPT": os.environ.get("CERT_MANAGER_API_ENDPT").strip(),
    "IAM_TOKEN_ENDPT": os.environ.get("CERT_MANAGER_IAM_TOKEN_ENDPT").strip(),
    "CLOUD_API_KEY": os.environ.get("CERT_MANAGER_CLOUD_API_KEY").strip(),
    "CERT_CRN": os.environ.get("CERT_MANAGER_CERT_CRN").strip()
}

# QUESTHUB Database Credentials
QUEST_HUB: Dict[str, str] = {
    "DB_NAME": os.environ.get("QUEST_HUB_DB_NAME").strip(),
    "DB_PORT": os.environ.get("QUEST_HUB_DB_PORT").strip(),
    "DB_HOST": os.environ.get("QUEST_HUB_DB_HOST").strip(),
    "DB_USER": os.environ.get("QUEST_HUB_DB_USER").strip(),
    "DB_PASS": os.environ.get("QUEST_HUB_DB_PASS").strip(),
    "DB_SCHEMA": os.environ.get("QUEST_HUB_DB_SCHEMA").strip(),
    "DB_UPDATE_PARENT_OPP": str_to_bool(input_bool_str=os.environ.get("QUEST_HUB_DB_UPDATE_PARENT_OPP").strip()),
    "DB_UPDATE_BOM": str_to_bool(input_bool_str=os.environ.get("QUEST_HUB_DB_UPDATE_BOM").strip()),
}
DB_NEW_CONN: bool = str_to_bool(os.environ.get("QUEST_HUB_NEW"))
QUEST_HUB_ECHO_DEBUG: bool = str_to_bool(os.environ.get("QUEST_HUB_ECHO_DEBUG"))
CONNECTION_POOL_RECYCLE_SECONDS = 400
MAX_THREADS_COUNT = int(os.environ.get("MAX_THREADS_COUNT"))
CONNECTION_POOL_SIZE = MAX_THREADS_COUNT  # Formula for ThreadPoolExecutor to calc how many workers to use
# CONNECTION_POOL_SIZE = min(32, os.cpu_count() + 4)  # Formula for ThreadPoolExecutor to calc how many workers to use
# HUB API Credentials
HUB_API: Dict[str, str] = {
    "CERT_PATH": os.environ.get("HUB_API_CERT_PATH").strip(),
    "HOST_NAME": os.environ.get("HUB_API_HOST_NAME").strip(),
    "HOST_PORT": os.environ.get("HUB_API_HOST_PORT").strip(),
    "AUTH_URI": os.environ.get("HUB_API_AUTH_URI").strip(),
    "TXN_URI": os.environ.get("HUB_API_TXN_URI").strip(),
    "TXN_JSON_URI": os.environ.get("HUB_API_TXN_JSON_URI").strip(),
    "TXN_UTIL_URI": os.environ.get("HUB_API_TXN_UTIL_URI").strip(),
    "IBM_CLIENT_ID": os.environ.get("HUB_API_IBM_CLIENT_ID").strip(),
    "IBM_CLIENT_SECRET": os.environ.get("HUB_API_IBM_CLIENT_SECRET").strip(),
    "USE_STG": str_to_bool(os.environ.get("HUB_API_USE_STG")),
    "USE_DEV": str_to_bool(os.environ.get("HUB_API_USE_DEV")),
    "USER_ID": os.environ.get("HUB_API_USER_ID").strip(),
    "PASSWORD": os.environ.get("HUB_API_PASSWORD").strip(),
    "CLIENT_APP_ID": os.environ.get("HUB_API_CLIENT_APP_ID").strip(),
    "TARGET_ENV": os.environ.get("TARGET_ENV")
}

# QIL properties
QIL_API: Dict[str, Union[str, int]] = {
    "QIL62_CBEDETAIL_URI": os.environ.get("QIL_API_QIL62_CBEDETAIL_URI").strip(),
    "QIL63_CSCORESTATUS_URI": os.environ.get("QIL_API_QIL63_CSCORESTATUS_URI").strip(),
    "QIL64_CSCORE_URI": os.environ.get("QIL_API_QIL64_CSCORE_URI").strip(),
    "ROW_COUNT": int(os.environ.get("QIL_API_ROW_COUNT").strip())
}

API_TIMEOUT_SECONDS = int(os.environ.get("API_TIMEOUT_SECONDS"))
MAX_RETRY_COUNT = int(os.environ.get("MAX_RETRY_COUNT"))
