import json
from http import HTTPStatus
from typing import *


from app import hub_api_client, app_logger
from util import constants

logger = app_logger.get_logger()
def create_cbe_json(dna_id: str, root_oppty_num: str, cbe_detail: dict):
    """ Creates a CBE json to upload to the HUB

        Args:
            dna_id (str): DNA ID from a transaction
            root_oppty_num (str): Opportunity Number of the root opportunity
            cbe_detail (List[Dict[str, str, str]]): List of opportunity and parent opportunity hierarchies including parent opportunity number, child opportunity number, and level

        :return:
         Dict containing deal dna, root opportunity number, and cbe deal details
        """
    lbom_list = []
    # get the bom list

    bomlevel = {}
    for k, v in cbe_detail.items():
        if k == "parent_oppty_num":
            key = "parentOpportunity"
            bomlevel[key] = v
        elif k == "oppty_num":
            key = "childOpportunity"
            bomlevel[key] = v
        elif k == "level_num":
            key = "level"
            bomlevel[key] = str(v)
    lbom_list.append(bomlevel)

    # construct deal dna json
    return {"dealDnaId": dna_id, "rootOpportunity": root_oppty_num, "cbeDealDetails": lbom_list}


def create_cscore_json(dna_id: str, total_score: int, coaching_priority: str, calculated_coaching_status: str,
                       cscore_details: List[Dict[str, Union[str, int, Dict]]]) -> \
        Dict[
            str, Union[str, int, List]]:
    """ Creates a CBE json to upload to the HUB

        Args:
            dna_id (str): DNA ID from a transaction
            root_oppty_num (str): Opportunity Number of the root opportunity
            cbe_detail (List[Dict[str, str, str]]): List of opportunity and parent opportunity hierarchies including parent opportunity number, child opportunity number, and level

        :return:
         Dict containing deal dna, root opportunity number, and cbe deal details
        """
    ret_json = {"dealDnaId": dna_id.strip(), "totalScore": total_score, "coachingPriority": coaching_priority.strip(),
                "calculatedCoachingStatus": calculated_coaching_status.strip(), "status": "COMPLETED",
                "cScoreDetails": cscore_details}
    if constants.EXTRA_LOGGING is True:
        app_logger.get_logger().debug(f"CREATE_CSCORE_JSON: Cscore Json {ret_json}")
    return ret_json


def upload_json_attachment(tx_id: int, attachment_json: Dict[str, Union[str, List]], headers: Dict[str, str]) -> Tuple[
    str, str]:
    """ Uploads a JSON attachment to the HUB

        Args:
            tx_id (str): Transaction ID
            attachment_json (Dict[List[Dict[str, str]]): Opportunity Number of the root opportunity
            cbe_detail (List[Dict[str, str, str]]): Dict containing deal dna, root opportunity number, and cbe deal details

        :return:
         Response from the API call
        """
    app_logger.get_logger().debug(f"Uploading CBE Deal JSON attachment for TX: {tx_id}")
    ret_attachment: Tuple(str, str) = None
    try:
        if constants.HUB_API.get("USE_STG") is True:
            headers["usestg"] = "true"
        elif constants.HUB_API.get("USE_DEV") is True:
            headers["useodi"] = "true"

        api_conn = hub_api_client.get_connection()
        api_conn.request(method="POST",
                         url=constants.HUB_API.get("TXN_JSON_URI").replace("{{TX_ID}}", f"{tx_id}"),
                         headers=headers,
                         body=attachment_json)

        if constants.EXTRA_LOGGING is True:
            app_logger.get_logger().debug(f"UPLOAD_JSON_API: TX ID {tx_id}, Attachment JSON: {attachment_json}")
            logger.debug(f"""
            Attachment URL (host): {api_conn.host}
            Attachment URL2 (replaced host): {constants.HUB_API.get("TXN_JSON_URI").replace("{{TX_ID}}", f"{tx_id}")}
            Attachment headers: {headers}
            Attachment body: {attachment_json}                
                            """)
        response = api_conn.getresponse()
        data = response.read().decode(constants.DEFAULT_CHARACTER_ENCODING)
        json_data: Dict[str:str] = json.loads(data)
        if response.code == HTTPStatus.CREATED.value:
            api_conn.close()
            ret_attachment = response.code, data
            if constants.EXTRA_LOGGING is True:
                app_logger.get_logger().debug(f"UPLOAD_JSON_API: Response {ret_attachment}")
        else:
            api_conn.close()
            err_code = response.code
            err_reason = f"{json_data.get('httpMessage', json_data.get('message'))} - {json_data.get('moreInformation',json_data.get('details'))}"
            if not err_reason or err_reason.strip() == "":
                err_reason = "No error reason returned"
            ret_attachment = err_code, err_reason
        api_conn.close()
        return ret_attachment
    except Exception as ex:
        app_logger.get_logger().error(
            f"ERROR: Failed when calling HUB attachment service with exception: {ex}\nC-score attachment payload for TX {tx_id} was {attachment_json}")
        raise
