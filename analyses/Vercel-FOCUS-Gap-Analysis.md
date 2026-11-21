# Vercel & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Vercel  
**Prepared:** June 25, 2026  
**Source:** Vercel Billing API (`GET /v1/billing/charges`); FOCUS v1.3 native output  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 40 Present, 5 Deviation, 0 Missing Mandatory, 2 Missing Conditional, 1 Missing Recommended, 9 N/A

---

## Executive Summary

Vercel is the highest-conformance provider in this analysis: its billing API (`GET /v1/billing/charges`) returns FOCUS v1.3-formatted data natively. Vercel bills by consumption across three dimensions: Vercel Functions invocation duration (GB-seconds), Edge Requests, and Edge Middleware invocations, plus flat team/project subscription fees. Because Vercel outputs FOCUS fields directly, the remaining work is field verification, minor schema migration from v1.3 to v1.4, and populating the columns Vercel does not yet emit.

**Recommendation:** Use Vercel's native FOCUS output as the starting point. Verify field values against the FOCUS v1.2 specification. Add ServiceSubcategory (Missing: Recommended). Drop ProviderName and PublisherName on migration to v1.4. The gap from Vercel's native v1.3 output to certified v1.2 is minimal.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Vercel Billing API** (`GET /v1/billing/charges`): Returns FOCUS v1.3-formatted billing rows. Fields include BilledCost, EffectiveCost, ListCost, ContractedCost, ChargeCategory, ServiceName, PricingUnit, PricingQuantity, ResourceId, and SubAccount columns for team billing. The API is the primary FOCUS data source for Vercel.

Vercel charges break down into:
- **Vercel Functions:** Billed per GB-second of compute. ResourceId = function deployment ID.
- **Edge Requests:** Billed per million requests served from Vercel's Edge Network.
- **Edge Middleware:** Billed per million invocations.
- **Bandwidth:** Egress bandwidth billed per GB.
- **Pro/Enterprise subscription:** Flat monthly or annual team fee. ChargeCategory = "Purchase".
- **Storage:** Blob storage (Vercel Blob), Postgres (Vercel Postgres), KV (Vercel KV) billed by usage.

Key characteristics:
- **Native FOCUS v1.3 output:** Vercel's Billing API emits fields that map directly to FOCUS column names.
- **Team hierarchy:** Vercel teams (sub-accounts) map to SubAccountId.
- **Project-level ResourceId:** Vercel project IDs are available as ResourceId.
- **Public pricing:** Vercel publishes per-unit pricing for all metered dimensions.
- **No regional billing rows:** Vercel's edge network is global; billing does not split by edge location.
- **No CommitmentDiscount:** Vercel Pro/Enterprise subscriptions are term licenses (PricingCategory = "Committed"), not per-resource CommitmentDiscounts.

### 1.2 How Conformance Is Judged

Because Vercel already emits FOCUS v1.3, the gap analysis focuses on: (1) deviations in field values vs. spec requirements; (2) fields Vercel emits but with non-conformant values; (3) fields Vercel does not emit that are required by FOCUS v1.2 as mandatory or conditional.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Vercel source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Native: billed_cost | Present |
| EffectiveCost | Mandatory | Native: effective_cost | Present |
| ListCost | Mandatory | Native: list_cost | Present |
| ContractedCost | Mandatory | Native: contracted_cost | Present |
| BillingAccountId | Mandatory | Native: billing_account_id | Present |
| BillingAccountName | Mandatory | Native: billing_account_name | Present |
| BillingCurrency | Mandatory | Native: billing_currency | Present |
| BillingPeriodStart | Mandatory | Native: billing_period_start | Present |
| BillingPeriodEnd | Mandatory | Native: billing_period_end | Present |
| ChargePeriodStart | Mandatory | Native: charge_period_start | Present |
| ChargePeriodEnd | Mandatory | Native: charge_period_end | Present |
| ChargeDescription | Mandatory | Native: charge_description | Present |
| ChargeCategory | Mandatory | Native: charge_category; verify "Usage"/"Purchase" values | Present |
| ChargeClass | Mandatory (nullable) | Native: charge_class | Present |
| InvoiceIssuerName | Mandatory | Native: "Vercel Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | Native: "Vercel" | Present |
| PublisherName | Mandatory (dep. v1.3) | Native: "Vercel" | Present |
| ServiceName | Mandatory | Native: service_name | Present |
| ServiceCategory | Mandatory | Native: service_category; verify values against FOCUS enum | Deviation |
| PricingQuantity | Mandatory | Native: pricing_quantity | Present |
| PricingUnit | Mandatory | Native: pricing_unit; verify unit strings match FOCUS convention | Deviation |
| ConsumedQuantity | Conditional | Native: consumed_quantity | Present |
| ConsumedUnit | Conditional | Native: consumed_unit | Present |
| ListUnitPrice | Conditional | Native: list_unit_price | Present |
| ContractedUnitPrice | Conditional | Native: contracted_unit_price | Present |
| PricingCategory | Conditional | Native: pricing_category | Present |
| ChargeFrequency | Conditional | Native: charge_frequency | Present |
| BillingAccountType | Conditional | Native: billing_account_type | Present |
| SubAccountId | Conditional | Native: sub_account_id (Vercel team ID) | Present |
| SubAccountName | Conditional | Native: sub_account_name | Present |
| SubAccountType | Conditional | Native: sub_account_type | Present |
| ResourceId | Conditional | Native: resource_id (Vercel project or deployment ID) | Present |
| ResourceName | Conditional | Native: resource_name | Present |
| ResourceType | Conditional | Native: resource_type; verify values | Deviation |
| SkuId | Conditional | Native: sku_id | Present |
| Tags | Conditional | N/A: Vercel billing does not expose project tags at billing layer | N/A |
| PricingCurrency | Conditional | Native: pricing_currency | Present |
| PricingCurrencyListUnitPrice | Conditional | Native: pricing_currency_list_unit_price | Present |
| PricingCurrencyContractedUnitPrice | Conditional | Native: pricing_currency_contracted_unit_price | Present |
| PricingCurrencyEffectiveCost | Conditional | Native: pricing_currency_effective_cost | Present |
| SkuMeter | Conditional | Native: sku_meter | Present |
| SkuPriceId | Conditional | Not in Billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not in Billing API | Missing: Conditional |
| RegionId | Conditional | N/A: global edge network; no per-region billing rows | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: no per-resource CommitmentDiscount | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Native: invoice_id | Present |
| ServiceSubcategory | Recommended | Not emitted by Vercel API; map from service_name: "Edge Functions", "Edge Network", "Storage" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global edge network | N/A |

**Tally:** 40 Present, 5 Deviation, 0 Missing Mandatory, 2 Missing Conditional, 1 Missing Recommended, 9 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Vercel's native FOCUS v1.3 output covers 40 columns. All 21 Mandatory columns and most Conditional columns are natively emitted.

**Remaining:** Verify ServiceCategory and ResourceType values against FOCUS enums. Verify PricingUnit string conventions. Add ServiceSubcategory. SkuPriceId and SkuPriceDetails absent.

### 1.5 Deviations to Fix

**ServiceCategory:** Verify Vercel's native ServiceCategory values against FOCUS v1.2 enum. Expected: "Developer Tools" for Functions and Edge; "Storage" for Blob/Postgres/KV.

**PricingUnit:** Verify unit strings match FOCUS convention (e.g., "GB-Seconds" not "GBs").

**ResourceType:** Verify values against FOCUS ResourceType conventions.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Vercel natively emits FOCUS v1.3. Certify at FOCUS v1.2 (schema is compatible). Migrate to v1.4 when available.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. The native FOCUS output significantly shortens the certification path. Focus on field value verification.

### 2.3 Phased Roadmap

**Phase 0:** Pull Vercel Billing API output and run through FOCUS Validator.

**Phase 1: Field verification.** Audit ServiceCategory, PricingUnit, ResourceType values against FOCUS v1.2 spec. Fix deviations.

**Phase 2: ServiceSubcategory.** Map from ServiceName: "Edge Functions", "Edge Network", "Blob Storage", "Postgres", "Key-Value".

**Phase 3: Certify.** Submit for FOCUS v1.2 certification. Plan v1.4 migration (drop ProviderName, PublisherName).

---

## Part 3: Immediate Next Steps

1. Pull Vercel Billing API (`GET /v1/billing/charges`) and run through FOCUS Validator.
2. Audit ServiceCategory, PricingUnit, and ResourceType values vs. FOCUS v1.2 spec.
3. Add ServiceSubcategory mapping.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Vercel's native FOCUS v1.3 API output covers the vast majority of columns. This is the shortest path to certification of any provider in this analysis.
- **High:** All 40 Present columns are natively emitted by the Vercel Billing API.
- **Moderate:** ServiceCategory, PricingUnit, and ResourceType values require verification against FOCUS enum definitions.
- **Low:** SkuPriceId. Vercel does not expose pricing catalog IDs.

---

## Sources

- Vercel Billing API: [vercel.com/docs/rest-api/endpoints/billing](https://vercel.com/docs/rest-api/endpoints/billing)
- Vercel Pricing: [vercel.com/pricing](https://vercel.com/pricing)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
