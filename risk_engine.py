from dataclasses import dataclass
from typing import List, Dict

@dataclass
class VendorRiskInput:
    """Input payload representing a vendor's current operational state."""
    breach_status: str
    certification_status: str
    contract_status: str
    vendor_type: str


@dataclass
class RiskAssessmentResult:
    """Output results containing the assessment score, level, and breakdown."""
    risk_score: int
    risk_level: str
    explanations: List[str]


class RiskAssessmentEngine:
    """
    Risk Assessment Engine for calculating vendor risk levels and scores.
    Uses base scores and modifiers based on GRC configurations.
    """
    
    # Base risk values based on vendor type data sensitivity
    BASE_SCORES: Dict[str, int] = {
        "payment processor": 40,
        "cloud provider": 35,
        "integration partner": 30,
        "software vendor": 20,
        "consultancy": 15
    }
    
    # Additive risk scores based on security breach incidents
    BREACH_MODIFIERS: Dict[str, int] = {
        "none": 0,
        "breached_recent": 35,
        "breached_last_12_months": 20,
        "under_investigation": 25
    }
    
    # Additive risk scores based on security credentials expiration
    CERT_MODIFIERS: Dict[str, int] = {
        "active": 0,
        "expired": 20
    }
    
    # Additive risk scores based on active network/data integration with expired contract
    CONTRACT_MODIFIERS: Dict[str, int] = {
        "active": 0,
        "expired": 15
    }

    def assess_risk(self, input_data: VendorRiskInput) -> RiskAssessmentResult:
        """
        Assess risk factors of a vendor and compute final score, category tier, and details.
        
        Args:
            input_data (VendorRiskInput): Vendor details.
            
        Returns:
            RiskAssessmentResult: Calculated score, tier, and textual step explanations.
            
        Raises:
            ValueError: If inputs contain illegal values.
        """
        explanations: List[str] = []
        
        # 1. Normalize and validate inputs
        v_type = input_data.vendor_type.strip().lower()
        b_status = input_data.breach_status.strip().lower()
        c_status = input_data.certification_status.strip().lower()
        k_status = input_data.contract_status.strip().lower()
        
        # Base Score Lookup
        if v_type not in self.BASE_SCORES:
            raise ValueError(
                f"Invalid vendor_type '{input_data.vendor_type}'. "
                f"Must be one of: {', '.join(self.BASE_SCORES.keys())}"
            )
        base_score = self.BASE_SCORES[v_type]
        explanations.append(f"Base risk factor for vendor type '{input_data.vendor_type}' is {base_score}.")

        # Breach Modifier Lookup
        if b_status not in self.BREACH_MODIFIERS:
            raise ValueError(
                f"Invalid breach_status '{input_data.breach_status}'. "
                f"Must be one of: {', '.join(self.BREACH_MODIFIERS.keys())}"
            )
        breach_mod = self.BREACH_MODIFIERS[b_status]
        if breach_mod > 0:
            explanations.append(
                f"Added {breach_mod} risk points due to breach history status '{input_data.breach_status}'."
            )
        else:
            explanations.append("No breach history risk points applied (breach status is None).")

        # Certification Modifier Lookup
        if c_status not in self.CERT_MODIFIERS:
            raise ValueError(
                f"Invalid certification_status '{input_data.certification_status}'. "
                f"Must be one of: {', '.join(self.CERT_MODIFIERS.keys())}"
            )
        cert_mod = self.CERT_MODIFIERS[c_status]
        if cert_mod > 0:
            explanations.append(
                f"Added {cert_mod} risk points because security certification is '{input_data.certification_status}'."
            )
        else:
            explanations.append("No certification risk points applied (certification status is Active).")

        # Contract Modifier Lookup
        if k_status not in self.CONTRACT_MODIFIERS:
            raise ValueError(
                f"Invalid contract_status '{input_data.contract_status}'. "
                f"Must be one of: {', '.join(self.CONTRACT_MODIFIERS.keys())}"
            )
        contract_mod = self.CONTRACT_MODIFIERS[k_status]
        if contract_mod > 0:
            explanations.append(
                f"Added {contract_mod} risk points because vendor contract is '{input_data.contract_status}' (potential orphaned access)."
            )
        else:
            explanations.append("No contract risk points applied (contract status is Active).")

        # 2. Score Aggregation
        calculated_score = base_score + breach_mod + cert_mod + contract_mod
        
        # Clamp score between 0 and 100
        final_score = max(0, min(100, calculated_score))
        if final_score != calculated_score:
            explanations.append(f"Aggregate risk score ({calculated_score}) was clamped to fit range [0, 100].")

        # 3. Categorize Risk Level
        # 0-30 = Low, 31-60 = Medium, 61-80 = High, 81-100 = Critical
        if final_score <= 30:
            level = "Low"
        elif final_score <= 60:
            level = "Medium"
        elif final_score <= 80:
            level = "High"
        else:
            level = "Critical"
            
        explanations.append(f"Final calculated risk score is {final_score}, categorized as a {level.upper()} risk profile.")

        return RiskAssessmentResult(
            risk_score=final_score,
            risk_level=level,
            explanations=explanations
        )
