from app import hub_api_util
from util import common_utils


class TestHubApiUtil:
    def test_create_cscore_tx_and_attachment(self):
        SAMPLE_ROOT_OPPTY_NUM = "Z7-80SVX1Q"
        SAMPLE_DNA_ID = "G200319PnNt"
        SAMPLE_ATTACHMENT_JSON = \
            {
                "dealDnaId": "G200319PnNt",
                "totalScore": 95,
                "coachingPriority": "High",
                "calculatedCoachingStatus": "Central",
                "status": "COMPLETED",
                "cScoreDetails": [
                    {
                        "criteriaValue": "89.8%",
                        "criteriaName": "Strategic Offerings % <70",
                        "criteriaScore": 8
                    },
                    {
                        "criteriaValue": "false",
                        "criteriaName": "Troubled Account",
                        "criteriaScore": 0
                    },
                    {
                        "criteriaValue": "0.0%",
                        "criteriaName": "Cloud % <60",
                        "criteriaScore": 10
                    },
                    {
                        "criteriaValue": "0.0%",
                        "criteriaName": "IBM Cloud % <10",
                        "criteriaScore": 4
                    },
                    {
                        "criteriaValue": "Y",
                        "criteriaName": "No Red Hat",
                        "criteriaScore": 10
                    },
                    {
                        "criteriaValue": "Y",
                        "criteriaName": "Multi-Country Opportunity",
                        "criteriaScore": 3
                    },
                    {
                        "criteriaValue": "Y",
                        "criteriaName": "Regulated Industry",
                        "criteriaScore": 5
                    },
                    {
                        "criteriaValue": "Y",
                        "criteriaName": "Top Account",
                        "criteriaScore": 3
                    },
                    {
                        "criteriaValue": "$789000000.00",
                        "criteriaName": "TCV",
                        "criteriaScore": 50
                    },
                    {
                        "criteriaValue": "N",
                        "criteriaName": "Single Line of Business",
                        "criteriaScore": 0
                    },
                    {
                        "criteriaValue": "Y",
                        "criteriaName": "Includes Strategy/Advisory Offering?",
                        "criteriaScore": 2
                    }
                ]
            }
        SAMPLE_HEADERS = common_utils.CSCORE_TX_AND_ATTACHMENT_HEADERS
        resp, err = hub_api_util.create_cscore_tx_and_attachment(root_oppty_num=SAMPLE_ROOT_OPPTY_NUM, dna_id=SAMPLE_DNA_ID, attachment_json=SAMPLE_ATTACHMENT_JSON, headers=SAMPLE_HEADERS)
        assert resp is not None
        assert err is not None