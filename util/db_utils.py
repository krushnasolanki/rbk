import http
import json
import os
import ssl

import sqlalchemy
from sqlalchemy import schema
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, Session, sessionmaker
from sqlalchemy.sql import text

from app import app_logger
from util import constants

SQL_ALC_METADATA: schema.MetaData = None
DB_SCHEMA: str = None
CERTFILE_NAME: str = None


# ================= FUNCTIONS ================= #

def get_connection_details() -> Engine:
    """  Gets the connection properties from the environment variables

    :return:
     Instance of Engine object with proper connection properties
    """
    DB_NAME: str = os.environ.get("QUEST_HUB_DB_NAME").strip()
    DB_PORT: str = os.environ.get("QUEST_HUB_DB_PORT").strip()
    DB_HOST: str = os.environ.get("QUEST_HUB_DB_HOST").strip()
    DB_USER: str = os.environ.get("QUEST_HUB_DB_USER").strip()
    DB_PASS: str = os.environ.get("QUEST_HUB_DB_PASS").strip()
    DB_NEW: bool = constants.DB_NEW_CONN

    # Save connection url to a string so its easily manipulated if need-be
    db_url = f'db2+ibm_db://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME};SECURITY=SSL;'

    # # If underlying database is a DashDB or DB2 Warehouse, then we don't need to pass in a cert like we did before
    # if not DB_NEW:
    #     get_hubcertificate()
    #     db_url += f'SSLServerCertificate={CERTFILE_NAME}'

    ENGINE = sqlalchemy.create_engine(db_url,
                                      echo=constants.QUEST_HUB_ECHO_DEBUG,
                                      pool_size=constants.CONNECTION_POOL_SIZE,
                                      pool_recycle=constants.CONNECTION_POOL_RECYCLE_SECONDS, )

    return ENGINE


def get_schema_metadata() -> schema.MetaData:
    """  Returns the single schema metadata instance to use across the application

    :return:
     Instance of Schema Metadata object mapped binded to the engine and DB schema
    """
    global SQL_ALC_METADATA
    global DB_SCHEMA

    if SQL_ALC_METADATA is None:
        engine = get_connection_details()
        DB_SCHEMA = os.environ.get("QUEST_HUB_DB_SCHEMA")
        SQL_ALC_METADATA = schema.MetaData(bind=engine, schema=DB_SCHEMA)
        SQL_ALC_METADATA.reflect(only=['parent_opportunities', 'buying_event_bom'])
    return SQL_ALC_METADATA


def initialize_db_connection():
    """  Initializes the DB connection by mapping the metadata to a single session instance

    :return:
        N/A
    """
    global SESSION
    global SQL_ALC_METADATA

    # comment this for plain unsecured db connection
    # if not constants.DB_NEW_CONN:
    #     get_hubcertificate()

    metadata: schema.MetaData = get_schema_metadata()
    if metadata is not None:
        sessions_factory = sessionmaker(bind=metadata.bind, autoflush=True, autocommit=False,
                                        expire_on_commit=True)
        return scoped_session(sessions_factory)
        # SESSION = scoped_session(sessions_factory)
    else:
        SESSION = None


def prepare_reflection():
    initialize_db_connection()
    if len(SQL_ALC_METADATA.tables) < 2:
        raise Exception(f"Not able to reflect both Performance tables")


Session = initialize_db_connection()


def get_session():
    """  Returns the single scoped_session instance to use across the application

    :return:
     Instance of Session to make DB calls
    """
    # global SESSION
    # if SESSION is None:
    #     initialize_db_connection()

    if SQL_ALC_METADATA is None:
        initialize_db_connection()

    # if SESSION is None:
    #     app_logger.get_logger().error("ERROR ACQUIRING DB SESSION .. ABORTING ..")
    #     exit(1)

    # session: orm.Session = Session()
    thread_sess = Session()
    return thread_sess


# TODO - Uncomment after access to official prod server
def get_hubtoken():
    cloud_api_key: str = constants.CERT_MANAGER.get("CLOUD_API_KEY")
    iam_endpt: str = constants.CERT_MANAGER.get("IAM_TOKEN_ENDPT").strip()

    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "Accept": "application/json"}
    body = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={cloud_api_key}"
    host = iam_endpt.split("//")[-1].split("/")[0]

    try:
        context = ssl.create_default_context()
        connection = http.client.HTTPSConnection(host=host, context=context)
        connection.request(method="POST", url=iam_endpt, headers=headers, body=body)
        response = connection.getresponse()
        data = response.read().decode(constants.DEFAULT_CHARACTER_ENCODING)
        jsonData = json.loads(data)

        if jsonData is not None and 'access_token' in jsonData:
            token = jsonData['access_token']
            return token
        else:
            if jsonData is not None and 'errorCode' in jsonData:
                error = f"DB CONNECTION: ERROR RETRIEVING CERT MANAGER TOKEN --> {jsonData['errorCode']}::" \
                        f"{jsonData['errorMessage']}"
                app_logger.get_logger().error(error)
                return error
            else:
                app_logger.get_logger().error("DB CONNECTION: NO TOKEN RETURNED!!")
                return None
    except Exception as e:
        app_logger.get_logger().error(f"EXCEPTION THROWN DURING HUB DB TOKEN RETRIEVAL STEP.. {e.__str__}::{data}")
        return None


# def get_hubcertificate():
#     global CERTFILE_NAME
#     CERTFILE_NAME = f"{constants.PROJECT_ROOT}/hubdb2_server.pem"
#
#     token = get_hubtoken()
#     if token is None:
#         return False
#     if token.find('ERROR') != -1:
#         return False
#
#     hub_dbcert_crn: str = constants.CERT_MANAGER.get("CERT_CRN").strip()
#     hub_dbcert_crn = urllib.parse.quote(hub_dbcert_crn, safe='')
#     certmgr_endpt: str = constants.CERT_MANAGER.get("API_ENDPT").strip()
#     # pass the oauth token for authentication
#     headers = {"Authorization": f"Bearer {token}",
#                "Accept": "*/*"}
#     host = certmgr_endpt.split("//")[-1].split("/")[0]
#     try:
#         context = ssl.create_default_context()
#         connection = http.client.HTTPSConnection(host=host, context=context)
#         connection.request(method="GET", url=f"{certmgr_endpt}/{hub_dbcert_crn}", headers=headers)
#         response = connection.getresponse()
#         data = response.read().decode("utf-8")
#         try:
#             jsonData = json.loads(data)
#         except Exception as e:
#             app_logger.get_logger().error(f"ERROR RETURNED RETRIEVING HUB CERTIFICATE..{e.__str__()}::{data}")
#             return False
#
#         if 'data' in jsonData:
#             certificate = jsonData["data"]["content"]
#         else:
#             app_logger.get_logger().error(f"DB CONNECTION: ERROR RETRIEVING SERVER CERTIFICATE.. {jsonData}")
#             return False
#
#         with open(CERTFILE_NAME, "w") as certfile:
#             certfile.write(certificate)
#         return True
#     except Exception as e:
#         app_logger.get_logger().error(f"EXCEPTION THROWN WHEN RETRIEVING HUB CERTIFICATE -- {e.__str__}")
#         return False


# Jim Episale requested the following SQL statement be added to the end of the C-Score process to 'clean up' the transaction table
def clean_up_transaction_table() -> None:
    SESSION = get_session()

    # using update_data dict we protect the app
    # from SQL injection attacks
    # and the query is easier to be managed
    update_data = {
        "SET_ROW_STATUS_CD": "'H'",
        "SELECT_ROW_STATUS_CD": "'I'",
        "APPLICATION_ID": 1001
    }
    # stmt = text(
    #     f"UPDATE QUEST.HUB_TRANSACTION SET ROW_STATUS_CD = {update_data['SET_ROW_STATUS_CD']} WHERE TX_UID IN (SELECT TX_UID FROM (SELECT DEAL_DNA_UID, TX_TYPE_CD, MAX(MIN_TX) AS TX_UID, COUNT(*) FROM (SELECT DEAL_DNA_UID, RNA_REVISION_NUM, REFERENCE_TX_ID, TX_TYPE_CD, MIN(TX_UID) AS MIN_TX, MAX(TX_UID) AS MAX_TX FROM QUEST.HUB_TRANSACTION WHERE ROW_STATUS_CD = {update_data['SELECT_ROW_STATUS_CD']} AND APPLICATION_ID = {update_data['APPLICATION_ID']} GROUP BY DEAL_DNA_UID, RNA_REVISION_NUM, REFERENCE_TX_ID, TX_TYPE_CD) GROUP BY DEAL_DNA_UID, TX_TYPE_CD HAVING COUNT(*) > 1 WITH UR))")

    # Ensure there is only 1 c-score tx active for all deals
    cleanup_stmt = text(f"""
    UPDATE QUEST.HUB_TRANSACTION
SET ROW_STATUS_CD = {update_data['SET_ROW_STATUS_CD']}
WHERE TX_UID IN (SELECT TX_UID
                 FROM (SELECT DEAL_DNA_UID, TX_TYPE_CD, MAX(MIN_TX) AS TX_UID, COUNT(*)
                       FROM (SELECT DEAL_DNA_UID,
                                    RNA_REVISION_NUM,
                                    REFERENCE_TX_ID,
                                    TX_TYPE_CD,
                                    MIN(TX_UID) AS MIN_TX,
                                    MAX(TX_UID) AS MAX_TX
                             FROM QUEST.HUB_TRANSACTION
                             WHERE ROW_STATUS_CD = {update_data['SELECT_ROW_STATUS_CD']}
                                AND TX_TYPE_CD = 'CSCORE'
                               AND APPLICATION_ID = {update_data['APPLICATION_ID']}
                             GROUP BY DEAL_DNA_UID, RNA_REVISION_NUM, REFERENCE_TX_ID, TX_TYPE_CD)
                       GROUP BY DEAL_DNA_UID, TX_TYPE_CD
                       HAVING COUNT(*) > 1
                       WITH UR))
    """)

    # if SESSION is None:
    #     get_session()

    res = SESSION.execute(cleanup_stmt, update_data)
    SESSION.commit()
