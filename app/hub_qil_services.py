import json
from http import HTTPStatus
from typing import *


from app import app_logger, hub_api_client as auth
from util import constants

logger = app_logger.get_logger()


# QIL 62
def call_deal_dna_qil62() -> Tuple:
    try:
        app_logger.get_logger().debug(f"Processing QIL 62")

        qil62_uri = constants.QIL_API.get("QIL62_CBEDETAIL_URI")
        token = auth.get_auth_token()
        headers = {"Authorization": token,
                   "content-type": "application/json",
                   "X-IBM-Client-Id": constants.HUB_API.get("IBM_CLIENT_ID"),
                   "X-IBM-Client-Secret": constants.HUB_API.get("IBM_CLIENT_SECRET"),
                   "Accept": "application/json"
                   }

        if constants.HUB_API.get("USE_STG") is True:
            headers["usestg"] = "true"
        elif constants.HUB_API.get("USE_DEV") is True:
            headers["useodi"] = "true"

        body: dict = {
            "separator": ";",
            "inputParameterList": [
            ]
        }

        connection = auth.get_connection()
        connection.request(method="POST", url=qil62_uri, headers=headers, body=body)
        response = connection.getresponse()
        data = response.read().decode(constants.DEFAULT_CHARACTER_ENCODING)
        json_data = json.loads(data)

        if response.code == HTTPStatus.OK.value:
            if constants.EXTRA_LOGGING is True:
                logger.debug(f"""
                QIL62 headers: {headers}
                QIL62 URL: {qil62_uri}
                """)
            connection.close()
            return response.code, json_data
        else:
            err_code = response.code
            err_reason = f"{json_data.get('httpMessage', json_data.get('message'))} - {json_data.get('moreInformation', json_data.get('details'))}"
            return err_code, err_reason
    except Exception as exception:
        app_logger.get_logger().error(
            f"ERROR CALLING QIL {qil62_uri}  \n {exception}")
        raise


# QIL 64
def calculate_cscore(root_opportunity: str, deal_dna_id: str) -> Tuple:
    app_logger.get_logger().debug(f"Calculating C-Score (QIL64) for root oppty: {root_opportunity}")
    total_score: int = 0
    cscore_txn_ind: bool = False

    qil64_uri = constants.QIL_API.get("QIL64_CSCORE_URI")
    body = None
    try:
        token = auth.get_auth_token()
        headers = {"Authorization": token,
                   "content-type": "application/json",
                   "X-IBM-Client-Id": constants.HUB_API.get("IBM_CLIENT_ID"),
                   "X-IBM-Client-Secret": constants.HUB_API.get("IBM_CLIENT_SECRET"),
                   "Accept": "application/json"
                   }

        if constants.HUB_API.get("USE_STG") is True:
            headers["usestg"] = "true"
        elif constants.HUB_API.get("USE_DEV") is True:
            headers["useodi"] = "true"

        body: dict = {
            "separator": ";",
            "inputParameterList": [
                {"name": "rootOpptyNum", "value": root_opportunity},
                {"name": "CBE_DNA_UID", "value": deal_dna_id}
            ]
        }

        connection = auth.get_connection()
        connection.request(method="POST", url=qil64_uri, headers=headers, body=body)
        response = connection.getresponse()
        data = response.read().decode(constants.DEFAULT_CHARACTER_ENCODING)
        json_data = json.loads(data)
        if response.code == HTTPStatus.OK.value:
            for score in json_data:
                total_score = total_score + score["rule_score"]
                new_cscore_tx_indc = score["new_cscore_tx_indc"]
                if new_cscore_tx_indc == "TRUE":
                    cscore_txn_ind = True

            formatted_json_data = [
                {"criteriaValue": score_details["rule_value"], "criteriaName": score_details["rule_name"],
                 "criteriaScore": score_details["rule_score"]} for score_details in json_data]

            if constants.EXTRA_LOGGING is True:
                app_logger.get_logger().debug(
                    f"""
                    QIL64_API_RESPONSE: Original json data {json_data} 
                     ------------------------
                     Formatted Json Data {formatted_json_data}
                     """)

                logger.debug(f"""
                                QIL64 headers: {headers}
                                QIL64 URL: {qil64_uri}
                                """)
            connection.close()
            return response.code, (cscore_txn_ind, total_score, formatted_json_data)
        else:
            err_code = response.code
            err_reason = f"{json_data.get('httpMessage', json_data.get('message'))} - {json_data.get('moreInformation', json_data.get('details'))}"
            # connection.close()
            return err_code, err_reason
    except Exception as exception:
        app_logger.get_logger().error(
            f"ERROR: Error calling QIL64 for Root Opportunity : {root_opportunity} with exception: {exception} \nQIL64 payload was: {body}")
        raise


# QIL 63
def retrieve_deals_for_cscore_calculation(max_result_count: int = -1) -> Tuple:
    """ Provides a list of Root opptys with an indicator that says whether the root oppty needs a CScore Transaction or not

          Args:
              max_result_count (int): Max number of results to return from the QiL

          :return:
           1. Response Code of the QiL call
           2. Payload of QiL call (either an error reason, or a list)
          """
    app_logger.get_logger().debug(f"Calling QIL63 to get Root Opptys ")
    try:
        qil63_uri = constants.QIL_API.get("QIL63_CSCORESTATUS_URI")
        token = auth.get_auth_token()

        # Create headers and body for API call
        headers = {"Authorization": token,
                   "content-type": "application/json",
                   "X-IBM-Client-Id": constants.HUB_API.get("IBM_CLIENT_ID"),
                   "X-IBM-Client-Secret": constants.HUB_API.get("IBM_CLIENT_SECRET"),
                   "Accept": "application/json"
                   }

        if constants.HUB_API.get("USE_STG") is True:
            headers["usestg"] = "true"
        elif constants.HUB_API.get("USE_DEV") is True:
            headers["useodi"] = "true"

        body: dict = {}
        max_result_count = int(max_result_count)
        if max_result_count > 0:
            row_count_param = {"name": "rowCt", "value": max_result_count}
            body: dict = {
                "separator": ";",
                "inputParameterList": [
                    row_count_param
                ]
            }
        else:
            body: dict = {
                "separator": ";",
                "inputParameterList": [
                ]
            }

        connection = auth.get_connection()
        connection.request(method="POST", url=qil63_uri, headers=headers, body=body)
        response = connection.getresponse()
        data = response.read().decode(constants.DEFAULT_CHARACTER_ENCODING)
        json_data = json.loads(data)

        if response.code == HTTPStatus.OK.value:
            for deal in json_data:
                deal["oppty_num"] = deal["oppty_num"].strip()
                deal["deal_dna_uid"] = deal["deal_dna_uid"].strip()

            if constants.EXTRA_LOGGING is True:
                logger.debug(f"""
                                QIL63 headers: {headers}
                                QIL63 URL: {qil63_uri}
                                """)
            connection.close()
            return response.code, json_data
        else:
            err_code = response.code
            err_reason = f"{json_data.get('httpMessage', json_data.get('message'))} - {json_data.get('moreInformation', json_data.get('details'))}"
            connection.close()
            return err_code, err_reason
    except Exception as ex:
        app_logger.get_logger().error(f"ERROR: Failed when calling QiL63 with exception: {ex}")
        raise
