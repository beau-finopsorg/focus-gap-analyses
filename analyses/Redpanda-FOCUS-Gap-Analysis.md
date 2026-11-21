# Redpanda & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Redpanda Data, Inc.  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Public Redpanda documentation only: Redpanda Cloud billing docs (Billing and Support, View Billing Activity, payment methods, billing notifications, AWS/GCP/Azure Marketplace commit and pay-as-you-go pages); Dedicated tiers reference; BYOC on GCP cluster docs; Cloud Control Plane API reference; Agentic Data Plane cost and usage, cost-allocation tags, budgets, and provider configuration docs; redpanda.com pricing and price-estimator pages  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 19 Present, 8 Deviation, 2 Missing Mandatory, 18 Missing Conditional, 3 Missing Recommended, 7 N/A

> **Public billing docs are thin.** Redpanda documents its billing meters and units, and a Billing activity page with a monthly per-resource CSV export. It does not publish per-unit prices, the CSV's column list, a sample export, an invoice format, or any billing, usage, or invoice API. Much of the column table below is therefore inferred from how the Billing activity UI is described, not from a documented schema. Treat the "Present" statuses as provisional until Redpanda shares a sample CSV.

---

## Executive Summary

Redpanda sells Kafka-compatible data streaming as Redpanda Cloud (Serverless, Dedicated, and BYOC clusters), plus Redpanda Connect pipelines, Redpanda SQL, the Agentic Data Plane (ADP), support plans, and a self-managed Enterprise Edition. Cloud usage is metered in USD, accrues hourly in UTC (partial hours bill as full hours), and is charged to the default card on the first of each month after any credit balance is applied. Customers can also buy through AWS, GCP, or Azure Marketplace, either pay-as-you-go or by private offer with a monthly or annual minimum spend.

This analysis covers the two directions in which Redpanda touches FOCUS:

1. **Redpanda as a data generator for its own charges.** This is a usable start with large holes. The Billing activity page breaks charges down per resource and per meter (Compute, Ingress, Egress, Storage, Uptime, Partitions) with quantity, unit price, and amount, and exports a monthly per-resource CSV. Of the 21 Mandatory columns, 19 have a likely source and 2 are missing. One gap is substantive: **EffectiveCost**, because prepaid credits, promotional credits, commit rollovers, and private-offer discounts all exist, and the Billing activity amounts are shown "before any discounts are applied." **ContractedCost** is a rate-card join. BilledCost needs rework for the same reason.
2. **Redpanda as an allocation layer for third-party LLM spend.** ADP already tracks estimated model spend by agent, model, provider, user, and tag, with an API (`SpendingService`) and CSV export. It does not emit FOCUS and does not mention it.

The structural gap sits outside the column table: there is no billing API. The Cloud Control Plane API has 18 endpoint groups and none covers billing, usage, cost, or invoices. A FinOps tool can only get Redpanda charges by a person downloading a CSV each month.

**Recommendation:** Publish a FOCUS export per organization, delivered through a new Control Plane API endpoint and optionally pushed to object storage: one Usage row per resource × meter × day (Redpanda already accrues hourly, so daily is cheap), with BilledCost after discounts, separate Credit rows for credit draw-down, a Purchase row for the support plan, and commit tracking in the CommitmentDiscount columns. Carry resource group into SubAccountId, cluster region into RegionId, and the cluster ID into ResourceId.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

Redpanda's own billing data (the subject of the column table):

- **Billing activity page** (Billing → Billing activity, Admin role): Select the current or a previous month. Usage totals are subtotaled by resource type and "shown before any discounts are applied." The Resources breakdown filters by resource type (All, Dedicated, Serverless, Redpanda Connect pipeline, Support), resource group, and resource name, with a toggle for deleted resources. Expanding a resource shows meter rows "with quantity, unit price, and amount."
- **CSV export:** "a CSV summary of your monthly charges per resource." The columns are not documented and no sample is published.
- **Billing meters and units** (Billing and Support page; no prices published):
  - Serverless: Uptime (hours, not charged when partitions and storage are both 0), Ingress (GB), Egress (GB), Partitions (per hour), Storage (GB in object storage per hour). Rates vary by region.
  - Dedicated: Uptime (hours, by region and tier), Ingress (GB, by region), Egress (GB, by AZ count), Storage (GB-hours, each byte counted once despite replication factor 3).
  - BYOC: Compute in RPU-hours (1 RPU = 2 vCPU + 8 GB memory), Ingress (GB), Ingress to Iceberg topics (GB, charged on top of standard ingress), Egress (GB, by AZ count), Storage (GB-hours). "The rate decreases as usage increases."
  - Redpanda SQL: RPU-hours at a different rate from BYOC.
  - Redpanda Connect: compute units per hour per pipeline (1 compute unit = 0.1 CPU + 400 MB memory), by cloud and region.
  - Support plans: Basic, Enterprise, and Premium, billed as a resource. Premium is required for BYOVPC/BYOVNet clusters.
- **Pricing pages:** redpanda.com lists Serverless (pay-as-you-go or annual commit), BYOC (annual commitment), and Enterprise Edition (30-day trial). The price estimator is a contact-sales form. No per-unit prices are published there.
- **Cloud Control Plane API** (`https://api.redpanda.com`, v1): Clusters, Networks, Resource Groups, Regions, Organization, users, roles, and service accounts. No billing, usage, cost, or invoice endpoints.

Redpanda's spend data for third-party LLMs (assessed separately in 1.4):

- **ADP Cost and usage:** USD, "model costs only," estimated from a default per-model price table with per-provider overrides (input, output, cache read, and cache write rates in dollars per million tokens). Stored in USD microcents.
- **Dimensions:** provider, model, user, agent, provider type, and tag. Each spending event snapshots the agent's key/value tags at call time.
- **API:** `redpanda.api.adp.v1alpha1.SpendingService` (`GetSpendingBreakdown`, `GetSpendingSummary`, `GetSpendingTimeSeries`, `GetSpendingTimeSeriesByDimension`, `GetSpendingTagKeys`), hourly or daily. CSV exports exist; their columns are not documented. No FOCUS output.

Key characteristics:

- **Hierarchy:** Organization → resource groups → clusters, networks, and pipelines. One payment method covers all billable resources in the organization. Signing up through a marketplace creates a separate organization limited to that cloud.
- **Credits and commits:** Prepaid credits are "drawn down by usage." Commits are "a minimum spend over a contract period." Trials may carry promotional credits. Unused monthly marketplace commitment rolls over until the end of the term; overage is charged.
- **Regions:** Dedicated runs in 12 GCP, 12 AWS, and 5 Azure regions; single-AZ and multi-AZ clusters are supported. Prices vary by region, but how region appears in billing data is not documented.
- **Labels:** BYOC on GCP accepts up to 16 `cloud_provider_tags` "for cost allocation," but these are applied to resources in the customer's own GCP project. Nothing documents labels on Serverless or Dedicated clusters, or labels in Redpanda's billing data.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Redpanda deploys clusters in cloud regions, groups resources into resource groups, runs separate direct and marketplace organizations, and sells minimum-spend commits with discounts, so RegionId, RegionName, SubAccountId, SubAccountName, BillingAccountType, and the CommitmentDiscount family apply. Redpanda prices and bills in USD only and sells no capacity reservations; those columns are N/A and should exist as null. Resource groups are the only sub-account type, so SubAccountType is N/A. Feature levels follow the FOCUS v1.2 Content Constraints, spot-checked against the live spec on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Redpanda source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Billing activity amount per resource and meter, but shown before discounts; credit draw-down not itemized | Deviation |
| EffectiveCost | Mandatory | Not available: needs private-offer discounts, prepaid and promotional credit allocation, and commit amortization and rollover | Missing: Mandatory |
| ListCost | Mandatory | Billing activity amount (quantity × unit price, before discounts) | Present |
| ContractedCost | Mandatory | Not exposed; equals ListCost on pay-as-you-go, private-offer rate × PricingQuantity otherwise | Missing: Mandatory |
| BillingAccountId | Mandatory | Redpanda organization ID | Present |
| BillingAccountName | Mandatory | Organization name | Present |
| BillingCurrency | Mandatory | "USD" | Present |
| BillingPeriodStart | Mandatory | First day of the calendar month (UTC) | Present |
| BillingPeriodEnd | Mandatory | First day of the following month (exclusive) | Present |
| ChargePeriodStart | Mandatory | Month start (CSV is a monthly summary; accrual is hourly) | Present |
| ChargePeriodEnd | Mandatory | Month end | Present |
| ChargeDescription | Mandatory | Resource name plus meter row (e.g., "orders-prod: Ingress") | Present |
| ChargeCategory | Mandatory | Derive: "Usage" for metered rows; "Purchase" for support plans and commit fees; "Credit" for credit draw-down; "Tax" if applicable | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued charges | Present |
| InvoiceIssuerName | Mandatory | "Redpanda Data, Inc." for direct; "Amazon Web Services", "Google", or "Microsoft" for marketplace organizations | Present |
| ProviderName | Mandatory (dep. v1.3) | "Redpanda" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Redpanda" | Present |
| ServiceName | Mandatory | Resource type: "Redpanda Serverless", "Redpanda Dedicated", "Redpanda BYOC", "Redpanda Connect", "Redpanda SQL", "Support" | Present |
| ServiceCategory | Mandatory | Derive: "Analytics" for streaming clusters and SQL; "Integration" for Connect; "Other" for support plans | Deviation |
| PricingQuantity | Mandatory | Meter quantity; BYOC rates decline with volume (tiered), so compute against the rate basis | Deviation |
| PricingUnit | Mandatory | Normalize: "Hours", "GB", "GB-Hours", "Partition-Hours", "RPU-Hours", "Compute Unit-Hours" | Deviation |
| ConsumedQuantity | Conditional | Meter quantity | Present |
| ConsumedUnit | Conditional | Implicit per meter; normalize to FOCUS unit format | Deviation |
| ListUnitPrice | Conditional | Unit price shown per meter row | Present |
| ContractedUnitPrice | Conditional | Not exposed; private-offer rates | Missing: Conditional |
| PricingCategory | Conditional | Derive: "Standard" for pay-as-you-go; "Committed" for usage drawn against a commit | Deviation |
| BillingAccountType | Conditional | Not exposed; direct vs. AWS, GCP, or Azure Marketplace organization | Missing: Conditional |
| SubAccountId | Conditional | Resource group exists as a Billing activity filter; not documented in the CSV | Missing: Conditional |
| SubAccountName | Conditional | Resource group name; same as above | Missing: Conditional |
| SubAccountType | Conditional | N/A: resource group is the only sub-account type | N/A |
| ResourceId | Conditional | Cluster, network, and pipeline IDs exist in the Control Plane API; not documented in billing | Missing: Conditional |
| ResourceName | Conditional | Resource name in the per-resource breakdown | Present |
| ResourceType | Conditional | "Serverless Cluster", "Dedicated Cluster", "BYOC Cluster", "Connect Pipeline", "Support Plan" from the resource type filter | Present |
| SkuId | Conditional | Not exposed; Dedicated and BYOC tiers and Serverless plan are candidates | Missing: Conditional |
| Tags | Conditional | Not in billing; BYOC GCP `cloud_provider_tags` land in the customer's GCP bill, not Redpanda's | Missing: Conditional |
| PricingCurrency | Conditional | N/A: priced and billed in USD only | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Meter rows: Compute, Ingress, Egress, Storage, Uptime, Partitions | Present |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed for region, tier, AZ count, and BYOC volume tiers | Missing: Conditional |
| RegionId | Conditional | Not in billing; cluster cloud region (e.g., "us-east-1") | Missing: Conditional |
| RegionName | Conditional | Not in billing | Missing: Conditional |
| CommitmentDiscountId | Conditional | Commit or private-offer ID; not exposed | Missing: Conditional |
| CommitmentDiscountName | Conditional | Not exposed | Missing: Conditional |
| CommitmentDiscountType | Conditional | Not exposed (e.g., "Annual Commit", "Monthly Commit") | Missing: Conditional |
| CommitmentDiscountCategory | Conditional | "Spend"; not exposed | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | "Used"/"Unused" against the minimum spend | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | USD drawn against the commit | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | "USD" | Missing: Conditional |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Not in Billing activity; card charges and marketplace bills carry their own IDs | Missing: Recommended |
| ChargeFrequency | Recommended | Derive: "Usage-Based" for meters; "Recurring" for support plans and commit fees | Deviation |
| ServiceSubcategory | Recommended | Not exposed; map to an allowed v1.2 value (e.g., "Streaming Analytics" for clusters) | Missing: Recommended |
| AvailabilityZone | Recommended | Not in billing; populate for single-AZ clusters, null for multi-AZ | Missing: Recommended |

**Tally:** 19 Present, 8 Deviation, 2 Missing Mandatory, 18 Missing Conditional, 3 Missing Recommended, 7 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Organization identity, USD-only billing, calendar-month periods, per-resource and per-meter breakdown, list unit prices and pre-discount amounts, and resource names and types. Meters are clean and well defined, which is the hardest part of a FOCUS mapping and the part Redpanda has already done.

**Substantive (1 of 2 Mandatory gaps):**

- **EffectiveCost.** Prepaid credits, promotional credits, minimum-spend commits with monthly rollover, and private-offer discounts all exist, and none of them appear in Billing activity amounts. Producing EffectiveCost means applying the negotiated discount per line and amortizing commit and credit effects back to the usage they cover. On a pay-as-you-go card account with no credits, EffectiveCost equals ListCost; on the BYOC accounts that matter most, it does not.

**Trivial (1 of 2 Mandatory gaps):**

- **ContractedCost.** Equal to ListCost on pay-as-you-go. For private offers, Redpanda already holds the contract rates; expose them per meter.

**Substantive, beyond the column table:**

- **No billing API.** The Control Plane API covers clusters, networks, and identity but no billing. A monthly CSV downloaded by an Admin is the only programmatic-adjacent path.
- **Monthly grain.** Redpanda accrues hourly but exports a monthly summary per resource. Daily anomaly detection and mid-month forecasting are impossible from the export.
- **No region or tags in billing.** Prices vary by region, AZ count, and tier, but none of those are documented in the export, and there is no first-party cost-allocation label on clusters.
- **Marketplace split.** Marketplace organizations see Redpanda bills "directly in the marketplace," where Redpanda typically appears as one subscription line in the hyperscaler's FOCUS data. A Redpanda export with InvoiceIssuerName set to the marketplace is the only way to break that line down.

**Redpanda as an allocation layer for third-party LLM spend:**

ADP's spend tracking is close to FOCUS in substance: hourly or daily cost by provider, model, agent, user, and tag, with tags snapshotted at call time. Two points stand out:

- **It is an estimate, not a bill.** Costs come from a price table that customers can override, and subscription-covered calls record $0. Like Kong AI Cost Management, Redpanda is not the invoice issuer for this spend, so exporting it as FOCUS cost columns risks double-counting against the model provider's own FOCUS data.
- **The tag model is the asset.** ADP already does what Redpanda's own billing does not: key/value cost-allocation tags, preserved as of the charge. Redpanda should bring the same model to clusters and pipelines.

### 1.5 Deviations to Fix

**BilledCost:** Emit post-discount amounts per resource and meter, plus Credit rows for credit draw-down and Purchase rows for support and commit fees, so that BilledCost summed per billing period equals the card charge or marketplace bill.

**ChargeCategory:** "Usage" for metered rows; "Purchase" for support plans and commit fees; "Credit" for prepaid and promotional credit draw-down; "Tax" where tax is charged.

**ServiceCategory:** "Analytics" for Serverless, Dedicated, and BYOC clusters and Redpanda SQL; "Integration" for Redpanda Connect; "Other" for support plans.

**PricingQuantity and PricingUnit:** Uptime, partitions, storage, and Connect compute are flat per region and tier, so PricingQuantity equals consumption there. BYOC rates decrease with volume, so those meters are tiered: compute PricingQuantity against the rate basis and express tiers in SkuPriceDetails. Normalize units to "Hours", "GB", "GB-Hours", "Partition-Hours", "RPU-Hours", and "Compute Unit-Hours".

**ConsumedUnit, PricingCategory, ChargeFrequency:** Derive from meter type and plan as shown in the table.

**Already right:** USD-only billing, calendar-month periods, explicit list unit prices, and a per-resource, per-meter row structure map cleanly.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is a candidate release scheduled for ratification on December 3, 2026; its scope is on the FOCUS site. The v1.3 Contract Commitment dataset fits Redpanda's minimum-spend commits and rollover better than per-row CommitmentDiscount columns alone, and the v1.4 Invoice Detail dataset addresses the missing invoice linkage.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (USD only, no capacity reservations, one sub-account type) and the decision on modeling minimum-spend commits as spend-based commitment discounts. Certification would cover the Redpanda Cloud billing export, not ADP's LLM spend estimates.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one month's Billing activity CSV for a pay-as-you-go organization and a BYOC private-offer organization, with the matching charges. Hand-build a v1.2 file and run it through the Validator. Decide the commit model.

**Phase 1: Close Mandatory gaps.** Apply private-offer rates for ContractedCost and ContractedUnitPrice. Apply discounts and allocate credits and commit effects for EffectiveCost. Emit post-discount BilledCost with Credit and Purchase rows so it reconciles to the charge.

**Phase 2: Fix deviations and add a feed.** Derive ChargeCategory, ServiceCategory, ChargeFrequency, and PricingCategory; normalize PricingUnit and ConsumedUnit; compute PricingQuantity against BYOC tiers. Move to daily rows and expose the export through a Control Plane API billing endpoint.

**Phase 3: Allocation and Conditional columns.** Add ResourceId, SubAccountId and SubAccountName from resource groups, RegionId, RegionName, and AvailabilityZone from the cluster, BillingAccountType for marketplace organizations, SkuId, SkuPriceId, and SkuPriceDetails, the CommitmentDiscount family, InvoiceId, and ServiceSubcategory. Add first-party key/value labels on clusters and pipelines and carry them into Tags, reusing ADP's tag model.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Invoice Detail and Contract Commitment datasets; certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **After Phase 1:** Invoice reconciliation, actuals-based budgeting, and amortized spend reporting for Redpanda Cloud.
- **After Phase 2:** Daily anomaly detection on ingress, egress, and storage; spend by service category across providers; automated ingestion into FinOps tools.
- **After Phase 3:** Chargeback and showback by resource group, cluster, region, or label; unit economics per GB streamed; and commit burn-down tracking.
- **Already available (ADP):** Allocation of estimated LLM spend by agent, model, user, and tag, with budgets.
- **Out of scope:** Capacity reservation management and multi-currency analysis.

---

## Part 3: Immediate Next Steps

1. Follow up with the Redpanda contact from KubeCon NA 2026 to reach the owner of Redpanda Cloud billing and the ADP cost team.
2. Request a sample Billing activity CSV and confirm its columns (resource ID, resource group, region, tier, discounts, credits).
3. Confirm whether a billing or usage API exists internally or is planned, and whether BYOC private-offer discounts are per-unit rates or a percentage off total.
4. Build a v1.2 sample from one billing month and run it through the FOCUS Validator.
5. Open the RFI with `member-cert@finops.org` and discuss FinOps Foundation membership.

---

## Confidence Summary

- **High:** Meter names, units, hourly UTC accrual with full-hour rounding, USD-only pricing, first-of-month card charges after credits, and the Billing activity filters and monthly CSV export come from Redpanda's billing docs.
- **High:** The Cloud Control Plane API has no billing, usage, cost, or invoice endpoint group.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints; spot-checked against the live spec on November 17, 2026, and v1.4 remains the latest ratified version.
- **Moderate:** Present status for ResourceName, ResourceType, ListUnitPrice, ListCost, SkuMeter, and ChargeDescription. These rest on the Billing activity UI description; the CSV's columns are undocumented and may not carry all of them.
- **Moderate:** ListCost and ListUnitPrice as list prices. Docs say amounts are "before any discounts," but private-offer accounts may show contract rates in the unit price column.
- **Moderate:** Treating minimum-spend commits as spend-based commitment discounts. If Redpanda models them as flat prepayments with no rate benefit, the seven CommitmentDiscount columns become N/A.
- **Moderate:** ServiceCategory "Analytics" with ServiceSubcategory "Streaming Analytics" for streaming clusters; confirm against the v1.2 allowed-value tables.
- **Low:** InvoiceIssuerName as "Redpanda Data, Inc." No public invoice names the issuing entity.
- **Low:** Current per-unit prices. Redpanda publishes none; third-party and older figures were not used.

---

## Sources

- Redpanda Cloud Billing and Support: [docs.redpanda.com/redpanda-cloud/billing/billing/](https://docs.redpanda.com/redpanda-cloud/billing/billing/)
- View Billing Activity: [docs.redpanda.com/redpanda-cloud/billing/view-billing-activity/](https://docs.redpanda.com/redpanda-cloud/billing/view-billing-activity/)
- Manage Billing (index, payment methods, notifications, marketplace commit and pay-as-you-go): [docs.redpanda.com/redpanda-cloud/billing/](https://docs.redpanda.com/redpanda-cloud/billing/)
- Dedicated Tiers: [docs.redpanda.com/cloud-data-platform/reference/tiers/dedicated-tiers/](https://docs.redpanda.com/cloud-data-platform/reference/tiers/dedicated-tiers/)
- Create a BYOC Cluster on GCP: [docs.redpanda.com/cloud-data-platform/get-started/cluster-types/byoc/gcp/create-byoc-cluster-gcp/](https://docs.redpanda.com/cloud-data-platform/get-started/cluster-types/byoc/gcp/create-byoc-cluster-gcp/)
- Cloud Control Plane API: [docs.redpanda.com/api/cloud-controlplane-api](https://docs.redpanda.com/api/cloud-controlplane-api)
- ADP Cost and Usage: [docs.redpanda.com/agentic-data-plane/control/cost-usage/](https://docs.redpanda.com/agentic-data-plane/control/cost-usage/)
- ADP Cost-Allocation Tags: [docs.redpanda.com/agentic-data-plane/control/cost-allocation-tags/](https://docs.redpanda.com/agentic-data-plane/control/cost-allocation-tags/)
- ADP Budgets: [docs.redpanda.com/agentic-data-plane/control/budgets/](https://docs.redpanda.com/agentic-data-plane/control/budgets/)
- Redpanda Pricing: [redpanda.com/pricing](https://www.redpanda.com/pricing)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
