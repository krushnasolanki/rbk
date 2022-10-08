from app import hub_qil_services


class TestHubQilServices:
    def test_calculate_cscore(self):
        root_opportunity = "Z7-80SVX1Q"
        deal_dna_id = "191220191EEIUTf"

        response, value = hub_qil_services.calculate_cscore(root_opportunity=root_opportunity, deal_dna_id=deal_dna_id)
        assert response is not None
        assert value is not None

    def test_retrieve_deals_for_cscore_calculation(self):

        response, value = hub_qil_services.retrieve_deals_for_cscore_calculation()
        assert response is not None
        assert value is not None

    def test_call_deal_dna_qil62(self):
        root_opportunity = "Z7-80SVX1Q"

        response, value = hub_qil_services.call_deal_dna_qil62()
        assert response is not None
        assert value is not None
