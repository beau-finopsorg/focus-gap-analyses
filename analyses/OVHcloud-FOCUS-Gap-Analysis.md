# OVHcloud & FOCUS: Data Generator Gap Analysis

*Analysis run: June 30, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** OVHcloud  
**Prepared:** June 30, 2026  
**Source:** OVHcloud v1 API (`/me/bill`, `/me/bill/{billId}/details`, `/me/consumption/usage/*`, `/cloud/project/{serviceName}/usage/*`); OVHcloud Labs Finops FOCUS export; OVHcloud Control Panel  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 27 Present, 24 Deviation, 0 Missing Mandatory, 2 Missing Conditional, 1 Missing Recommended, 3 N/A

---

## Executive Summary

OVHcloud is a European cloud and hosting provider (Public Cloud, Bare Metal, Hosted Private Cloud, Web/domains) billing Public Cloud compute hourly and storage per GB-hour, with one consolidated invoice per project on the first of the following month. The data needed for FOCUS conformance is split across two surfaces: the monthly invoice (`billing.Bill` plus `billing.BillDetail` line items) carries billed amounts, invoice ID, and currency, while the hourly usage tree (`cloud.usage.*` and `me.consumption.Transaction`) carries region, plan codes, resource IDs, and per-hour quantities. All 21 Mandatory columns have a source once the two surfaces are joined. OVHcloud already publishes a FOCUS 1.0 export through OVHcloud Labs, which is a strong starting point but is best-effort, Public-Cloud-only, and one specification generation behind.

Three columns are N/A under OVHcloud's model: Public Cloud exposes no resource tags in usage or billing data, and there is no CapacityReservation construct (two columns). OVHcloud does sell Savings Plans (its commitment-discount mechanic), so the CommitmentDiscount family applies and is not N/A. The single most important substantive question is how Savings Plan discounts are represented in the line items: discounts are described as applied directly to the bill, so reconciling ListCost against BilledCost and EffectiveCost at the resource line, rather than treating them as equal, is the real work.

**Recommendation:** Build one FOCUS row per Public Cloud resource per charge period, joining `cloud.usage`/`me.consumption` (region, planCode, resource ID, hourly quantity) to `billing.Bill`/`BillDetail` (invoice ID, currency, billed amounts). ResourceId from instanceId/volumeId, SubAccountId from the Public Cloud project (serviceName), BillingAccountId from the NIC handle, RegionId from the OVHcloud region trigram, AvailabilityZone derived from the region string where a 3-AZ region applies.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

OVHcloud's billing and usage data lives in the OVH v1 REST API across two surfaces.

**Monthly invoice surface:**
- `GET /me/bill` returns bill IDs; `GET /me/bill/{billId}` returns a `billing.Bill` with `billId`, `date`, `orderId`, `pdfUrl`, and three Price objects (`priceWithTax`, `priceWithoutTax`, `tax`). Each Price carries `currencyCode`, `value`, and a display `text`.
- `GET /me/bill/{billId}/details/{billDetailId}` returns a `billing.BillDetail` with `description`, `domain`, `quantity` (typed as string), `unitPrice`, `totalPrice`, `periodStart`, and `periodEnd`. There is no planCode, region, serviceName, or tag at this layer: `domain` plus `description` are the only resource identifiers.

**Hourly usage surface:**
- `GET /cloud/project/{serviceName}/usage/current` and `/usage/history` return `cloud.usage` records with a `period` (`from`/`to`), `hourlyUsage`, and `monthlyUsage`. Hourly resources break into `instance[]`, `volume[]`, `storage[]`, `snapshot[]`, and bandwidth arrays. Each line carries `region`, a `Quantity` (`unit` of Hour, GiB, or GiBh, plus `value`), and `totalPrice`; leaf detail objects carry `instanceId` and `volumeId`.
- `GET /me/consumption/usage/current|forecast|history` returns `me.consumption.Transaction` records with `beginDate`, `endDate`, `serviceId`, a Price (`valueInUcents`, `currencyCode`), and elements carrying `planFamily`, `planCode`, and `quantity`.

Key characteristics:
- **Hourly compute:** Public Cloud instances billed per commenced hour from ACTIVE to deletion; usage updates every hour. Resource-level and hourly data are available through the usage and consumption endpoints.
- **Storage:** Object and block storage billed per GB-hour, with `region` and `totalPrice` per line.
- **Monthly invoice aggregation:** the formal `billing.Bill` is generated on the first of the following month, one per Public Cloud project, with `BillDetail` line items.
- **Projects as sub-accounts:** the NIC handle (nichandle) is the billing entity; Public Cloud projects (serviceName) provide isolation and dedicated billing. Project maps to SubAccountId, NIC to BillingAccountId.
- **Savings Plans:** OVHcloud's commitment-discount mechanic, a 1 to 36 month commitment on eligible instance families, billed monthly in advance, with discounts applied directly to the bill. Monthly-rate instances offer a further commitment-style reduction over hourly rate.
- **Currency:** prices carry an ISO `currencyCode` (EUR, USD, GBP, PLN, CAD, and others by subsidiary). Currency is bound to the account subsidiary, effectively one billing currency per account.
- **Regions and zones:** `region` is present on every Public Cloud usage line. OVHcloud offers 3-AZ regions, 1-AZ regions, and Local Zones; region codes are location trigrams (GRA, RBX, SBG, BHS).

### 1.2 How Conformance Is Judged

FOCUS conformance is judged column by column against the feature level each column carries. Feature levels for this analysis were verified against the FOCUS v1.2 specification Content Constraints tables, not recalled from memory. OVHcloud has no CapacityReservation construct, so both CapacityReservation columns are N/A. Public Cloud exposes no resource tags in billing or usage data, so Tags is N/A. OVHcloud does sell Savings Plans, so the seven CommitmentDiscount columns apply and are classified as deviations or gaps to build, not N/A.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

Feature levels verified against the FOCUS Specification v1.2.

| FOCUS Column | Level (v1.2) | OVHcloud source | Status |
|---|---|---|---|
| BilledCost | Mandatory | BillDetail totalPrice (net of Savings Plan discount applied to the bill) | Present |
| EffectiveCost | Mandatory | Derive: amortize Savings Plan prepay across covered hours; else = BilledCost | Deviation |
| ListCost | Mandatory | Derive: public hourly/GB-hour rate × quantity, pre-discount | Deviation |
| ContractedCost | Mandatory | Derive: = BilledCost for on-demand; reflect committed rate under Savings Plan | Deviation |
| BillingAccountId | Mandatory | NIC handle (nichandle) | Present |
| BillingAccountName | Mandatory | Account holder name | Present |
| BillingCurrency | Mandatory | Price.currencyCode (EUR, USD, GBP, PLN, CAD) | Present |
| BillingPeriodStart | Mandatory | First day of the invoiced month | Present |
| BillingPeriodEnd | Mandatory | First day of the following month (exclusive) | Present |
| ChargePeriodStart | Mandatory | Usage period from (hourly) or BillDetail periodStart | Present |
| ChargePeriodEnd | Mandatory | Usage period to (hourly) or BillDetail periodEnd | Present |
| ChargeDescription | Mandatory | BillDetail description; enrich with planCode for usage lines | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for metered lines; "Purchase" for Savings Plan prepay; "Tax" for tax | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | OVHcloud billing entity (e.g., "OVH SAS") | Present |
| ProviderName | Mandatory (dep. v1.3) | "OVHcloud" | Present |
| PublisherName | Mandatory (dep. v1.3) | "OVHcloud" | Present |
| ServiceName | Mandatory | Derive from planFamily/planCode (e.g., "Public Cloud Compute", "Object Storage") | Deviation |
| ServiceCategory | Mandatory | Derive: "Compute" for instances; "Storage" for volume/object; "Networking" for bandwidth | Deviation |
| PricingQuantity | Mandatory | Usage Quantity.value (Hour, GiB, GiBh) | Present |
| PricingUnit | Mandatory | Normalize Quantity.unit to FOCUS unit string ("Hours", "GiB", "GiB-Hours") | Deviation |
| ConsumedQuantity | Conditional | = usage Quantity.value | Present |
| ConsumedUnit | Conditional | = normalized Quantity.unit | Deviation |
| ListUnitPrice | Conditional | Public per-unit rate from OVHcloud pricing | Present |
| ContractedUnitPrice | Conditional | = ListUnitPrice on-demand; committed rate under Savings Plan | Deviation |
| PricingCategory | Conditional | Derive: "Standard" on-demand; "Committed" under Savings Plan | Deviation |
| ChargeFrequency | Recommended | Derive: "Usage-Based" hourly; "Recurring" for monthly-rate and Savings Plan | Deviation |
| BillingAccountType | Conditional | Derive: "Billing Account" | Present |
| SubAccountId | Conditional | Public Cloud project ID (serviceName) | Present |
| SubAccountName | Conditional | Project description/name | Present |
| SubAccountType | Conditional | Derive: "Public Cloud Project" | Present |
| ResourceId | Conditional | instanceId / volumeId from usage detail leaves | Present |
| ResourceName | Conditional | Instance/volume name where set; else reference | Deviation |
| ResourceType | Conditional | Derive from planCode/usage array (e.g., "Instance b3-8", "Block Storage") | Deviation |
| SkuId | Conditional | planCode | Present |
| Tags | Conditional | N/A: Public Cloud exposes no resource tags in usage or billing data | N/A |
| PricingCurrency | Conditional | = Price.currencyCode | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice in pricing currency | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice in pricing currency | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost in pricing currency | Deviation |
| SkuMeter | Conditional | planFamily + Quantity.unit (e.g., "Instance b3-8 Hours") | Present |
| SkuPriceId | Conditional | Not in usage or billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not in usage or billing API | Missing: Conditional |
| RegionId | Conditional | OVHcloud region trigram (GRA, RBX, SBG, BHS) | Present |
| RegionName | Conditional | Region display name (e.g., "Gravelines, France") | Present |
| CommitmentDiscountId | Conditional | Savings Plan identifier (from Savings Plan API) | Deviation |
| CommitmentDiscountName | Conditional | Savings Plan name | Deviation |
| CommitmentDiscountType | Conditional | Derive: "Spend" or "Usage" commitment | Deviation |
| CommitmentDiscountCategory | Conditional | Derive: "Committed Use" | Deviation |
| CommitmentDiscountStatus | Conditional | Derive: "Used" / "Unused" against covered hours | Deviation |
| CommitmentDiscountQuantity | Conditional | Committed quantity (instances/months) | Deviation |
| CommitmentDiscountUnit | Conditional | Commitment unit (e.g., "Instance-Months") | Deviation |
| CapacityReservationId | Conditional | N/A: no capacity reservation construct | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | billId | Present |
| ServiceSubcategory | Recommended | Map from planFamily (e.g., "Virtual Machines", "Object Storage") | Missing: Recommended |
| AvailabilityZone | Recommended | Derive from region string where a 3-AZ region applies; else null | Deviation |

**Tally:** 27 Present, 24 Deviation, 0 Missing Mandatory, 2 Missing Conditional, 1 Missing Recommended, 3 N/A. The 3 N/A are Tags plus the two CapacityReservation columns. The CommitmentDiscount family is not N/A because OVHcloud sells Savings Plans; those seven columns are classified as deviations to build from the Savings Plan API.

### 1.4 What Is Solved, and What Remains

**Solved:** All 21 Mandatory columns have a source once the hourly usage surface and the monthly invoice surface are joined. Resource IDs, regions, plan codes, projects, hourly quantities, invoice IDs, and currency are all natively available. The OVHcloud Labs FOCUS export already demonstrates a working transform for Public Cloud.

**Substantive gaps (real data work, not plumbing):**
- **Cost reconciliation under Savings Plans.** ListCost, EffectiveCost, and ContractedCost are not a trivial copy of the billed amount. Savings Plan discounts are applied directly to the bill and Savings Plans are billed monthly in advance, so producing EffectiveCost requires amortizing prepaid commitment across covered hours and ListCost requires reconstructing the pre-discount public rate. For pure on-demand usage with no commitment, the four cost columns collapse to the billed amount and the work is trivial; under a Savings Plan they do not.
- **Joining two surfaces.** The invoice line items carry billed amounts but no planCode, region, or resource ID; the usage tree carries those but its prices are usage estimates. A conformant per-resource row requires joining them, which is real engineering rather than a field rename.

**Trivial gaps (derivable from data present):** PricingQuantity and PricingUnit from the usage Quantity for flat-rate hourly and GB-hour SKUs; ChargeCategory, ServiceCategory, ServiceName, and ResourceType from planFamily/planCode; SubAccountType and BillingAccountType as constants.

**Remaining Conditional/Recommended:** SkuPriceId and SkuPriceDetails are absent from both surfaces. ServiceSubcategory is not emitted and would be mapped from planFamily.

### 1.5 Deviations to Fix

**Tags:** Public Cloud has no tag exposure in usage or billing data. This is the largest single attribution gap. Until OVHcloud ships resource tagging, allocation depends on project (SubAccountId) and resource ID, and Tags stays null.

**Cost columns:** populate ListCost from public rates, EffectiveCost from amortized Savings Plan economics, and ContractedCost from the committed rate. Do not set all three equal to BilledCost when a Savings Plan is in force.

**PricingUnit / ConsumedUnit:** normalize OVHcloud Quantity units (Hour, GiB, GiBh) to FOCUS unit strings ("Hours", "GiB", "GiB-Hours").

**ChargeCategory:** "Usage" for metered lines, "Purchase" for Savings Plan prepay, "Tax" for the tax line, "Credit" for credits and vouchers.

**ServiceCategory:** "Compute" for instances, "Storage" for block and object storage, "Networking" for bandwidth.

**CommitmentDiscount family:** populate from the Savings Plan API and join to covered usage lines. Confirm against a real Savings Plan invoice whether the discount appears as a discrete line item or as an adjusted price.

**AvailabilityZone:** derive from the region string where a 3-AZ region applies; leave null for 1-AZ regions and Local Zones.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2, the current certification baseline. OVHcloud's existing Labs export targets FOCUS 1.0 and should be advanced two minor versions, dropping ProviderName and PublisherName for v1.4.

### 2.2 What Certification Requires

The program is "FinOps Certified FOCUS v1.2 Conformant"; contact `member-cert@finops.org` for the RFI. Membership is required for certification, though contributing to the specification is open and free. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Document Tags and CapacityReservation as not applicable to the Public Cloud model, and document the Savings Plan mapping for the CommitmentDiscount family. Validate with the FOCUS Validator and convert with the FOCUS Converter against the FOCUS Requirements Model.

### 2.3 Phased Roadmap

**Phase 0:** Validate the existing OVHcloud Labs FOCUS 1.0 export against the FOCUS Validator. Confirm scope (Public Cloud first) and pull one month of `cloud.usage`/`me.consumption` plus the matching `billing.Bill`/`BillDetail`.

**Phase 1: Join and Mandatory close.** Join the hourly usage surface to the monthly invoice. Populate the four cost columns including Savings Plan reconciliation, the trivial Mandatory derivations (PricingQuantity, PricingUnit, ChargeCategory, ServiceCategory, ServiceName), and core identity (ResourceId, SubAccountId, BillingAccountId, RegionId).

**Phase 2: Deviations.** Normalize units, enums, currency-pair columns, and ChargeFrequency. Derive AvailabilityZone for 3-AZ regions.

**Phase 3: Conditional and Recommended.** Populate the CommitmentDiscount family from the Savings Plan API; add ServiceSubcategory. Document SkuPriceId/SkuPriceDetails as not exposed.

**Phase 4: Mature and certify.** Advance from v1.0 to v1.2 for certification and v1.4 for build target. Drop ProviderName and PublisherName. Extend coverage beyond Public Cloud (Bare Metal, Hosted Private Cloud). Validate and certify.

### 2.4 FOCUS Use Cases Unlocked

- **As soon as Phase 1 lands (resource, project, region, day):** cost reporting by project and region, resource-level cost visibility, and chargeback by project.
- **After Phase 2/3 (cost reconciliation, commitment data):** Savings Plan coverage and utilization analysis, effective-cost trending, and actuals-based budgeting.
- **Out of scope for this model:** tag-based allocation (no Public Cloud tags) and capacity reservation analysis (no reservation construct).

---

## Part 3: Immediate Next Steps

1. Run the existing OVHcloud Labs FOCUS 1.0 export through the FOCUS Validator to baseline conformance.
2. Pull one month of `cloud.usage`/`me.consumption` and the matching `billing.Bill`/`BillDetail` for a project that uses a Savings Plan.
3. Confirm at the line level how Savings Plan discounts appear, then implement the Phase 1 join and cost reconciliation.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** OVHcloud exposes hourly, resource-level usage (region, planCode, instanceId, quantity) and monthly invoice line items (billId, currency, billed amounts). All 21 Mandatory columns have a source. Source field names are grounded in the OVH v1 API schema.
- **High:** Public Cloud project maps to SubAccountId and NIC handle to BillingAccountId. Region is native; the existing OVHcloud Labs FOCUS 1.0 export confirms a working Public Cloud transform.
- **Moderate:** EffectiveCost, ListCost, and ContractedCost under Savings Plans require reconciliation; the precise line-level representation of the discount (discrete line item versus adjusted price) should be confirmed against a real Savings Plan invoice.
- **Moderate:** AvailabilityZone derivation depends on whether the usage `region` string carries the AZ suffix; the schema shows a flat region string, so derivation may be required.
- **Low:** Currency immutability per account is inferred from the subsidiary binding rather than an explicit statement. Coverage beyond Public Cloud (Bare Metal, Hosted Private Cloud, Web) was not field-confirmed and is treated as provisional.

This analysis reflects the data sources reviewed, not a formal certification result. OVHcloud does not hold the FinOps Certified FOCUS designation; the readiness band below is an assessment of the reviewed data, not a certification.

---

## Sources

- OVHcloud v1 API schema (`/me`, `/cloud`): [api.ovh.com/console](https://api.ovh.com/console/)
- OVHcloud Public Cloud billing guide: [help.ovhcloud.com](https://help.ovhcloud.com/csm/en-public-cloud-compute-billing)
- OVHcloud Savings Plan: [us.ovhcloud.com/public-cloud/savings-plan](https://us.ovhcloud.com/public-cloud/savings-plan/)
- OVHcloud Labs Finops FOCUS export: [labs.ovhcloud.com/en/finops-focus](https://labs.ovhcloud.com/en/finops-focus/)
- OVHcloud multi-AZ regions: [ovhcloud.com/en/about-us/global-infrastructure/multi-az](https://www.ovhcloud.com/en/about-us/global-infrastructure/multi-az/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS Specification v1.4: [finops.org/insights/introducing-focus-1-4](https://www.finops.org/insights/introducing-focus-1-4/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
