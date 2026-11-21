# Twilio & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Twilio Inc.  
**Prepared:** November 17, 2026  
**Origin:** FOCUS data generator landscape and readiness list  
**Source:** Public Twilio documentation only: Usage Records API reference; Subaccounts API reference; Messaging Pricing API (v1) and Voice Pricing API (v2); BulkExport docs; call log usage discrepancy guide; Twilio pricing page  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 14 Present, 12 Deviation, 3 Missing Mandatory, 17 Missing Conditional, 2 Missing Recommended, 9 N/A

---

## Executive Summary

Twilio sells usage-priced communications APIs: Programmable Voice, Messaging (SMS, MMS, RCS, WhatsApp), phone numbers, Verify, Lookup, Video, Studio, TaskRouter, and roughly 150 other metered usage categories. Pricing is pay-as-you-go with "discounts as you scale," and rates vary by destination country, carrier, and sending number type. Usage from up to 1,000 subaccounts rolls up to one main account and one balance.

Twilio already publishes a priced usage API, which most SaaS vendors do not. The **Usage Records API** returns, per account and per usage category, a daily (or monthly or yearly) record with `price`, `price_unit`, `usage`, `usage_unit`, `count`, and `description`, and it can be called per subaccount. Separately, the **Pricing API** exposes both a `base_price` (retail) and a `current_price` that "accounts for any volume or custom price discounts," per country, carrier, and number type.

**Public billing documentation is thin where FOCUS needs it most.** No invoice API, invoice field list, or cost export is documented. Twilio does not say whether Usage Records `price` is list or net of discounts, promotional credits, and contract terms. Its own reference warns that "the sum of the `Price` of all UsageRecords may not be equal to the `Price` of `TotalPrice`," so the usage data does not reconcile to the bill by design. Twilio help center billing articles did not render to an automated fetch, and no public page documents committed-spend contracts, tax lines, the invoicing entity, or billing currencies beyond the `usd`, `eur`, and `jpy` examples.

Of the 21 Mandatory FOCUS columns, 18 have a source and 3 are missing. Two are substantive: **EffectiveCost**, because promotional credits, prepaid balances, and negotiated contracts are not reflected in any documented row-level surface; and **ListCost**, because a usage category such as `sms-outbound-longcode` aggregates every destination country and carrier at different rates, so no rate can be joined at that grain. **ContractedCost** is plumbing if `price` already carries the account's discounted rate.

**Recommendation:** Build a monthly FOCUS export per main account from the systems that already feed Usage Records and the Pricing API: one Usage row per subaccount × usage category × destination country × day, with `base_price` and `current_price` joined as ListUnitPrice and ContractedUnitPrice, Purchase rows for phone number rentals and registration fees, Tax rows, and Credit rows for promotional credits, so that BilledCost reconciles to the invoice.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

- **Usage Records API:** `GET /2010-04-01/Accounts/{AccountSid}/Usage/Records`, with subresources `Daily`, `Monthly`, `Yearly`, `AllTime`, `Today`, `Yesterday`, `ThisMonth`, and `LastMonth`. Parameters: `Category`, `StartDate`, `EndDate` (GMT `YYYY-MM-DD` or offsets such as `-30days`), and `IncludeSubaccounts` (default `true`). Fields: `account_sid`, `api_version`, `as_of`, `category`, `count`, `count_unit`, `description`, `start_date`, `end_date` (inclusive), `price`, `price_unit`, `usage`, `usage_unit`, `uri`, `subresource_uris`. Finest grain is daily. Example values: `"price": "2192.84855"`, `"price_unit": "usd"`; numeric fields arrive as strings.
- **Usage categories:** About 158 categories across Voice, SMS and MMS, RCS, WhatsApp, phone numbers, Lookup, trunking, Sync, TaskRouter, Video, Verify, Studio, and others, plus roll-ups such as `calls`, `sms`, and `totalprice`. Naming is inconsistent (`Usage-RCS-Messages` in mixed case; a published typo, `call-progess-events`).
- **Pricing API:** Messaging v1 (`pricing.twilio.com/v1/Messaging/Countries/{IsoCountry}`) returns outbound prices per carrier (MCC/MNC) and number type and inbound prices per number type. Voice v2 returns per-minute prices by origination and destination prefix and inbound by number type. Every price carries `base_price` ("the retail price") and `current_price` ("accounts for any volume or custom price discounts").
- **Subaccounts API:** One level of subaccounts under a main account, each with `owner_account_sid` and a friendly name, up to 1,000 by default. "Twilio bills all subaccount usage directly to your main account. You'll have one Twilio balance for all subaccounts."
- **BulkExport:** Daily GZIP JSON dumps of Messages, Calls, Conferences, and Participants, deleted after seven days, US1 only. It is an activity log, not a cost export, and "Price data may not be present for every Message record."
- **Invoices:** Not documented publicly. No invoice API, invoice line schema, or billing export is published.

Key characteristics:

- **Pricing:** Pay-as-you-go, per message, per minute, per lookup, per number per month, with volume discounts and custom (negotiated) pricing reflected in `current_price`. Segment and other enterprise products are sales-quoted.
- **Rounding:** The reconciliation guide defines `usage` for calls as billed minutes per call, rounded under the pricing model's minimums; failed and busy calls are not billed.
- **Currency:** `price_unit` is "the currency associated with the account," with `usd`, `eur`, and `jpy` as documented examples.
- **Regions:** Twilio operates US1, IE1, and AU1 processing regions; prices vary by destination country and carrier, not by Twilio region.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Subaccounts are a first-class, billable allocation unit, so the SubAccount family applies. Phone numbers, messaging services, and calls carry resource SIDs, so the Resource family applies. Twilio sells in more than one processing region, so RegionId applies. This analysis treats negotiated committed-spend contracts as applicable to the CommitmentDiscount family; that rests on standard enterprise contracting, not on a public Twilio document. Twilio has one billing account type, prices in the account's billing currency, no capacity reservations, no customer-selected zones, and no general resource tagging; those columns are N/A and should exist as null. Feature levels follow the FOCUS v1.2 Content Constraints.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Twilio source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Usage Records `price` per category per day; not tied to an invoice, sum of categories does not equal `totalprice`, and treatment of credits is undocumented | Deviation |
| EffectiveCost | Mandatory | Not available: needs promotional credits, prepaid balances, and committed-spend contracts amortized onto usage rows | Missing: Mandatory |
| ListCost | Mandatory | Not exposed; `base_price` exists in the Pricing API but usage categories aggregate destinations with different rates | Missing: Mandatory |
| ContractedCost | Mandatory | Not exposed; `current_price` × PricingQuantity, or `price` if it already carries the contracted rate | Missing: Mandatory |
| BillingAccountId | Mandatory | Main account SID (`AC...`) | Present |
| BillingAccountName | Mandatory | Main account `friendly_name` (Accounts API join) | Present |
| BillingCurrency | Mandatory | `price_unit`, but emitted lowercase (`"usd"`); normalize to uppercase ISO 4217 | Deviation |
| BillingPeriodStart | Mandatory | Calendar month (`Monthly` subresource, `start_date`) | Present |
| BillingPeriodEnd | Mandatory | Calendar month end, made exclusive | Present |
| ChargePeriodStart | Mandatory | `start_date` (GMT) on the `Daily` subresource | Present |
| ChargePeriodEnd | Mandatory | `end_date` is the last included date (inclusive); emit `end_date` + 1 day as an exclusive timestamp | Deviation |
| ChargeDescription | Mandatory | `description` (e.g., "Caller Name Lookups") | Present |
| ChargeCategory | Mandatory | Not emitted; derive "Usage" for metered traffic, "Purchase" for number rentals and registration fees, "Tax" for taxes and surcharges, "Credit" for promotional credits and refunds | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for rebills and adjustments | Present |
| InvoiceIssuerName | Mandatory | "Twilio Inc." (or the regional Twilio entity that invoices the account) | Present |
| ProviderName | Mandatory (dep. v1.3) | "Twilio" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Twilio" | Present |
| ServiceName | Mandatory | Not emitted; derive from the category family: "Programmable Voice", "Programmable Messaging", "Phone Numbers", "Verify", "Lookup", "Video" | Deviation |
| ServiceCategory | Mandatory | Not emitted; derive "Business Applications" for Voice and Messaging, "Security" for Verify, "Identity" for Lookup, "Media" for Video, "Storage" for recording storage | Deviation |
| PricingQuantity | Mandatory | `usage`, a string; for some categories `usage_unit` is `"usd"` (e.g., `calleridlookups`), so the quantity is a dollar amount | Deviation |
| PricingUnit | Mandatory | `usage_unit`, free-text lowercase plurals (`minutes`, `messages`, `usd`); normalize to FOCUS unit format | Deviation |
| ConsumedQuantity | Conditional | `usage` (billed quantity) or `count` (events) | Present |
| ConsumedUnit | Conditional | `usage_unit` / `count_unit`; normalize as for PricingUnit | Deviation |
| ListUnitPrice | Conditional | Not in usage data; Pricing API `base_price` per country, carrier, and number type | Missing: Conditional |
| ContractedUnitPrice | Conditional | Not in usage data; Pricing API `current_price` | Missing: Conditional |
| PricingCategory | Conditional | Not emitted; derive "Standard" for pay-as-you-go, "Committed" for usage drawn against a contract | Deviation |
| BillingAccountType | Conditional | N/A: one account type (main account) | N/A |
| SubAccountId | Conditional | Subaccount SID (`account_sid` with `IncludeSubaccounts=false`) | Present |
| SubAccountName | Conditional | Subaccount `friendly_name` (Accounts API join) | Present |
| SubAccountType | Conditional | Not emitted; constant "Subaccount" | Missing: Conditional |
| ResourceId | Conditional | Not in usage data; phone number, messaging service, trunk, or Verify service SID | Missing: Conditional |
| ResourceName | Conditional | Not in usage data; phone number or service friendly name | Missing: Conditional |
| ResourceType | Conditional | Not in usage data; "Phone Number", "Messaging Service", "SIP Trunk", "Verify Service" | Missing: Conditional |
| SkuId | Conditional | `category` is the closest identifier, but it spans destinations and number types priced differently | Deviation |
| Tags | Conditional | N/A: Twilio has no general resource tagging surfaced in billing; subaccounts are the allocation mechanism | N/A |
| PricingCurrency | Conditional | N/A: prices are quoted in the account's billing currency | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | `description` per category | Present |
| SkuPriceId | Conditional | Not exposed; would key country × carrier (MCC/MNC) × number type, or origination × destination prefix for Voice | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; destination country, carrier, number type, and volume tier belong here | Missing: Conditional |
| RegionId | Conditional | Not in usage data; Twilio processing region (US1, IE1, AU1) | Missing: Conditional |
| RegionName | Conditional | Not in usage data | Missing: Conditional |
| CommitmentDiscountId | Conditional | Committed-spend contract; not documented or exported | Missing: Conditional |
| CommitmentDiscountName | Conditional | Not exposed | Missing: Conditional |
| CommitmentDiscountType | Conditional | Not exposed | Missing: Conditional |
| CommitmentDiscountCategory | Conditional | "Spend"; not exposed | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | "Used"/"Unused"; not exposed | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | Not exposed | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | Not exposed | Missing: Conditional |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Not in usage data; invoices are not exposed by API | Missing: Recommended |
| ChargeFrequency | Recommended | Not emitted; derive "Usage-Based" for traffic, "Recurring" for number rentals, "One-Time" for registration fees | Deviation |
| ServiceSubcategory | Recommended | Not exposed; map each product to an allowed v1.2 value | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: zones are not customer-selected or billed | N/A |

**Tally:** 14 Present, 12 Deviation, 3 Missing Mandatory, 17 Missing Conditional, 2 Missing Recommended, 9 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Account and subaccount identity, a priced usage record per category per day by API, a documented quantity and unit on every record, and a public Pricing API that already separates retail from discounted rates. Few usage-priced SaaS vendors expose this much.

**Substantive (2 of 3 Mandatory gaps):**

- **EffectiveCost.** Twilio accounts run on a prepaid or invoiced balance with promotional credits and, for larger customers, negotiated contracts. None of that appears on a documented row. EffectiveCost requires applying credits and amortizing any committed spend onto usage rows, which Twilio's billing system can do but no public surface does.
- **ListCost.** A category such as `sms-outbound-longcode` covers every destination country and carrier, each with its own `base_price`. ListCost cannot be computed from Usage Records at their current grain; it needs the destination and number type on each row, which today exist only in per-message and per-call logs.

**Trivial (1 of 3 Mandatory gaps):**

- **ContractedCost.** If `price` already reflects `current_price` (the documented "volume or custom price discounts"), ContractedCost equals `price` before credits. Twilio should confirm that, then expose it.

**Substantive, beyond the column table:**

- **No reconciliation to the invoice.** Twilio's own reference says category prices do not sum to `totalprice`. A FOCUS dataset must reconcile: BilledCost summed per InvoiceId has to equal the invoice. The missing costs (taxes, surcharges, uncategorized fees) need their own rows.
- **No resource dimension.** Usage Records are per category and account only. Phone numbers, messaging services, and trunks carry SIDs, but usage cannot be grouped by them. Customers who do not split workloads into subaccounts cannot allocate Twilio spend below the account.
- **Daily is the floor.** No hourly grain exists, which limits anomaly detection on traffic spikes such as SMS pumping fraud.

### 1.5 Deviations to Fix

**BilledCost:** Emit priced rows that, together with Purchase, Tax, and Credit rows, sum to the invoice total per InvoiceId. Retire the `totalprice` gap.

**BillingCurrency:** Uppercase ISO 4217 (`USD`, `EUR`, `JPY`). Twilio's own Pricing API sample already returns `"USD"`.

**ChargePeriodEnd:** Convert the inclusive `end_date` to an exclusive timestamp (`end_date` + 1 day, 00:00 UTC).

**ChargeCategory, ChargeFrequency, PricingCategory:** Derive from category family and contract status as shown in the table.

**ServiceName and ServiceCategory:** Group the roughly 158 categories into product-level ServiceName values and map each to a v1.2 ServiceCategory.

**PricingQuantity and PricingUnit:** Emit numeric quantities, not strings. Replace `usd`-denominated usage with the real billed unit (lookups, minutes, messages). Normalize unit names to FOCUS unit format.

**SkuId:** Split categories by destination country and number type, or emit `category` as SkuId with the price key in SkuPriceId.

**Already right:** Daily priced records, a clean main-account and subaccount hierarchy that maps directly to BillingAccount and SubAccount, and a Pricing API with retail and discounted rates side by side.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is a candidate release; its scope is on the FOCUS site. The v1.4 Invoice Detail dataset directly addresses Twilio's largest structural gap, the lack of invoice-level data by API.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (single account type, single pricing currency, no reservations, zones, or general tagging) and how committed-spend contracts are modeled.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one month of `Daily` Usage Records with `IncludeSubaccounts=false` for each subaccount, plus the invoice, for a pay-as-you-go account and a contracted account. Hand-build a v1.2 file and run it through the Validator. Quantify the `totalprice` gap and confirm whether `price` is list, discounted, or net of credits.

**Phase 1: Close Mandatory gaps.** Add destination country and number type to usage rows so `base_price` can be joined for ListCost. Expose ContractedCost from `current_price`. Apply credits and contract amortization for EffectiveCost. Add Tax, Credit, and uncategorized-fee rows so BilledCost reconciles to the invoice.

**Phase 2: Fix deviations.** Uppercase currency, exclusive ChargePeriodEnd, numeric quantities, real units in place of `usd`, and derived ChargeCategory, ChargeFrequency, PricingCategory, ServiceName, and ServiceCategory.

**Phase 3: Allocation and Conditional columns.** Add resource SIDs (phone number, messaging service, trunk, Verify service) and processing region to usage rows; populate SubAccountType, ListUnitPrice, ContractedUnitPrice, SkuPriceId, SkuPriceDetails, the CommitmentDiscount family for contracted accounts, InvoiceId, and ServiceSubcategory. Deliver by API and scheduled push to object storage.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Invoice Detail dataset; certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **Today, with minor plumbing:** Spend by subaccount (showback for customers who already isolate workloads or end customers by subaccount) and daily spend trending by category.
- **After Phase 1:** Invoice reconciliation, actuals-based budgeting and forecasting, and discount and credit realization.
- **After Phase 2:** Spend by service category across providers and unit-cost analysis per minute and per message.
- **After Phase 3:** Chargeback by phone number or messaging service, destination-country cost analysis, commitment utilization tracking, and anomaly detection on traffic pumping by country.
- **Out of scope:** Capacity reservation management, availability zone analysis, and multi-currency analysis.

---

## Part 3: Immediate Next Steps

1. Reach the owners of Twilio billing and the Usage Records API through the FOCUS landscape outreach channel.
2. Confirm whether Usage Records `price` is list, discounted (`current_price`), or net of promotional credits, and what makes up the `totalprice` gap.
3. Confirm what invoices contain (line items, per-subaccount detail, tax and surcharge lines) and which Twilio entity issues them by region.
4. Confirm whether committed-spend contracts exist and how they are invoiced.
5. Ask whether destination country, number type, and resource SID can be added as group-by dimensions on Usage Records.
6. Build a v1.2 sample from one billing month and run it through the FOCUS Validator; open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Usage Records fields, subresources, parameters, daily floor, lowercase `price_unit`, string-typed numerics, and the `totalprice` caveat come from Twilio's Usage Records reference.
- **High:** Subaccounts bill to the main account with one shared balance, per the Subaccounts reference.
- **High:** The Pricing API exposes `base_price` and `current_price` ("accounts for any volume or custom price discounts") per country, carrier, and number type for Messaging, and per prefix for Voice.
- **High:** Feature levels match the bundled FOCUS v1.2 Content Constraints table (verified June 23, 2026); v1.4 remains the latest ratified version and v1.5 is a candidate release. A live spot-check through the FOCUS MCP was not run for this analysis.
- **Moderate:** EffectiveCost as substantive. If Usage Records `price` is already net of credits and no account has committed spend, EffectiveCost collapses to `price` and becomes trivial.
- **Moderate:** BillingCurrency as a deviation. ISO 4217 codes are uppercase; whether the FOCUS Validator rejects lowercase should be confirmed in Phase 0.
- **Moderate:** ServiceCategory mappings; communications APIs have no exact v1.2 value, and "Business Applications" is the closest fit.
- **Low:** CommitmentDiscount family as applicable. The pricing page promises "the freedom to scale up or down without contracts" and no public document describes committed spend. If none exists, the seven columns become N/A.
- **Low:** Present status for BillingPeriodStart and BillingPeriodEnd as calendar months, and for InvoiceIssuerName as "Twilio Inc." Twilio help center billing articles could not be read, and no public invoice sample names the billing cycle or issuing entity.
- **Low:** Tags as N/A. A per-message tagging feature, if one exists, would make Tags applicable.
- **Low:** RegionId as applicable. Prices do not vary by processing region, so Twilio may argue that region is not a billing dimension.

---

## Sources

- Twilio Usage Records API: [twilio.com/docs/usage/api/usage-record](https://www.twilio.com/docs/usage/api/usage-record)
- Twilio Subaccounts API: [twilio.com/docs/iam/api/subaccounts](https://www.twilio.com/docs/iam/api/subaccounts)
- Twilio Messaging Pricing API: [twilio.com/docs/messaging/api/pricing](https://www.twilio.com/docs/messaging/api/pricing)
- Twilio Voice Pricing API: [twilio.com/docs/voice/pricing](https://www.twilio.com/docs/voice/pricing)
- Twilio BulkExport: [twilio.com/docs/usage/bulkexport](https://www.twilio.com/docs/usage/bulkexport)
- Resolve Call Log Usage Discrepancies: [twilio.com/docs/voice/resolve-call-log-usage-discrepancies](https://www.twilio.com/docs/voice/resolve-call-log-usage-discrepancies)
- Twilio Pricing: [twilio.com/en-us/pricing](https://www.twilio.com/en-us/pricing)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
