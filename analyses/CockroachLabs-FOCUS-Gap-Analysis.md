# Cockroach Labs & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Cockroach Labs, Inc.  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Public Cockroach Labs documentation only: CockroachDB Cloud API billing endpoints (`GET /api/v1/invoices`, `GET /api/v1/invoices/{invoice_id}`, OpenAPI spec versions 2023-04-10 through 2026-09-15); Billing Management, Understand Costs, Folders, Labels, and Request Unit metrics docs; `ccloud` CLI reference; Cockroach Continuum pricing page and Editions and Add-ons docs; Cloud Terms and Conditions  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 20 Present, 17 Deviation, 2 Missing Mandatory, 13 Missing Conditional, 1 Missing Recommended, 4 N/A

> **Public billing docs: richer than most, with specific holes.** Cockroach Labs publishes a typed, versioned invoice API with per-cluster line items, quantity units, unit costs, adjustments, folders, and labels, which is more than most database vendors offer. The holes matter for FOCUS: the Console CSV exports (the only source of daily rows and per-locality charges) have no published column list; public list prices cover only AWS us-east-1 compute, with storage, data transfer, other regions, and BYOC unpublished; and the billing docs still describe the legacy Basic/Standard/Advanced plans two months after the September 15, 2026 Continuum pricing change. Statuses that rest on the CSV are provisional until Cockroach Labs shares a sample export.

---

## Executive Summary

Cockroach Labs sells CockroachDB, a distributed SQL database, as CockroachDB Cloud on AWS, Google Cloud, and Azure, and as self-hosted Enterprise licenses. On September 15, 2026, new Cloud organizations moved to Cockroach Continuum pricing: two editions (Standard and Mission Critical) billed per vCPU-hour, metered by the minute, plus usage-based storage, data transfer, and add-ons (Data Sync, Data Replication, Cluster Virtualization, Advanced Compliance) that appear as separate line items. Existing organizations stay on the legacy Basic (Request Units), Standard (provisioned vCPU-hours), and Advanced (per-node-hour) plans unless they opt in. Annual and committed-use contracts are paid as prepaid CockroachDB Cloud Credits with volume discounts, drawn down at the end of each billing period.

The invoice API is a strong base. Every line item sits under a full cluster object (ID, name, plan or edition, cloud provider, regions, folder, labels), and the invoice carries an ID, a status (`DRAFT` or `FINALIZED`), and inclusive-start, exclusive-end period bounds that already match FOCUS semantics. Of the 21 Mandatory columns, 19 have a source and 2 are missing. One gap is substantive: **EffectiveCost**, because prepaid credits, contract volume discounts, free monthly usage, trial credit, and invoice-level adjustments all exist, and adjustments are "not tied to a particular cluster." **ListCost** is a rate-card join.

The deepest structural issue is currency. Contract organizations see totals denominated in `CRDB_CLOUD_CREDITS` or `COCKROACH_CREDITS`, which the API lists as currencies beside `USD`. FOCUS requires an ISO 4217 BillingCurrency, but since v1.2 it models virtual currencies through the PricingCurrency columns. Cockroach Labs' credits are a textbook fit for that design, and remodeling them is most of the work.

**Recommendation:** Publish a FOCUS export per organization through a new Cloud API endpoint (and `ccloud billing`), built from the same data as the Daily CSV: one Usage row per cluster × line item × locality × day, with BillingCurrency in USD, credits in PricingCurrency, adjustments as Credit or Purchase rows, and the credit purchase as a commitment. Carry the cluster ID into ResourceId, the folder into SubAccountId, cluster labels into Tags, and locality into RegionId.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

- **Cloud API invoices** (`https://cockroachlabs.cloud/api/v1/invoices`, roles `BILLING_COORDINATOR` or `CLUSTER_ADMIN`; not marked preview): list filterable by `status`, `start_time`, and `end_time`, plus a single-invoice endpoint. Fields:
  - Invoice: `invoice_id`, `status` (`FINALIZED` | `DRAFT`), `period_start` (inclusive), `period_end` (exclusive), `totals[]` and `balances[]` as per-currency amounts.
  - `invoice_items[]` sorted by cluster name: the full `cluster` object and per-cluster `totals[]`.
  - `line_items[]` ("from the Metronome invoice"): `description` (e.g., "t3 micro"), `quantity`, `quantity_unit` (`HOURS` | `REQUEST_UNITS` | `GIB` | `GIB_HOURS` | `VCPU_HOURS`), `unit_cost`, `total`.
  - `adjustments[]`: `name` and `amount`, for "credits or costs that adjust the value of the invoice (e.g. a Serverless Free Credit or Premium Support adjustment)." Not tied to a cluster.
  - `folder_resources[]` (Preview): `resource_id`, `resource_type` (`FOLDER` | `CLUSTER`), `parent_id`, `organization_id`, `name`, `path[]`, `labels`.
  - Currency enum: `USD`, `CRDB_CLOUD_CREDITS`, `COCKROACH_CREDITS` (Continuum organizations get the latter). Amounts are tracked as arbitrary-precision decimals but serialized as 64-bit floats.
- **Cluster object** (embedded per invoice item): `id`, `name`, `cloud_provider` (`GCP` | `AWS` | `AZURE`), `regions[]` (`name`, `node_count`, `primary`, `machine_type`, `num_virtual_cpus`), `plan` (`BASIC` | `STANDARD` | `ADVANCED`) or `edition` (`STANDARD` | `MISSION_CRITICAL`), `labels`, `parent_id` (Preview), `config`.
- **Console Billing page** (Billing Coordinator or Billing Viewer):
  - **Export Monthly CSV:** one row per line item for all clusters. Adjustments are "appended as additional rows at the end of the file, with no cluster-specific details." Adds "Cluster path" when folders are used.
  - **Export Daily CSV:** the same rows broken down by day, adding "Usage date" and "Locality (for multi-region charge breakdowns)." Only for invoices posted in 2026 or later.
  - **Export Invoice PDF.** No published CSV column list or sample.
- **`ccloud billing invoice list|get`** wraps the API. The Terraform provider has no billing data source.

Key characteristics:

- **Plans and meters:** Legacy Basic bills Request Units ($0.20 per million) and storage ($0.50 per GiB-month) with $15 of free monthly usage. Legacy Standard bills provisioned vCPU-hours at the most expensive region's rate, plus storage GiB-hours. Legacy Advanced bills per node-hour by vCPU, cloud, and region, plus provisioned storage and AWS IOPS. Data transfer (same-region, cross-region, public internet), managed backups (tiered by GiB-month), and changefeeds (tiered) are separate.
- **Continuum:** Standard from $0.057 per vCPU-hour ($0.092 in AWS us-east-1); Mission Critical $0.162 in AWS us-east-1. Add-ons are priced as vCPU-hour multipliers (Data Sync $0.006 on Standard, $0.023 on Mission Critical). A 30-day trial carries $400 of credit.
- **Credits and contracts:** Annual and committed-use contracts buy CockroachDB Cloud Credits with undisclosed volume discounts. "At the end of each billing period, invoice payments are deducted from your organization's Credits."
- **Hierarchy:** Organization → folders (up to four levels, 65 per organization) → clusters. "Clusters are billed to their residing folder at billing period end."
- **Labels:** Key/value, up to 50 per cluster or folder, lowercase keys and values. Present in the invoice cluster object.
- **Marketplaces:** AWS and Google Cloud Marketplace subscriptions are documented in billing docs; the pricing page also lists Azure Marketplace.
- **Out of scope:** Self-hosted Enterprise licenses. They carry no published usage or invoice data.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. CockroachDB Cloud deploys clusters in cloud regions, groups them into folders, supports key/value labels, sells through marketplaces as well as directly, and prices contracts in a virtual currency (credits) bought at a discount. RegionId, RegionName, SubAccountId, SubAccountName, Tags, BillingAccountType, the PricingCurrency family, and the CommitmentDiscount family therefore apply. Cockroach Labs sells no capacity reservations, folders are the only sub-account type, and zones are not billed separately, so CapacityReservationId, CapacityReservationStatus, SubAccountType, and AvailabilityZone are N/A and should exist as null. Feature levels follow the FOCUS v1.2 Content Constraints, spot-checked against the live spec on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Cockroach Labs source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Line item `total`; denominated in credits for contract organizations, adjustments unallocated, float serialization | Deviation |
| EffectiveCost | Mandatory | Not available: needs USD value of credits drawn, contract discount, and allocation of free usage, trial credit, and adjustments to clusters | Missing: Mandatory |
| ListCost | Mandatory | Not exposed; `unit_cost` may be the contract rate; join list rate card × PricingQuantity | Missing: Mandatory |
| ContractedCost | Mandatory | Line item `total` (`unit_cost` × `quantity`); needs USD conversion for credit organizations | Deviation |
| BillingAccountId | Mandatory | Organization ID (API is organization-scoped; `organization_id` in `folder_resources`) | Present |
| BillingAccountName | Mandatory | Organization name | Present |
| BillingCurrency | Mandatory | `currency` on `totals`; `CRDB_CLOUD_CREDITS` and `COCKROACH_CREDITS` are not ISO 4217 | Deviation |
| BillingPeriodStart | Mandatory | `period_start` (inclusive) | Present |
| BillingPeriodEnd | Mandatory | `period_end` (exclusive) | Present |
| ChargePeriodStart | Mandatory | Daily CSV "Usage date"; API offers only the invoice period | Present |
| ChargePeriodEnd | Mandatory | Usage date + 1 day | Present |
| ChargeDescription | Mandatory | Line item `description`; adjustment `name` | Present |
| ChargeCategory | Mandatory | Derive: "Usage" for line items; "Credit" for free-usage and trial adjustments; "Purchase" for Premium Support and credit purchases | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued charges | Present |
| InvoiceIssuerName | Mandatory | "Cockroach Labs, Inc." for direct; "Amazon Web Services", "Google", or "Microsoft" for marketplace | Present |
| ProviderName | Mandatory (dep. v1.3) | "Cockroach Labs" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Cockroach Labs" | Present |
| ServiceName | Mandatory | Cluster `plan` or `edition` (e.g., "CockroachDB Cloud Standard", "CockroachDB Cloud Mission Critical") | Present |
| ServiceCategory | Mandatory | Derive: "Databases" for clusters, storage, backups, and add-ons; "Networking" for data transfer | Deviation |
| PricingQuantity | Mandatory | `quantity`; backups and changefeeds are tiered and Basic has a free allowance, so compute against the rate basis | Deviation |
| PricingUnit | Mandatory | Normalize `quantity_unit`: "Hours", "1M Request Units", "GiB", "GiB-Hours", "vCPU-Hours" | Deviation |
| ConsumedQuantity | Conditional | `quantity` | Present |
| ConsumedUnit | Conditional | `quantity_unit` enum; normalize to FOCUS unit format | Deviation |
| ListUnitPrice | Conditional | `unit_cost` on pay-as-you-go; contract organizations need the list rate card | Deviation |
| ContractedUnitPrice | Conditional | `unit_cost`; in credits for contract organizations | Deviation |
| PricingCategory | Conditional | Derive: "Standard" for pay-as-you-go; "Committed" for credit-funded usage | Deviation |
| BillingAccountType | Conditional | Not exposed; direct vs. AWS, Google Cloud, or Azure Marketplace organization | Missing: Conditional |
| SubAccountId | Conditional | Cluster `parent_id` (Preview) and `folder_resources[].resource_id` | Present |
| SubAccountName | Conditional | `folder_resources[].name`; `path[]` gives the full folder path | Present |
| SubAccountType | Conditional | N/A: folder is the only sub-account type | N/A |
| ResourceId | Conditional | Cluster `id` | Present |
| ResourceName | Conditional | Cluster `name` | Present |
| ResourceType | Conditional | Cluster `config` and `plan`/`edition` (e.g., "Serverless Cluster", "Dedicated Cluster") | Present |
| SkuId | Conditional | Not exposed; meaning sits in free-text `description` | Missing: Conditional |
| Tags | Conditional | Cluster `labels` (key/value map, up to 50); folder labels in `folder_resources` | Present |
| PricingCurrency | Conditional | Credits currency exists but is reported as the billing currency; remodel as "CockroachDB Cloud Credits" | Deviation |
| PricingCurrencyListUnitPrice | Conditional | Not exposed | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | `unit_cost` in credits for contract organizations | Deviation |
| PricingCurrencyEffectiveCost | Conditional | Not available; credits drawn after allocation of adjustments | Missing: Conditional |
| SkuMeter | Conditional | Derive from `quantity_unit` and `description` (e.g., "Compute", "Storage", "Request Units", "Data Transfer") | Deviation |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed for region, backup and changefeed tiers, free allowance, and add-on multipliers | Missing: Conditional |
| RegionId | Conditional | Daily CSV "Locality"; API has cluster `regions[].name` but no per-line region | Deviation |
| RegionName | Conditional | Map from cloud-native region code | Deviation |
| CommitmentDiscountId | Conditional | Contract or credit grant ID; not exposed | Missing: Conditional |
| CommitmentDiscountName | Conditional | Not exposed | Missing: Conditional |
| CommitmentDiscountType | Conditional | Not exposed (e.g., "Annual Credit Commitment") | Missing: Conditional |
| CommitmentDiscountCategory | Conditional | "Spend"; not exposed | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | "Used"/"Unused" against the credit balance | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | Credits drawn; `balances[]` gives the remaining balance only | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | "Credits" | Missing: Conditional |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | `invoice_id` | Present |
| ChargeFrequency | Recommended | Derive: "Usage-Based" for metered lines; "Recurring" for support and contract fees | Deviation |
| ServiceSubcategory | Recommended | Not exposed; map to "Relational Databases" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: clusters span zones within a region; zones are not billed | N/A |

**Tally:** 20 Present, 17 Deviation, 2 Missing Mandatory, 13 Missing Conditional, 1 Missing Recommended, 4 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Organization identity, FOCUS-shaped billing period bounds, invoice IDs and status, per-cluster line items with quantity and unit cost, cluster ID, name, and type, folder hierarchy, and key/value labels inside billing data. Allocation, usually the weakest area for a database vendor, is the strongest here.

**Substantive (1 of 2 Mandatory gaps):**

- **EffectiveCost.** Discounts and credits exist in four forms: prepaid credits bought at a volume discount, free monthly usage on Basic, trial credit, and invoice-level adjustments with "no cluster-specific details." Producing EffectiveCost means pricing each line in USD at the contract's effective credit rate and allocating free-usage and support adjustments back to clusters. On a pay-as-you-go organization with no adjustments, EffectiveCost equals the line total; on contract organizations it does not.

**Trivial (1 of 2 Mandatory gaps):**

- **ListCost.** Cockroach Labs holds the full list rate card; expose it per line. Public prices are not enough to reconstruct it, since only AWS us-east-1 compute is published.

**Substantive, beyond the column table:**

- **Credits as a currency.** The API reports credits as a peer of USD. FOCUS keeps BillingCurrency in ISO 4217 and expresses virtual currencies through PricingCurrency, PricingCurrencyContractedUnitPrice, and PricingCurrencyEffectiveCost. Cockroach Labs needs the USD value of a credit per contract to fill BilledCost and EffectiveCost.
- **Daily and regional data are Console-only.** The API stops at the monthly invoice. Day-level rows and per-locality splits for multi-region clusters exist only in a manually downloaded CSV, and only for invoices from 2026 onward.
- **No SKU or meter identity.** Line meaning lives in free-text `description`, so any mapping to SkuId, SkuMeter, ServiceCategory, or ChargeCategory is string parsing until Cockroach Labs exposes a meter or product code. Metronome, the billing engine behind the line items, already holds these codes.
- **Two pricing models at once.** Legacy and Continuum organizations differ in plans, units, and credit currency names. A FOCUS export has to cover both.

### 1.5 Deviations to Fix

**BilledCost and BillingCurrency:** Report BillingCurrency as "USD." For pay-as-you-go, BilledCost is the line total. For credit-funded usage, emit BilledCost of 0 on usage rows and a Purchase row for the credit purchase, and move the credit amount to the PricingCurrency columns. Serialize amounts as decimals, not 64-bit floats.

**ContractedCost and ContractedUnitPrice:** Convert `unit_cost` and `total` from credits to USD at the contract rate.

**ChargeCategory:** "Usage" for line items; "Credit" for Serverless Free Credit and trial adjustments; "Purchase" for Premium Support and credit purchases; "Tax" if tax is ever invoiced.

**ServiceCategory:** "Databases" for compute, storage, backups, and add-ons; "Networking" for data transfer lines.

**PricingQuantity and PricingUnit:** Compute and storage are flat per region, so PricingQuantity equals consumption there. Managed backups and changefeeds are tiered by GiB-month, and Basic has a free allowance; compute PricingQuantity against the rate basis and express tiers in SkuPriceDetails. Normalize `REQUEST_UNITS` to "1M Request Units" to match the price basis, and `GIB_HOURS` and `VCPU_HOURS` to "GiB-Hours" and "vCPU-Hours."

**RegionId and RegionName:** Carry the Daily CSV "Locality" into the API line item and map cloud-native codes to names.

**ConsumedUnit, PricingCategory, SkuMeter, ChargeFrequency:** Derive as shown in the table.

**Already right:** Inclusive-start, exclusive-end periods, a stable invoice ID with draft/final status, cluster identity on every line, and key/value labels match FOCUS without transformation.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is a candidate release scheduled for ratification on December 3, 2026; its scope is on the FOCUS site. The v1.3 Contract Commitment dataset fits prepaid credit contracts better than per-row CommitmentDiscount columns alone, and the v1.4 Invoice Detail dataset maps to the existing invoice object and its `DRAFT`/`FINALIZED` status.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (no capacity reservations, one sub-account type, zones not billed) and the decisions on modeling credits as a pricing currency and contracts as spend-based commitment discounts. Certification would cover CockroachDB Cloud, not self-hosted licenses.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one month's Daily CSV and API invoice for a pay-as-you-go organization and a credit-contract organization, on both legacy and Continuum pricing. Hand-build a v1.2 file and run it through the Validator. Decide the credit and commitment model.

**Phase 1: Close Mandatory gaps.** Expose list rates for ListCost. Value credits in USD and allocate adjustments to clusters for EffectiveCost. Move credits to PricingCurrency and emit USD BilledCost with Purchase and Credit rows so it reconciles to the invoice.

**Phase 2: Fix deviations and add a feed.** Derive ChargeCategory, ServiceCategory, ChargeFrequency, and PricingCategory; normalize units; compute PricingQuantity against backup and changefeed tiers. Add usage date and locality to the API line item, or ship a FOCUS export endpoint, so daily data no longer requires a Console download.

**Phase 3: Conditional columns.** Expose Metronome product codes as SkuId, SkuPriceId, and SkuMeter, with tiers and region in SkuPriceDetails. Add BillingAccountType for marketplace organizations, the CommitmentDiscount family, and ServiceSubcategory. Snapshot labels at billing time and promote `parent_id` out of preview.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Invoice Detail and Contract Commitment datasets; certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **Available now (from API and CSV with transformation):** Showback and chargeback by cluster, folder, and label; spend by plan or edition; month-over-month cost trends.
- **After Phase 1:** Invoice reconciliation, actuals-based budgeting, and amortized spend reporting for contract organizations.
- **After Phase 2:** Daily anomaly detection, per-region cost for multi-region clusters, and automated ingestion into FinOps tools without Console downloads.
- **After Phase 3:** Unit economics per vCPU-hour or per million Request Units across editions, credit burn-down tracking, and marketplace-versus-direct comparison.
- **Out of scope:** Capacity reservation management and availability-zone analysis.

---

## Part 3: Immediate Next Steps

1. Follow up with the Cockroach Labs contact from KubeCon NA 2026 to reach the owner of CockroachDB Cloud billing and the Metronome integration.
2. Request a sample Daily CSV and confirm its columns, and confirm whether `unit_cost` is the list or contracted rate for credit organizations.
3. Confirm the USD value of a credit per contract, whether invoice labels are snapshots or current values, and how marketplace-billed usage appears in the API.
4. Build a v1.2 sample from one billing month and run it through the FOCUS Validator.
5. Open the RFI with `member-cert@finops.org` and discuss FinOps Foundation membership.

---

## Confidence Summary

- **High:** Invoice API endpoints, fields, enums, and roles come from the published OpenAPI reference (2026-09-15 version).
- **High:** Monthly and Daily CSV exports exist; the Daily CSV adds "Usage date" and "Locality" and covers 2026-onward invoices only; adjustments carry no cluster details.
- **High:** Continuum pricing (editions, per-vCPU-hour rates for AWS us-east-1, per-minute metering, $400 trial credit, September 15, 2026 effective date) comes from the pricing page.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints; spot-checked against the live spec on November 17, 2026, and v1.4 remains the latest ratified version.
- **Moderate:** Present status for ChargePeriodStart and ChargePeriodEnd rests on the Daily CSV, whose columns are not published.
- **Moderate:** Tags as Present. Labels are in the invoice cluster object, but the docs do not say whether they are snapshots at billing time or current values.
- **Moderate:** Modeling credits as a PricingCurrency and contracts as spend-based commitment discounts. If credits always equal $1, PricingCurrency becomes simpler but the commitment model still applies.
- **Moderate:** ServiceSubcategory "Relational Databases" for distributed SQL; confirm against the v1.2 allowed-value table.
- **Low:** Whether `unit_cost` reflects list or contracted rates for credit organizations. Not documented.
- **Low:** InvoiceIssuerName for marketplace and non-US customers. The Cloud Terms name Cockroach Labs, Inc.; no public invoice sample confirms the issuer on all paths.
- **Low:** Prices outside AWS us-east-1 compute, including storage, data transfer, and BYOC. Not published.

---

## Sources

- Cloud API, List Invoices: [docs.cockroachlabs.com/docs/api/cloud/v1/billing/list-invoices-for-a-given-organization](https://docs.cockroachlabs.com/docs/api/cloud/v1/billing/list-invoices-for-a-given-organization.md)
- Cloud API, Get Invoice: [docs.cockroachlabs.com/docs/api/cloud/v1/billing/get-a-specific-invoice-for-an-organization](https://docs.cockroachlabs.com/docs/api/cloud/v1/billing/get-a-specific-invoice-for-an-organization.md)
- Billing Management: [docs.cockroachlabs.com/docs/cockroachcloud/billing-management](https://docs.cockroachlabs.com/docs/cockroachcloud/billing-management.md)
- Understand CockroachDB Cloud Costs: [docs.cockroachlabs.com/docs/cockroachcloud/costs](https://docs.cockroachlabs.com/docs/cockroachcloud/costs.md)
- Plan a Basic Cluster: [docs.cockroachlabs.com/docs/cockroachcloud/plan-your-cluster-basic](https://docs.cockroachlabs.com/docs/cockroachcloud/plan-your-cluster-basic.md)
- Folders: [docs.cockroachlabs.com/docs/cockroachcloud/folders](https://docs.cockroachlabs.com/docs/cockroachcloud/folders.md)
- Labels: [docs.cockroachlabs.com/docs/cockroachcloud/labels](https://docs.cockroachlabs.com/docs/cockroachcloud/labels.md)
- Request Unit Metrics: [docs.cockroachlabs.com/docs/cockroachcloud/metrics-request-units](https://docs.cockroachlabs.com/docs/cockroachcloud/metrics-request-units.md)
- `ccloud` Reference: [docs.cockroachlabs.com/docs/cockroachcloud/ccloud-reference](https://docs.cockroachlabs.com/docs/cockroachcloud/ccloud-reference.md)
- Editions and Add-ons: [docs.cockroachlabs.com/docs/continuum/editions-and-add-ons](https://docs.cockroachlabs.com/docs/continuum/editions-and-add-ons.md)
- Cockroach Labs Pricing: [cockroachlabs.com/pricing](https://www.cockroachlabs.com/pricing)
- Cloud Terms and Conditions: [cockroachlabs.com/cloud-terms-and-conditions](https://www.cockroachlabs.com/cloud-terms-and-conditions/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
