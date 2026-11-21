# Tigris & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Tigris Data Inc.  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Tigris public pricing page and `pricing.md`; Tigris docs (billing, organizations, bucket locations, storage tiers, S3 API compatibility, Partner Integrations API); Tigris blog (billing on Prometheus, Fly.io billing launch); Fly.io Tigris and pricing docs  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 11 Present, 12 Deviation, 4 Missing Mandatory, 12 Missing Conditional, 1 Missing Recommended, 17 N/A

---

## Executive Summary

Tigris is a globally distributed, S3-compatible object storage service. Buckets default to a Global location that places data near where it is accessed, with Multi-region, Dual-region, and Single-region options. Pricing is simple and fully published: storage per GB-month by tier and location type, Class A and Class B requests per 1,000, object notifications per 1,000, retrieval fees on two tiers, and zero egress. Customers buy direct from Tigris Data Inc. or through Fly.io, which passes Tigris charges through on the Fly invoice.

**Public billing documentation is thin.** Tigris documents a dashboard Usage page, monthly invoices and receipts, and nothing else a customer can pull programmatically. There is no billing export, cost API, CSV download, or customer-facing metrics endpoint, and the S3 bucket metrics and inventory APIs return 501. The only usage and invoice API is the Partner Integrations API, which is partner-only and whose endpoint reference pages returned 404 on November 17, 2026, so its fields are not public. Several Tigris doc pages cited by search engines also returned 404. This analysis therefore assesses what Tigris's billing model and data model could supply, not a dataset that exists today.

On that basis, of the 21 Mandatory columns, 10 map directly, 7 need derivation, and 4 are missing. **2 of the 4 missing Mandatory columns are substantive.** BilledCost and EffectiveCost exist only as invoice totals; the free tier (5 GB Standard storage, 10,000 Class A and 100,000 Class B requests per month) and any credits are applied at the organization-month level and would have to be allocated back to bucket-by-day rows. ListCost and ContractedCost are a price-sheet join once usage exists at meter grain.

The encouraging part: Tigris already computes billing from per-organization, per-bucket Prometheus metrics (request counts, storage by tier), and already produces daily per-organization usage for partners. The data exists inside Tigris; it is not exposed to customers.

**Recommendation:** Publish a daily FOCUS export per organization with one row per bucket × meter (storage tier and location type, Class A requests, Class B requests, retrieval, notifications) × day, carrying bucket name, location, bucket tags, and priced ListCost, BilledCost, and EffectiveCost, with free-tier allocation and Credit and Tax rows that reconcile to the invoice. Deliver it as a dashboard download and an API, and extend the same export to the Partner Integrations API so Fly.io can pass it through.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

- **Dashboard Usage page:** Current and historical charges, plus downloadable past invoices and receipts. Shows storage size and object count per bucket. No documented line-item or CSV export.
- **Monthly invoice:** Calendar-month, USD, issued at period end and auto-charged. Stripe is the billing system. Invoice line structure is not documented.
- **Partner Integrations API** (`mgmt.storage.dev`): Get Account Invoice (consolidated monthly per partner), Get Invoice (monthly per organization), and Get Usage (daily per organization). Partner-only; field names are not public; per-bucket breakdown is not documented.
- **Internal metering:** Per Tigris's September 23, 2025 engineering blog, charges are computed from Prometheus metrics in VictoriaMetrics, per organization and per bucket, including request counts and storage tier. No customer metrics endpoint is documented.
- **Fly.io path:** Buckets created through Fly appear on the regular Fly bill under the Fly organization; there is no separate Tigris invoice or account.

Key characteristics:

- **Storage tiers (single-region / multi-region, per GB-month):** Standard $0.02 / $0.025; Infrequent Access $0.01 / $0.015 (30-day minimum, $0.01/GB retrieval); Archive $0.004 / $0.006 (90-day minimum, about one-hour restore); Archive Instant Retrieval $0.004 / $0.006 (90-day minimum, $0.03/GB retrieval). S3 storage classes `STANDARD`, `STANDARD_IA`, `GLACIER`, `GLACIER_IR`.
- **Location types:** Global (default, $0.02/GB-month Standard, no per-region charge), Multi-region (USA or EUR), Dual-region (billed at single-region price per region), Single-region. Region codes `sjc`, `ord`, `iad`, `ams`, `fra`. Price varies by location type, not by region.
- **Requests:** Class A (PUT, COPY, POST, LIST) $0.005 per 1,000 single-region, $0.01 per 1,000 multi-region; Class B (GET, SELECT, others) $0.0005 per 1,000. DELETE, CANCEL, and unauthorized requests are free.
- **Other meters:** Object notifications $0.01 per 1,000 events. Egress is free. No fees for forks, snapshots, or lifecycle rules.
- **Free tier:** 5 GB Standard storage, 10,000 Class A, and 100,000 Class B requests per month.
- **Enterprise:** "Custom" pricing by contacting sales. No committed-use, reserved, or prepaid terms are published.
- **Hierarchy:** User, Organization (billed separately, roles Owner/Admin/Member), Bucket. No projects or sub-accounts.
- **Tags:** S3 `PutBucketTagging` and `PutObjectTagging` are supported. The console has no tag UI, and nothing indicates tags reach billing.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Because Tigris has no customer billing dataset, this analysis marks a column Present when the value exists in a customer-visible Tigris surface (dashboard, invoice, organization settings) and maps one-to-one, and Deviation when it exists but must be derived or re-cut. Missing means no documented customer surface carries it.

Tigris publishes no commitment, reservation, or prepaid program, so the CommitmentDiscount and CapacityReservation families are N/A. Organizations have no sub-account layer, so the SubAccount family is N/A. Pricing and billing are USD only, so the PricingCurrency family is N/A. Zones are not exposed, so AvailabilityZone is N/A. Tigris does deploy into named regions and supports bucket tags, so RegionId, RegionName, and Tags apply. Feature levels below follow the FOCUS v1.2 Content Constraints, spot-checked against the live spec on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Tigris source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice totals only; free tier and credits applied at organization-month level, never at bucket or day grain | Missing: Mandatory |
| EffectiveCost | Mandatory | No amortization needed (no published commitments), but requires the same free-tier and credit allocation as BilledCost | Missing: Mandatory |
| ListCost | Mandatory | Not in data; public price sheet × usage by tier, location type, and request class | Missing: Mandatory |
| ContractedCost | Mandatory | Not in data; = ListCost for self-serve, custom Enterprise rate otherwise | Missing: Mandatory |
| BillingAccountId | Mandatory | Tigris organization ID; Fly organization ID for Fly-provisioned buckets | Present |
| BillingAccountName | Mandatory | Organization name | Present |
| BillingCurrency | Mandatory | "USD" | Present |
| BillingPeriodStart | Mandatory | First day of calendar month | Present |
| BillingPeriodEnd | Mandatory | First day of following month (exclusive) | Present |
| ChargePeriodStart | Mandatory | Monthly only for customers; daily exists in partner Get Usage and internal metrics | Deviation |
| ChargePeriodEnd | Mandatory | As above | Deviation |
| ChargeDescription | Mandatory | Invoice line text (undocumented); derive from meter, tier, and location (e.g., "Standard storage · single-region · iad") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for metered lines; "Credit" for free tier and promotional credits; "Tax" where applied | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued invoices | Present |
| InvoiceIssuerName | Mandatory | "Tigris Data Inc." for direct; "Fly.io" for Fly-provisioned buckets | Present |
| ProviderName | Mandatory (dep. v1.3) | "Tigris" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Tigris" | Present |
| ServiceName | Mandatory | "Tigris Object Storage" | Present |
| ServiceCategory | Mandatory | Not emitted; constant "Storage" | Deviation |
| PricingQuantity | Mandatory | GB-months, 1,000-request blocks, GB retrieved, 1,000 notifications; free tier makes storage and requests tiered, so compute against the rate basis | Deviation |
| PricingUnit | Mandatory | Not emitted; normalize to "GB-Months", "1000 Requests", "GB", "1000 Events" | Deviation |
| ConsumedQuantity | Conditional | Storage bytes by tier and request counts exist in internal metrics; dashboard shows storage size per bucket | Deviation |
| ConsumedUnit | Conditional | Implied; emit "GB-Months", "Requests", "GB", "Events" | Deviation |
| ListUnitPrice | Conditional | Not in data; public price sheet | Missing: Conditional |
| ContractedUnitPrice | Conditional | Not in data; = ListUnitPrice for self-serve, Enterprise contract otherwise | Missing: Conditional |
| PricingCategory | Conditional | Derive: "Standard" for all metered usage | Deviation |
| BillingAccountType | Conditional | Not emitted; "Organization" (direct) or "Fly Organization" (via Fly) | Deviation |
| SubAccountId | Conditional | N/A: no project or sub-account layer under an organization | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | Not on any billing surface; bucket is the natural resource (bucket names are unique) | Missing: Conditional |
| ResourceName | Conditional | Not on any billing surface; bucket name | Missing: Conditional |
| ResourceType | Conditional | Not emitted; "Bucket" | Missing: Conditional |
| SkuId | Conditional | Not exposed; tier × location type × meter forms a small SKU set | Missing: Conditional |
| Tags | Conditional | S3 bucket tags exist; not carried into billing | Missing: Conditional |
| PricingCurrency | Conditional | N/A: priced and billed in USD only | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Not exposed; "Storage", "Class A Requests", "Class B Requests", "Retrieval", "Object Notifications" | Missing: Conditional |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed for tier, location type, and minimum storage duration | Missing: Conditional |
| RegionId | Conditional | Not on billing surfaces; bucket location config (`sjc`, `ord`, `iad`, `ams`, `fra`, or Global/Multi-region) | Missing: Conditional |
| RegionName | Conditional | Not on billing surfaces | Missing: Conditional |
| CommitmentDiscountId | Conditional | N/A: no published commitment program | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number on downloadable invoices | Present |
| ChargeFrequency | Recommended | Derive: "Usage-Based" | Deviation |
| ServiceSubcategory | Recommended | Not emitted; "Object Storage" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: zones are not exposed | N/A |

**Tally:** 11 Present, 12 Deviation, 4 Missing Mandatory, 12 Missing Conditional, 1 Missing Recommended, 17 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Organization as billing account, USD-only calendar-month billing, invoice numbers, a single service with a small and fully published price sheet, and no commitment or reservation mechanics to model. Tigris's pricing is among the easiest in this library to express in FOCUS.

**Substantive (2 of 4 Mandatory gaps):**

- **BilledCost.** Customers get invoice totals only. Row-level BilledCost requires pricing each bucket-by-meter-by-day row, allocating the monthly free tier across rows, and emitting Credit and Tax rows so the sum reconciles to the invoice.
- **EffectiveCost.** With no published commitments, EffectiveCost equals BilledCost on usage rows, but it inherits the same free-tier and credit allocation. If Enterprise contracts include prepaid or committed spend, amortization is added.

**Trivial (2 of 4 Mandatory gaps):**

- **ListCost.** Join the public price sheet by tier, location type, and request class. Storage and requests are tiered by the free allowance, so compute against the rate basis rather than copying consumption.
- **ContractedCost.** Equals ListCost for self-serve; join the Enterprise contract rate otherwise.

**Substantive, beyond the column table:**

- **No customer dataset.** Every column above is a design target, not a delivered field. The first deliverable is an export of any shape.
- **No bucket grain.** Billing is computed per bucket internally but surfaced per organization. Without bucket rows there is no showback, chargeback, or tag-based allocation.
- **Fly.io pass-through.** Fly-provisioned usage is billed by Fly under a Fly organization. A Tigris FOCUS export only reaches those customers if Fly carries it, which depends on the Partner Integrations API exposing it.
- **Global location.** Global buckets have no fixed region. RegionId needs a rule (null, or a synthetic "global" value) and SkuPriceDetails must carry the location type that actually drives price.

### 1.5 Deviations to Fix

**PricingQuantity, PricingUnit, ConsumedQuantity, ConsumedUnit:** Emit storage as GB-Months per tier and location type, requests in their native counts with PricingUnit "1000 Requests", retrieval in GB, and notifications as "1000 Events". Keep minimum-duration charges for early-deleted Infrequent Access and Archive objects as their own rows.

**ChargePeriodStart and ChargePeriodEnd:** Move from monthly to daily, which Tigris already produces for partners.

**ServiceCategory, ChargeCategory, ChargeFrequency, PricingCategory, ChargeDescription, BillingAccountType:** Derive as shown in the table.

**Already right:** Organization identity, USD currency, calendar-month billing periods, and invoice numbers map cleanly.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is in release candidate with ratification scheduled for December 3, 2026. The Invoice Detail dataset (v1.4) suits the Fly.io consolidated-invoice path.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (no sub-accounts, commitments, reservations, zones, or alternate currencies) and the RegionId rule for Global buckets.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one month of internal per-bucket metrics for a test organization with the matching invoice. Hand-build a FOCUS file, run it through the Validator, and settle the free-tier allocation rule and the Global-bucket RegionId rule.

**Phase 1: Export.** Ship a daily per-organization CSV and API at bucket × meter × day grain with BillingAccount, ChargePeriod, Service, Resource, Region, Sku, Pricing, and Consumed columns. This is the prerequisite for everything else.

**Phase 2: Close Mandatory gaps.** Price each row for ListCost and ListUnitPrice; join Enterprise rates for ContractedCost and ContractedUnitPrice; allocate the free tier and credits for BilledCost and EffectiveCost; emit Credit and Tax rows that reconcile to the invoice.

**Phase 3: Fill Conditional and Recommended.** Carry S3 bucket tags into Tags as key-value pairs; add SkuPriceId, SkuPriceDetails, and ServiceSubcategory. Expose the same export through the Partner Integrations API for Fly.io.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add recency and completeness metadata (v1.3) and the Invoice Detail dataset (v1.4); certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **Today:** Monthly organization-level spend from invoices; manual per-bucket storage trending from the dashboard.
- **After Phase 1:** Per-bucket usage trending, request-pattern anomaly detection, and tier-mix analysis.
- **After Phase 2:** Invoice reconciliation, bucket-level showback and chargeback in dollars, and actuals-based budgeting and forecasting.
- **After Phase 3:** Tag-based allocation, cross-provider object storage unit cost comparison (Tigris vs. S3, R2, GCS), and Fly.io customers seeing Tigris spend in FOCUS.
- **Out of scope:** Commitment utilization, capacity reservation management, availability zone analysis, and sub-account rollups.

---

## Part 3: Immediate Next Steps

1. Follow up with the Tigris contact from KubeCon NA 2026 to identify the owner of billing and the Partner Integrations API.
2. Ask Tigris to confirm whether any customer usage export exists that the public docs do not describe, and to share the Get Usage and Get Invoice field schemas.
3. Confirm the invoicing legal entity, tax handling, credit programs, and whether Enterprise contracts include committed spend.
4. Build a v1.2 sample from one month of per-bucket metrics and run it through the FOCUS Validator.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Published prices, tiers, location types, region codes, free-tier allowances, and zero egress, from the Tigris pricing page, `pricing.md`, and docs.
- **High:** No customer billing export, cost API, or metrics endpoint is publicly documented, and S3 bucket metrics and inventory APIs return 501.
- **High:** Fly-provisioned Tigris usage is billed on the Fly invoice, per Fly.io docs.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints; spot-checked against the live spec on November 17, 2026, and v1.4 remains the latest ratified version.
- **Moderate:** Billing is computed from per-organization, per-bucket Prometheus metrics, per Tigris's own engineering blog rather than product docs.
- **Moderate:** "Tigris Data Inc." as InvoiceIssuerName; the service terms page returned 404 and the name rests on a search-result snippet.
- **Moderate:** No commitment program. None is published, but Enterprise pricing is "custom"; if contracts include committed spend, the seven CommitmentDiscount columns become applicable.
- **Low:** Partner Integrations API fields and grain; endpoint reference pages returned 404 on November 17, 2026.
- **Low:** Infrequent Access minimum duration (current pages say 30 days; an archived snippet said 90), the "$50 free credits" offer, tax handling, and invoice line structure, none of which could be confirmed from live pages.

---

## Sources

- Tigris Pricing: [tigrisdata.com/pricing](https://www.tigrisdata.com/pricing/) · [pricing.md](https://www.tigrisdata.com/pricing.md)
- Tigris Billing: [tigrisdata.com/docs/account-management/billing](https://www.tigrisdata.com/docs/account-management/billing/)
- Tigris Organizations: [tigrisdata.com/docs/account-management/organizations](https://www.tigrisdata.com/docs/account-management/organizations/)
- Tigris Bucket Locations: [tigrisdata.com/docs/buckets/locations](https://www.tigrisdata.com/docs/buckets/locations/)
- Tigris Storage Tiers: [tigrisdata.com/docs/objects/tiers](https://www.tigrisdata.com/docs/objects/tiers/)
- Tigris S3 API Compatibility: [tigrisdata.com/docs/api/s3](https://www.tigrisdata.com/docs/api/s3/)
- Tigris Partner Integrations: [tigrisdata.com/docs/partner-integrations](https://tigrisdata.com/docs/partner-integrations/)
- Tigris blog, billing on Prometheus (Sept. 23, 2025): [tigrisdata.com/blog/billing-prometheus](https://www.tigrisdata.com/blog/billing-prometheus/)
- Tigris blog, enabling billing in July: [tigrisdata.com/blog/enabling-billing-for-tigris-in-july](https://www.tigrisdata.com/blog/enabling-billing-for-tigris-in-july/)
- Fly.io Tigris docs: [docs.fly.io/tigris](https://docs.fly.io/tigris) · [Fly.io Pricing](https://docs.fly.io/about/pricing/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
