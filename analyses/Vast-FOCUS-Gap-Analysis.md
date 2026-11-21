# VAST Data & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** VAST Data  
**Prepared:** June 25, 2026  
**Source:** VAST Cloud billing portal; VAST Data contract invoices  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 22 Present, 8 Deviation, 0 Missing Mandatory, 6 Missing Conditional, 1 Missing Recommended, 20 N/A

---

## Executive Summary

VAST Data offers two billing models: on-premises VAST systems (hardware + software subscription billed per effective TB) and VAST Cloud (managed all-flash storage-as-a-service billed by capacity provisioned). This analysis focuses on VAST Cloud, which maps more directly to a FOCUS data generator. VAST Cloud bills per TB per month of provisioned capacity; there is no per-file or per-request metering. All 21 Mandatory columns have source data. Twenty columns are N/A: no resource IDs at the file level, no sub-account hierarchy, no regional multi-row billing, and no CommitmentDiscount constructs. The 8 Deviations cover cost enrichment and enum derivation.

**Recommendation:** Map VAST Cloud billing to one FOCUS row per storage cluster × billing period. PricingUnit = "TB-Month". ChargeCategory = "Usage" for consumption-based tiers or "Purchase" for committed capacity. ServiceCategory = "Storage". Enterprise pricing requires supplementary contract data.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**VAST Cloud Billing Portal and Invoices**: VAST Cloud billing is managed through enterprise contracts and monthly invoices. Key fields: cluster name, provisioned TB, billing period, tier (hot, warm), contracted rate, total amount. On-premises VAST systems appear as software subscription invoices with effective TB capacity.

Key characteristics:
- **Capacity-based billing:** VAST Cloud charges per TB provisioned per month. No per-file, per-object, or per-request metering.
- **Storage tiers:** VAST offers hot (all-NVMe) and warm (QLC-based) storage tiers at different per-TB rates.
- **On-premises systems:** VAST physical systems (hardware appliances) carry a software subscription billed per effective TB after data reduction (deduplication + compression). Different billing model from cloud-hosted.
- **Enterprise pricing:** All VAST Data pricing is negotiated. No public per-TB list prices for enterprise agreements.
- **No sub-account hierarchy:** VAST Cloud billing is at the organization level. Volume or dataset allocation requires supplementary logic.
- **No resource IDs:** Storage capacity billing does not expose file, volume, or object IDs.
- **No regional billing rows:** VAST Cloud deployments may be in specific data centers, but billing does not generate per-region rows.
- **No CommitmentDiscount:** Committed capacity is billed as a flat subscription (PricingCategory = "Committed"), not a FOCUS CommitmentDiscount.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. VAST committed capacity = PricingCategory "Committed". CommitmentDiscount columns are N/A.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | VAST Data source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item total per cluster per billing period | Present |
| EffectiveCost | Mandatory | Annual: = BilledCost; multi-year: amortize across term | Deviation |
| ListCost | Mandatory | Published per-TB rate; not available for enterprise contracts | Deviation |
| ContractedCost | Mandatory | Contracted TB rate × provisioned TB; not in billing portal | Deviation |
| BillingAccountId | Mandatory | VAST Cloud account ID | Present |
| BillingAccountName | Mandatory | Customer organization name | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Start of provisioning period | Present |
| ChargePeriodEnd | Mandatory | End of provisioning period | Present |
| ChargeDescription | Mandatory | Cluster name + tier (e.g., "VAST Cloud Hot Tier · my-cluster · 500 TB") | Present |
| ChargeCategory | Mandatory | Derive: "Usage" for consumption-based; "Purchase" for committed capacity | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "VAST Data, Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "VAST Data" | Present |
| PublisherName | Mandatory (dep. v1.3) | "VAST Data" | Present |
| ServiceName | Mandatory | "VAST Cloud Hot Tier" or "VAST Cloud Warm Tier" or "VAST Data On-Premises" | Present |
| ServiceCategory | Mandatory | Derive: "Storage" for all VAST Data products | Deviation |
| PricingQuantity | Mandatory | Provisioned TB per billing period | Present |
| PricingUnit | Mandatory | "TB-Month" for all storage capacity billing | Deviation |
| ConsumedQuantity | Conditional | N/A: VAST bills by provisioned capacity, not consumed bytes | N/A |
| ConsumedUnit | Conditional | N/A | N/A |
| ListUnitPrice | Conditional | Not published for enterprise; requires supplementary data | Missing: Conditional |
| ContractedUnitPrice | Conditional | Contracted per-TB rate; not in billing portal | Missing: Conditional |
| PricingCategory | Conditional | "Committed" for contracted capacity; "Standard" for on-demand tiers | Deviation |
| ChargeFrequency | Conditional | "Recurring" for monthly capacity charges | Deviation |
| BillingAccountType | Conditional | "Enterprise" | Present |
| SubAccountId | Conditional | N/A: no sub-account billing hierarchy | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | N/A: capacity billing has no file or volume IDs | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | VAST storage tier code (e.g., "vast-cloud-hot", "vast-cloud-warm") | Present |
| Tags | Conditional | N/A: no resource-level tags in capacity billing | N/A |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | Missing: enterprise pricing not publicly available | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | Missing: enterprise pricing not in billing portal | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost; Deviation for multi-year amortization | Deviation |
| SkuMeter | Conditional | "Hot Tier TB-Month" or "Warm Tier TB-Month" | Missing: Conditional |
| SkuPriceId | Conditional | Not in billing portal | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable | Missing: Conditional |
| RegionId | Conditional | N/A: VAST Cloud deployments are single-site | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: committed capacity is a contract term, not FOCUS CommitmentDiscount | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from VAST billing portal | Present |
| ServiceSubcategory | Recommended | "All-Flash Storage", "Warm Tier Storage", "On-Premises Storage" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: single-site deployments | N/A |

**Tally:** 22 Present, 8 Deviation, 0 Missing Mandatory, 6 Missing Conditional, 1 Missing Recommended, 20 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Cluster names, storage tiers, provisioned TB, billing period, invoice number. All 21 Mandatory columns have source data.

**Remaining:** All pricing requires supplementary contract data. SkuMeter, SkuPriceId absent.

### 1.5 Deviations to Fix

**PricingUnit:** "TB-Month" for all capacity billing rows.

**ChargeCategory:** "Usage" for on-demand; "Purchase" for committed capacity contracts.

**ServiceCategory:** "Storage" for all VAST Data products.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document committed capacity contracts as PricingCategory = "Committed".

### 2.3 Phased Roadmap

**Phase 0:** Confirm billing portal invoice export access. Pull sample invoices for all active clusters and tiers.

**Phase 1: Cloud capacity transform.** Map hot and warm tier rows. Derive ChargeCategory, ServiceCategory, PricingUnit = "TB-Month".

**Phase 2: On-premises systems.** Add on-premises software subscription rows with effective-TB pricing.

**Phase 3: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Confirm VAST billing portal invoice export access.
2. Pull sample invoices for all active VAST Cloud clusters.
3. Implement Phase 1 capacity transform and run through FOCUS Validator.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** VAST Cloud invoices expose cluster name, provisioned TB, and tier. All 22 Present columns are grounded in billing fields.
- **High:** The 20 N/A columns correctly reflect capacity-based SaaS billing with no resource IDs.
- **Moderate:** ChargeCategory: "Usage" vs. "Purchase" depends on whether VAST Cloud is billed as on-demand or committed capacity. Confirm with VAST contract terms.
- **Low:** ListCost and ContractedCost. VAST Data does not publish enterprise list prices.

---

## Sources

- VAST Data Cloud: [vastdata.com/cloud](https://www.vastdata.com/cloud)
- VAST Data Documentation: [support.vastdata.com](https://support.vastdata.com)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
