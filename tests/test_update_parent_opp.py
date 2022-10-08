from app import hub_parent_opp_update


class TestHubUpdateParentOpp:

    def test_update_parent_opp_success(self):
        test_parent_opp = 'ODI-TEST'
        test_cscore = 0
        test_tcv_value = -1000
        test_salesstage_cd = '1'
        result = hub_parent_opp_update.update_parent_opportunities(test_parent_opp, test_cscore,
                                                         test_tcv_value, test_salesstage_cd)
        print(f"Result: {result}")
        assert result is not None

    def test_update_parent_opp_fail(self):
        test_parent_opp = 'ZZZZZ'
        test_cscore = 80
        test_tcv_value = 35000
        test_salesstage_cd = '7'
        # negative test with invalid parent opp
        result = hub_parent_opp_update.update_parent_opportunities(root_opportunity=test_parent_opp,
                                                         cscore_total_score=test_cscore,
                                                         tcv_value=test_tcv_value, sales_stage_cd=test_salesstage_cd)

        assert result is None
