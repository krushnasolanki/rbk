import concurrent
import os
import time
import traceback
from concurrent.futures.process import ProcessPoolExecutor
from copy import deepcopy
from datetime import datetime
from http import HTTPStatus
from queue import Queue
from typing import List, Tuple

from ibm_db_dbi import OperationalError
from loguru import logger
from sqlalchemy.exc import DisconnectionError

from app import app_logger, hub_api_util, hub_attachment, hub_parent_opp_update, hub_qil_services, msteams_client
from util import common_utils, constants, db_utils

cscore_logger = app_logger.get_logger()


NOTIFICATION_QUEUE = Queue()


def get_coaching_status_and_priority(tcv: float, total_score: int) -> Tuple[str, str]:
    # Get the calculated coaching status and priority for the deal
    cscore_logger.debug(f"Calculating Coaching Status and Priority")
    ret_status_and_priority = ()
    TCV_1M = 1000000.0
    if tcv >= TCV_1M:
        if total_score > 50:
            ret_status_and_priority = "Central", "High"
        elif 25 <= total_score <= 50:
            ret_status_and_priority = "Market", "Medium"
        elif total_score < 25:
            ret_status_and_priority = "N/A", "Low"
    elif tcv < TCV_1M:
        if total_score > 50:
            ret_status_and_priority = "N/A", "High"
        elif 25 <= total_score <= 50:
            ret_status_and_priority = "N/A", "Medium"
        elif total_score < 25:
            ret_status_and_priority = "N/A", "Low"
    else:
        pass

    return ret_status_and_priority


def format_tcv(cscore_json_data: List, oppty_num=None) -> float:
    tcv_value = None
    try:
        for criteria in cscore_json_data:
            if criteria["criteriaName"].upper().strip() == "TCV":
                tcv_value = criteria["criteriaValue"]
                break
        tcv_value = tcv_value.replace("$", "").strip()
        tcv_value = float(tcv_value)
        return tcv_value
    except Exception as ex:
        cscore_logger.error(
            f"ERROR: TCV data missing from JSON for oppty num: {oppty_num} while trying to format TCV value. Given TCV value was: {tcv_value}")
        raise ValueError(f"MISSING TCV VALUE: {oppty_num}")


def merge_cscore_results(cscore_payload: dict, deal: dict, root_oppty_num: str, dna_id: str):
    # Get the TCV for the deal
    try:
        deal["cscore_txn_ind"] = cscore_payload[0]
        deal["new_calculated_total_score"] = cscore_payload[1]
        deal["cscore_json_data"] = cscore_payload[2]
        tcv_value: float = format_tcv(cscore_json_data=deal["cscore_json_data"],
                                      oppty_num=root_oppty_num)
        deal["tcv"] = tcv_value
        cscore_logger.debug(
            f"Deal {dna_id}, root oppty: {root_oppty_num}, \t TCV: {deal['tcv']}, \t Newly calculated C-Score: {deal['new_calculated_total_score']} \t and Status: {deal['cs_status']}")
    except Exception as ex:
        raise


@logger.catch
def calculate_cscore(root_oppty_num: str, dna_uid: str, max_retries=constants.MAX_RETRY_COUNT) -> dict:
    retry_count = 0
    while retry_count <= max_retries + 1:
        cscore_status, cscore_payload = hub_qil_services.calculate_cscore(root_opportunity=root_oppty_num,
                                                                          deal_dna_id=dna_uid)
        if cscore_status != HTTPStatus.OK.value:
            if retry_count >= max_retries:
                cscore_logger.error(f"ERROR_FINAL: Error calling QIL 64\t"
                                    f"OPPTY: {root_oppty_num}\t"
                                    f"DEAL DNA: {dna_uid}\t"
                                    f"RESPONSE CODE: {cscore_status}\t"
                                    f"REASON: {cscore_payload.__str__()}\t"
                                    f"RETRIES ATTEMPTED: {retry_count}\t"
                                    )
                NOTIFICATION_QUEUE.put(f"*****CSCORE*****\n"
                                       f"API: QIL #64\n"
                                       f"URI: {constants.QIL_API.get('QIL64_CSCORE_URI')}\n"
                                       f"OPPORTUNITY NUM: {root_oppty_num}\n"
                                       f"DEAL DNA ID{dna_uid}\n"
                                       f"RESPONSE CODE: {cscore_status}\n"
                                       f"REASON: {cscore_payload.__str__()}\n"
                                       f"RETRIES ATTEMPTED: {retry_count}"
                                       )
                return None
            else:
                retry_count += 1
                cscore_logger.error(f"ERROR_RETRY: QIL 64 retry #{retry_count}\t"
                                    f"OPPTY: {root_oppty_num}\t"
                                    f"DEAL DNA: {dna_uid}\t"
                                    f"RESPONSE CODE: {cscore_status}\t"
                                    f"REASON: {cscore_payload.__str__()}\t"
                                    f"RETRY #: {retry_count}"
                                    )
                continue
        else:
            cscore_logger.debug(f"DEBUG: Successfully called QIL 64 \t" +
                                f"Oppty: {root_oppty_num}\t"
                                f"Deal Dna: {dna_uid}\t"
                                f"RETRIES ATTEMPTED: {retry_count}\t"
                                )
        return cscore_payload


@logger.catch
def create_tx_and_json(deal: dict, deal_tcv, deal_new_cscore, dna_id, root_oppty_num,
                       max_retries=constants.MAX_RETRY_COUNT) -> dict:
    # Calculate coaching status and coaching priority
    calculated_coaching_status, coaching_priority = get_coaching_status_and_priority(tcv=deal_tcv,
                                                                                     total_score=deal_new_cscore)

    # create cscore json for upload
    cscore_json = hub_attachment.create_cscore_json(dna_id=dna_id, total_score=deal_new_cscore,
                                                    coaching_priority=coaching_priority,
                                                    calculated_coaching_status=calculated_coaching_status,
                                                    cscore_details=deal["cscore_json_data"])

    retry_count = 0
    while retry_count <= max_retries + 1:
        tx_attachment_status, tx_attachment_payload = hub_api_util.create_cscore_tx_and_attachment(
            root_oppty_num=root_oppty_num, dna_id=dna_id, attachment_json=cscore_json,
            headers=deepcopy(common_utils.CSCORE_TX_AND_ATTACHMENT_HEADERS))

        # Check if attachment was created, and if not, go to next oppty
        if tx_attachment_status != HTTPStatus.OK.value:
            if retry_count == max_retries:
                cscore_logger.error(f"ERROR_FINAL: Unable to create C-Score TX and attachment\t"
                                    f"deal: {deal['deal_dna_uid']}\t"
                                    f"oppty: {deal['oppty_num']}\t"
                                    f"total score: {deal['new_calculated_total_score']}\t"
                                    f"RESPONSE CODE: {tx_attachment_status}\t"
                                    f"RETRIES ATTEMPTED: {retry_count}"
                                    )
                NOTIFICATION_QUEUE.put(f"*****CSCORE*****\n"
                                       f"API: C-Score TXN and ATTACHMENT\n"
                                       f"URI: {constants.HUB_API.get('TXN_UTIL_URI')}\n"
                                       f"DEAL DNA UID: {deal['deal_dna_uid']}\n"
                                       f"OPPORTUNITY NUM: {deal['oppty_num']}\n"
                                       f"TOTAL SCORE: {deal['new_calculated_total_score']}\n"
                                       f"RESPONSE CODE: {tx_attachment_status}\n"
                                       f"REASON: {tx_attachment_payload.__str__()}\n"
                                       f"RETRIES ATTEMPTED: {retry_count}"
                                       )
                return None
            else:
                retry_count += 1
                cscore_logger.error(f"ERROR_RETRY: Cscore UTIL retry:\t"
                                    f"deal: {deal['deal_dna_uid']}\t"
                                    f"oppty: {deal['oppty_num']}\t"
                                    f"total score: {deal['new_calculated_total_score']}\t"
                                    f"RESPONSE CODE: {tx_attachment_status}\t"
                                    f"RETRY #: {retry_count}"
                                    )
                continue
        else:
            cscore_logger.debug(f"DEBUG: Successfully created C-Score TX and attachment\t"
                                f"deal: {deal['deal_dna_uid']}\t"
                                f"oppty: {deal['oppty_num']}\t"
                                f"total score: {deal['new_calculated_total_score']}\t"
                                f"RETRIES ATTEMPTED: {retry_count}"
                                )

        deal["tx_uid"] = tx_attachment_payload
        deal_tx_uid = tx_attachment_payload
        cscore_logger.debug(f"TX ID for oppty {deal['oppty_num']} is: {deal_tx_uid}")
        return tx_attachment_payload


@logger.catch
def update_cscore_perf_table(root_oppty_num: str, deal_new_cscore, deal_tcv, deal_sales_stage_cd, perf_table: str,
                             max_retries=constants.MAX_RETRY_COUNT, ) -> Tuple[int, int]:
    # Exit out of function is a table wasn't passed in
    if perf_table is None:
        err_msg = f"No performance table updated for {root_oppty_num}. Check config to ensure that it is set to True"
        cscore_logger.error(err_msg)
        NOTIFICATION_QUEUE.put(err_msg)
        return -1, -1

    retry_count = 0
    while retry_count <= max_retries + 1:
        # Does perf table update depending on which table name was passed in
        parent_opp_status = None
        bom_status = None
        if "parent_opportunities" in perf_table:
            parent_opp_status = hub_parent_opp_update.update_parent_opportunities(
                root_opportunity=root_oppty_num,
                cscore_total_score=deal_new_cscore,
                tcv_value=deal_tcv,
                sales_stage_cd=deal_sales_stage_cd)

        if "buying_event_bom" in perf_table:
            bom_status = hub_parent_opp_update.update_buying_event_bom(
                root_opportunity=root_oppty_num,
                cscore_total_score=deal_new_cscore,
                tcv_value=deal_tcv,
                sales_stage_cd=deal_sales_stage_cd)


        # If both Parent Opp AND BOM fail, then retry
        if (parent_opp_status is None or parent_opp_status < 1) and (bom_status is None or bom_status < 1):
            # If the status number is -429 (made up), then the record is not in the table and no amout of retrying will fix that
            if bom_status == -429:
                retry_count = max_retries

            if parent_opp_status == -429:
                retry_count = max_retries
                
            if retry_count == max_retries:
                cscore_logger.error(
                    f"ERROR_FINAL: Unable to update C-score in performance table ({perf_table})\t"
                    f"OPPORTUNITY NUM: {root_oppty_num}\t"
                    f"TOTAL SCORE: {deal_new_cscore}\t"
                    f"TCV: {deal_tcv}\t"
                    f"SALES STAGE CODE: {deal_sales_stage_cd}\t"
                    f"RETRIES ATTEMPTED: {retry_count}"
                )
                if "buying_event_bom" in perf_table:
                    NOTIFICATION_QUEUE.put(f"*****CSCORE*****\n"
                                           f"API: C-Score Performance Table Update ({perf_table})\n"
                                           f"OPPORTUNITY NUM: {root_oppty_num}\n"
                                           f"TOTAL SCORE: {deal_new_cscore}\n"
                                           f"TCV: {deal_tcv}\n"
                                           f"SALES STAGE CODE: {deal_sales_stage_cd}\n"
                                           f"RETRIES ATTEMPTED: {retry_count}\n"
                                           )
                return None, None
            else:
                retry_count += 1
                cscore_logger.error(f"ERROR_RETRY: C-Score Perf table retry\t"
                                    f"OPPORTUNITY NUM: {root_oppty_num}\t"
                                    f"TOTAL SCORE: {deal_new_cscore}\t"
                                    f"TCV: {deal_tcv}\t"
                                    f"SALES STAGE CODE: {deal_sales_stage_cd}\t"
                                    f"RETRY #: {retry_count}"
                                    )
                continue
        else:
            cscore_logger.debug(
                f"DEBUG: Successfully updated C-score in performance table ({perf_table})\t"
                f"OPPORTUNITY NUM: {root_oppty_num}\t"
                f"TOTAL SCORE: {deal_new_cscore}\t"
                f"TCV: {deal_tcv}\t"
                f"SALES STAGE CODE: {deal_sales_stage_cd}\t"
                f"RETRIES ATTEMPTED: {retry_count}"
            )
            if "parent_opportunities" in perf_table:
                return parent_opp_status, 0
            else:
                return 0, bom_status


@logger.catch
def run_cscore_process(deal: dict):
    try:
        root_oppty_num = deal["oppty_num"].strip()
        dna_id = deal["deal_dna_uid"].strip()
        deal_status = deal["cs_status"].upper().strip()
        deal_sales_stage_cd = deal['sales_stage_cd'].strip()
        deal_new_cscore = -100  # Used as just a dummy value until its actual value is set later
        deal_tcv = -100  # Used as just a dummy value until its actual value is set later

        # ======  Call QIL 64 ======
        cscore_payload = calculate_cscore(root_oppty_num=root_oppty_num,
                                          dna_uid=dna_id)
        if not cscore_payload:
            return

        # Merging payload from C-Score calculation call into Qil63 payload and getting TCV
        merge_cscore_results(cscore_payload=cscore_payload,
                             deal=deal,
                             root_oppty_num=root_oppty_num,
                             dna_id=dna_id)
        deal_new_cscore = deal["new_calculated_total_score"]
        deal_tcv = deal["tcv"]

        if deal_status == "I" or deal_status == "U":
            # ====== Cscore Table Update ======

            # Allows for updating of Both Parent Opp table and Bom table based on environment variable
            perf_table_payload_popp = None
            if constants.QUEST_HUB["DB_UPDATE_PARENT_OPP"] is True:
                perf_table_payload_popp = update_cscore_perf_table(root_oppty_num=root_oppty_num,
                                                              deal_new_cscore=deal_new_cscore,
                                                              deal_tcv=deal_tcv,
                                                              deal_sales_stage_cd=deal_sales_stage_cd,
                                                              perf_table="parent_opportunities")[0]
            else:
                perf_table_payload_popp = 1
                # if not perf_table_payload_popp or perf_table_payload_popp < 0:  # Returns null or -1 if record not in table
                #     return
            perf_table_payload_bom = None
            if constants.QUEST_HUB["DB_UPDATE_BOM"] is True:
                perf_table_payload_bom = update_cscore_perf_table(root_oppty_num=root_oppty_num,
                                                              deal_new_cscore=deal_new_cscore,
                                                              deal_tcv=deal_tcv,
                                                              deal_sales_stage_cd=deal_sales_stage_cd,
                                                              perf_table="buying_event_bom")[1]
            else:
                perf_table_payload_bom = 1

            if (not perf_table_payload_bom or perf_table_payload_bom < 0) and (not perf_table_payload_popp or perf_table_payload_popp < 0):  # Returns null or -1 if record not in table
                    return

            # ====== Call Transaction / Attachment UTIL ======
            tx_attachment_payload = create_tx_and_json(deal=deal,
                                                       deal_tcv=deal_tcv,
                                                       deal_new_cscore=deal_new_cscore,
                                                       dna_id=dna_id,
                                                       root_oppty_num=root_oppty_num)
        else:
            # Record NOT I or U
            cscore_logger.debug(f"Skipping C-Score TX process for "
                                f"deal id: {dna_id} with "
                                f"root oppty {root_oppty_num}")
    except (TimeoutError, DisconnectionError, OperationalError) as e:
        if "read operation timed out" in e.__str__().lower():
            # Dont exit the program if the API itself times out, just if the DB connection does
            pass
        else:
            raise
    except ValueError as e:
        cscore_logger.exception(
            f"Caught exception during overall C-score process. Exception: {e}")
    except Exception as ex:
        cscore_logger.exception(
            f"Caught exception during overall C-score process. Exception: {traceback.format_exc()}")
        NOTIFICATION_QUEUE.put(f"*****CSCORE*****\n"
                               f"OPPORTUNITY NUM: {deal['oppty_num']}\n"
                               f"Caught exception during overall C-score process.\n"
                               f" Exception: {traceback.format_exc()}")


def msteams_notification_callback(future):
    while not NOTIFICATION_QUEUE.empty():
        msteams_client.post_to_msteams(NOTIFICATION_QUEUE.get())
        NOTIFICATION_QUEUE.task_done()


if __name__ == '__main__':
    try:
        # Post Initial message to msteams
        # msteams_client.post_to_msteams(f"*C-Score Batch Run Thread*\n{datetime.utcnow()} UTC")

        cscore_logger.debug(f"Reflecting Database tables")

        # Init db connection with reflection
        db_utils.prepare_reflection()

        cscore_logger.info(f"Triggering C-Score with datetime {datetime.utcnow()}")
        start = time.time()

        # Call qil63 to get all Deals that need to be calculated
        cscore_determine_resp_code, root_oppty_payload = hub_qil_services.retrieve_deals_for_cscore_calculation(
            max_result_count=constants.QIL_API.get("ROW_COUNT"))

        # If the call was unsuccessful then throw an exception
        if cscore_determine_resp_code != HTTPStatus.OK.value:
            msteams_client.post_to_msteams(f"****CSCORE ERROR****"
                                       f"ERROR CREATING QIL #63\n"
                                       f"URI: {constants.QIL_API.get('QIL63_CSCORESTATUS_URI')}\n"
                                       f"RESPONSE CODE : {cscore_determine_resp_code}\n"
                                       f"REASON: {root_oppty_payload}!")
            cscore_logger.critical(f"CRITICAL: Unable to call QIL 63 with exception. RESPONSE CODE: "
                                   f"{cscore_determine_resp_code} and REASON: {root_oppty_payload}")
            exit(1)

        cscore_logger.info(f"Result amount from QIL 63: {len(root_oppty_payload)}")
        cscore_logger.debug(f"Results from QIL 63 ({constants.QIL_API.get('QIL63_CSCORESTATUS_URI')}: {root_oppty_payload}")

        """ CALCULATE C-SCORE AND GET TCV FOR ALL DEALS / OPPTYS  """
        threads = []
        cscore_logger.info(f"CPU CORES: {constants.MAX_THREADS_COUNT}")
        cscore_logger.info(f"MAX WORKERS: {constants.MAX_THREADS_COUNT // 2}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=constants.MAX_THREADS_COUNT) as executor:
            for deal in root_oppty_payload:
                cscore_logger.debug(f"Starting C-Score Process for Oppty: "
                                    f"{deal['oppty_num'].strip()} with SS Code: {deal['sales_stage_cd']}")
                threads.append(executor.submit(run_cscore_process, deal))

            #  msteams out all notifications accrued during the run
            for task in threads:
                task.add_done_callback(msteams_notification_callback)

        # Run query to clean up transaction table
        db_utils.clean_up_transaction_table()

        cscore_logger.info(f"Ending C-Score with datetime {datetime.utcnow()}")
        elapsed_time_fl = (time.time() - start)
        cscore_logger.info(f"Total elapsed time for C-SCORE PROCESS was: "
                           f"{elapsed_time_fl // 60} minutes (or {elapsed_time_fl} seconds)")
    except Exception as ex:
        cscore_logger.critical(
            f"CRITICAL: Critical exception caught. Exiting program... \t{traceback.format_exc()}")
        msteams_client.post_to_msteams(f"*****CSCORE*****"
                                   f"CRITICAL: Critical exception caught. Exiting program... {traceback.format_exc()}")
        exit(1)
