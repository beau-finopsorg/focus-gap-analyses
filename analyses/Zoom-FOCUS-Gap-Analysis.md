# Zoom & FOCUS: Data Generator Gap Analysis

*Analysis run: November 18, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Zoom Communications, Inc.  
**Prepared:** November 18, 2026  
**Source:** Zoom Billing API (`GET /accounts/{accountId}/billing/invoices`, `GET /accounts/{accountId}/billing/invoices/{invoiceId}`, `GET /accounts/{accountId}/billing/usage`, `GET /accounts/{accountId}/billing/information`); Zoom Phone reports API (`GET /phone/reports/call_charges`, plus SMS and fax charge reports); Zoom pricing page  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 9 Present, 20 Deviation, 3 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 17 N/A

---

## Executive Summary

Zoom sells per-license subscriptions (Zoom Workplace Basic, Pro, Business, Business Plus, Enterprise) billed monthly or annually in advance, plus add-ons (Large Meetings, Webinars, Sessions/Events, Rooms, Cloud Storage, Contact Center, Zoom Phone) and metered usage (Zoom Phone pay-as-you-go calling, SMS, and fax; Video SDK minutes above the included allowance). Large customers run a master account with sub-accounts, and Zoom also sells through resellers and partners.

Zoom is ahead of most SaaS vendors in this library on programmatic billing access. The invoice detail endpoint returns line items with `charge_name`, `start_date`, `end_date`, `quantity`, `total_amount`, and `tax_amount`, and the Zoom Phone call charges report carries per-call `rate`, `charge_mode`, `currency`, and `total_charge`. What it lacks is price context and allocation detail: no unit or list price on invoice lines, no unit of measure, no SKU or price ID for direct customers, no per-user or per-resource attribution, and plan usage that reports counts and storage as strings with no cost attached. The invoice APIs are also heavily rate limited (invoice detail: one request every 30 minutes, 100 per day per account).

All 21 Mandatory columns except three have a documented source or a direct derivation. One of the three gaps is substantive. **EffectiveCost** requires amortizing annual prepaid licenses and add-ons across their term; invoice lines carry the billed amount only. **ListCost** and **PricingUnit** are plumbing: Zoom owns its price book and units. **BilledCost** is present but needs tax split out of each line into its own Tax rows.

Zoom is also a FOCUS consumer: its FinOps team uses FOCUS to consolidate its own multi-cloud and data-center cost data. That makes the ask familiar to the people Zoom would staff it with.

**Recommendation:** Publish a monthly FOCUS export per billing account (and per sub-account under a master), built from the invoice line items Zoom already exposes. One Purchase row per license subscription and add-on per term with list and contracted unit prices, one Usage row per metered product (Phone calling, SMS, fax, Video SDK minutes) per charge period, separate Tax rows, and Credit rows for promotions and service credits. Add SkuId and SkuPriceId from the plan catalog and amortize prepaid terms for EffectiveCost.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

Zoom's public billing surface, all under `https://api.zoom.us/v2` and available on Pro or higher plans (pass `me` as `accountId` for your own account):

- **`GET /accounts/{accountId}/billing/invoices`** (`from`, `to`; range up to one year, within the past three years): top-level `currency` and `invoices[]` of `{id, invoice_number, invoice_date, due_date, target_date, status, total_amount, tax_amount, balance}`. Rate limit HEAVY.
- **`GET /accounts/{accountId}/billing/invoices/{invoiceId}`**: the same header fields plus `invoice_items[]` of `{charge_name, charge_number, charge_type, start_date, end_date, quantity, total_amount, tax_amount, partner_sku, purchase_order_number}`. `charge_type` example: "Billed on master". No unit price, list price, or unit of measure. One request every 30 minutes, 100 per day per account.
- **`GET /accounts/{accountId}/billing/usage`**: plan usage per subscription (`plan_base`, `plan_recording`, `plan_webinar`, `plan_phone_*`, `plan_zoom_video_management`, and others), each with `zr_sub_refer_id`. Seat plans report `hosts`, `usage`, `pending`; storage plans report `free_storage`, `plan_storage`, `plan_storage_usage`, `plan_storage_exceed` as strings (e.g., "10 GB"). No cost or price fields.
- **`GET /accounts/{accountId}/billing/information`** and **`GET /accounts/{accountId}/plans`**: plan `type`, `hosts`, `status` (active, cancelled, expired), `service_effective_date`, `next_invoice_date`. Video SDK plans carry `overage_price` and `included_minutes`.
- **`GET /phone/reports/call_charges`** (and `sms_charges`, `fax_charges`): monthly per-call charge records with duration in minutes, `charge_mode` (per_min, per_call, per_call_per_min, and variants), `rate`, `currency`, `total_charge`, and `billing_number`; filterable by billing account.
- **Master account APIs:** Zoom states that only approved partners may use master account APIs to manage sub-accounts' billing. Sub-account invoice reports exist (`/accounts/billing/invoice_reports`) under the `billing:master` scope.

Key characteristics:

- **License subscriptions:** Workplace Pro and Business per user, monthly or annual (annual discounted); Enterprise and Business Plus through sales. Pro and Business include 10 GB cloud recording per license; Enterprise includes unlimited.
- **Add-ons:** Cloud storage blocks, Large Meetings, Webinars, Sessions, Rooms, Contact Center, Zoom Phone (metered, regional unlimited, global select).
- **Metered usage:** Zoom Phone pay-as-you-go calling billed per minute or per call by destination; SMS and fax charges; Video SDK minutes above `included_minutes` at `overage_price`.
- **Hierarchy:** Master account with sub-accounts; charges can be billed on master or on each sub-account.
- **Channels:** Direct self-serve, direct sales, and partners/resellers (`partner_sku` and `purchase_order_number` support reseller billing).
- **No tags, no cloud regions:** Phone rates vary by calling destination, not by service region.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Zoom documents no commitment-based discounts: annual billing is a subscription term, and plan allowances (cloud storage, Video SDK minutes) are included quantities, not drawn-down commitments. The CommitmentDiscount family is therefore N/A, as are capacity reservations, region columns, alternate pricing currencies, and tags. Those columns should exist as null. Master accounts with sub-accounts trigger the SubAccount columns. Feature levels follow the FOCUS v1.2 Content Constraints, consistent with the live-spec check performed for this library on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Zoom source | Status |
|---|---|---|---|
| BilledCost | Mandatory | `invoice_items[].total_amount`; split `tax_amount` into separate Tax rows | Deviation |
| EffectiveCost | Mandatory | Not available: needs amortization of annual prepaid licenses and add-ons | Missing: Mandatory |
| ListCost | Mandatory | Not exposed; join Zoom price book × PricingQuantity | Missing: Mandatory |
| ContractedCost | Mandatory | Derive from pre-tax `total_amount` where no credits are netted into the line | Deviation |
| BillingAccountId | Mandatory | `accountId` | Present |
| BillingAccountName | Mandatory | Not on invoice; join account name from the Accounts API | Deviation |
| BillingCurrency | Mandatory | Invoice `currency` | Present |
| BillingPeriodStart | Mandatory | Not explicit; derive from `target_date` and the subscription cycle | Deviation |
| BillingPeriodEnd | Mandatory | Not explicit; derive as above | Deviation |
| ChargePeriodStart | Mandatory | `invoice_items[].start_date` (date only; convert to ISO 8601 datetime) | Deviation |
| ChargePeriodEnd | Mandatory | `invoice_items[].end_date` (date only; convert and make exclusive) | Deviation |
| ChargeDescription | Mandatory | `invoice_items[].charge_name` | Present |
| ChargeCategory | Mandatory | `charge_type` ("Billed on master") is not a FOCUS value; derive "Purchase", "Usage", "Tax", "Credit" | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued charges | Present |
| InvoiceIssuerName | Mandatory | "Zoom Communications, Inc."; reseller name for partner-billed accounts | Present |
| ProviderName | Mandatory (dep. v1.3) | "Zoom" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Zoom" | Present |
| ServiceName | Mandatory | Derive from `charge_name` and plan type (e.g., "Zoom Workplace", "Zoom Phone", "Zoom Webinars", "Zoom Rooms", "Zoom Contact Center", "Zoom Video SDK") | Deviation |
| ServiceCategory | Mandatory | Derive: "Business Applications" for Workplace, Phone, Webinars, Events, Rooms, Contact Center; "Storage" for cloud storage add-ons; "Developer Tools" for Video SDK; "AI and Machine Learning" for paid AI add-ons | Deviation |
| PricingQuantity | Mandatory | `invoice_items[].quantity` (licenses); Phone minutes or calls from charge reports | Present |
| PricingUnit | Mandatory | Not exposed; "Licenses", "Minutes", "Calls", "Messages", "GB" | Missing: Mandatory |
| ConsumedQuantity | Conditional | `/billing/usage` `usage`, `plan_storage_usage` (strings); Phone call duration | Deviation |
| ConsumedUnit | Conditional | Embedded in strings (e.g., "10 GB"); parse and normalize | Deviation |
| ListUnitPrice | Conditional | Not exposed; public pricing page for self-serve plans | Missing: Conditional |
| ContractedUnitPrice | Conditional | Derive `total_amount` ÷ `quantity` for flat-rate licenses; Phone `rate` for calls | Deviation |
| PricingCategory | Conditional | Derive: "Standard" (no commitment pricing) | Deviation |
| BillingAccountType | Conditional | Derive from master, sub-account, direct, or partner relationship | Deviation |
| SubAccountId | Conditional | Sub-account `accountId`; master-billed lines carry `charge_type` only | Deviation |
| SubAccountName | Conditional | Join sub-account name from master account API (approved partners only) | Deviation |
| SubAccountType | Conditional | Not exposed ("Sub Account") | Missing: Conditional |
| ResourceId | Conditional | Not exposed; candidates are licensed user, phone number, Room, and SDK app IDs | Missing: Conditional |
| ResourceName | Conditional | Not exposed | Missing: Conditional |
| ResourceType | Conditional | Not exposed | Missing: Conditional |
| SkuId | Conditional | `partner_sku` (partner-billed only); `charge_number` is a charge ID, not a SKU | Deviation |
| Tags | Conditional | N/A: no billing tags or labels | N/A |
| PricingCurrency | Conditional | N/A: priced in billing currency | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | `plan_*` usage node names; Phone `charge_mode` | Deviation |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed for monthly vs. annual terms, Phone destination rates, Video SDK included minutes and overage price | Missing: Conditional |
| RegionId | Conditional | N/A: nothing priced by service region | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: no commitment discounts documented | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | `invoice_number` (or `id`) | Present |
| ChargeFrequency | Recommended | Derive: "Recurring" for licenses and add-ons; "Usage-Based" for Phone, SMS, fax, and Video SDK overage | Deviation |
| ServiceSubcategory | Recommended | Not exposed; map each product to an allowed v1.2 ServiceSubcategory value | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: no zones | N/A |

**Tally:** 9 Present, 20 Deviation, 3 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 17 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Line-item invoices with service periods, quantities, amounts, and per-line tax; per-call Phone charges with rates and currency; plan and usage state per subscription; a master and sub-account hierarchy; and stable invoice numbers. All exposed through a documented, authenticated API.

**Substantive (1 of 3 Mandatory gaps):**

- **EffectiveCost.** Annual licenses and add-ons are billed in advance. EffectiveCost requires amortizing each purchase across its service term (the `start_date` and `end_date` on the line make this mechanical) and allocating any negotiated Enterprise discounts or service credits back to the charges they offset.

**Trivial (2 of 3 Mandatory gaps):**

- **ListCost.** Zoom owns the price book; join list unit price × PricingQuantity. Self-serve prices are public.
- **PricingUnit.** Zoom knows the unit for every charge; add it to the invoice line. For Phone calling, PricingQuantity and PricingUnit depend on `charge_mode`: per-minute charges price on minutes, per-call charges on calls, and "after T duration" modes need computation against the rate basis, not a copy of call duration.

**Substantive, beyond the column table:**

- **No allocation dimension.** Invoice lines are per subscription, not per user, phone number, or Room. Customers cannot charge back Zoom spend below the sub-account level from billing data. The Phone charges report is the one exception.
- **Usage without cost.** `/billing/usage` reports seat counts and storage consumption with no price, and storage values are strings with embedded units.
- **Rate limits.** Invoice detail allows one request every 30 minutes and 100 per day per account. A tenant with dozens of sub-accounts and monthly invoices cannot backfill quickly.
- **Partner gating.** Master account billing APIs are limited to approved partners, so a large enterprise may not be able to pull sub-account billing without Zoom's involvement.

### 1.5 Deviations to Fix

**BilledCost:** Emit `tax_amount` as its own Tax row per line instead of carrying it alongside `total_amount`, and state whether `total_amount` is pre- or post-tax.

**ChargePeriodStart and ChargePeriodEnd:** Convert dates to ISO 8601 UTC datetimes with an exclusive end.

**BillingPeriodStart and BillingPeriodEnd:** Expose the invoice's billing period explicitly rather than only `target_date`.

**ChargeCategory:** Replace `charge_type` with FOCUS values: "Purchase" for licenses and add-ons, "Usage" for Phone, SMS, fax, and Video SDK overage, "Tax" and "Credit" rows from the invoice.

**ServiceName and ServiceCategory:** Publish a fixed product list mapped as shown in the table.

**ContractedCost and ContractedUnitPrice:** Add unit price to each invoice line so these are read, not divided.

**ConsumedQuantity and ConsumedUnit:** Return storage usage as a number plus unit, and add cost to `/billing/usage`.

**SkuId and SkuMeter:** Populate a SKU for direct customers, not only partners, and expose meter names on invoice lines.

**BillingAccountName, BillingAccountType, SubAccountId, SubAccountName:** Put names and the master or sub-account relationship on every line.

**PricingCategory and ChargeFrequency:** Derive from product type as shown in the table.

**Already right:** Line-level invoice items with service dates and quantities, per-line tax, per-call Phone rates with currency, invoice numbers, and a real account hierarchy.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is a release candidate with ratification scheduled for December 3, 2026. Zoom's invoice header endpoint maps closely to the v1.4 Invoice Detail and billing-period datasets.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (no commitments, reservations, regions, tags, or alternate pricing currencies) and how partner-billed accounts are represented.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one billing period of invoice detail for a self-serve Pro account, a master account with sub-accounts, and a Zoom Phone metered account. Hand-build a FOCUS file and run it through the Validator. Confirm whether `total_amount` includes tax and whether credits are netted into lines.

**Phase 1: Close Mandatory gaps.** Add unit, list unit price, and contracted unit price to invoice lines. Amortize annual licenses and add-ons for EffectiveCost. Emit Tax and Credit rows so BilledCost reconciles to each invoice.

**Phase 2: Fix deviations.** Map ChargeCategory, ServiceName, ServiceCategory, ChargeFrequency, and PricingCategory; convert charge dates to datetimes; expose billing periods; join names onto every row; fold Phone call charges into the same dataset with PricingQuantity computed per `charge_mode`.

**Phase 3: Allocation and Conditional columns.** Add SubAccountType; ResourceId, ResourceName, and ResourceType (user, phone number, Room, SDK app); SkuId, SkuPriceId, and SkuPriceDetails for all customers; and ServiceSubcategory. Relax invoice API rate limits or deliver the dataset as a scheduled export.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Invoice Detail dataset; certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **After Phase 1:** Invoice reconciliation, amortized spend reporting, and actuals-based budgeting and forecasting.
- **After Phase 2:** Spend by service category across providers, Phone usage cost trending, and license-versus-usage mix analysis.
- **After Phase 3:** Chargeback and showback by sub-account, user, or Room; license utilization against cost; and anomaly detection on Phone and Video SDK overages.
- **Out of scope:** Commitment discount utilization, capacity reservation management, region-based analysis, and tag-based allocation (unless Zoom adds labels).

---

## Part 3: Immediate Next Steps

1. Reach Zoom's FinOps team, already a FOCUS consumer, to identify the owner of billing data and the Billing API.
2. Request a sample invoice detail payload (self-serve, master with sub-accounts, and Phone metered) to confirm tax treatment, credit handling, and `charge_type` values.
3. Confirm the scope of the partner restriction on master account billing APIs for direct enterprise customers.
4. Build a v1.2 sample from one billing period and run it through the FOCUS Validator.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Invoice list and detail fields, plan usage fields, scopes, rate limits, and the approved-partner restriction come from Zoom's Master Account Billing API reference.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints, and "Business Applications" is a valid ServiceCategory value.
- **Moderate:** Zoom Phone call charges fields (`charge_mode`, `rate`, `currency`, `total_charge`) come from secondary mirrors of the Zoom Phone API reference; the official page could not be loaded.
- **Moderate:** Whether `total_amount` on invoice lines is pre- or post-tax, and whether discounts and credits are netted into lines. Undocumented; this drives the BilledCost and ContractedCost classifications.
- **Moderate:** Commitment discount family as N/A. If Enterprise contracts include prepaid credit pools or drawn-down minute commitments, these seven columns become applicable.
- **Moderate:** Zoom as a FOCUS consumer rests on a third-party vendor blog, not a Zoom statement. No public Zoom statement on producing FOCUS data was found.
- **Low:** Pricing. Workplace Pro at $14.16 and Business at $18.33 per user per month billed annually ($16.99 and $21.99 monthly) come from third-party summaries as of October 2026, not Zoom's own page, and are not used in any classification.
- **Low:** Multi-currency billing. Zoom bills in several currencies; whether Phone charge records can differ from invoice currency is unconfirmed.

---

## Sources

- Zoom Master Account Billing API reference: [developers.zoom.us/docs/api/billing/ma/](https://developers.zoom.us/docs/api/billing/ma/)
- Zoom Developer Forum, invoices for sub-accounts: [devforum.zoom.us/t/invoice-for-sub-account/76892](https://devforum.zoom.us/t/invoice-for-sub-account/76892)
- Zoom Phone API, Get call charges usage report (mirror): [developers.qodex.ai](https://developers.qodex.ai/zoom-public/zoom-phone-api/phone-reports-call_charges/get-call-charges-usage-report)
- Zoom Community, Charge and Rate in CallLog endpoint: [community.zoom.com](https://community.zoom.com/t5/Zoom-Phone-System/Charge-and-Rate-in-CallLog-Endpoint/m-p/50283)
- Zoom pricing summary 2026 (third party): [eesel.ai/blog/zoom-pricing](https://www.eesel.ai/blog/zoom-pricing)
- PointFive, FinOps Foundation's FOCUS initiative: [pointfive.co](https://www.pointfive.co/blog/finops-foundations-focus-initiative)
- FOCUS ServiceCategory (v1.2): [focus.finops.org](https://focus.finops.org/docs/specification/v1-2/columns/service-category/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
