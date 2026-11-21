# Heroku & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Heroku (a Salesforce company)  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Heroku Platform API (Team and Enterprise Account Daily/Monthly Usage, Account and Team Invoices); Enterprise Account usage dashboard and CSV download; Heroku Dev Center billing and Enterprise docs; Heroku pricing page  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 15 Present, 15 Deviation, 4 Missing Mandatory, 14 Missing Conditional, 1 Missing Recommended, 8 N/A

---

## Executive Summary

Heroku is Salesforce's platform as a service. Customers run apps on dynos (Eco, Basic, Standard, Performance, and Private and Shield dynos in Private Spaces, plus the Kubernetes-based Fir generation), attach first-party data add-ons (Heroku Postgres, Key-Value Store, Apache Kafka on Heroku, Managed Inference and Agents) and third-party Elements Marketplace add-ons, and buy Heroku Connect and Private or Shield Spaces. Self-serve usage is prorated to the second against a monthly cap and billed in arrears. Enterprise customers prepay a contract denominated in dyno units and add-on credits, and Salesforce invoices the whole contract as a single line item.

Heroku exposes more structured usage data than most PaaS vendors. The Platform API returns daily and monthly usage per team and per app, and the Enterprise Account dashboard breaks the same data down by team and app with CSV download. The problem is the unit of measure: every usage figure is in dyno units or credits, not dollars, and no surface emits a priced line item. Fifteen of 57 FOCUS v1.2 columns map directly and 17 of 21 Mandatory columns have a source, but the four missing Mandatory columns are the cost columns.

Two of the four are substantive. **BilledCost** exists only as invoice totals (`charges_total`, `credits_total`, and category totals on team invoices), never at the app-by-day grain of the usage data, and for Enterprise customers the Salesforce invoice is one line. **EffectiveCost** requires amortizing the prepaid Enterprise contract across the dyno units and credits it funds. **ListCost** and **ContractedCost** are price-table joins Heroku can do internally, provided usage is first exported at dyno-size and add-on-plan grain rather than as normalized units.

Allocation is better than average but not complete. Apps and teams give real ResourceName and SubAccount dimensions, but the usage API returns `app_name` only (no app UUID), rolls every add-on into four credit buckets, omits region, and Heroku has no tags.

**Recommendation:** Publish a daily FOCUS export per Team and per Enterprise Account with one row per app × SKU (dyno size, add-on plan, Space, Connect) × day, carrying the app UUID, region, and priced ListCost, ContractedCost, BilledCost, and EffectiveCost. Model the Enterprise contract as commitment discounts (dyno units and add-on credits) with Purchase rows and Used/Unused draw-down, and emit Tax and Credit rows so BilledCost reconciles to the invoice. Deliver it through the Platform API alongside the existing usage endpoints.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

- **Team Daily and Monthly Usage** (`GET /teams/{id}/usage/daily`, `/usage/monthly`): Per-day or per-month values for `dynos` (dyno units), `addons`, `data` (first-party add-on credits), `partner` (third-party add-on credits), `space` (Space credits), and, monthly only, `connect` (average Connect rows synced). An `apps` array repeats these per `app_name`.
- **Enterprise Account Daily and Monthly Usage** (`GET /enterprise-accounts/{id}/usage/daily`, `/usage/monthly`): The same measures with a `teams` array in place of `apps`.
- **Account and Team Invoices** (`GET /account/invoices`, `GET /teams/{id}/invoices`): `number`, `period_start`, `period_end`, `charges_total`, `credits_total`, `total`, `state`; team invoices add `platform_total`, `addons_total`, `database_total`, `dyno_units`, `weighted_dyno_hours`, and `payment_status`. No line items.
- **Enterprise Account usage dashboard:** Monthly usage for the past 12 months and daily usage for up to 31-day windows within the past 6 months, by team and app, with "Download as CSV" and `heroku enterprise:usage:daily|monthly --csv`. Heroku labels daily figures as estimates.
- **Self-serve Billing tab:** Current usage updated nightly, accurate through 00:00 UTC of the prior day. No documented line-item export.

Key characteristics:

- **Dynos:** Prorated to the second on wall-clock time with a monthly maximum. Eco is $5 for 1,000 shared hours; Basic $7; Standard-1X $25 and Standard-2X $50; Performance-M through Performance-2XL $250 to $1,500; Private-S through Private-2XL $125 to $1,500; Shield-S through Shield-2XL $150 to $1,800; Fir sizes from `dyno-1c-0.5gb` ($25) to `dyno-32c-64gb` ($2,400) per month.
- **Dyno units:** One unit equals one Standard-1X running for a month (Standard-2X is 2 units, Performance-L is 16). The usage API reports dynos in these units, which normalizes away the dyno size.
- **Add-on credits:** One credit equals $1, in three pools: General, Heroku Data, and Partner. Overage draws General credits in a fixed order (third-party add-ons, Heroku Data, Private Spaces, Shield Spaces); dyno and Connect overage is billed directly.
- **Data and AI add-ons:** Postgres, Key-Value Store, and Kafka are priced per plan per month; Managed Inference and Agents is priced per million input and output tokens. All land in the `data` credit bucket.
- **Hierarchy:** Personal account, Team, and Enterprise Account (containing Teams), then apps and add-ons. Apps and add-ons have UUIDs in the Platform API.
- **Regions:** Common Runtime `us` and `eu`; Private Spaces in `dublin`, `frankfurt`, `london`, `montreal`, `mumbai`, `oregon`, `singapore`, `sydney`, `tokyo`, and `virginia`. No billing surface carries region.
- **No tags:** Heroku has no app or add-on labels.
- **Invoicing:** Self-serve accounts are invoiced by Heroku and pay by card. Enterprise charges appear as one line item on a Salesforce invoice; itemized detail exists only in the usage downloads.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Heroku's Enterprise contract prepays dyno units and add-on credits at a contracted rate for a term and draws them down with usage, so this analysis treats the CommitmentDiscount family as applicable. Heroku deploys into named regions, so RegionId and RegionName apply. Heroku has no capacity reservations, availability zones, alternate pricing currencies, or tags; those columns are N/A and should exist as null. Feature levels below follow the FOCUS v1.2 Content Constraints, spot-checked against the live spec on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Heroku source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Not at row grain: only invoice totals (`charges_total`, `platform_total`, `addons_total`, `database_total`); Enterprise invoice is one Salesforce line | Missing: Mandatory |
| EffectiveCost | Mandatory | Not available: needs amortization of the prepaid Enterprise contract across dyno units and credits consumed | Missing: Mandatory |
| ListCost | Mandatory | Not in usage data; join public price list × usage at dyno-size and add-on-plan grain | Missing: Mandatory |
| ContractedCost | Mandatory | Not in usage data; = ListCost for self-serve, Enterprise order-form rate per dyno unit and credit otherwise | Missing: Mandatory |
| BillingAccountId | Mandatory | Team `id` or Enterprise Account `id` (UUID); personal account ID for self-serve individuals | Present |
| BillingAccountName | Mandatory | Team or Enterprise Account `name` | Present |
| BillingCurrency | Mandatory | "USD" (no currency field; all prices are USD) | Present |
| BillingPeriodStart | Mandatory | Invoice `period_start` | Present |
| BillingPeriodEnd | Mandatory | Invoice `period_end` | Present |
| ChargePeriodStart | Mandatory | Daily usage `date` or monthly usage `month` | Present |
| ChargePeriodEnd | Mandatory | `date` + 1 day, or end of `month` | Present |
| ChargeDescription | Mandatory | Not emitted; derive from app, usage measure, and SKU (e.g., "Standard-2X dynos · my-app") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for metered dynos, add-ons, Spaces, Connect; "Purchase" for Enterprise contract; "Tax" and "Credit" from invoice | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued charges | Present |
| InvoiceIssuerName | Mandatory | "Heroku" for self-serve; "Salesforce, Inc." for Enterprise | Present |
| ProviderName | Mandatory (dep. v1.3) | "Heroku" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Heroku" for first-party; Elements partner name for third-party add-ons, which the `partner` bucket does not identify | Deviation |
| ServiceName | Mandatory | Usage buckets (`dynos`, `data`, `partner`, `space`, `connect`); split into "Heroku Dynos", "Heroku Postgres", "Heroku Key-Value Store", "Apache Kafka on Heroku", "Heroku Managed Inference and Agents", "Heroku Private Spaces", "Heroku Connect" | Deviation |
| ServiceCategory | Mandatory | Derive: "Compute" for dynos; "Databases" for Postgres and Key-Value Store; "Integration" for Kafka and Connect; "AI and Machine Learning" for Managed Inference and Agents; "Networking" for Spaces | Deviation |
| PricingQuantity | Mandatory | `dynos` (dyno units) and credit values; must become quantity in each SKU's rate basis | Deviation |
| PricingUnit | Mandatory | Not emitted; normalize to "Dyno-Months" or "Hours" per dyno size, "Months" per add-on plan, "1M Tokens" for inference | Deviation |
| ConsumedQuantity | Conditional | `dynos` and credit values (normalized, not physical consumption) | Deviation |
| ConsumedUnit | Conditional | Implied "dyno units" and "credits"; emit explicit FOCUS-format units | Deviation |
| ListUnitPrice | Conditional | Not in data; public pricing page per dyno size and add-on plan | Missing: Conditional |
| ContractedUnitPrice | Conditional | Not in data; Enterprise order form | Missing: Conditional |
| PricingCategory | Conditional | Derive: "Standard" for self-serve and overage; "Committed" for usage drawn from prepaid dyno units and credits | Deviation |
| BillingAccountType | Conditional | Derive from endpoint: "Personal", "Team", or "Enterprise Account" | Present |
| SubAccountId | Conditional | Enterprise usage `teams` entries (team ID) | Present |
| SubAccountName | Conditional | Team name | Present |
| SubAccountType | Conditional | Not emitted; constant "Team" | Deviation |
| ResourceId | Conditional | `app_name` only; join to app UUID via `GET /apps` (names can be renamed and reused) | Deviation |
| ResourceName | Conditional | `app_name` | Present |
| ResourceType | Conditional | Not emitted; "App" at current grain, add-on and dyno formation types if grain improves | Deviation |
| SkuId | Conditional | Not in usage data; dyno size and add-on plan IDs exist in the Platform API | Missing: Conditional |
| Tags | Conditional | N/A: no app or add-on tags | N/A |
| PricingCurrency | Conditional | N/A: priced and billed in USD only | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Usage buckets act as coarse meters (`dynos`, `data`, `partner`, `space`, `connect`); need per-SKU meters | Deviation |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed for dyno size, plan tier, and token direction | Missing: Conditional |
| RegionId | Conditional | Not in usage data; app `region` and Space region exist in the Platform API | Missing: Conditional |
| RegionName | Conditional | Not in usage data | Missing: Conditional |
| CommitmentDiscountId | Conditional | Enterprise contract or credit pool ID; not exposed | Missing: Conditional |
| CommitmentDiscountName | Conditional | Not exposed | Missing: Conditional |
| CommitmentDiscountType | Conditional | Not exposed (e.g., "Dyno Units", "Add-on Credits") | Missing: Conditional |
| CommitmentDiscountCategory | Conditional | "Usage" for dyno units; "Spend" for $1 add-on credits; not exposed | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | "Used"/"Unused" against the contract balance; not exposed | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | Dyno units or credits drawn | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | "Dyno Units" or "Credits" | Missing: Conditional |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice `number` (self-serve and Team); Salesforce invoice number for Enterprise | Present |
| ChargeFrequency | Recommended | Derive: "Usage-Based" for metered usage; "Recurring" or "One-Time" for the Enterprise contract per its payment schedule | Deviation |
| ServiceSubcategory | Recommended | Not emitted; map each service to an allowed v1.2 value | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: zones are not exposed to customers | N/A |

**Tally:** 15 Present, 15 Deviation, 4 Missing Mandatory, 14 Missing Conditional, 1 Missing Recommended, 8 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Billing account and sub-account (Team, Enterprise Account), billing and charge periods at daily grain, app-level usage, invoice numbers, and a programmatic API. Heroku already has the delivery path most vendors lack.

**Substantive (2 of 4 Mandatory gaps):**

- **BilledCost.** Invoices carry only totals, and Enterprise invoices are a single Salesforce line. Producing row-level BilledCost means pricing each app-by-SKU-by-day row and reconciling it, plus Tax and Credit rows, to the invoice total.
- **EffectiveCost.** Enterprise customers prepay dyno units and add-on credits for a contract term. EffectiveCost requires amortizing that prepayment onto the usage it funds and billing overage at its own rate.

**Trivial (2 of 4 Mandatory gaps):**

- **ListCost.** Heroku owns the public price list. Join it by dyno size and add-on plan, then multiply by PricingQuantity. This depends on exporting usage at SKU grain first (see below).
- **ContractedCost.** Equals ListCost for self-serve. For Enterprise, join the order-form rate per dyno unit and per credit.

**Substantive, beyond the column table:**

- **Normalized units.** Dyno units and credits collapse dyno size and add-on plan. A Performance-L day and sixteen Standard-1X days look identical, so no downstream pricing, rightsizing, or SKU analysis is possible from the current data.
- **Add-on opacity.** Postgres, Key-Value Store, Kafka, and Managed Inference and Agents share one `data` bucket; every Elements partner shares one `partner` bucket. Customers cannot see which add-on drove spend or which partner published it.
- **App identity.** The usage API keys on `app_name`, which can be renamed or reused after deletion. ResourceId needs the app UUID.
- **Daily accuracy.** Heroku labels daily Enterprise figures as estimates, and self-serve usage lags a day. A FOCUS export should state recency and completeness (v1.3 adds columns for this).

### 1.5 Deviations to Fix

**PricingQuantity, PricingUnit, ConsumedQuantity, ConsumedUnit:** Replace dyno units and credits with quantities in each SKU's rate basis: dyno time per dyno size (for example "Hours" against an hourly rate derived from the monthly cap), plan-months per add-on plan, and "1M Tokens" per direction for Managed Inference and Agents. Keep dyno units as an `x_DynoUnits` custom column for Enterprise reconciliation.

**ServiceName, ServiceCategory, PublisherName:** Split the `data` and `partner` buckets into named services. Use "Compute" for dynos, "Databases" for Postgres and Key-Value Store, "AI and Machine Learning" for Managed Inference and Agents, "Integration" for Kafka and Connect, and "Networking" for Spaces. Emit the Elements partner as PublisherName for third-party add-ons.

**ResourceId and ResourceType:** Emit the app UUID; add add-on UUIDs as their own resources when grain improves.

**ChargeCategory, ChargeFrequency, PricingCategory, ChargeDescription, SubAccountType, SkuMeter:** Derive as shown in the table.

**Already right:** Team and Enterprise IDs, daily and monthly periods, app names, invoice numbers and periods, and USD-only pricing map cleanly.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is in release candidate with ratification scheduled for December 3, 2026. The Contract Commitment dataset (v1.3) fits Heroku's Enterprise contract, and the Invoice Detail dataset (v1.4) fits the Salesforce single-line invoice.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (no tags, zones, reservations, or alternate currencies) and the decision on modeling dyno units and add-on credits as commitment discounts. Salesforce, as Heroku's parent and invoice issuer for Enterprise, should be part of the conversation.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one month of Team and Enterprise Account daily usage plus the matching invoices. Hand-build a FOCUS file, run it through the Validator, and decide the commitment model for dyno units and credits.

**Phase 1: SKU grain.** Re-cut usage by app UUID × dyno size or add-on plan × region × day. This is the prerequisite for every cost column.

**Phase 2: Close Mandatory gaps.** Join the price list for ListCost and ListUnitPrice, the order form for ContractedCost and ContractedUnitPrice, and price each row for BilledCost. Add Tax and Credit rows so BilledCost reconciles to the invoice. Amortize the Enterprise prepayment for EffectiveCost.

**Phase 3: Fix deviations and fill Conditional columns.** Derive ChargeCategory, ServiceCategory, ChargeFrequency, and PricingCategory; split ServiceName and PublisherName; emit RegionId, RegionName, SkuId, SkuPriceId, SkuPriceDetails, the CommitmentDiscount family, and ServiceSubcategory. Expose the export through the Platform API and the Enterprise CSV.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Contract Commitment and Invoice Detail datasets; certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **Today, from the current API:** Usage trending and anomaly detection by app and team in dyno units and credits (not dollars).
- **After Phase 1:** Dyno rightsizing, add-on inventory by plan, and regional footprint analysis.
- **After Phase 2:** Invoice reconciliation, chargeback and showback by team and app in dollars, actuals-based budgeting and forecasting, and Enterprise contract burn-down.
- **After Phase 3:** Cross-provider spend by service category, unit economics for Managed Inference and Agents tokens, and commitment utilization.
- **Out of scope:** Tag-based allocation (unless Heroku adds labels), availability zone analysis, and capacity reservation management.

---

## Part 3: Immediate Next Steps

1. Follow up with the Heroku contact from KubeCon NA 2026 to identify the owner of the usage API and Enterprise billing.
2. Confirm whether Heroku's internal metering already records usage by dyno size, add-on plan, and region (it must, to bill self-serve accounts by the second).
3. Confirm the invoicing entity for self-serve accounts and whether any non-USD billing exists.
4. Build a v1.2 sample from one month of Team usage and run it through the FOCUS Validator.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Usage endpoints and field names (Team and Enterprise Account daily and monthly usage, Account and Team invoices), taken from Heroku's published API schema.
- **High:** Dyno-unit definition, add-on credit pools, per-second proration, and the single-line Salesforce Enterprise invoice, from Heroku Dev Center and Help.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints; spot-checked against the live spec on November 17, 2026, and v1.4 remains the latest ratified version.
- **Moderate:** Heroku has no tags. No tagging feature appears in any Heroku doc reviewed; third-party add-ons offer workarounds only.
- **Moderate:** Treating Enterprise dyno units and add-on credits as commitment discounts. If Heroku models the contract as a plain prepayment with no rate benefit, the seven CommitmentDiscount columns become N/A and the contract moves to the Contract Commitment dataset only.
- **Moderate:** SubAccountId from the Enterprise usage `teams` array. The array carries a per-team breakdown; the exact identifier fields were not confirmed.
- **Moderate:** USD as the only billing currency. Prices are published in USD and no currency field exists, but no doc rules out non-USD Enterprise contracts.
- **Low:** InvoiceIssuerName for self-serve accounts. Docs say Heroku invoices them but do not name the legal entity.
- **Low:** Monetary units on Team invoice fields (whole dollars vs. cents) and the Fir dyno-unit conversion, neither of which is documented.

---

## Sources

- Heroku Platform API Reference: [devcenter.heroku.com/articles/platform-api-reference](https://devcenter.heroku.com/articles/platform-api-reference)
- Heroku API schema (heroku-go mirror): [github.com/heroku/heroku-go](https://github.com/heroku/heroku-go/blob/master/v5/schema.json)
- Usage and Billing: [devcenter.heroku.com/articles/usage-and-billing](https://devcenter.heroku.com/articles/usage-and-billing)
- Enterprise Account Usage: [devcenter.heroku.com/articles/enterprise-account-usage](https://devcenter.heroku.com/articles/enterprise-account-usage)
- Heroku Enterprise (dyno units and credits): [devcenter.heroku.com/articles/heroku-enterprise](https://devcenter.heroku.com/articles/heroku-enterprise)
- Heroku Regions: [devcenter.heroku.com/articles/regions](https://devcenter.heroku.com/articles/regions)
- Enterprise invoices via Salesforce: [help.heroku.com/SVYFZ1C8](https://help.heroku.com/SVYFZ1C8/how-do-i-view-invoices-for-my-enterprise-team)
- Heroku Pricing: [heroku.com/pricing](https://www.heroku.com/pricing)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
