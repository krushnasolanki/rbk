from app import opportunity_cscore_controller


class TestOpportunityCscoreController:
    def test_format_tcv_zero_value(self):
        sample_json_data = [
            {
                "criteriaValue": "1",
                "criteriaName": "Single Line of Business",
                "criteriaScore": 20
            },
            {
                "criteriaValue": "$.00",
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
        EXPECTED_TCV_VAL = 0.00
        tcv_val = opportunity_cscore_controller.format_tcv(cscore_json_data=sample_json_data)
        assert tcv_val is not None
        assert isinstance(tcv_val, float)
        assert tcv_val == EXPECTED_TCV_VAL

    def test_format_tcv_non_zero_value(self):
        sample_json_data = [
            {
                "criteriaValue": "1",
                "criteriaName": "Single Line of Business",
                "criteriaScore": 20
            },
            {
                "criteriaValue": "$250000.00",
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
        EXPECTED_TCV_VAL = 250000.00
        tcv_val = opportunity_cscore_controller.format_tcv(cscore_json_data=sample_json_data)
        assert tcv_val is not None
        assert isinstance(tcv_val, float)
        assert tcv_val == EXPECTED_TCV_VAL

    def test_format_tcv_non_zero_negative_value(self):
        sample_json_data = [
            {
                "criteriaValue": "1",
                "criteriaName": "Single Line of Business",
                "criteriaScore": 20
            },
            {
                "criteriaValue": "$-250000.00",
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
        EXPECTED_TCV_VAL = -250000.00
        tcv_val = opportunity_cscore_controller.format_tcv(cscore_json_data=sample_json_data)
        assert tcv_val is not None
        assert isinstance(tcv_val, float)
        assert tcv_val == EXPECTED_TCV_VAL

    def test_format_tcv_zero_negative_value(self):
        sample_json_data = [
            {
                "criteriaValue": "1",
                "criteriaName": "Single Line of Business",
                "criteriaScore": 20
            },
            {
                "criteriaValue": "$-.00",
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
        EXPECTED_TCV_VAL = -0.00
        tcv_val = opportunity_cscore_controller.format_tcv(cscore_json_data=sample_json_data)
        assert tcv_val is not None
        assert isinstance(tcv_val, float)
        assert tcv_val == EXPECTED_TCV_VAL

    def test_run_cscore_process_insert(self):
        TEST_DEAL = {'cs_status': 'I', 'deal_dna_uid': 'G200421yyCd', 'oppty_num': 'loydtest6', 'tx_uid': None,
                     'sales_stage_cd': 'LO'}
        opportunity_cscore_controller.run_cscore_process(deal=TEST_DEAL)

    def test_run_cscore_process_update(self):
        TEST_DEAL = {'cs_status': 'U', 'deal_dna_uid': 'G200421yyCd', 'oppty_num': 'loydtest6', 'tx_uid': 668678,
                     'sales_stage_cd': 'LO'}
        opportunity_cscore_controller.run_cscore_process(deal=TEST_DEAL)

