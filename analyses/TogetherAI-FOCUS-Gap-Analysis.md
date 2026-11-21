# Together AI & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Together AI  
**Prepared:** June 25, 2026  
**Source:** Together AI API (`/v1/billing/usage`); Together AI dashboard  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 26 Present, 12 Deviation, 0 Missing Mandatory, 2 Missing Conditional, 1 Missing Recommended, 16 N/A

---

## Executive Summary

Together AI operates two billing models: serverless inference (pay-per-token for open-source and proprietary models) and dedicated endpoints (pay-per-GPU-hour for custom deployments). Each model requires a distinct FOCUS row structure. Serverless rows have no resource IDs (stateless API) and token-based PricingUnit. Dedicated endpoint rows have endpoint IDs as ResourceId and hourly PricingUnit. All 21 Mandatory columns have source data for both models. The 12 Deviations cover unit and enum derivation, dedicated endpoint resource mapping, and enterprise pricing. The data source is the Together AI billing API with team-level usage breakdown.

**Recommendation:** Implement serverless inference rows first (token-based, similar to Anthropic). Add dedicated endpoint rows in a second pass using hourly billing and endpoint ID as ResourceId. The two row types require separate transform logic but share the same FOCUS column set.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Together AI API** (`GET /v1/billing/usage`): Returns usage data per model and per team. Serverless usage provides input token, output token counts, and costs. Dedicated endpoint usage provides hours of compute consumed per endpoint instance.

**Together AI Dashboard**: Monthly billing summaries with invoice numbers.

Key characteristics for FOCUS:

- **Dual billing model:** Serverless inference (per-token, many open-source models: Llama, Mistral, Qwen, etc.) and dedicated endpoints (per-GPU-hour, custom model deployments on reserved GPU capacity). Each requires distinct FOCUS row logic.
- **Team hierarchy:** Together AI organizations contain Teams. Team-level usage breakdown maps to SubAccountId and SubAccountName.
- **Public rate card:** Together AI publishes per-model per-token pricing for serverless and per-GPU-type hourly pricing for dedicated endpoints.
- **Endpoint resource IDs:** Dedicated endpoints have unique endpoint IDs that serve as ResourceId. Serverless calls have no per-request IDs in billing aggregates.
- **Fine-tuning:** Together AI supports fine-tuning with training token billing plus inference.
- **No regional routing exposure:** Together AI does not expose region assignment to customers via the billing API.
- **No commitment discounts:** Usage-only pricing; no reserved capacity model at the commitment layer.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Each column carries a feature level: Mandatory, Conditional, or Recommended. N/A is a valid FOCUS state for columns the provider's billing model genuinely does not produce. For Together AI, some columns apply only to dedicated endpoint rows (ResourceId) and are null for serverless rows within the same dataset.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Together AI source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item amount by model and usage type | Present |
| EffectiveCost | Mandatory | = BilledCost (no prepaid commitment amortization) | Present |
| ListCost | Mandatory | Public rate × PricingQuantity from Together AI rate card | Present |
| ContractedCost | Mandatory | = ListCost for standard API; enterprise negotiated rates not exposed via API | Deviation |
| BillingAccountId | Mandatory | Together AI organization account ID | Present |
| BillingAccountName | Mandatory | Organization name | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Start of aggregation period | Present |
| ChargePeriodEnd | Mandatory | End of aggregation period | Present |
| ChargeDescription | Mandatory | Derive: model name + usage type (e.g., "meta-llama/Llama-3-70b-chat-hf · Input Tokens") or endpoint name + "GPU-Hours" | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for all charges | Deviation |
| ChargeClass | Mandatory (nullable) | null except for correction charges | Present |
| InvoiceIssuerName | Mandatory | "Together Computer, Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "Together AI" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Together AI" | Present |
| ServiceName | Mandatory | Derive: "Together AI Inference" for serverless; "Together AI Endpoints" for dedicated | Deviation |
| ServiceCategory | Mandatory | Derive: "AI and Machine Learning" | Deviation |
| PricingQuantity | Mandatory | Token count (÷ 1M) for serverless; GPU-hours for dedicated endpoints | Present |
| PricingUnit | Mandatory | Normalize: "1M Input Tokens" or "1M Output Tokens" for serverless; "GPU-Hours" for dedicated endpoints | Deviation |
| ConsumedQuantity | Conditional | = PricingQuantity | Present |
| ConsumedUnit | Conditional | = PricingUnit | Present |
| ListUnitPrice | Conditional | Published rate per 1M tokens (serverless) or per GPU-hour (dedicated) | Present |
| ContractedUnitPrice | Conditional | = ListUnitPrice for standard; enterprise rates require supplementary data | Deviation |
| PricingCategory | Conditional | Derive: "Standard" for serverless on-demand; "Committed" for dedicated endpoint reservations | Deviation |
| ChargeFrequency | Conditional | Derive: "Usage-Based" for serverless; "Recurring" for dedicated endpoint hourly billing | Deviation |
| BillingAccountType | Conditional | Derive from account tier | Present |
| SubAccountId | Conditional | Together AI team ID | Present |
| SubAccountName | Conditional | Team name | Present |
| SubAccountType | Conditional | "Team" | Present |
| ResourceId | Conditional | Dedicated endpoint ID (null for serverless rows) | Deviation |
| ResourceName | Conditional | Endpoint name from Together AI API (null for serverless rows) | Deviation |
| ResourceType | Conditional | GPU instance type for dedicated endpoint (null for serverless rows) | Deviation |
| SkuId | Conditional | Model ID (serverless) or endpoint configuration ID (dedicated) | Present |
| Tags | Conditional | N/A: Together AI billing does not include request-level tags | N/A |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation because enterprise rates require supplementary data | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost | Present |
| SkuMeter | Conditional | Derive: "Input Tokens", "Output Tokens" for serverless; "GPU-Hours" for dedicated | Deviation |
| SkuPriceId | Conditional | No pricing catalog rate ID exposed in billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable (flat per-unit pricing) | Missing: Conditional |
| RegionId | Conditional | N/A: Together AI API does not expose regional routing to customers | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: no savings plan or reserved capacity model | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from Together AI dashboard | Present |
| ServiceSubcategory | Recommended | No native field; "Large Language Models" for serverless; "GPU Compute" for dedicated endpoints | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global API with no customer-visible zone assignment | N/A |

**Tally:** 26 Present, 12 Deviation, 0 Missing Mandatory, 2 Missing Conditional, 1 Missing Recommended, 16 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Token quantities, team hierarchy, billing period, invoice numbers, and public pricing for both serverless and dedicated endpoints. All 21 Mandatory columns have source data.

**Remaining:** Dedicated endpoint ResourceId/Name/Type derivation requires separate logic from serverless rows. Enterprise ContractedCost requires supplementary data. SkuPriceId absent from billing API.

### 1.5 Deviations to Fix

**Dual row structure:** Implement two transform branches — one for serverless inference (token-based, no ResourceId) and one for dedicated endpoints (GPU-hour, endpoint ID as ResourceId). Both emit to the same FOCUS schema.

**PricingUnit:** Serverless: "1M Input Tokens" / "1M Output Tokens". Dedicated: "GPU-Hours".

**PricingCategory:** Serverless on-demand: "Standard". Dedicated endpoints with committed GPU allocation: "Committed".

**ChargeFrequency:** Serverless: "Usage-Based". Dedicated endpoint hourly billing: "Recurring".

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. The dual billing model (serverless + dedicated) must be documented in the conformance gap report.

### 2.3 Phased Roadmap

**Phase 0:** Pull one month of usage data for both serverless and dedicated endpoint charges. Identify all active models and endpoint configurations.

**Phase 1: Serverless inference.** Map token-based rows for all active LLM models. Derive ChargeCategory, ServiceName, ServiceCategory, PricingCategory, ChargeFrequency, PricingUnit, SkuMeter.

**Phase 2: Dedicated endpoints.** Add endpoint rows with ResourceId (endpoint ID), ResourceName, ResourceType (GPU type), PricingUnit = "GPU-Hours", ChargeFrequency = "Recurring". Finalize ServiceSubcategory mapping.

**Phase 3: Certify.** Drop ProviderName, PublisherName (v1.4). Validate with FOCUS Validator. Submit for certification.

### 2.4 FOCUS Use Cases Together AI Customers Unlock

**After Phase 1:** Per-model serverless inference cost by team. Open-source vs. proprietary model cost comparison. Cross-provider AI cost comparison.

**After Phase 2:** Serverless vs. dedicated endpoint cost per workload. GPU utilization cost analysis for dedicated endpoints.

---

## Part 3: Immediate Next Steps

1. Enable Together AI billing API access and pull one month of team-level usage data.
2. Build rate cards: serverless (model × token type → ListUnitPrice) and dedicated endpoint (GPU type → hourly rate).
3. Implement Phase 1 serverless transform and run through FOCUS Validator.
4. Design the dual-branch transform for serverless vs. dedicated endpoint rows.
5. Open the RFI with `member-cert@finops.org` once Phase 1 data is validator-clean.

---

## Confidence Summary

- **High:** Serverless inference billing is structurally clear. Token count × rate = cost, with a public rate card.
- **High:** Team hierarchy maps cleanly to SubAccountId and SubAccountName.
- **Moderate:** Dedicated endpoint row mapping. Endpoint IDs and GPU types may require enrichment from the endpoint management API rather than the billing API alone.
- **Low:** Enterprise ContractedCost. Together AI does not expose negotiated rates via the billing API.

---

## Sources

- Together AI Documentation: [docs.together.ai](https://docs.together.ai)
- Together AI Pricing: [together.ai/pricing](https://www.together.ai/pricing)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
