from datetime import datetime

from ibm_db_dbi import OperationalError
from sqlalchemy.exc import DisconnectionError

from app import app_logger
from util import db_utils


def update_parent_opportunities(root_opportunity: str,
                                cscore_total_score: int,
                                tcv_value: float,
                                sales_stage_cd: str) -> int:

    app_logger.get_logger().debug(f"Updating PARENT_OPPORTUNITIES for: {root_opportunity} "
                              f"with: Total score: {cscore_total_score}, TCV: {tcv_value},"
                              f" and Sales Stage Code:{sales_stage_cd}")

    sess = db_utils.get_session()
    metadata = db_utils.SQL_ALC_METADATA
    try:
        root_opportunity = root_opportunity.strip()


        table_parent_opportunities = metadata.tables['Q2CHUB.parent_opportunities']

        # check the existing number of rows into database
        result = sess.query(table_parent_opportunities) \
            .filter(table_parent_opportunities.c.oppty_num == root_opportunity) \
            .count()

        if result is None or result < 1:
            app_logger.get_logger().error(
                f"PARENT_OPPORTUNITIES RECORDS NOT UPDATED FOR {root_opportunity} .... "
                f"Opp may not exist in PARENT_OPPORTUNITIES table. Investigate")
            result = -429
        else:
            update_data: dict = {
                'be_cscore_num': cscore_total_score,
                'beusd_tcv_amt': tcv_value,
                'be_salesstage_cd': sales_stage_cd
            }
            # update databse with the new values
            sess.query(table_parent_opportunities) \
                .filter(table_parent_opportunities.c.oppty_num == root_opportunity) \
                .update(update_data, synchronize_session=False)

            sess.commit()

            app_logger.get_logger().debug(f"PARENT_OPPORTUNITIES opportunity {root_opportunity} updated "
                                      f"with total score of {cscore_total_score}, and tcv val {tcv_value},"
                                      f" sales stage code {sales_stage_cd} :: row update count {result}")

    except (TimeoutError, DisconnectionError, OperationalError) as e:
        raise
    except Exception as ex:
        app_logger.get_logger().exception(
            f"Error: EXCEPTION THROWN UPDATING TABLE PARENT_OPPORTUNITIES ... {ex.__str__()}")
        raise
    finally:
        db_utils.Session.remove()
    return result


def update_buying_event_bom(root_opportunity: str,
                            cscore_total_score: int,
                            tcv_value: float,
                            sales_stage_cd: str) -> int:
    app_logger.get_logger().debug(f"Updating BUYING_EVENT_BOM {root_opportunity} "
                              f"with: Total score: {cscore_total_score}, "
                              f"TCV: {tcv_value}, and Sales Stage Code:{sales_stage_cd}")

    sess = db_utils.get_session()
    metadata = db_utils.SQL_ALC_METADATA
    try:
        root_opportunity = root_opportunity.strip()

        # if sess is None:
        #     sess = db_utils.get_session()
        #     metadata = db_utils.SQL_ALC_METADATA
        #     # we can reflect it ourselves from a database, using options
        #     # such as 'only' to limit what tables we look at...
        #     metadata.reflect(only=['parent_opportunities', 'buying_event_bom'])

        table_buying_event_bom = metadata.tables['Q2CHUB.buying_event_bom']

        # check the existing number of rows into database
        result = sess.query(table_buying_event_bom) \
            .filter(table_buying_event_bom.c.oppty_num == root_opportunity) \
            .count()

        if result is None or result < 1:
            app_logger.get_logger().error(
                f"BUYING_EVENT_BOM RECORDs NOT UPDATED FOR {root_opportunity} ... "
                f"Opp may not exist in BUYING_EVENT_BOM table. Investigate")
            result = -429
        else:
            update_data: dict = {
                'be_cscore_num': cscore_total_score,
                'beusd_tcv_amt': tcv_value,
                'be_sales_stage_cd': sales_stage_cd,
                'update_id': 'QUESTESA',
                'update_ts': datetime.utcnow()
            }
            # update databse with the new values
            sess.query(table_buying_event_bom) \
                .filter(table_buying_event_bom.c.oppty_num == root_opportunity) \
                .update(update_data, synchronize_session=False)

            sess.commit()

            app_logger.get_logger().debug(f"BUYING_EVENT_BOM opportunity {root_opportunity} updated "
                                      f"with total score of {cscore_total_score}, and tcv val {tcv_value}, "
                                      f"sales stage code {sales_stage_cd} :: row update count {result}")

    except (TimeoutError, DisconnectionError, OperationalError) as e:
        raise
    except Exception as ex:
        app_logger.get_logger().exception(
            f"Error: EXCEPTION THROWN UPDATING TABLE BUYING_EVENT_BOM ... {ex.__str__()}")
        raise
    finally:
        db_utils.Session.remove()
    return result
