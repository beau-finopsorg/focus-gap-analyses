# Datadog & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Datadog  
**Prepared:** June 25, 2026  
**Source:** Datadog Usage API (`GET /api/v1/usage/`); Datadog billing dashboard  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 28 Present, 10 Deviation, 0 Missing Mandatory, 2 Missing Conditional, 1 Missing Recommended, 16 N/A

---

## Executive Summary

Datadog bills by usage metering across a portfolio of observability products: infrastructure hosts, APM traced hosts, log bytes ingested, custom metrics, synthetics API tests, and more. Each product type has a distinct PricingUnit. Datadog's Usage API provides multi-product, multi-org usage breakdowns with daily granularity. All 21 Mandatory columns have source data. The 10 Deviations cover enum derivation, unit normalization, and enterprise ContractedCost. Sixteen columns are N/A: no per-resource IDs in billing aggregates, no regional billing, and no commitment discount constructs (annual commitment pricing is a pricing tier, not a FOCUS CommitmentDiscount).

**Recommendation:** Datadog's Usage API provides detailed per-product, per-org consumption data with daily granularity. Implement one FOCUS row per Datadog product × child org × billing period. Derive PricingUnit from the product type. The public pricing page covers on-demand ListUnitPrice; annual commitment rates require supplementary pricing data.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Datadog Usage API** (`GET /api/v1/usage/{product}`): Returns daily and monthly usage broken down by product and by child org (for multi-org accounts). Products include infra hosts, APM traces, logs, custom metrics, synthetics, network monitoring, CI/CD, and others. Fields include usage quantity and cumulative cost where available.

**Datadog Billing Dashboard**: Monthly invoices with line items per product. Invoice numbers available here.

Key characteristics for FOCUS:

- **Multi-product metering:** Each Datadog product (Logs, APM, Infra, Synthetics, etc.) is a distinct FOCUS row type with its own PricingUnit.
- **Multi-org billing:** Datadog organizations can have child orgs. The Usage API provides per-child-org breakdowns, mapping to SubAccountId and SubAccountName.
- **Public on-demand pricing:** Datadog publishes per-unit on-demand pricing for all major products. ListUnitPrice is derivable without supplementary data.
- **Annual commitment pricing:** Annual plan customers receive discounted rates in exchange for an annual usage commitment. This is a pricing tier (PricingCategory = "Committed"), not a FOCUS CommitmentDiscount construct.
- **Enterprise pricing:** Large accounts may have custom pricing not accessible via the Usage API.
- **No resource IDs:** Datadog billing aggregates usage by product and time period; there are no per-resource instance IDs at the billing layer.
- **No regional billing:** Datadog is a global SaaS platform. Data centers are selected by Datadog region (US1, EU1, etc.) but this does not produce separate billing line items.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Annual commitment pricing maps to PricingCategory = "Committed", not to the CommitmentDiscount column family. CommitmentDiscount columns are N/A for Datadog.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Datadog source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item amount by product | Present |
| EffectiveCost | Mandatory | = BilledCost (no prepaid commitment amortization) | Present |
| ListCost | Mandatory | On-demand rate × usage quantity from Datadog pricing page | Present |
| ContractedCost | Mandatory | Annual commitment or enterprise negotiated rate × quantity; not in Usage API for enterprise | Deviation |
| BillingAccountId | Mandatory | Datadog organization account ID | Present |
| BillingAccountName | Mandatory | Organization name | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Start of usage period (daily or monthly) | Present |
| ChargePeriodEnd | Mandatory | End of usage period | Present |
| ChargeDescription | Mandatory | Derive: product name (e.g., "Datadog APM Traces · Traced Requests") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for all metered product consumption | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "Datadog, Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "Datadog" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Datadog" | Present |
| ServiceName | Mandatory | Datadog product name: "Datadog Infrastructure", "Datadog APM", "Datadog Logs", etc. | Present |
| ServiceCategory | Mandatory | Derive: "Management and Governance" for observability products | Deviation |
| PricingQuantity | Mandatory | Usage quantity per product: hosts, traced requests, GB ingested, custom metric time series, etc. | Present |
| PricingUnit | Mandatory | Normalize: "Hosts", "Traced Requests", "GB", "Custom Metric Time Series", "API Tests", etc. | Deviation |
| ConsumedQuantity | Conditional | = PricingQuantity | Present |
| ConsumedUnit | Conditional | = PricingUnit | Present |
| ListUnitPrice | Conditional | On-demand rate per usage unit from Datadog pricing page | Present |
| ContractedUnitPrice | Conditional | Annual commitment or enterprise rate per usage unit; Deviation for enterprise accounts | Deviation |
| PricingCategory | Conditional | Derive: "Standard" for on-demand; "Committed" for annual plan commitment | Deviation |
| ChargeFrequency | Conditional | Derive: "Usage-Based" | Deviation |
| BillingAccountType | Conditional | Derive from Datadog account tier | Present |
| SubAccountId | Conditional | Datadog child org ID | Present |
| SubAccountName | Conditional | Child org name | Present |
| SubAccountType | Conditional | "Organization" | Present |
| ResourceId | Conditional | N/A: Datadog billing aggregates by product and time period; no per-resource IDs | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | Datadog product code (e.g., "infra_host", "apm_trace_search") | Present |
| Tags | Conditional | N/A: Datadog billing does not include host or resource tags at the billing layer | N/A |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation because enterprise rates require supplementary data | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost | Present |
| SkuMeter | Conditional | Derive: "Hosts", "Traced Requests", "GB", "Custom Metric Time Series", per product | Deviation |
| SkuPriceId | Conditional | No pricing catalog ID in Datadog billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable (flat per-unit pricing per product tier) | Missing: Conditional |
| RegionId | Conditional | N/A: Datadog billing is not region-specific | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: annual commitment is a pricing tier, not a FOCUS CommitmentDiscount | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from Datadog billing dashboard | Present |
| ServiceSubcategory | Recommended | Map from product: "Infrastructure Monitoring", "APM", "Log Management", "Synthetic Monitoring" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global SaaS with no per-zone billing | N/A |

**Tally:** 28 Present, 10 Deviation, 0 Missing Mandatory, 2 Missing Conditional, 1 Missing Recommended, 16 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Per-product usage quantities, child org hierarchy, billing period, public on-demand pricing, invoice numbers. All 21 Mandatory columns have source data. The Usage API provides daily granularity for all major products.

**Remaining:** Enterprise ContractedCost requires supplementary pricing data. Annual commitment rates may be derived from contract data. SkuPriceId and SkuPriceDetails absent from billing API.

### 1.5 Deviations to Fix

**PricingUnit normalization:** Each Datadog product has a distinct unit: Infra → "Hosts", APM → "Traced Requests", Logs → "GB", Custom Metrics → "Custom Metric Time Series", Synthetics → "API Tests". Build a product → PricingUnit mapping table from Datadog's product taxonomy.

**ChargeCategory:** All Datadog metered consumption → "Usage". Credit adjustments → "Credit".

**PricingCategory:** On-demand plan: "Standard". Annual commitment plan: "Committed". Derive from account plan type.

**SkuMeter:** = PricingUnit (Datadog's meter dimension is the product's billing unit).

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. The annual commitment pricing model must be documented as PricingCategory = "Committed", not as CommitmentDiscount.

### 2.3 Phased Roadmap

**Phase 0:** Enable Usage API access. Pull one month of per-product, per-org daily usage data. Map product codes to PricingUnit labels.

**Phase 1: Core metered transform.** Map Infrastructure and APM rows first (largest spend for most customers). Derive ChargeCategory, ServiceName, ServiceCategory, PricingCategory, PricingUnit, SkuMeter. Add child org SubAccount mapping.

**Phase 2: Full product portfolio.** Extend to all active Datadog products: Logs, Synthetics, Custom Metrics, CI/CD, Network, etc. Integrate supplementary pricing data for annual commitment ContractedCost.

**Phase 3: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate with FOCUS Validator. Submit for certification.

### 2.4 FOCUS Use Cases Datadog Customers Unlock

**After Phase 1:** Per-product cost by child org. On-demand vs. annual commitment rate comparison. Infrastructure + APM cost allocation by team.

**After Phase 2:** Full observability portfolio cost breakdown. ServiceSubcategory-level cost by product category. Cross-product cost efficiency analysis.

---

## Part 3: Immediate Next Steps

1. Enable Datadog Usage API access and pull one month of per-product, per-org usage data.
2. Build a product → PricingUnit mapping table from Datadog's product taxonomy.
3. Implement Phase 1 transform (Infra + APM) and run through FOCUS Validator.
4. Identify account plan type (on-demand vs. annual commitment) for PricingCategory derivation.
5. Open the RFI with `member-cert@finops.org` once Phase 1 data is validator-clean.

---

## Confidence Summary

- **High:** Datadog's Usage API provides detailed per-product, per-org, per-day consumption data. All 28 Present columns are grounded in documented API fields.
- **High:** Child org hierarchy maps cleanly to SubAccountId and SubAccountName.
- **Moderate:** PricingUnit normalization. Datadog has 20+ distinct billing dimensions; the mapping table must cover all active products.
- **Low:** Enterprise ContractedCost. Custom negotiated rates are not accessible via the Usage API.

---

## Sources

- Datadog Usage API: [docs.datadoghq.com/api/latest/usage-metering/](https://docs.datadoghq.com/api/latest/usage-metering/)
- Datadog Pricing: [datadoghq.com/pricing/](https://www.datadoghq.com/pricing/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
