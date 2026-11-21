# Fastly & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Fastly, Inc.  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Fastly Invoices API v3 (`/billing/v3/invoices`, `/invoices/{invoice_id}`, `/invoices/month-to-date`); Usage Metrics API v3 (`/billing/v3/usage-metrics`, `/service-usage-metrics`); Historical Stats usage endpoints (`/stats/usage`, `/stats/usage_by_service`, `/stats/usage_by_month`); Fastly billing guides; Fastly pricing and package entitlements pages  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 15 Present, 13 Deviation, 2 Missing Mandatory, 14 Missing Conditional, 1 Missing Recommended, 12 N/A

---

## Executive Summary

Fastly is an edge cloud platform. Customers buy Full-Site Delivery (CDN), Compute (edge WebAssembly), security (Next-Gen WAF, DDoS Protection, Bot Management), Image Optimizer, KV and Object Storage, DNS, and Observability. Self-serve Growth accounts pay as they go on tiered, per-region rates for bandwidth (per GB) and requests (per 10,000), after a monthly free allowance. Package customers pay a fixed monthly fee (for example, Network Services Basic at $1,500) for bundled allowances. Enterprise terms are set in a Service Order. Fastly bills monthly in arrears.

**Public billing documentation is thin.** The Invoices and Usage Metrics API references list field names and one-line descriptions in a single flat table, with no example payloads, no nesting, no enumeration of products or usage types, and no statement of the unit basis behind `rate` and `units`. Nothing public describes how credits, taxes, free-tier allowances, package fees, or committed spend appear on a line item, or how fresh the data is. Several classifications below are inferences from field names and should be confirmed with a real response.

On what is documented, the Invoices API is a reasonable starting point. Each invoice line carries `amount` ("Billed amount for line item"), `rate`, `units`, `product_name`, `product_line`, `product_group`, `region`, `usage_type`, and `description`, under an invoice with `customer_id`, `invoice_id`, `currency_code`, and ISO 8601 billing dates. Fifteen of 57 FOCUS v1.2 columns map directly and 19 of 21 Mandatory columns have a source. The two missing Mandatory columns are EffectiveCost (substantive) and ListCost (trivial, but tiered).

The larger problem sits outside the Mandatory columns. Line items are **monthly and account-wide**: one row per product × region × usage type per invoice, with no service ID. Fastly's own guide states that "an itemized list of billing charges per service is not available." Per-service data exists only as unrated usage (Usage Metrics and Historical Stats). A FOCUS consumer can allocate cost to services only by pro-rating invoice dollars across usage counts, which Fastly is better placed to do. Fastly has no tags and no documented sub-account hierarchy, so the service is the only allocation dimension available.

**Recommendation:** Publish a FOCUS export per customer with one row per service × product × billing region × usage type × day, carrying the service ID and name as ResourceId and ResourceName, and priced ListCost (public tiered rate), ContractedCost, BilledCost, and EffectiveCost. Emit package fees as Recurring Purchase rows and amortize them across the usage they fund. Emit Credit and Tax rows so BilledCost reconciles to the invoice. Deliver it through the existing `/billing/v3/` API alongside invoices, and publish an example response for every billing endpoint.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

- **Invoices API** (`GET /billing/v3/invoices`, `GET /billing/v3/invoices/{invoice_id}`, `GET /billing/v3/invoices/month-to-date`): Invoice fields `customer_id`, `invoice_id`, `statement_number`, `invoice_posted_on`, `billing_start_date`, `billing_end_date` (ISO 8601), `currency_code`, `monthly_transaction_amount`, and `transaction_line_items`. Line-item fields `description`, `amount`, `rate` ("Price per unit"), `units`, `product_name`, `product_line` (e.g., `Network Services`, `Security`), `product_group` (e.g., `Compute`, `Full-Site Delivery`), `region`, `usage_type` (e.g., `requests`, `bandwidth`), and `credit_coupon_code`. Cursor pagination, up to 200 invoices per page.
- **Usage Metrics API** (`GET /billing/v3/usage-metrics`, `GET /billing/v3/service-usage-metrics`): Monthly usage by product, and by service on the second endpoint. Fields include `product_id` (e.g., `cdn_usage`), `usage_type`, `name` (e.g., "North America Requests"), `unit`, `region`, `month`, `quantity`, `raw_quantity`, and `last_updated_at`. No cost fields. Fastly says this API is for customers who do not receive invoices.
- **Historical Stats usage endpoints** (`GET /stats/usage`, `/stats/usage_by_service`, `/stats/usage_by_month`): "Unrated request and bandwidth used by a service, aggregated by billing region." `usage_by_month` with `billable_units=true` converts bandwidth to GB and requests to units of 10,000.
- **Invoice details page:** Per-invoice CSV export ("Print & export > Export to CSV") and PDF. Not available in bulk from the Invoices page. Credit memos list the invoices they were applied to and the amount credited.

Key characteristics:

- **Pricing model:** Free, Growth (pay as you go with volume tiers), and Enterprise (custom). Bandwidth is "Billed per GB per Region per month" (for example, $0.12 per GB in North America and Europe and $0.28 in Africa, India, and South Korea for the 100 GB to 10 TB tier). Requests are "Billed per 10,000 Requests per Region per month."
- **Free allowances:** 100 GB of Full-Site Delivery bandwidth, 1 million requests, 10 million Compute requests, 100 million Compute vCPU milliseconds, 100,000 Image Optimizer requests, and 5 GB of Object Storage per month.
- **Packages:** Network Services (Basic $1,500, Starter $6,000 per month; Advantage and Ultimate through sales), Compute (Starter $500), Observability (Starter $1,500), and Security (Core, Core Plus, Total, through sales). Each bundles monthly allowances, with add-ons sold per item. Overage terms are not published.
- **Billing regions:** Ten, with Historical Stats codes `usa`, `europe`, `asia`, `anzac`, `asia_india`, `asia_southkorea`, `africa_std`, `mexico`, `southamerica_std`, and `saudi_arabia`.
- **Grain:** Invoices are monthly and account-wide. Service-level data is usage only.
- **Credits:** Credit memos and a `credit_coupon_code` on line items. How a credit lands on a line (netted, separate line, or memo only) is not documented.
- **No tags:** The Service model has `name` and `comment` but no tags or labels, and the API has no tags collection.
- **Legacy pricing:** Accounts created before November 4, 2025 may be on a separate legacy price list.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Fastly packages and Enterprise Service Orders exchange a fixed monthly fee or contracted term for bundled allowances at a lower effective rate, so this analysis treats the CommitmentDiscount family as applicable. Fastly prices by billing region, so RegionId and RegionName apply. Fastly delivers a service per customer, so ResourceId, ResourceName, and ResourceType apply. Fastly documents no capacity reservations, availability zones, tags, sub-account hierarchy, multiple billing account types, or alternate pricing currencies; those columns are N/A and should exist as null. Feature levels below follow the FOCUS v1.2 Content Constraints, spot-checked against the live spec on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Fastly source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Line-item `amount` ("Billed amount for line item"), at monthly product × region × usage-type grain | Present |
| EffectiveCost | Mandatory | Not available: package fees and Service Order terms must be amortized onto the usage they fund | Missing: Mandatory |
| ListCost | Mandatory | Not emitted; compute from public tiered per-region rates × `units` | Missing: Mandatory |
| ContractedCost | Mandatory | Derive `rate` × `units`; confirm `rate` is the contracted rate and not a blend across tiers | Deviation |
| BillingAccountId | Mandatory | Invoice `customer_id` | Present |
| BillingAccountName | Mandatory | Not on invoice; join customer name from the Customer API | Deviation |
| BillingCurrency | Mandatory | Invoice `currency_code` | Present |
| BillingPeriodStart | Mandatory | Invoice `billing_start_date` | Present |
| BillingPeriodEnd | Mandatory | Invoice `billing_end_date` | Present |
| ChargePeriodStart | Mandatory | `billing_start_date` (line items are monthly) | Present |
| ChargePeriodEnd | Mandatory | `billing_end_date` | Present |
| ChargeDescription | Mandatory | Line-item `description` | Present |
| ChargeCategory | Mandatory | Not emitted; derive "Usage" for metered lines, "Purchase" for package fees, "Credit" for credit memos and coupons, "Tax" if taxes are invoiced | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued charges | Present |
| InvoiceIssuerName | Mandatory | "Fastly, Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "Fastly" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Fastly" | Present |
| ServiceName | Mandatory | Line-item `product_name` | Present |
| ServiceCategory | Mandatory | Derive from `product_line` and `product_group`: "Networking" for delivery and DNS; "Security" for WAF, DDoS, and Bot Management; "Compute" for Compute; "Storage" for KV and Object Storage; "Management and Governance" for Observability | Deviation |
| PricingQuantity | Mandatory | Line-item `units`; unit basis undocumented (requests are priced per 10,000), and tiered rates require computation against the rate basis | Deviation |
| PricingUnit | Mandatory | `usage_type` names the measure (`bandwidth`, `requests`), not the unit; normalize to "GB", "10K Requests", and so on | Deviation |
| ConsumedQuantity | Conditional | Line-item `units`, or `raw_quantity` from Usage Metrics | Deviation |
| ConsumedUnit | Conditional | Implied by `usage_type`; Usage Metrics `unit` is "unit" when no explicit unit exists | Deviation |
| ListUnitPrice | Conditional | Not in data; public pricing page, tiered per region | Missing: Conditional |
| ContractedUnitPrice | Conditional | Line-item `rate`; confirm it is a single contracted rate rather than a tier blend | Deviation |
| PricingCategory | Conditional | Derive: "Standard" for pay-as-you-go and overage; "Committed" for usage drawn from package or Service Order allowances | Deviation |
| BillingAccountType | Conditional | N/A: one billing account type documented | N/A |
| SubAccountId | Conditional | N/A: no sub-account hierarchy documented | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | Service ID exists in usage APIs but not on any priced line; Fastly states per-service charges are not available | Missing: Conditional |
| ResourceName | Conditional | Service `name` exists in the Services API; not on priced lines | Missing: Conditional |
| ResourceType | Conditional | Not emitted (e.g., "Delivery Service", "Compute Service", "KV Store") | Missing: Conditional |
| SkuId | Conditional | Not on invoice lines; Usage Metrics `product_id` (e.g., `cdn_usage`) is the closest identifier | Missing: Conditional |
| Tags | Conditional | N/A: services have no tags or labels | N/A |
| PricingCurrency | Conditional | N/A: no pricing currency distinct from `currency_code` documented | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Line-item `usage_type` (e.g., `bandwidth`, `requests`); Usage Metrics `name` (e.g., "North America Requests") is closer | Deviation |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed for volume tier and billing region | Missing: Conditional |
| RegionId | Conditional | `region` is a display name; map to Historical Stats codes (`usa`, `europe`, `asia_india`, and so on) | Deviation |
| RegionName | Conditional | Line-item `region` | Present |
| CommitmentDiscountId | Conditional | Package or Service Order ID; not exposed | Missing: Conditional |
| CommitmentDiscountName | Conditional | Package name (e.g., "Network Services Basic"); not exposed | Missing: Conditional |
| CommitmentDiscountType | Conditional | Not exposed (e.g., "Package", "Service Order") | Missing: Conditional |
| CommitmentDiscountCategory | Conditional | "Usage" for request and bandwidth allowances; "Spend" for committed dollar amounts; not exposed | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | "Used"/"Unused" against monthly allowances; not exposed | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | Allowance drawn (e.g., requests against "100 Million Requests per month") | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | "Requests", "GB", and so on | Missing: Conditional |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice `invoice_id` (`statement_number` also available) | Present |
| ChargeFrequency | Recommended | Derive: "Usage-Based" for metered lines; "Recurring" for package fees and per-item add-ons | Deviation |
| ServiceSubcategory | Recommended | Not emitted; map each product to an allowed v1.2 value (e.g., "Content Delivery" for Full-Site Delivery) | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: billing regions are the only location dimension | N/A |

**Tally:** 15 Present, 13 Deviation, 2 Missing Mandatory, 14 Missing Conditional, 1 Missing Recommended, 12 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Billing account, currency, billing periods, invoice ID, billed amount per line, product names, billing region, and a paginated, programmatic Invoices API with a month-to-date endpoint. Fastly already has the delivery path most edge and SaaS vendors lack.

**Substantive (1 of 2 Mandatory gaps):**

- **EffectiveCost.** Package customers pay a fixed monthly fee for bundled allowances, and Enterprise customers are billed "as specified in your applicable ordering document." EffectiveCost requires spreading the package fee or contracted amount across the usage it covers, and netting credit memos back to the lines they offset. Pay-as-you-go Growth accounts with no credits are the only case where EffectiveCost equals BilledCost.

**Trivial (1 of 2 Mandatory gaps):**

- **ListCost.** Fastly owns the public price list. Apply the tiered, per-region rate to `units`. Because rates fall with volume, ListCost must be computed tier by tier, not as `units` × one rate. Accounts on legacy pricing need the legacy table.

**Substantive, beyond the column table:**

- **No per-service cost.** Line items carry no service ID. Fastly's guide confirms per-service charges are not available. Allocation to teams or applications needs ResourceId on priced rows, and Fastly holds the metering needed to produce them.
- **Monthly grain.** Every priced row spans the full billing month. Daily rows are a prerequisite for anomaly detection and timely showback.
- **Thin documentation.** No example payloads, no list of `product_name`, `product_group`, `usage_type`, or `region` values, no unit basis for `rate` and `units`, and no description of credit, tax, free-tier, or package-fee lines. A consumer cannot build a reliable mapping from the public docs alone.
- **Free tier and allowances.** Free and package allowances are invisible in the line items. A FOCUS export should show usage within an allowance at zero BilledCost with PricingCategory and CommitmentDiscount columns explaining why.

### 1.5 Deviations to Fix

**PricingQuantity, PricingUnit, ConsumedQuantity, ConsumedUnit:** Emit explicit units in FOCUS format ("GB" for bandwidth, "10K Requests" or "Requests" for requests, "vCPU-Milliseconds" for Compute, "GB-Months" for storage). Compute PricingQuantity against the rate basis, and keep ConsumedQuantity as the raw measured quantity (`raw_quantity`).

**ContractedCost and ContractedUnitPrice:** Confirm whether `rate` is the contracted rate for a single tier or a blended rate across tiers. If blended, split lines by tier or carry tier detail in SkuPriceDetails.

**ServiceCategory and ChargeCategory:** Derive from `product_line` and the line type, as shown in the table. Emit credit memos and coupons as Credit rows.

**RegionId:** Map the `region` display name to a stable code; the Historical Stats codes already exist.

**BillingAccountName, PricingCategory, ChargeFrequency, SkuMeter:** Derive as shown in the table.

**Already right:** Customer ID, ISO 8601 billing dates, ISO 4217 currency code, invoice ID, billed amount, product name, region name, and line description map cleanly.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is in release candidate with ratification scheduled for December 3, 2026. The Contract Commitment dataset (v1.3) fits Fastly packages and Service Orders, and the Invoice Detail dataset (v1.4) fits the existing Invoices API almost directly.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (no tags, zones, reservations, sub-accounts, or alternate currencies) and the decision on modeling packages and Service Orders as commitment discounts. Public sample data would also fix the documentation gap.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one month of invoices for a Growth account and a package account, plus `service-usage-metrics` for the same month. Hand-build a FOCUS file from the invoice lines, run it through the Validator, and record how credits, taxes, free tier, and package fees actually appear.

**Phase 1: Service and day grain.** Re-cut priced usage by service ID × product × billing region × usage type × day. This is the prerequisite for allocation and for every downstream use case.

**Phase 2: Close Mandatory gaps.** Compute ListCost and ListUnitPrice from the tiered public table, confirm `rate` for ContractedCost, emit package fees as Purchase rows and credits as Credit rows, and amortize package and Service Order amounts for EffectiveCost. Reconcile BilledCost to `monthly_transaction_amount`.

**Phase 3: Fix deviations and fill Conditional columns.** Derive ChargeCategory, ServiceCategory, ChargeFrequency, and PricingCategory; normalize units; emit RegionId, ResourceId, ResourceName, ResourceType, SkuId, SkuPriceId, SkuPriceDetails, the CommitmentDiscount family, and ServiceSubcategory. Expose the export through `/billing/v3/` and publish example responses.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Contract Commitment and Invoice Detail datasets; certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **Today, from the Invoices API:** Monthly spend by product and billing region, invoice-level reporting, and month-to-date tracking.
- **After Phase 1:** Cost allocation and showback by service, daily anomaly detection, and regional traffic cost analysis.
- **After Phase 2:** Invoice reconciliation, actuals-based budgeting and forecasting, package utilization, and list-versus-contracted savings reporting.
- **After Phase 3:** Cross-provider spend by service category (Fastly alongside other CDN and cloud networking spend), unit economics per request and per GB, and commitment utilization.
- **Out of scope:** Tag-based allocation (unless Fastly adds service labels), availability zone analysis, and capacity reservation management.

---

## Part 3: Immediate Next Steps

1. Follow up with the Fastly contact from KubeCon NA 2026 to identify the owner of the Invoices API and billing data platform.
2. Request a real Invoices API response (redacted) covering a credit, a package fee, free-tier usage, and taxes, and confirm the unit basis of `rate` and `units`.
3. Confirm whether internal metering already records priced usage by service and day (the Historical Stats data suggests it does for bandwidth and requests).
4. Confirm whether Enterprise Service Orders include committed spend, and which legal entity issues invoices outside the US.
5. Build a v1.2 sample from one month of invoices and run it through the FOCUS Validator.
6. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Invoices API, Usage Metrics API, and Historical Stats usage endpoint paths and field names, taken from Fastly's published API reference.
- **High:** Fastly's statement that per-service itemized charges are not available, monthly billing in arrears, credit memos, and per-invoice CSV export, from Fastly's billing guides.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints; spot-checked against the live spec on November 17, 2026, and v1.4 remains the latest ratified version.
- **Moderate:** Field nesting within the invoice and usage responses. The reference lists all fields in one flat table; the line-item grouping is inferred from field order and descriptions.
- **Moderate:** Treating packages and Service Orders as commitment discounts. If Fastly models packages as plain recurring fees with no rate benefit, the seven CommitmentDiscount columns become N/A and the package moves to the Contract Commitment dataset only.
- **Moderate:** No tags and no sub-account hierarchy. Neither appears in the Services API or billing guides reviewed; the Organizations and Account APIs were not checked in depth.
- **Moderate:** Single billing account type and no alternate pricing currency. The presence of `currency_code` implies non-USD invoicing may exist.
- **Low:** Whether `rate` is a contracted single-tier rate or a blend, whether `units` for requests counts single requests or blocks of 10,000, and how credits, taxes, free tier, and package fees appear on line items. None is documented.
- **Low:** InvoiceIssuerName for customers outside the US. "Fastly, Inc." is the parent entity; regional subsidiaries may invoice some customers.

---

## Sources

- Fastly Invoices API: [fastly.com/documentation/reference/api/account/invoices/](https://www.fastly.com/documentation/reference/api/account/invoices/)
- Fastly Usage Metrics API: [fastly.com/documentation/reference/api/account/billing-usage-metrics/](https://www.fastly.com/documentation/reference/api/account/billing-usage-metrics/)
- Fastly Historical Stats API: [fastly.com/documentation/reference/api/metrics-stats/historical-stats/](https://www.fastly.com/documentation/reference/api/metrics-stats/historical-stats/)
- About the charges on your bill: [fastly.com/documentation/guides/.../about-the-charges-on-your-bill/](https://www.fastly.com/documentation/guides/organizations-and-accounts/billing/about-the-charges-on-your-bill/)
- Monitoring billing and usage details: [fastly.com/documentation/guides/.../monitoring-billing-and-usage-details](https://www.fastly.com/documentation/guides/organizations-and-accounts/billing/monitoring-billing-and-usage-details)
- Fastly Service model: [fastly.com/documentation/reference/api/services/service/](https://www.fastly.com/documentation/reference/api/services/service/)
- Fastly Pricing: [fastly.com/pricing](https://www.fastly.com/pricing)
- Fastly Package Entitlements: [fastly.com/package-entitlements/](https://www.fastly.com/package-entitlements/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
