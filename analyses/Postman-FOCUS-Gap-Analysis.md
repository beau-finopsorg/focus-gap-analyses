# Postman & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Postman, Inc.  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Postman API Billing endpoints (`GET /accounts`, `GET /accounts/{accountId}/invoices`); Postman API Analytics endpoint (`GET /analytics`); Postman billing and resource usage docs; Postman pricing page; AWS Marketplace listing  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 8 Present, 9 Deviation, 11 Missing Mandatory, 11 Missing Conditional, 1 Missing Recommended, 17 N/A

---

## Executive Summary

Postman sells per-user subscriptions (Free, Solo, Team, Enterprise) billed monthly or annually in advance, plus metered pay-as-you-go overages for AI credits, monitoring requests, Flows credits, cloud performance testing (VU hours), and Context Graph API queries. Seats added mid-term through Auto-Flex are billed in arrears, monthly or quarterly. All prices and invoices are in USD, and fees are tax-exclusive.

**Public billing documentation is thin.** Postman documents more programmatic billing access than most SaaS vendors in this library, but what it exposes is shallow. The Billing API returns the account (state, sales channel, seat counts) and a list of *paid* invoices with a single total each: no line items, no billing period, no tax, no discounts, no usage. The Analytics API carries AI credit usage and seat consumption but no cost or currency fields, and appears to be Enterprise-only. The in-app resource usage dashboard tracks a dozen meters but documents no export. Postman publishes no invoice line-item format, no usage-to-cost mapping, and no FOCUS or FinOps statement. Much of this analysis therefore infers what Postman's billing system (Stripe) holds internally rather than reading it from documented fields.

Only 6 of 21 Mandatory columns map to a documented source today, 4 more need derivation, and 11 are missing. Two of those 11 are substantive. **BilledCost** has no line-level public source: the invoices endpoint gives paid totals only, so open invoices, overages, Auto-Flex true-ups, and tax cannot be separated. **EffectiveCost** needs amortization of annual prepaid seats and allocation of any Enterprise discounts. The other nine are plumbing once Postman exposes the invoice lines it already generates.

**Recommendation:** Extend the existing Billing API with a FOCUS-shaped invoice-line endpoint (or a monthly FOCUS export per billing account): one Purchase row per seat subscription and add-on per term, one Usage row per metered product per billing period, Auto-Flex seat true-ups as their own Purchase rows, and separate Tax and Credit rows so BilledCost reconciles to each invoice. Return all invoice statuses, not only `PAID`.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

Postman's public billing surface has three parts:

- **`GET /accounts`** (Billing API): `id`, `teamId`, `billingEmail`, `state` (FREE, PAID, EXPIRED_TRIAL, OVERDUE, SUSPENDED, BLOCKED, PAYMENT_DISPUTED), `salesChannel` (SELF_SERVE or SALES_SERVE), and `slots{total, consumed, available, unbilled}`, where `unbilled` counts Auto-Flex seats not yet invoiced.
- **`GET /accounts/{accountId}/invoices?status=PAID`** (Billing API, added January 2024): `data[]` of `{id, status, issuedAt, totalAmount{value, currency}, links{web{href}}}`. `PAID` is the only allowed status. The docs do not state whether `value` is in major or minor currency units.
- **`GET /analytics`** (Analytics API): tabular metrics by `resource`, `view`, and `period`. Usage-relevant metrics include `ai:credit_usage` (`usage`, `limit`, in millicredits), `ai:credit_usage_by_model` (`created_at`, `model`, `ai_credits_used`, `message_count`), `ai:usage_leaderboard` (per-user credits), `team:license_consumption`, `team:last_autoflex_cycle`, monitor runs, and Flow executions. No cost or currency fields.

In the product:

- **Plan and payments:** Plan, subscription cycle, "expected cost upon renewal," payment methods (card, ACH in the US, Apple Pay, Google Pay; processed by Stripe), and past invoices downloadable one at a time. Postman's billing docs state that invoicing is available for Enterprise teams only.
- **Resource usage:** Postman API calls, monitor requests, scheduled collection runs, Cloud Agent requests, performance-test VU hours, Flows credits, Agent Mode credits, storage, specifications, packages, and integrations, against plan limits. Only Monitoring has a drill-down ("View detailed usage"). No export is documented.

Key characteristics:

- **Seat subscriptions:** Solo $9 per month; Team $19 per user per month billed annually; Enterprise through sales. Each plan includes monthly allowances (AI credits, monitoring requests, Postman API calls, Flows credits).
- **Metered overages (pay-as-you-go, toggled per product):** AI credits ($0.05 Solo, $0.04 Team, $0.035 Enterprise per credit); monitoring ($20 per 50,000 requests); Flows ($1 per 1,000 credits); cloud performance testing ($0.04 per VU hour); Context Graph API queries ($0.01 per query after 5,000). With pay-as-you-go off, limits act as caps.
- **Add-ons:** Simple Security (SSO/SAML) at $6 per user per month; Advanced Security Administration and Premium Support through sales.
- **Auto-Flex:** Admins add seats without paying up front; seats still held on the Auto-Flex date are billed monthly (monthly plans) or quarterly (annual plans).
- **Channels:** Self-serve, sales-served, and AWS Marketplace (Team from 10 seats, Enterprise from 20, on 1, 2, or 3-year terms; added seats and monitoring billed separately).
- **Hierarchy:** Billing account maps to a team (`teamId`). Enterprise Organizations group multiple teams; how their billing rolls up is undocumented.
- **No tags, no region pricing:** An EU data region exists (`api.eu.postman.com`) but nothing is priced by region.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Postman documents no commitment-based discounts: annual billing is a subscription term, and plan allowances are included quantities, not drawn-down commitments. The CommitmentDiscount family is therefore N/A, as are capacity reservations, region columns, alternate pricing currencies, and tags. Those columns should exist as null. Enterprise Organizations that bill several teams under one contract trigger the SubAccount columns. Feature levels follow the FOCUS v1.2 Content Constraints, spot-checked against the live spec on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Postman source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Not available at line level; invoices API returns only paid invoice totals | Missing: Mandatory |
| EffectiveCost | Mandatory | Not available: needs amortization of annual prepaid seats and add-ons, plus discount allocation | Missing: Mandatory |
| ListCost | Mandatory | Not exposed; join Postman price book × PricingQuantity | Missing: Mandatory |
| ContractedCost | Mandatory | Not exposed; invoice line unit price × quantity (Enterprise and Marketplace rates are negotiated) | Missing: Mandatory |
| BillingAccountId | Mandatory | `/accounts` `id` | Present |
| BillingAccountName | Mandatory | Not on `/accounts`; join team name via `teamId` | Deviation |
| BillingCurrency | Mandatory | `totalAmount.currency` ("USD") | Present |
| BillingPeriodStart | Mandatory | Not exposed; subscription cycle shown in Plan and payments UI only | Missing: Mandatory |
| BillingPeriodEnd | Mandatory | Not exposed | Missing: Mandatory |
| ChargePeriodStart | Mandatory | Not exposed; invoice line service period | Missing: Mandatory |
| ChargePeriodEnd | Mandatory | Not exposed | Missing: Mandatory |
| ChargeDescription | Mandatory | Not exposed; invoice line description | Missing: Mandatory |
| ChargeCategory | Mandatory | Derive: "Purchase" for seats, add-ons, and Auto-Flex true-ups; "Usage" for metered overages; "Tax" and "Credit" rows from invoice | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued charges | Present |
| InvoiceIssuerName | Mandatory | "Postman, Inc." (Postman); AWS for Marketplace purchases | Present |
| ProviderName | Mandatory (dep. v1.3) | "Postman" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Postman" | Present |
| ServiceName | Mandatory | Derive from plan, add-on, and resource usage meter names (e.g., "Postman Enterprise", "Postman AI", "Postman Monitors", "Postman Flows", "Postman Performance Testing") | Deviation |
| ServiceCategory | Mandatory | Derive: "Developer Tools" for plans, monitors, Flows, and performance testing; "AI and Machine Learning" for AI credits; "Security" for SSO add-ons | Deviation |
| PricingQuantity | Mandatory | Not exposed; compute against the rate basis (seats; credits; 50,000-request monitoring blocks; 1,000-credit Flows blocks; VU hours) | Missing: Mandatory |
| PricingUnit | Mandatory | Not exposed; "Users", "Credits", "Requests", "VU-Hours", "Queries" | Missing: Mandatory |
| ConsumedQuantity | Conditional | Analytics `ai:credit_usage` (millicredits) and resource usage dashboard; no export for other meters | Deviation |
| ConsumedUnit | Conditional | Millicredits in Analytics; normalize to FOCUS unit format | Deviation |
| ListUnitPrice | Conditional | Not exposed; public pricing page | Missing: Conditional |
| ContractedUnitPrice | Conditional | Not exposed | Missing: Conditional |
| PricingCategory | Conditional | Derive: "Standard" (no commitment pricing) | Deviation |
| BillingAccountType | Conditional | `salesChannel` (SELF_SERVE, SALES_SERVE) | Present |
| SubAccountId | Conditional | Not exposed; Enterprise Organization teams | Missing: Conditional |
| SubAccountName | Conditional | Not exposed | Missing: Conditional |
| SubAccountType | Conditional | Not exposed ("Team") | Missing: Conditional |
| ResourceId | Conditional | Not exposed; candidates are seat (user), monitor, Flow, and performance test IDs | Missing: Conditional |
| ResourceName | Conditional | Not exposed | Missing: Conditional |
| ResourceType | Conditional | Not exposed | Missing: Conditional |
| SkuId | Conditional | Not exposed; internal plan and add-on codes | Missing: Conditional |
| Tags | Conditional | N/A: no billing tags or labels | N/A |
| PricingCurrency | Conditional | N/A: priced and billed in USD only | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Resource usage dashboard meter names (UI only) | Deviation |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed for monthly vs. annual, per-plan overage rates, and block sizes | Missing: Conditional |
| RegionId | Conditional | N/A: EU data region exists but nothing is priced by region | N/A |
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
| InvoiceId | Recommended | Invoices API `id` (e.g., "inv_7UDSYBJPGQU93N7M") | Present |
| ChargeFrequency | Recommended | Derive: "Recurring" for seats and add-ons; "Usage-Based" for metered overages | Deviation |
| ServiceSubcategory | Recommended | Not exposed; map each product to an allowed v1.2 ServiceSubcategory value | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: no zones | N/A |

**Tally:** 8 Present, 9 Deviation, 11 Missing Mandatory, 11 Missing Conditional, 1 Missing Recommended, 17 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Billing account ID, account type (sales channel), currency, invoice IDs, and seat counts are already exposed through a documented, authenticated API. Few SaaS vendors have that much. Plan names, meter names, and public list prices exist for deriving the rest.

**Substantive (2 of 11 Mandatory gaps):**

- **BilledCost.** No public source carries line-level charges. The invoices endpoint returns one total per paid invoice, so seat charges, overages, Auto-Flex true-ups, add-ons, and tax cannot be separated, and open or overdue invoices are invisible. The lines exist in Postman's billing system; the work is exposing them and splitting tax and credits into their own rows.
- **EffectiveCost.** Annual plans and add-ons are billed in advance, and Auto-Flex seats are trued up monthly or quarterly. EffectiveCost requires amortizing purchases across their service term and allocating any negotiated Enterprise or Marketplace discounts back to the charges they offset.

**Trivial (9 of 11 Mandatory gaps):**

- **ListCost and ContractedCost.** Postman owns the price book and the contracted rates; join unit price × PricingQuantity.
- **BillingPeriodStart/End and ChargePeriodStart/End.** Postman already tracks the subscription cycle and each invoice line's service period.
- **ChargeDescription.** Invoice line description.
- **PricingQuantity and PricingUnit.** Derivable for seats, AI credits, VU hours, and Context Graph queries (flat rates). Monitoring and Flows are sold in blocks (50,000 requests, 1,000 credits), so PricingQuantity must be computed against the block rate basis, not copied from consumed requests or credits.

**Substantive, beyond the column table:**

- **Thin public billing docs.** No invoice line-item format, no usage export, no usage-to-cost mapping, and an undocumented unit for `totalAmount.value`. Every Present or Deviation status that depends on invoice contents is inferred, not documented.
- **Paid-only invoices.** A FinOps tool polling the API sees spend only after payment, which breaks accruals and month-end close.
- **Usage without cost.** The Analytics API reports AI credit usage per model and per user, which is good allocation material, but carries no price or currency and appears gated to Enterprise.
- **Allocation.** No tags, no ResourceId on any cost record, and undocumented billing roll-up for Enterprise Organizations. Customers cannot charge back Postman spend to teams today.
- **AWS Marketplace.** Marketplace contracts invoice through AWS, so that spend appears in the customer's AWS billing data rather than any Postman export. Postman should document how the two reconcile.

### 1.5 Deviations to Fix

**BillingAccountName:** Add the team or organization name to `/accounts`, or document the join to `teamId`.

**ChargeCategory:** "Purchase" for seat subscriptions, add-ons, and Auto-Flex true-ups; "Usage" for metered overages; "Tax" and "Credit" rows from the invoice.

**ServiceName and ServiceCategory:** Publish a fixed product list. "Developer Tools" for plans, Monitors, Flows, and performance testing; "AI and Machine Learning" for AI credits; "Security" for SSO and security administration add-ons.

**ConsumedQuantity and ConsumedUnit:** Convert millicredits to credits, and extend the Analytics metrics to every billed meter (monitor requests, Flows credits, VU hours, Context Graph queries).

**SkuMeter:** Promote the resource usage dashboard's meter names into the exported data.

**PricingCategory and ChargeFrequency:** Derive from product type as shown in the table.

**Already right:** USD-only billing, stable invoice IDs, an explicit account state and sales channel, and seat counts that distinguish billed from unbilled seats.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is a release candidate with ratification scheduled for December 3, 2026. The Invoice Detail and billing-period datasets introduced in v1.4 map closely to Postman's existing invoices endpoint and are a natural next step for it.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (no commitments, reservations, regions, tags, or alternate currencies) and how AWS Marketplace contracts are represented.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one billing period of invoice lines from Postman's billing system for a self-serve Team account and a sales-served Enterprise organization. Hand-build a FOCUS file and run it through the Validator. Confirm the unit of `totalAmount.value` and the Enterprise Organization billing roll-up.

**Phase 1: Close Mandatory gaps.** Expose invoice lines with service periods, descriptions, quantities, and unit prices. Join the price book for ListCost. Amortize annual seats and add-ons for EffectiveCost. Emit Tax and Credit rows so BilledCost reconciles to each invoice.

**Phase 2: Fix deviations.** Derive ChargeCategory, ServiceName, ServiceCategory, ChargeFrequency, and PricingCategory; normalize PricingUnit and ConsumedUnit; compute PricingQuantity against block rates for Monitoring and Flows.

**Phase 3: Allocation and Conditional columns.** Add SubAccountId and SubAccountName for Enterprise Organization teams; ResourceId, ResourceName, and ResourceType (user, monitor, Flow, performance test); SkuId, SkuPriceId, and SkuPriceDetails; and ServiceSubcategory. Return all invoice statuses from the API.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Invoice Detail dataset; certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **After Phase 1:** Invoice reconciliation, accruals before payment, actuals-based budgeting and forecasting, and amortized spend reporting.
- **After Phase 2:** Spend by service category across providers, and seat-versus-overage mix analysis.
- **After Phase 3:** Chargeback and showback by team, AI credit unit economics per user or model, and anomaly detection on pay-as-you-go overages.
- **Out of scope:** Commitment discount utilization, capacity reservation management, region-based analysis, and tag-based allocation (unless Postman adds labels).

---

## Part 3: Immediate Next Steps

1. Follow up with the Postman contact from KubeCon NA 2026 to identify the owner of billing and the Billing API.
2. Request a sample invoice (self-serve Team and Enterprise) to confirm line-item fields, tax treatment, and the `totalAmount.value` unit.
3. Confirm how Enterprise Organizations with multiple teams are billed and how AWS Marketplace contracts reconcile.
4. Build a v1.2 sample from one billing period and run it through the FOCUS Validator.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** The Billing API exposes only account data and paid invoice totals; the field lists come from Postman's API reference. Billing is USD-only and tax-exclusive. Published plan prices and overage rates come from Postman's pricing page.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints; spot-checked against the live spec on November 17, 2026, and v1.4 remains the latest ratified version.
- **Moderate:** Status of columns that depend on invoice line contents. Postman does not document line items, so their presence in its billing system is inferred.
- **Moderate:** Commitment discount family as N/A. If Enterprise contracts include prepaid credit pools or drawn-down commitments, these seven columns become applicable.
- **Moderate:** No public FOCUS, FinOps, or cost-export statement by Postman. This rests on absence of evidence.
- **Low:** Analytics API plan gating; Postman's reports are Enterprise-only, but the API reference does not state it.
- **Low:** SubAccount applicability. Enterprise Organization billing roll-up is undocumented.
- **Low:** Monthly-billing prices and the 2026 plan restructure (Solo, single-user Free). Postman's page shows annual prices only; other figures come from third parties and are not used in this report.

---

## Sources

- Postman API: Get accounts: [learning.postman.com/api-docs/api-reference/billing/get-accounts](https://learning.postman.com/api-docs/api-reference/billing/get-accounts.md)
- Postman API: Get account invoices: [learning.postman.com/api-docs/api-reference/billing/get-account-invoices](https://learning.postman.com/api-docs/api-reference/billing/get-account-invoices.md)
- Postman API: Get analytics data: [learning.postman.com/api-docs/api-reference/analytics/get-analytics-data](https://learning.postman.com/api-docs/api-reference/analytics/get-analytics-data.md)
- Postman Blog, Access billing data with the Postman API: [blog.postman.com](https://blog.postman.com/easily-access-your-billing-data-with-the-postman-api/)
- Postman Billing: [learning.postman.com/docs/billing/billing](https://learning.postman.com/docs/billing/billing.md)
- Postman Resource Usage: [learning.postman.com/docs/billing/resource-usage](https://learning.postman.com/docs/billing/resource-usage)
- Postman Flows Usage: [learning.postman.com/docs/billing/flows-usage](https://learning.postman.com/docs/billing/flows-usage)
- Postman Monitor Pricing: [learning.postman.com/docs/postman/monitors/pricing_monitors](https://learning.postman.com/docs/postman/monitors/pricing_monitors)
- Postman Auto-Flex: [learning.postman.com/auto-flex-policy](https://learning.postman.com/auto-flex-policy)
- Postman Buying through AWS Marketplace: [learning.postman.com/docs/billing/buying-aws](https://learning.postman.com/docs/billing/buying-aws.md)
- Postman Enterprise Organizations: [learning.postman.com/docs/administration/enterprise/organizations](https://learning.postman.com/docs/administration/enterprise/organizations.md)
- Postman Pricing: [postman.com/pricing/](https://www.postman.com/pricing/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
