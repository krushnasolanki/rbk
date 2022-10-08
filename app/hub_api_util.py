import json
from http import HTTPStatus
from typing import Dict


from app import app_logger
from app import hub_api_client
from util import constants

logger = app_logger.get_logger()


def create_cscore_tx_and_attachment(root_oppty_num: str, dna_id: str, attachment_json: Dict, headers: Dict):
    root_oppty_num = root_oppty_num.strip()
    app_logger.get_logger().debug(
        f"Creating C-Score transaction and C-Score attachment for oppty num: {root_oppty_num}")

    try:
        if constants.HUB_API.get("USE_STG") is True:
            headers["usestg"] = "true"
        elif constants.HUB_API.get("USE_DEV") is True:
            headers["useodi"] = "true"

        headers["htx-opptyNum"] = root_oppty_num
        if constants.CSCORE_RECALC is True:
            headers["htx-appVersionBuildTxt"] = f"QUESTESA_RECALC_{constants.RECALC_DATE}"

        api_uri = f"{constants.HUB_API.get('TXN_UTIL_URI')}"
        api_uri_str = f"{api_uri.replace('{{DNA_ID}}', dna_id).replace('{{OPPTY_NUM}}', root_oppty_num).strip()}"
        # api_uri = f"{api_uri.replace('{{OPPTY_NUM}}', root_oppty_num).strip()}"
        api_conn = hub_api_client.get_connection()
        json_body = attachment_json

        # Add extra debugging if needed
        if constants.EXTRA_LOGGING is True:
            app_logger.get_logger().debug(
                f"UTIL_SERVICE: Root Oppty {root_oppty_num}, Deal DNA: {dna_id}, attachment_json, {attachment_json}, header oppty num: {headers['htx-opptyNum']}")

        api_conn.request(method="POST",
                         url=api_uri_str,
                         headers=headers,
                         body=json_body)
        response = api_conn.getresponse()

        data = response.read().decode(constants.DEFAULT_CHARACTER_ENCODING)
        json_data: Dict[str:str] = json.loads(data)
        resp_status = response.code
        if resp_status == HTTPStatus.OK.value:
            ret_tx = (response.code, json_data['txUid'])

            if constants.EXTRA_LOGGING is True:
                app_logger.get_logger().debug(
                    f"UTIL_SERVICE: RESPONSE {json_data}")

                logger.debug(f"""
                                C-Score UTIL headers: {json.dumps(headers, indent=3, sort_keys=True)}
                                C-Score UTIL URL orig: {api_uri}
                                C-Score UTIL URL new instance: {api_uri_str}
                                """)
        else:
            err_code = response.code
            err_reason = f"{json_data.get('httpMessage', json_data.get('message'))} - {json_data.get('moreInformation', json_data.get('details'))}"

            if err_reason.strip() == "":
                err_reason = "No error reason returned"

            ret_tx = err_code, err_reason
            app_logger.get_logger().error(f"Error creating C-Score UTIL:\nAPI:{api_uri}\nJSON Body: {json_body}")

        api_conn.close()
        return ret_tx
    except Exception as ex:
        app_logger.get_logger().error(
            f"ERROR: Failed when creating C-Score transaction and C-Score attachment: {ex}\nC-score TX payload was: {attachment_json}")
        raise
