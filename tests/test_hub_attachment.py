from app import hub_attachment
from util import common_utils


class TestHubAttachment:
    def test_create_cbe_json(self):
        deal_dna_id = "191220191EEIUTf"
        root_oppty_num = "Z7-80SVX1Q"
        deal_details = [
            {
                "parentOpportunity": "Z7-80SVX1Q",
                "childOpportunity": "6I-0E8NHPK",
                "level": "1"
            },
            {
                "parentOpportunity": "Z7-80SVX1Q",
                "childOpportunity": "JH-2G5T4OS",
                "level": "1"
            },
            {
                "parentOpportunity": "Z7-80SVX1Q",
                "childOpportunity": "X7-5ICZR2O",
                "level": "1"
            },
            {
                "parentOpportunity": "Z7-80SVX1Q",
                "childOpportunity": "Z7-80SVX1Q",
                "level": "0"
            }
        ]

        ret_json = hub_attachment.create_cbe_json(deal_dna_id, root_oppty_num, deal_details)
        assert ret_json is not None
        assert len(ret_json) == 3
        assert ret_json["dealDnaId"] == deal_dna_id
        assert ret_json["rootOpportunity"] == root_oppty_num
        assert ret_json["cbeDealDetails"] == deal_details

    def test_create_cscore_json(self):
        deal_dna_id = "191220191EEIUTf"
        total_score = 100
        coaching_priority = "High"
        calculated_coaching_status = "Market"
        status = "COMPLETED"
        cscore_details = [
            {
                "criteriaValue": "1",
                "criteriaName": "Single Line of Business",
                "criteriaScore": 20
            },
            {
                "criteriaValue": "25000000",
                "criteriaName": "TCV",
                "criteriaScore": 30
            },
            {
                "criteriaValue": "True",
                "criteriaName": "Cloud % <60",
                "criteriaScore": 10
            },
            {
                "criteriaValue": "Y",
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
                "criteriaName": "Regulated Industry",
                "criteriaScore": 5
            },
            {
                "criteriaValue": "Y",
                "criteriaName": "Multi-Country Opportunity",
                "criteriaScore": 3
            },
            {
                "criteriaValue": "Y",
                "criteriaName": "Top Account",
                "criteriaScore": 3

            },
            {
                "criteriaValue": "Y",
                "criteriaName": "Troubled Account",
                "criteriaScore": 3
            },
            {
                "criteriaValue": "Y",
                "criteriaName": "Strategic Offerings % < 70",
                "criteriaScore": 10
            },
            {
                "criteriaValue": "Y",
                "criteriaName": "Includes Strategy/Advisory Offering?",
                "criteriaScore": 2
            }
        ]

        ret_json = hub_attachment.create_cscore_json(dna_id=deal_dna_id, total_score=total_score,
                                                     coaching_priority=coaching_priority,
                                                     calculated_coaching_status=calculated_coaching_status,
                                                     cscore_details=cscore_details)
        assert ret_json is not None
        assert len(ret_json) == 6
        assert ret_json["dealDnaId"] == deal_dna_id
        assert ret_json["totalScore"] == total_score
        assert ret_json["coachingPriority"] == coaching_priority
        assert ret_json["calculatedCoachingStatus"] == calculated_coaching_status
        assert ret_json["status"] == status
        assert ret_json["cScoreDetails"] == cscore_details

    def test_upload_json_attachment_cbe(self):
        tx_id = 444523
        deal_dna_id = "191220191EEIUTf"
        root_oppty_num = "Z7-80SVX1Q"
        deal_details = [
            {
                "parentOpportunity": "Z7-80SVX1Q",
                "childOpportunity": "6I-0E8NHPK",
                "level": "1"
            },
            {
                "parentOpportunity": "Z7-80SVX1Q",
                "childOpportunity": "JH-2G5T4OS",
                "level": "1"
            },
            {
                "parentOpportunity": "Z7-80SVX1Q",
                "childOpportunity": "X7-5ICZR2O",
                "level": "1"
            },
            {
                "parentOpportunity": "Z7-80SVX1Q",
                "childOpportunity": "Z7-80SVX1Q",
                "level": "0"
            }
        ]
        attachment_json = hub_attachment.create_cbe_json(dna_id=deal_dna_id, root_oppty_num=root_oppty_num,
                                                         cbe_detail=deal_details)
        resp = hub_attachment.upload_json_attachment(tx_id=tx_id, attachment_json=attachment_json,
                                                     headers=common_utils.CBE_ATTACHMENT_HEADERS)
        assert resp is not None

    def test_upload_json_attachment_cscore(self):
        tx_id = 444523
        deal_dna_id = "191220191EEIUTf"
        total_score = 100
        coaching_priority = "High"
        calculated_coaching_status = "Market"
        cscore_details = [
            {
                "criteriaValue": "1",
                "criteriaName": "Single Line of Business",
                "criteriaScore": 20
            },
            {
                "criteriaValue": "25000000",
                "criteriaName": "TCV",
                "criteriaScore": 30
            },
            {
                "criteriaValue": "True",
                "criteriaName": "Cloud % <60",
                "criteriaScore": 10
            },
            {
                "criteriaValue": "Y",
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
                "criteriaName": "Regulated Industry",
                "criteriaScore": 5
            },
            {
                "criteriaValue": "Y",
                "criteriaName": "Multi-Country Opportunity",
                "criteriaScore": 3
            },
            {
                "criteriaValue": "Y",
                "criteriaName": "Top Account",
                "criteriaScore": 3

            },
            {
                "criteriaValue": "Y",
                "criteriaName": "Troubled Account",
                "criteriaScore": 3
            },
            {
                "criteriaValue": "Y",
                "criteriaName": "Strategic Offerings % < 70",
                "criteriaScore": 10
            },
            {
                "criteriaValue": "Y",
                "criteriaName": "Includes Strategy/Advisory Offering?",
                "criteriaScore": 2
            }
        ]
        ret_json = hub_attachment.create_cscore_json(dna_id=deal_dna_id, total_score=total_score,
                                                     coaching_priority=coaching_priority,
                                                     calculated_coaching_status=calculated_coaching_status,
                                                     cscore_details=cscore_details)

        resp = hub_attachment.upload_json_attachment(tx_id=tx_id, attachment_json=ret_json,
                                                     headers=common_utils.CBE_ATTACHMENT_HEADERS)
        assert resp is not None
