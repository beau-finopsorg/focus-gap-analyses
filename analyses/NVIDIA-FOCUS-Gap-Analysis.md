# NVIDIA & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** NVIDIA  
**Prepared:** November 17, 2026  
**Context:** KubeCon + CloudNativeCon North America 2026 booth outreach  
**Source:** Public NVIDIA documentation only: NVIDIA Air (DSX Air) Billing Records API (`GET /api/v3/billing-records/`, `/summary/`, `POST /csv-report/`); NVIDIA Run:ai Reports API (`/api/v1/org-unit/reports`); DGX Cloud, DGX Cloud Lepton, and NVIDIA AI Enterprise product, licensing, and pricing pages  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 11 Present, 16 Deviation, 5 Missing Mandatory, 6 Missing Conditional, 2 Missing Recommended, 17 N/A

---

## Executive Summary

NVIDIA sells cloud and software through four routes, and only one of them has a public, machine-readable billing feed. **DGX Cloud** is sold through private offers on the AWS, Google Cloud, Azure, and OCI marketplaces, so the hyperscaler invoices it and it already lands in those providers' FOCUS exports. **NVIDIA AI Enterprise** is licensed per GPU (term subscriptions at $4,500 per GPU per year partner list price, perpetual licenses, or $1 per GPU-hour pay-as-you-go on cloud marketplaces) and is sold through partners and marketplaces, which again puts the invoice with someone else. **DGX Cloud Lepton** and **NVIDIA Run:ai** have no public billing or cost documentation: Lepton's legacy billing guide now returns 404, and Run:ai's Consumption Report exposes GPU, CPU, and memory allocation by organizational unit with no monetary field. **NVIDIA Air** (the DSX Air data center simulation service) is the exception: it has a documented Billing Records API with per-simulation-run records, org identifiers, timestamps, and compute-hour quantities.

This analysis therefore maps the NVIDIA Air Billing Records API column by column against FOCUS v1.2 and treats the rest of the portfolio as scope context. The verdict: the usage half of FOCUS is in good shape, and the cost half does not exist. Air records carry resource IDs, org hierarchy, start and end timestamps, and a quantity, but no price, no cost, and no currency. Of 21 Mandatory columns, 5 are missing, and 4 of those are substantive (BilledCost, EffectiveCost, ListCost, ContractedCost). Compute hours are sold as prepaid grants through NVIDIA sales with no published rate, so producing the cost columns requires joining contract pricing and amortizing grants, not multiplying by a rate card.

**Recommendation:** Add a price and currency to Air billing records (or publish a compute-hour rate card keyed to the NCA contract), emit grant purchases as Purchase rows, and amortize them into EffectiveCost on usage rows. In parallel, decide which products NVIDIA invoices directly through the NVIDIA Cloud Account (NCA): Lepton and direct AI Enterprise subscriptions are the higher-value FOCUS targets, and Run:ai's per-project allocation data is a natural source for FOCUS v1.3 split cost allocation inside Kubernetes clusters.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**NVIDIA Air Billing Records API** (`GET https://api.dsx-air.nvidia.com/api/v3/billing-records/`): Read-only records, one per simulation billing interval, filterable by `period_start`/`period_end`. Requires the Air Org Administrator role and a user bearer token. A summary endpoint returns totals, and `POST /api/v3/billing-records/csv-report/` produces a CSV export (presigned, time-limited link) with a caller-selected column list.

Record fields: `id`, `created`, `modified`, `org_id`, `org_display_name`, `org_nca_id`, `ngc_org_name`, `org_is_banned`, `simulation_uuid`, `sim_name`, `sim_creator`, `sim_owner`, `run_id`, `fleet_id`, `fleet_name`, `sim_cpu`, `sim_memory` (MiB), `sim_storage` (GB), `sim_compute_hours_rate`, `sim_compute_hours_consumed`, `sim_compute_hours_consumed_for_period`, `billing_started_at`, `billing_ended_at`.

Key characteristics:
- **Billable unit:** the compute hour, metered to the minute. One compute hour is 1 vCPU for 1 hour or 8 GB of memory for 1 hour, billed independently.
- **Prepaid grants:** compute hours are granted to an NGC org (free trial: 10,000 hours over 90 days); paid grants are bought through NVIDIA sales. The Organization model reports `total_compute_hours` and `remaining_compute_hours`, but grants are not billing records.
- **No money anywhere:** no price, cost, or currency field, and no public price list.
- **Hierarchy:** NVIDIA Cloud Account (NCA) contains NGC orgs; usage is attributed to simulation, run, creator/owner, and fleet.
- **No regions or tags:** fleets are the only placement concept; node labels exist in the topology but not in billing data.
- **Period clipping built in:** `sim_compute_hours_consumed_for_period` returns the overlap between a run and the query window, so daily or monthly rows are straightforward.

**Portfolio context (not scored column by column):**
- **DGX Cloud:** hyperscaler marketplace private offers; billed by AWS, Google Cloud, Azure, or OCI. NVIDIA spend appears in those providers' FOCUS exports as marketplace charges.
- **NVIDIA AI Enterprise:** per-GPU licensing; term, perpetual, or marketplace pay-as-you-go. The NVIDIA License System reports license usage for capacity planning, with no documented fields, export, or API.
- **DGX Cloud Lepton:** Organization and Workspace hierarchy tied to an NCA; three node group types (BYOC, BYOK, Lepton Managed). Python SDK resources include no billing, usage, or cost resource. Observability export sends logs and custom metrics to Datadog only.
- **NVIDIA Run:ai:** Consumption Reports (CSV) grouped by Nodepool, Project, Department, or Cluster over a date range. Column schema is not documented and there is no cost or price setting.
- **build.nvidia.com:** free inference trial; no documented credits, pricing, or usage API.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and populated, Conditional columns must be present when the provider's model triggers them, and values must match FOCUS formats and allowed values. Air has no commitment-discount or capacity-reservation construct, no regions or zones, and no cost tags on simulations, so those column families are N/A. Feature levels were taken from the bundled v1.2 table and spot-checked against the live specification on focus.finops.org.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | NVIDIA Air source | Status |
|---|---|---|---|
| BilledCost | Mandatory | No cost field; compute hours drawn from prepaid grants priced off-system | Missing: Mandatory |
| EffectiveCost | Mandatory | Requires amortizing grant purchase price across hours consumed | Missing: Mandatory |
| ListCost | Mandatory | No published compute-hour rate | Missing: Mandatory |
| ContractedCost | Mandatory | Contract rate held by NVIDIA sales, not in records | Missing: Mandatory |
| BillingAccountId | Mandatory | `org_nca_id` (NVIDIA Cloud Account) | Present |
| BillingAccountName | Mandatory | NCA name not emitted; join from NCA or fall back to `org_display_name` | Deviation |
| BillingCurrency | Mandatory | No currency field | Missing: Mandatory |
| BillingPeriodStart | Mandatory | No invoice period; derive from `period_start` query aligned to calendar month | Deviation |
| BillingPeriodEnd | Mandatory | Derive from `period_end` query aligned to calendar month | Deviation |
| ChargePeriodStart | Mandatory | Derive: later of `billing_started_at` and window start | Deviation |
| ChargePeriodEnd | Mandatory | Derive: earlier of `billing_ended_at` (or now) and window end | Deviation |
| ChargeDescription | Mandatory | Derive from `sim_name` + `fleet_name` (e.g., "NVIDIA Air simulation · spine-leaf-lab · fleet-a") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for runs; "Purchase" for grants; "Credit" for trial grants | Deviation |
| ChargeClass | Mandatory (nullable) | null; no correction mechanism documented | Present |
| InvoiceIssuerName | Mandatory | Not emitted; "NVIDIA Corporation" when sold direct, partner name when resold | Deviation |
| ProviderName | Mandatory (dep. v1.3) | "NVIDIA" | Present |
| PublisherName | Mandatory (dep. v1.3) | "NVIDIA" | Present |
| ServiceName | Mandatory | "NVIDIA Air" | Present |
| ServiceCategory | Mandatory | Derive: "Compute" (billed on vCPU and memory) | Deviation |
| PricingQuantity | Mandatory | `sim_compute_hours_consumed_for_period` | Present |
| PricingUnit | Mandatory | Unit implied by docs, not a field; set "Compute Hours" | Deviation |
| ConsumedQuantity | Conditional | `sim_compute_hours_consumed_for_period` | Present |
| ConsumedUnit | Conditional | Set "Compute Hours" | Deviation |
| ListUnitPrice | Conditional | No published rate | Missing: Conditional |
| ContractedUnitPrice | Conditional | Contract rate not in records | Missing: Conditional |
| PricingCategory | Conditional | Depends on undisclosed grant terms | Missing: Conditional |
| ChargeFrequency | Recommended | Derive: "Usage-Based" for runs; "One-Time" for grants | Deviation |
| BillingAccountType | Conditional | Derive from org type (Individual or Enterprise) | Deviation |
| SubAccountId | Conditional | `org_id` (NGC org) | Present |
| SubAccountName | Conditional | `ngc_org_name` / `org_display_name` | Present |
| SubAccountType | Conditional | Set "NGC Organization" | Deviation |
| ResourceId | Conditional | `simulation_uuid` | Present |
| ResourceName | Conditional | `sim_name` | Present |
| ResourceType | Conditional | Set "Simulation" | Deviation |
| SkuId | Conditional | No SKU identifier | Missing: Conditional |
| Tags | Conditional | N/A: no user-defined tags on simulations; node labels are topology metadata | N/A |
| PricingCurrency | Conditional | N/A: no separate pricing currency documented | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Derive "Compute Hours" (vCPU-hours + memory-8GB-hours) | Deviation |
| SkuPriceId | Conditional | No price identifier | Missing: Conditional |
| SkuPriceDetails | Conditional | `sim_compute_hours_rate` is a consumption rate, not a price; no price details | Missing: Conditional |
| RegionId | Conditional | N/A: fleets only, no regions | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: prepaid grants are not discount instruments | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | No invoice reference in records | Missing: Recommended |
| ServiceSubcategory | Recommended | Not emitted; "Virtual Machines" fits (Air nodes are VMs) | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: no zones | N/A |

**Tally:** 11 Present, 16 Deviation, 5 Missing Mandatory, 6 Missing Conditional, 2 Missing Recommended, 17 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Resource-level grain (`simulation_uuid`, `run_id`), a two-level account hierarchy (NCA to NGC org), precise start and end timestamps, period-clipped quantities, owner and fleet attribution, and a self-service CSV export. This is better usage plumbing than most providers rated Nascent.

**Substantive (4 of 5 Mandatory gaps):** BilledCost, EffectiveCost, ListCost, and ContractedCost. No cost exists in the dataset, compute hours are bought as prepaid grants at contract prices, and grants expire. Producing these columns means joining each org's grant price, amortizing it across consumed hours, and handling expired or voided hours. That is a billing-system change, not a transform.

**Trivial (1 of 5):** BillingCurrency is a constant once a cost exists.

**Out of scope here but material:** DGX Cloud, AI Enterprise, Lepton, and Run:ai have no public billing feed. For DGX Cloud and marketplace AI Enterprise, the hyperscaler's FOCUS export is the customer's source of truth today.

### 1.5 Deviations to Fix

**ChargePeriodStart / ChargePeriodEnd:** Records span a whole run. Clip each run to daily windows using `period_start`/`period_end` and `sim_compute_hours_consumed_for_period` so each FOCUS row covers one day.

**PricingUnit / ConsumedUnit / SkuMeter:** The compute hour is a composite of vCPU-hours and 8 GB memory-hours. Emit "Compute Hours" consistently, and consider splitting vCPU and memory into separate meters so consumption is auditable.

**ChargeCategory / ChargeFrequency:** Emit grant purchases as "Purchase" / "One-Time", trial grants as "Credit", and runs as "Usage" / "Usage-Based". Grants are currently invisible in billing records.

**BillingAccountName / InvoiceIssuerName:** Both depend on the commercial relationship (NCA, direct vs. partner) and are not in the record.

**ServiceCategory:** "Compute" is the closest allowed value; Air is billed on vCPU and memory.

**Already right:** Stable resource IDs, ISO 8601 timestamps, nullable end time for running sims, and the CSV report endpoint.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2. FOCUS v1.5 is a candidate release with ratification scheduled for December 3, 2026; its consumption currency for provider credits and its SKU Price dataset preview fit Air's compute-hour grants and are worth designing toward.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report. Use the FOCUS Validator against a sample export and document the N/A families (no regions, no commitment discounts, no capacity reservations, no cost tags).

### 2.3 Phased Roadmap

**Phase 0: Scope.** Confirm which NVIDIA products are invoiced directly through the NCA (Air, Lepton, direct AI Enterprise subscriptions) versus through hyperscalers and partners. Pull one month of Air billing records via the CSV report endpoint and run it through the FOCUS Validator to baseline.

**Phase 1: Cost columns for Air.** Attach a contract price and currency to each org's compute-hour grants; emit grants as Purchase rows; compute BilledCost, ListCost, ContractedCost, and EffectiveCost on daily usage rows.

**Phase 2: Deviations.** Daily charge periods, unit normalization, ChargeCategory/ChargeFrequency, BillingAccountName, InvoiceIssuerName, ServiceCategory, ServiceSubcategory, InvoiceId.

**Phase 3: Extend to directly billed products.** Apply the same schema to DGX Cloud Lepton (node-group GPU-hours, workspace as sub-account) and direct AI Enterprise subscriptions (Purchase / Recurring rows per GPU).

**Phase 4: Allocation and certification.** Map Run:ai Consumption Report allocation (cluster, department, project, node pool) to FOCUS v1.3 split cost allocation columns. Drop ProviderName and PublisherName for v1.4. Validate and certify.

---

## Part 3: Immediate Next Steps

1. Identify the NVIDIA owner for NCA billing and confirm which products NVIDIA invoices directly.
2. Generate one month of Air billing records via `POST /api/v3/billing-records/csv-report/` and validate a FOCUS-shaped transform.
3. Decide where compute-hour pricing lives (rate card or per-contract) and expose it with currency on billing records.
4. Publish the Run:ai Consumption Report column schema; it is the KubeCon audience's most likely FOCUS touchpoint.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** NVIDIA Air Billing Records API fields, endpoints, and the absence of any price, cost, or currency field (read from the API reference).
- **High:** DGX Cloud is sold through hyperscaler marketplace private offers, and AI Enterprise is licensed per GPU through partners and marketplaces (product and licensing pages).
- **High:** No public billing, usage, or cost API exists for DGX Cloud Lepton, Run:ai, or build.nvidia.com as of this date. Gated customer portals may hold more.
- **Moderate:** NCA as BillingAccountId and NGC org as SubAccountId. The docs tie Air billing to NGC orgs within an NCA but do not describe invoicing.
- **Moderate:** Prepaid compute-hour grants are not commitment discounts. If grants are sold at a discount to a list rate, the CommitmentDiscount family would apply.
- **Moderate:** ServiceCategory "Compute" and ServiceSubcategory "Virtual Machines" for a simulation service.
- **Low:** Whether NVIDIA or a partner is the InvoiceIssuerName for Air, Lepton, and AI Enterprise in a given deal.
- **Spec verification:** The FOCUS MCP server was unavailable. Feature levels came from the bundled v1.2 table (dated June 23, 2026), with ServiceSubcategory, ChargeFrequency, PricingUnit, Tags, and InvoiceId spot-checked against focus.finops.org; all matched. No version newer than v1.4 is ratified.

---

## Sources

- NVIDIA Air Billing Records API: [list](https://docs.nvidia.com/dsx-air/api-reference/billing/api-v-3-billing-records-list.md), [summary](https://docs.nvidia.com/dsx-air/api-reference/billing/api-v-3-billing-records-summary-retrieve.md), [CSV report](https://docs.nvidia.com/dsx-air/api-reference/billing/api-v-3-billing-records-csv-report-create.md)
- NVIDIA Air account setup: [docs.nvidia.com/dsx-air/account-setup](https://docs.nvidia.com/dsx-air/account-setup.md)
- NVIDIA Run:ai Reports: [run-ai-docs.nvidia.com](https://run-ai-docs.nvidia.com/saas/platform-management/monitor-performance/reports), [Reports API](https://run-ai-docs.nvidia.com/api/organizations/reports)
- DGX Cloud Lepton: [Python SDK reference](https://docs.nvidia.com/dgx-cloud/lepton/reference/api), [observability export](https://docs.nvidia.com/dgx-cloud/lepton/features/utilities/observability/export/), [product page](https://www.nvidia.com/en-us/data-center/dgx-cloud-lepton/)
- DGX Cloud: [nvidia.com/dgx-cloud](https://www.nvidia.com/en-us/data-center/dgx-cloud/)
- NVIDIA AI Enterprise licensing and pricing: [licensing guide](https://docs.nvidia.com/ai-enterprise/planning-resource/licensing-guide/latest/pricing.html), [License System](https://docs.nvidia.com/ai-enterprise/planning-resource/licensing-guide/latest/license-system.html)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/); FOCUS 1.5 release scope: [focus.finops.org](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
