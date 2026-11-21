# Anthropic & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Anthropic  
**Prepared:** June 25, 2026  
**Source:** Anthropic Admin API (`/v1/usage`); Anthropic billing portal  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 27 Present, 11 Deviation, 0 Missing Mandatory, 2 Missing Conditional, 1 Missing Recommended, 16 N/A

---

## Executive Summary

Anthropic bills for API access by token count, disaggregated by model and token type: input tokens, output tokens, cache write tokens, and cache read tokens. Each combination is a distinct FOCUS row. All 21 Mandatory columns have source data. The 11 Deviations cover enum derivation (ChargeCategory, ServiceCategory, PricingCategory, ChargeFrequency), unit normalization, and enterprise ContractedCost. Sixteen columns are legitimately N/A: no per-request resource IDs exist in billing aggregates, no regional routing is visible, and no commitment discount or capacity reservation model exists. The missing SkuPriceId and SkuPriceDetails reflect the absence of a pricing catalog ID structure in Anthropic's API.

**Recommendation:** The FOCUS transform for Anthropic is straightforward. The key structural decision is the granularity of each row: one FOCUS row per model × token type × workspace × day. Anthropic's admin usage API provides the workspace, model, and token type breakdown needed to produce this. The public rate card handles ListUnitPrice. Start with on-demand usage and add batch API rows with PricingCategory = "Dynamic" in a follow-on pass.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Anthropic Admin API** (`GET /v1/usage`): Provides usage data at the organization and workspace level, broken down by model, token type, and time period. Fields include input tokens, output tokens, cache creation tokens, cache read tokens, and associated costs. Workspace-level filtering is available for multi-workspace organizations.

**Anthropic Billing Portal**: Provides monthly invoices with line items by model and token type. Invoice numbers and billing currency are available here.

Key characteristics for FOCUS:

- **Token-based billing:** Every charge is a count of tokens consumed, priced per million. Token types differ in price: input, output, cache write, and cache read are each separately metered.
- **Model-level SKUs:** Each Claude model is a distinct pricing tier. The model ID (e.g., `claude-sonnet-4-6`) is the natural SkuId.
- **Public rate card:** Anthropic publishes per-model, per-token-type pricing. ListCost and ListUnitPrice are derivable from the public rate card without supplementary data.
- **Workspaces:** Anthropic organizations can contain multiple workspaces. The admin API returns usage data per workspace, mapping to FOCUS SubAccountId and SubAccountName.
- **Batch API:** Anthropic offers a batch inference API at 50% discount. Batch usage appears as a distinct pricing tier and maps to PricingCategory = "Dynamic".
- **No regional routing:** Anthropic's API does not expose region assignment to customers. Regional routing is internal to Anthropic's infrastructure.
- **No commitment discounts:** Anthropic has no reserved capacity or savings plan model. All usage is on-demand.
- **Enterprise negotiated rates:** Large enterprise customers may negotiate custom rates. These are not exposed via the admin API.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Each column carries a feature level: Mandatory, Conditional, or Recommended. N/A is a valid FOCUS state for columns that the provider's billing model genuinely does not produce.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Anthropic source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item amount by model and token type | Present |
| EffectiveCost | Mandatory | = BilledCost (no prepaid commitment amortization) | Present |
| ListCost | Mandatory | Public rate × PricingQuantity from Anthropic rate card | Present |
| ContractedCost | Mandatory | = ListCost for standard API customers; enterprise negotiated rates not exposed via API | Deviation |
| BillingAccountId | Mandatory | Anthropic organization account ID | Present |
| BillingAccountName | Mandatory | Organization name | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Start of aggregation period (day or month) | Present |
| ChargePeriodEnd | Mandatory | End of aggregation period | Present |
| ChargeDescription | Mandatory | Derive: model name + token type (e.g., "claude-sonnet-4-6 · Input Tokens") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for all token charges | Deviation |
| ChargeClass | Mandatory (nullable) | null except for correction charges | Present |
| InvoiceIssuerName | Mandatory | "Anthropic, PBC" | Present |
| ProviderName | Mandatory (dep. v1.3) | "Anthropic" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Anthropic" | Present |
| ServiceName | Mandatory | Derive: "Anthropic API" | Deviation |
| ServiceCategory | Mandatory | Derive: "AI and Machine Learning" | Deviation |
| PricingQuantity | Mandatory | Token count expressed in millions (usage ÷ 1,000,000) | Present |
| PricingUnit | Mandatory | Normalize: "1M Input Tokens", "1M Output Tokens", "1M Cache Write Tokens", "1M Cache Read Tokens" | Deviation |
| ConsumedQuantity | Conditional | = PricingQuantity | Present |
| ConsumedUnit | Conditional | = PricingUnit | Present |
| ListUnitPrice | Conditional | Published rate per 1M tokens for the model and token type | Present |
| ContractedUnitPrice | Conditional | = ListUnitPrice for standard customers; enterprise rates require supplementary data | Deviation |
| PricingCategory | Conditional | Derive: "Standard" for on-demand; "Dynamic" for Batch API | Deviation |
| ChargeFrequency | Conditional | Derive: "Usage-Based" | Deviation |
| BillingAccountType | Conditional | Derive from account tier (e.g., "Standard", "Enterprise") | Present |
| SubAccountId | Conditional | Anthropic workspace ID from admin API | Present |
| SubAccountName | Conditional | Workspace name | Present |
| SubAccountType | Conditional | "Workspace" | Present |
| ResourceId | Conditional | N/A: API usage billing aggregates have no per-request resource IDs | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | Claude model ID (e.g., "claude-sonnet-4-6") | Present |
| Tags | Conditional | N/A: Anthropic billing does not include request-level tags | N/A |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation because enterprise rates require supplementary data | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost | Present |
| SkuMeter | Conditional | Derive: "Input Tokens", "Output Tokens", "Cache Write Tokens", "Cache Read Tokens" | Deviation |
| SkuPriceId | Conditional | No pricing catalog rate ID exposed in Anthropic billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable (flat per-token pricing by model) | Missing: Conditional |
| RegionId | Conditional | N/A: Anthropic API does not expose regional routing to customers | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: Anthropic has no reserved capacity or savings plan model | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from Anthropic billing portal | Present |
| ServiceSubcategory | Recommended | No native field; "Large Language Models" as subcategory | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global API with no customer-visible zone assignment | N/A |

**Tally:** 27 Present, 11 Deviation, 0 Missing Mandatory, 2 Missing Conditional, 1 Missing Recommended, 16 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Token usage quantities, model IDs, workspace hierarchy, billing period, invoice numbers, and public pricing. All 21 Mandatory columns have source data. ListUnitPrice is derivable from the published rate card.

**Remaining:** Enterprise ContractedCost requires supplementary pricing data. SkuPriceId and SkuPriceDetails are absent. The 11 Deviations are all achievable through derivation logic, not structural API changes.

### 1.5 Deviations to Fix

**ChargeCategory:** All API token charges → "Usage". Credit adjustments → "Credit". Avoid "Purchase".

**ServiceName and ServiceCategory:** Derive "Anthropic API" and "AI and Machine Learning" as static values.

**PricingUnit:** Normalize to FOCUS format: "1M Input Tokens", "1M Output Tokens", "1M Cache Write Tokens", "1M Cache Read Tokens" per row.

**PricingCategory:** On-demand: "Standard". Batch API rows: "Dynamic" (50% discount applies variable pricing based on batch scheduling).

**SkuMeter:** Derive from the token type field in the admin API response: input → "Input Tokens", output → "Output Tokens", cache_creation → "Cache Write Tokens", cache_read → "Cache Read Tokens".

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. The 16 N/A columns must be documented as legitimately not applicable for a stateless API billing model with no regional routing or commitment discount constructs.

### 2.3 Phased Roadmap

**Phase 0:** Enable admin API access. Pull sample usage data across multiple workspaces and models for one billing month.

**Phase 1: Core token usage transform.** Map on-demand usage rows: BilledCost, ListCost, PricingQuantity/Unit (by token type), SkuId (model ID), SubAccount (workspace), BillingAccount, ChargePeriod, InvoiceId. Derive ChargeCategory, ServiceName, ServiceCategory, PricingCategory, ChargeFrequency, SkuMeter. Delivers conformant output for all Present and Deviation columns.

**Phase 2: Batch API and enterprise.** Add Batch API rows with PricingCategory = "Dynamic". Integrate enterprise negotiated rate data for ContractedCost and ContractedUnitPrice.

**Phase 3: Certify.** Add ServiceSubcategory = "Large Language Models". Drop ProviderName, PublisherName (v1.4). Validate with FOCUS Validator. Submit for certification.

### 2.4 FOCUS Use Cases Anthropic Customers Unlock

**After Phase 1:** Per-model cost breakdown. Token type cost analysis (input vs. output vs. cache). Cost allocation by workspace. Billed vs. list rate verification.

**After Phase 2:** On-demand vs. Batch API cost comparison. Enterprise discount verification via ContractedCost vs. ListCost.

---

## Part 3: Immediate Next Steps

1. Enable Anthropic admin API access and pull one month of workspace-level usage data.
2. Build a rate card mapping model × token type → ListUnitPrice from Anthropic's published pricing page.
3. Implement the Phase 1 on-demand transform. Run through the FOCUS Validator.
4. Design the SkuMeter derivation and PricingUnit normalization logic for all four token types.
5. Open the RFI with `member-cert@finops.org` once Phase 1 data is validator-clean.

---

## Confidence Summary

- **High:** Anthropic's token billing is structurally simple. Token count × rate = cost, with a public rate card. The 27 Present columns are grounded in documented API fields and published pricing.
- **High:** Workspace hierarchy maps cleanly to FOCUS SubAccountId and SubAccountName.
- **High:** The 16 N/A columns correctly reflect Anthropic's stateless API billing model. No regional routing, no resource IDs, and no commitment discount constructs exist in the API billing layer.
- **Moderate:** SkuMeter derivation for cache token types. Cache write and read tokens are billed at different rates and must be separated into distinct FOCUS rows.
- **Low:** Enterprise ContractedCost. Anthropic does not expose negotiated rates via the admin API.

---

## Sources

- Anthropic API Documentation: [docs.anthropic.com](https://docs.anthropic.com)
- Anthropic Admin API Usage Endpoint: [docs.anthropic.com/admin/usage](https://docs.anthropic.com)
- Anthropic Pricing: [anthropic.com/pricing](https://www.anthropic.com/pricing)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
