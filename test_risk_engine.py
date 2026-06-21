import unittest
from risk_engine import RiskAssessmentEngine, VendorRiskInput


class TestRiskAssessmentEngine(unittest.TestCase):
    
    def setUp(self):
        self.engine = RiskAssessmentEngine()

    def test_low_risk_scenario(self):
        vendor = VendorRiskInput(
            vendor_type="Consultancy",
            breach_status="NONE",
            certification_status="Active",
            contract_status="Active"
        )
        result = self.engine.assess_risk(vendor)
        self.assertEqual(result.risk_score, 15)
        self.assertEqual(result.risk_level, "Low")
        self.assertIn("Base risk factor for vendor type 'Consultancy' is 15.", result.explanations)
        self.assertIn("Final calculated risk score is 15, categorized as a LOW risk profile.", result.explanations)

    def test_medium_risk_scenario(self):
        vendor = VendorRiskInput(
            vendor_type="Software Vendor",
            breach_status="NONE",
            certification_status="Expired",
            contract_status="Active"
        )
        result = self.engine.assess_risk(vendor)
        self.assertEqual(result.risk_score, 40)
        self.assertEqual(result.risk_level, "Medium")
        self.assertIn("Added 20 risk points because security certification is 'Expired'.", result.explanations)

    def test_high_risk_scenario(self):
        vendor = VendorRiskInput(
            vendor_type="Integration Partner",
            breach_status="BREACHED_LAST_12_MONTHS",
            certification_status="Active",
            contract_status="Expired"
        )
        result = self.engine.assess_risk(vendor)
        self.assertEqual(result.risk_score, 65)
        self.assertEqual(result.risk_level, "High")
        self.assertIn("Added 20 risk points due to breach history status 'BREACHED_LAST_12_MONTHS'.", result.explanations)
        self.assertIn("Added 15 risk points because vendor contract is 'Expired' (potential orphaned access).", result.explanations)

    def test_critical_risk_clamped_scenario(self):
        vendor = VendorRiskInput(
            vendor_type="Payment Processor",
            breach_status="BREACHED_RECENT",
            certification_status="Expired",
            contract_status="Expired"
        )
        result = self.engine.assess_risk(vendor)
        # 40 (Payment Processor) + 35 (Recent) + 20 (Cert Expired) + 15 (Contract Expired) = 110 -> 100 clamped
        self.assertEqual(result.risk_score, 100)
        self.assertEqual(result.risk_level, "Critical")
        self.assertIn("Aggregate risk score (110) was clamped to fit range [0, 100].", result.explanations)

    def test_invalid_vendor_type(self):
        vendor = VendorRiskInput(
            vendor_type="Hardware Vendor",  # Invalid
            breach_status="NONE",
            certification_status="Active",
            contract_status="Active"
        )
        with self.assertRaises(ValueError) as context:
            self.engine.assess_risk(vendor)
        self.assertIn("Invalid vendor_type 'Hardware Vendor'", str(context.exception))

    def test_invalid_breach_status(self):
        vendor = VendorRiskInput(
            vendor_type="Consultancy",
            breach_status="RECURRING_BREACHES",  # Invalid
            certification_status="Active",
            contract_status="Active"
        )
        with self.assertRaises(ValueError) as context:
            self.engine.assess_risk(vendor)
        self.assertIn("Invalid breach_status 'RECURRING_BREACHES'", str(context.exception))


if __name__ == '__main__':
    unittest.main()
