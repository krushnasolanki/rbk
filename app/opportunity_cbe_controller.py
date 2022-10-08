import os
import time
import traceback
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from http import HTTPStatus
from queue import Queue
from typing import Tuple

from loguru import logger

from app import app_logger, hub_api_txn_process, hub_attachment, hub_qil_services, msteams_client
from util import common_utils, constants

cbe_logger = app_logger.get_logger()

NOTIFICATION_QUEUE = Queue()


def process_opportunity_cbe(root_opportunity_data: dict) -> Tuple:
    transaction_id, deal_dna_id = None, None
    root_opportunity = None
    try:
        # Trim the opportunity number to make sure there are no extra spaces
        root_opportunity = root_opportunity_data.get("parent_oppty_num")
        if not common_utils.string_empty_or_null(input_str=root_opportunity):
            root_opportunity = root_opportunity.strip()

        cbe_logger.debug(f"Processing CBE for Root Opportunity: {root_opportunity}")

        # For cbe status N, don't do anything
        if root_opportunity_data['cbe_status'].strip() == 'N':
            cbe_logger.debug(f"Deal DNA Transaction/Attachment already exist for root Opportunity: {root_opportunity}. Skipping")

        # For cbe status I, create CBE tx and attachment
        elif root_opportunity_data['cbe_status'].strip() == 'I':
            cbe_logger.debug(f"Creating Deal DNA Transaction for root Opportunity: {root_opportunity}")

            # call hub Transaction service to create CBE tx
            value_ddna = create_cbe_transaction(root_opportunity)
            if value_ddna is not None:
                cbe_logger.debug(f"Attaching DNA Transaction JSON for root Opportunity: {root_opportunity}")
                transaction_id: int = value_ddna[0]
                deal_dna_id: str = value_ddna[1].strip()

                # Create CBE json
                attachment_json = hub_attachment.create_cbe_json(dna_id=deal_dna_id, root_oppty_num=root_opportunity,
                                                                 cbe_detail=root_opportunity_data)

                # call hub attachment service
                value_ddna_json = upload_cbe_json(oppty_num=root_opportunity, json=attachment_json, tx_id=transaction_id)

                if value_ddna_json is not None:
                    return transaction_id, deal_dna_id

        # when cbe_status is J (JSON) or E(EDIT JSON)
        elif root_opportunity_data['cbe_status'] in ('J', 'E'):
            cbe_logger.debug(f"Attaching DNA Transaction JSON for root Opportunity: {root_opportunity}")
            transaction_id = root_opportunity_data['tx_uid'].strip()
            deal_dna_id = root_opportunity_data['deal_dna_uid']

            # Create CBE json
            attachment_json = hub_attachment.create_cbe_json(dna_id=deal_dna_id, root_oppty_num=root_opportunity,
                                                             cbe_detail=root_opportunity_data)

            # Call hub attachment service
            value_ddna_json = upload_cbe_json(oppty_num=root_opportunity, json=attachment_json, tx_id=transaction_id)

            if value_ddna_json is not None:
                return transaction_id, deal_dna_id

    except Exception as ex:
        cbe_logger.error(
            f"EXCEPTION THROWN PROCESSING ROOT OPP {root_opportunity} \n {traceback.format_exc()}")


@logger.catch
def create_cbe_transaction(root_opportunity, max_retries=constants.MAX_RETRY_COUNT):
    retry_count = 0
    # Retry loop to retry up to N times
    while retry_count <= max_retries + 1:
        ddna_response_cd = 0
        value_ddna = None

        ddna_response_cd, value_ddna = hub_api_txn_process.create_deal_transaction(root_oppty_num=root_opportunity)

        if ddna_response_cd != HTTPStatus.CREATED.value:
            if ddna_response_cd == HTTPStatus.BAD_REQUEST.value:  # ERROR 400
                # Don't retry on this error because it doesn't make sense to
                # Just skip the retry and log it out and move on
                retry_count = max_retries
                cbe_logger.debug(f"Not retrying on 400 error for {root_opportunity} (it just looks like we are)")
            if retry_count >= max_retries:
                err_msg = f"""API: DEAL DNA TRANSACTION
                                URI: {constants.HUB_API.get('TXN_URI'):<10}
                                OPPORTUNITY : {root_opportunity:<10} 
                                CODE : {ddna_response_cd:<10} 
                                REASON: {value_ddna:<10}"""

                cbe_logger.error(f"""ERROR_FINAL
                                {err_msg}""")

                NOTIFICATION_QUEUE.put(f"""****CBE ERROR****
                                        {err_msg}""")
                return None
            else:
                # Try
                retry_count += 1
                cbe_logger.error(f"ERROR CREATING DEAL DNA TX FOR {root_opportunity} "
                                 f"with response code: {ddna_response_cd}, reason: {value_ddna}, retry # {retry_count}")
                continue
        else:
            cbe_logger.debug(
                f" SUCCESSFULLY CREATED DEAL DNA TX FOR {root_opportunity}, RETRY COUNT: {retry_count}")
        return value_ddna


def upload_cbe_json(oppty_num, json, tx_id, max_retries=constants.MAX_RETRY_COUNT):
    retry_count = 0
    while retry_count <= max_retries + 1:
        ddna_json_response_cd, value_ddna_json = hub_attachment.upload_json_attachment(tx_id=tx_id,
                                                                                       attachment_json=json,
                                                                                       headers=common_utils.CBE_ATTACHMENT_HEADERS)

        if ddna_json_response_cd == HTTPStatus.BAD_REQUEST.value:  # ERROR 400
            # Don't retry on this error because it doesn't make sense to
            # Just skip the retry and log it out and move on
            retry_count = max_retries
        if ddna_json_response_cd != HTTPStatus.CREATED.value:
            if retry_count >= max_retries:
                err_msg = f"""API: DEAL DNA JSON ATTACHMENT
                               URI: {constants.HUB_API.get('TXN_JSON_URI')}
                               OPPORTUNITY : {oppty_num} 
                               CODE : {ddna_json_response_cd}
                               REASON : {value_ddna_json}
                               RETRIES ATTEMPTED: {retry_count}"""
                cbe_logger.error(f"""ERROR_FINAL
                                    {err_msg}""")
                NOTIFICATION_QUEUE.put(f"""****CBE ERROR****
                                            {err_msg}""")

                return None
            else:
                retry_count += 1
                cbe_logger.error(f"ERROR_FINAL CREATING DEAL DNA TX FOR {oppty_num} "
                                 f"with response code: {ddna_json_response_cd}, reason: {value_ddna_json}, retry # {retry_count}")
                continue
        return value_ddna_json


def msteams_notification_callback(future):
    while not NOTIFICATION_QUEUE.empty():
        msteams_client.post_to_msteams(NOTIFICATION_QUEUE.get())
        NOTIFICATION_QUEUE.task_done()


if __name__ == '__main__':
    try:
        # Post Initial message to msteams
        # msteams_client.post_to_msteams(f"*CBE Batch Run Thread*\n{datetime.utcnow()} UTC")

        cbe_logger.info(f"Starting CBE Batch process on date and time {datetime.utcnow()}")
        start = time.time()

        # call QIL#62 to determine cbe status
        qil62_response, json_data = hub_qil_services.call_deal_dna_qil62()

        # If return status code is not OK(200) then exit application
        if qil62_response != HTTPStatus.OK.value:
            # Pre-formatted error message
            err_msg = f""""
                                            ERROR CREATING QIL #62"
                                            URI: {constants.QIL_API.get('QIL62_CBEDETAIL_URI')}"
                                            ENVIRONMENT: {common_utils.get_environment()}"
                                            RESPONSE CODE : {qil62_response}"
                                            REASON: {json_data}"""

            cbe_logger.critical(f"""CRITICAL:
                                    {err_msg}""")

            msteams_client.post_to_msteams(f"""****CBE ERROR****
                                        {err_msg}""")
            exit(1)

        # Log results and result amounts from QIL62
        cbe_logger.info(f"Result amount from QIL 62: {len(json_data)}")
        cbe_logger.debug(f"Results from QIL 62: {json_data}")

        # Start creating CBE transactions
        threads = []
        with ThreadPoolExecutor(max_workers=constants.MAX_THREADS_COUNT) as executor:
            # Add all threads to a list
            for root_opportunity_data in json_data:
                threads.append(executor.submit(process_opportunity_cbe, root_opportunity_data))

                #  msteams out all notifications accrued during the run
            for task in threads:
                task.add_done_callback(msteams_notification_callback)

        # Log time elapsed for process
        cbe_logger.info(f"Ending CBE Batch process on date and time {datetime.utcnow()}")
        elapsed_time_fl = (time.time() - start)
        cbe_logger.info(f"Total elapsed time for CBE PROCESS:{elapsed_time_fl // 60} minutes ({elapsed_time_fl} secs)")
    except Exception as exception:
        cbe_logger.critical(f"CRITICAL: Critical exception caught \n {traceback.format_exc()}")
        msteams_client.post_to_msteams(f"****CBE ERROR****\n"
                                   f"CRITICAL: Critical exception caught \n {traceback.format_exc()}")
        exit(1)
