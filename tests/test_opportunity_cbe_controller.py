import json

import pytest

from app import opportunity_cbe_controller


class TestOpportunityCbeController:
    def test_process_opportunity_cbe(self):

        root_opportunity_data = dict(
            cbe_status='I',
            root_oppty_num='loydtest6',
            parent_oppty_num='loydtest6',
            oppty_num='loydtest6',
            level_num=0,
        )

        transaction_id, deal_dna_id = opportunity_cbe_controller.process_opportunity_cbe(root_opportunity_data=root_opportunity_data)
        assert transaction_id is not None
        assert deal_dna_id is not None

