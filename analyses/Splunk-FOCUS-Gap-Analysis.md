# Splunk & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Splunk (a Cisco company)  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Splunk Cloud Platform Cloud Monitoring Console (License Usage: Entitlement, Ingest, Workload, Activity Based Pricing, DDAS); Cloud Flex Portfolio Manager; `license_usage.log`; Splunk Observability Cloud subscription usage reports and `sf.org.*` organization metrics; splunk.com pricing pages  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 10 Present, 21 Deviation, 5 Missing Mandatory, 5 Missing Conditional, 2 Missing Recommended, 14 N/A

---

## Executive Summary

Splunk has rich, well-documented usage telemetry and almost no cost data alongside it. Splunk Cloud Platform meters ingest (GB/day), workload (Splunk Virtual Compute, SVC), and storage (DDAS/DDAA) in the Cloud Monitoring Console (CMC), with attribution by index, sourcetype, host, app, user, and search type. Splunk Observability Cloud publishes hourly and per-minute usage reports for hosts, containers, metric time series (MTS), APM, RUM, and Synthetics, with parent/child org breakdowns. Every one of these sources reports quantities only: no price, cost, or currency field appears in any of them. Money lives in order forms and invoices, plus two newer exceptions: the Activity Based Pricing dashboard (dollars drawn from a pool) and the Cloud Flex Portfolio Manager (costs by product license and stack, in controlled availability).

The verdict: 5 of 21 Mandatory columns are missing, and 4 of those are substantive (`BilledCost`, `EffectiveCost`, `ListCost`, `ContractedCost`). The fifth, `BillingCurrency`, is a contract lookup. The other 16 Mandatory columns have source data, 10 of them needing derivation or remapping. The cost gap is not plumbing: Splunk sells term capacity subscriptions (prepaid entitlements, not metered on-demand rates), so producing FOCUS cost columns means joining contract and invoice data to usage telemetry and amortizing the prepaid term across charge periods.

**Recommendation:** Build the FOCUS dataset on top of the Cloud Flex Portfolio Manager cost model, which already attributes cost by product license and stack. Emit one Purchase row per subscription invoice line and daily Usage rows per stack (Platform) or org (Observability) per meter, with `EffectiveCost` amortized from the entitlement. Expose it as a downloadable export and an API rather than a dashboard.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

Splunk has no single billing export. The relevant sources are:

- **CMC License Usage: Entitlement:** ingest limit in GB or total SVCs, DDAS and DDAA in GB, DDAA restore limit, Federated Search for S3 and Federated Analytics scan limits.
- **CMC License Usage: Ingest:** daily GB ingested from `license_usage_summary.log` (UTC days), splittable by index, sourcetype, host, source, and ingestion scenario via `license_usage.log` (`b` bytes, `idx`, `st`, `h`, `s`, `pool`). Host and source values can be "SQUASHED" at high cardinality.
- **CMC License Usage: Workload:** peak SVC at 1-hour, 15-minute, and 5-minute granularity, split by ingestion, search, and shared services, and by index, sourcetype, app, user, and search type.
- **CMC License Usage: Activity Based Pricing:** "Contract usage," the total dollar amount consumed from the customer's pool, plus remaining allocation. The only Platform dashboard with dollar values; no currency code is shown.
- **Cloud Flex Portfolio Manager (controlled availability):** Dollar Pool balance, Spending by Category (Platform, Security, Observability), Cost Over Time, and a table of costs by product license and stack with allocation and entitlement units. This is the closest existing source to a FOCUS cost dataset.
- **Observability Cloud usage reports (tab-delimited):** Monthly usage report (hourly rows: `Date`, `Hour Ending`, `# Hosts`, `# Containers`, `# Custom Metrics`, `# Archived custom metrics`); Hourly usage detail report (`Category Type`, `Category name`, `Token Id`, `Token Name`, `Category Key`, `Category Value`, `Cloud Provider`, `Cloud Region`, `Availability Zone`, `Project Name`, `Project Number`, `Subscription`); Dimension report (daily MTS and data points by dimension); APM detailed usage reports (per-minute, with monthly averages as the billed value); DPM plan reports.
- **Observability organization metrics:** `sf.org.apm.numTracesReceived`, `sf.org.apm.numSpanBytesReceived`, `sf.org.rum.session.org_quota.consumed`, `synthetics.run.count`, and related `sf.org.*` metrics, queryable like any other metric.

Key characteristics for FOCUS:

- **Quantity-only telemetry:** No usage source carries price, cost, or currency. Splunk's docs route billing questions to the account team.
- **Term subscriptions, not on-demand rates:** Platform is sold as ingest, workload, or activity-based subscriptions; Observability as host, MTS, DPM, or TAPM plans. Overage applies only when usage "consistently exceeds" capacity.
- **No public list prices for Platform:** Splunk Cloud Platform and Enterprise Security are "Get a quote." Observability Cloud, AppDynamics, and On-Call publish "starts at" prices only.
- **Multiple sales channels:** direct, partners, AWS Marketplace, Google Cloud Marketplace, and Carahsoft (public sector). The invoice issuer varies by channel.
- **Deployment regions:** Platform stacks run in customer-selected AWS, Google Cloud, and Azure regions (including AWS GovCloud). Observability orgs live in a realm (e.g., us0, us1, eu0, jp0, au0), each mapped to a cloud region.
- **Billing conversions:** one histogram counts as 8 MTS; ten archived MTS count as one real-time MTS; host plans include 100 (Standard) or 200 (Enterprise) custom MTS per host.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven, and each column's feature level determines whether it must be present. Splunk's entitlements are capacity subscriptions purchased up front with no on-demand rate to discount against, so they are not FOCUS commitment discounts: the seven `CommitmentDiscount*` columns are N/A, and negotiated contract rates carry `PricingCategory` = "Standard." The Cloud Flex dollar pool is a better fit for the v1.3+ Contract Commitment dataset than for the v1.2 commitment-discount columns. Feature levels below were taken from the FOCUS v1.2 Content Constraints tables.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Splunk source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Not in usage data; invoice lines and Cloud Flex/ABP dollar draw-down only | Missing: Mandatory |
| EffectiveCost | Mandatory | Not in usage data; requires amortizing prepaid term subscriptions across charge periods | Missing: Mandatory |
| ListCost | Mandatory | No public list price for Platform; Observability "starts at" prices only | Missing: Mandatory |
| ContractedCost | Mandatory | Order-form rates; not exposed in any dataset | Missing: Mandatory |
| BillingAccountId | Mandatory | Splunk customer account exists, but usage is keyed by stack (Platform) or org ID (Observability); map stack/org to account | Deviation |
| BillingAccountName | Mandatory | Customer account name; same mapping | Deviation |
| BillingCurrency | Mandatory | Not in any dataset, including the ABP dollar view; contract currency | Missing: Mandatory |
| BillingPeriodStart | Mandatory | Usage periods exist (UTC license days; Observability usage period, not calendar month); align to invoice period | Deviation |
| BillingPeriodEnd | Mandatory | Same as BillingPeriodStart | Deviation |
| ChargePeriodStart | Mandatory | Hourly (Observability, SVC) and daily (ingest) timestamps | Present |
| ChargePeriodEnd | Mandatory | Same | Present |
| ChargeDescription | Mandatory | Derive: product + meter (e.g., "Splunk Cloud Platform · Ingest GB/day") | Deviation |
| ChargeCategory | Mandatory | Derive: "Purchase" for subscription invoices; "Usage" for consumption and overage; "Credit" for credits | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | Varies by channel: Splunk (direct), AWS, Google, or reseller; not in usage data | Deviation |
| ProviderName | Mandatory (dep. v1.3) | "Splunk" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Splunk" | Present |
| ServiceName | Mandatory | Product names are the dashboard and report boundaries: "Splunk Cloud Platform", "Splunk Enterprise Security", "Splunk Infrastructure Monitoring", "Splunk APM", "Splunk RUM", "Splunk Synthetic Monitoring", "Splunk Log Observer" | Present |
| ServiceCategory | Mandatory | Derive: "Analytics" for Platform; "Security" for Enterprise Security; "Management and Governance" for Observability | Deviation |
| PricingQuantity | Mandatory | Billed measure differs from consumed: entitlement capacity (GB/day, SVC), monthly average (APM, hosts), session quota; compute per plan | Deviation |
| PricingUnit | Mandatory | Normalize: "GB/Day", "SVC", "Hosts", "Containers", "MTS", "Traces", "Sessions", "Runs" | Deviation |
| ConsumedQuantity | Conditional | GB ingested, peak SVC, host/container counts, MTS, traces, sessions, synthetic runs | Present |
| ConsumedUnit | Conditional | Units documented per meter | Present |
| ListUnitPrice | Conditional | No public price list for Platform | Missing: Conditional |
| ContractedUnitPrice | Conditional | Order-form rates; not exposed | Missing: Conditional |
| PricingCategory | Conditional | Derive: "Standard" (contracted rates; no commitment-discount construct) | Deviation |
| ChargeFrequency | Recommended | Derive: "Recurring" for subscriptions; "Usage-Based" for overage and ABP draw-down | Deviation |
| BillingAccountType | Conditional | Derive: direct vs. marketplace/partner account | Deviation |
| SubAccountId | Conditional | Platform stack name; Observability child org ID | Present |
| SubAccountName | Conditional | Stack name; child org name | Present |
| SubAccountType | Conditional | Derive: "Stack" or "Organization" | Deviation |
| ResourceId | Conditional | Attribution dimensions, not billed resources: index (Platform), host/container ID (Observability hourly detail report); define the convention | Deviation |
| ResourceName | Conditional | Index name; host name | Deviation |
| ResourceType | Conditional | Derive: "Index", "Host", "Container" | Deviation |
| SkuId | Conditional | Product license SKUs live on order forms and in Portfolio Manager, not in usage data | Missing: Conditional |
| Tags | Conditional | Observability dimensions, token names, and cloud project/subscription; Platform app/user/sourcetype; reshape to key-value JSON | Deviation |
| PricingCurrency | Conditional | N/A: pricing and billing currency are the same contract currency | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Derive: "Ingest", "SVC", "DDAS Storage", "Host", "Custom MTS", "APM Trace", "RUM Session", "Synthetic Run" | Deviation |
| SkuPriceId | Conditional | No price-catalog ID exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Entitlement conversions (8 MTS per histogram, 10 archived = 1 real-time, included MTS per host) documented but not emitted | Missing: Conditional |
| RegionId | Conditional | Stack cloud region; Observability realm mapped to cloud region | Deviation |
| RegionName | Conditional | Same | Deviation |
| CommitmentDiscountId | Conditional | N/A: capacity subscriptions, not discounted-rate commitments | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice numbers not exposed in any dataset | Missing: Recommended |
| ServiceSubcategory | Recommended | Map: "Log Management", "Security Information and Event Management", "Infrastructure Monitoring", "Application Performance Monitoring" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: Splunk manages zones; customers do not select them for their stack or org | N/A |

**Tally:** 10 Present, 21 Deviation, 5 Missing Mandatory, 5 Missing Conditional, 2 Missing Recommended, 14 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Granular, attributable usage. Hourly and daily charge periods, consumed quantities and units for every meter, stack and child-org hierarchy, index/sourcetype/app/user attribution on Platform, host/container/dimension attribution on Observability. This is a stronger allocation foundation than most SaaS vendors expose.

**Substantive (4 of 5 Mandatory gaps):**

- **`BilledCost`:** invoice amounts exist only in the billing system (and as dollar draw-down for ABP and Cloud Flex customers). They must be joined to usage rows.
- **`EffectiveCost`:** a prepaid annual subscription must be amortized across the term and allocated to stacks, orgs, and meters. Nothing in Splunk's data does this today except, partially, Portfolio Manager.
- **`ListCost` and `ContractedCost`:** Platform has no published rate card and contract rates live on order forms. Splunk must publish an internal list-price catalog per SKU and expose per-customer contracted rates.

**Trivial (1 of 5):** `BillingCurrency` is a lookup from the contract.

**Remaining non-Mandatory:** `ListUnitPrice`, `ContractedUnitPrice`, `SkuId`, `SkuPriceId`, `SkuPriceDetails` all depend on the same price catalog. `InvoiceId` requires exposing invoice numbers.

### 1.5 Deviations to Fix

**PricingQuantity vs. ConsumedQuantity:** these diverge by design. Ingest is billed against a daily GB entitlement; SVC against provisioned capacity; APM and host plans on monthly averages; Observability MTS with histogram and archived-metric conversions. `PricingQuantity` must reflect the billed measure per plan, not a copy of consumption.

**PricingUnit:** normalize per meter: "GB/Day", "SVC", "Hosts", "Containers", "MTS", "Traces", "Sessions", "Runs".

**ChargeCategory and ChargeFrequency:** subscription invoice lines are "Purchase"/"Recurring"; overage and ABP draw-down are "Usage"/"Usage-Based".

**InvoiceIssuerName:** reflect the actual issuer per channel (Splunk direct, AWS Marketplace, Google Cloud Marketplace, or reseller).

**Tags:** reshape Observability dimensions, token names, and cloud project fields, plus Platform app/user/sourcetype splits, into a key-value JSON object. Custom attribution fields that do not fit FOCUS columns should use the `x_` prefix.

**ResourceId:** decide whether index (Platform) and host/container (Observability) are resource identifiers or tags, document the choice, and apply it consistently.

**Already right:** hourly/daily timestamps in UTC, stable stack and org identifiers, and explicit unit names per meter.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2. The v1.3 Contract Commitment dataset is the natural home for Cloud Flex dollar pools and term entitlements, and v1.4's Invoice Detail dataset addresses the invoice-reconciliation gap directly.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Document the capacity-subscription model and why `CommitmentDiscount*` is null. Use the FOCUS Validator, Converter, and Requirements Model.

### 2.3 Phased Roadmap

**Phase 0: Validate scope.** Choose the first product line (Splunk Cloud Platform on Cloud Flex is the strongest candidate because Portfolio Manager already computes cost by stack). Confirm v1.2 certification and v1.4 build targets.

**Phase 1: Cost columns.** Publish an internal list-price catalog per SKU. Join order-form rates and invoice lines to stack/org usage. Emit Purchase rows (`BilledCost`) and daily amortized Usage rows (`EffectiveCost`, `ListCost`, `ContractedCost`). Add `BillingCurrency`, `BillingAccountId`, `InvoiceIssuerName`.

**Phase 2: Shape and enums.** Normalize `PricingUnit`, compute `PricingQuantity` per plan, derive `ChargeCategory`, `ChargeFrequency`, `ServiceCategory`, `PricingCategory`. Reshape `Tags` to key-value. Map stacks and realms to `RegionId`. Ship as a downloadable export and API, not just a dashboard.

**Phase 3: Round out.** Add `SkuId`, `SkuPriceId`, `SkuPriceDetails`, `ListUnitPrice`, `ContractedUnitPrice`, `InvoiceId`, `ServiceSubcategory`. Extend to Observability Cloud using the hourly usage reports and child-org hierarchy.

**Phase 4: Mature and certify.** Model Cloud Flex pools in the Contract Commitment dataset; add Invoice Detail (v1.4). Drop `ProviderName` and `PublisherName`. Validate and certify.

### 2.4 FOCUS Use Cases Splunk Customers Unlock

**Available now (quantities only):** usage trending by index, sourcetype, app, and child org; anomaly detection on ingest, SVC, and MTS consumption.

**After Phase 1:** cost allocation and chargeback by stack and child org; invoice reconciliation; actuals-based budgeting and forecasting; unit economics (cost per GB ingested, cost per host).

**After Phase 2:** multi-vendor observability cost comparison alongside other FOCUS providers; tag-based allocation by team and service.

**Out of scope:** commitment-discount utilization and capacity-reservation use cases (no such constructs).

---

## Part 3: Immediate Next Steps

1. Follow up with the Splunk contact from KubeCon NA 2026 to identify the owner of Portfolio Manager and the billing data platform.
2. Request a sample Portfolio Manager table export and one month of CMC license usage for a Cloud Flex stack.
3. Confirm the invoicing entity per channel and whether a list-price catalog exists internally.
4. Map one stack end to end (Purchase plus daily amortized Usage rows) and run it through the FOCUS Validator.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** All documented Splunk usage sources are quantity-only; no price, cost, or currency field appears in CMC ingest/workload/storage dashboards or Observability usage reports.
- **High:** Cost columns are a substantive gap. Splunk sells prepaid term subscriptions with no public Platform list prices.
- **High:** Observability report field names and Platform license log fields as listed (from Splunk docs and `license_usage.log` documentation).
- **Moderate:** Portfolio Manager as the cost foundation. It is in controlled availability, limited to Cloud Flex contracts, and no export option is documented.
- **Moderate:** `PricingCurrency*` as N/A. Assumes Splunk prices and bills in the same contract currency.
- **Moderate:** `CommitmentDiscount*` as N/A. Correct for ingest/workload entitlements; Cloud Flex dollar pools should be re-examined against the v1.3 Contract Commitment dataset.
- **Low:** No public usage REST endpoint was confirmed for Observability usage reports, and no ACS endpoint for license usage was found. Usage is reachable through `sf.org.*` metrics and Splunk searches.
- **Low:** Invoicing entity. Splunk was acquired by Cisco (2024); public footers show "Splunk LLC," "Splunk Inc.," and "Cisco Systems, Inc." Confirm with Splunk.
- **Not verified live:** FOCUS feature levels were taken from the bundled v1.2 reference (stamped June 23, 2026); the FOCUS MCP spot-check was unavailable in this session. v1.4 remains the latest ratified release (v1.5 is a candidate).

---

## Sources

- Splunk Cloud Platform, Monitor your entitlements: [help.splunk.com](https://help.splunk.com/en/splunk-cloud-platform/administer/admin-manual/10.5.2605/monitor-your-splunk-cloud-platform-deployment/use-the-license-usage-dashboards/monitor-your-entitlements)
- Splunk Cloud Platform, Use the License Usage dashboards: [docs.splunk.com](https://docs.splunk.com/Documentation/SplunkCloud/latest/Admin/MonitoringLicenseUsage)
- Workload Pricing and SVCs: What You Can See and Control: [splunk.com blog](https://www.splunk.com/en_us/blog/platform/workload-pricing-and-svcs-what-you-can-see-and-control)
- Understanding workload pricing in Splunk Cloud Platform: [Splunk Lantern](https://lantern.splunk.com/Manage_Performance_and_Health/Understanding_workload_pricing_in_Splunk_Cloud_Platform)
- Admin Config Service (ACS) API endpoint reference: [help.splunk.com](https://help.splunk.com/en/splunk-cloud-platform/administer/admin-config-service-manual/10.7/admin-config-service-acs-api-endpoint-reference)
- Splunk Observability Cloud, Monitor and manage subscription usage and billing: [help.splunk.com](https://help.splunk.com/en/splunk-observability-cloud/administer/monitor-subscription-usage-and-billing)
- Splunk Observability Cloud, View subscription usage for parent and child organizations: [help.splunk.com](https://help.splunk.com/en/splunk-observability-cloud/administer/monitor-subscription-usage-and-billing/view-parent-child-subscription-usage)
- Splunk Observability Cloud, View your realm, API endpoints, and organization: [help.splunk.com](https://help.splunk.com/en/splunk-observability-cloud/administer/org-reference-info/view-your-realm-api-endpoints-and-organization)
- Splunk Cloud Platform Service Details: [help.splunk.com](https://help.splunk.com/en/splunk-cloud-platform/get-started/service-terms-and-policies)
- Splunk Pricing: [splunk.com/en_us/products/pricing.html](https://www.splunk.com/en_us/products/pricing.html)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
