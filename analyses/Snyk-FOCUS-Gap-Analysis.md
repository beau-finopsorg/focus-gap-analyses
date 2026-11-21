# Snyk & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Snyk Limited  
**Prepared:** November 17, 2026  
**Source:** Public Snyk documentation only: Credit-Based Billing policy (dated August 4, 2026); Snyk pricing page; Snyk Platform Subscription docs (Viewing your plan, Subscription mechanics, Enterprise contract types, Track credit consumption); SKU-based licensing usage settings; Snyk Learn lesson on reviewing credit consumption  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 16 Present, 11 Deviation, 3 Missing Mandatory, 20 Missing Conditional, 1 Missing Recommended, 6 N/A

---

## Executive Summary

Snyk sells developer security testing: Snyk Code (SAST), Open Source (SCA), Container, IaC, Secrets, AI-SPM, API and Web (DAST), Coding Agent Security, and AI Pentesting. Its default Enterprise plan, the Snyk Platform Subscription, is consumption-based: customers prepay credits for the contract term and Snyk draws them down daily against a versioned rate card (for example, 1.0 credit per Active Contributor per day for Code, 0.33 per Monitored Image per day for Container, 4,000 per AI Pentesting assessment). The published list price is 1 credit = $1; each customer's per-credit price is set in its Order. Unused credits expire at term end, and consumption past the prepaid balance is invoiced in arrears. Free and Team plans, and older Enterprise contracts on SKU-based licensing, are priced per contributing developer instead.

**Public billing documentation is thin.** Snyk documents its rate card and units of measure in unusual detail, and the Tenant-level Billable Events Log records each consumption event by day, mapped to its Organization and Group, with a "Download CSV" button. But the CSV's columns are not documented, no REST API for usage, credits, or cost is documented, the log carries credits and counts but no dollar amounts, and nothing public describes invoice contents, tax, or the issuing entity. Every cost column below rests on the rate card and the Order's per-credit price, not on a documented data contract.

Of the 21 Mandatory FOCUS columns, 18 have a source and 3 are missing. One gap is substantive: **EffectiveCost**, because prepaid credits bought at a negotiated per-credit price are drawn down daily and expire unredeemed at term end. **ListCost** and **ContractedCost** are rate-card joins. Because Snyk prices in credits and charges a contract-specific dollar price per credit, the four PricingCurrency columns apply, which is uncommon for a SaaS vendor and a good fit for what FOCUS v1.2 added them for.

**Recommendation:** Turn the Billable Events Log into a documented FOCUS export at the Tenant level: one Usage row per capability × Organization × day, quantity in the rate card's unit, priced in credits (PricingCurrency) and converted to USD at the Order's per-credit price, with a Purchase row for each credit pre-purchase or top-up, a CommitmentDiscount draw-down against the credit balance, and on-demand rows for overage. Expose it by API, not only as a UI download.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

- **Billable Events Log** (Tenant settings > Plan and billing > Credit breakdown; Tenant Admin role): Each consumption event "by day as its own row, mapped to its Organization and Group." Defaults to the current billing period; date range adjustable. "Download CSV" exports the log. Data has a 24-hour lag. Column names are not documented; the implied fields are day, Organization, Group, capability, and billable event.
- **Credit breakdown charts:** Monthly credit consumption by Group and by capability, filterable by Group, capability, and date range. Credits only, no dollars.
- **Your Plan page:** Current billing period, available credits, enabled capabilities, and a badge showing whether the customer transacts through AWS Marketplace or Google Cloud Marketplace.
- **SKU-based licensing usage settings** (legacy and self-serve plans): Group or Organization Settings > Usage shows test usage for the current billing period and contributing developers, with a breakdown by integration (contributors, Organizations, repos). No export or cost data documented.
- **REST API:** No usage, credit, billing, or invoice endpoint is documented. The `snyk scm contributors count` CLI tool counts contributing developers from source control for planning; it is not a billing record.

Key characteristics:

- **Rate card (credits per unit):** Code 1.0 and Open Source 1.0 per Active Contributor per day; IaC 0.33, Secrets 0.66, and AI-SPM 0.66 per Active Contributor per day; Container 0.33 per Monitored Image per day; API and Web 3.0 per Provisioned Target per day; Coding Agent Security 1.0 per Active Machine per day; AI Pentesting 4,000 per completed Assessment.
- **Units of measure:** An Active Contributor committed to a private, Snyk-monitored repo in a rolling 90-day window (human and non-human, deduplicated by email username; a partial day counts as a full day). Monitored Images deduplicate by SHA-256 digest across the account per day. A Provisioned Target is each unique base URL. An Active Machine is a device or virtual environment with qualifying telemetry that day.
- **Credits:** Pre-purchased at the start of the subscription and valid for the full contract term; drawn down daily. Unused credits expire and are not refunded, credited, carried over, or transferred. Top-ups through the account team. After the balance is exhausted, consumption is on-demand and invoiced in arrears at the contract's per-credit price.
- **Versioned rate cards:** Each Enterprise order form links a specific rate card version, which can differ from the published page. New capabilities join the rate card automatically but default to off.
- **Hierarchy:** Tenant > Group > Organization > Project. Billing lives at the Tenant. Contributor and image deduplication is account-wide, so per-Organization counts do not sum cleanly to the billed total.
- **Plans:** Free ($0, 5 Projects, test limits); Team (from $25 per month, billed monthly, up to 10 developers, card payments through Stripe); Enterprise (Snyk Platform Subscription, contact sales). Legacy plans include SKU-based licensing priced on annual high-watermark license volume.
- **Currency:** USD is the only currency mentioned.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. This analysis scopes the Snyk Platform Subscription, the default Enterprise plan and the only one with a documented consumption record. Consumption is mapped to Organizations within Groups, so the SubAccount family applies. Each billable unit (contributor, image, target, machine, assessment) is an identifiable entity, and Snyk Projects carry tags, so the Resource family and Tags apply. Prepaid term credits drawn down by usage, with overage billed separately, make the CommitmentDiscount family applicable. Snyk prices in credits at a contract-specific dollar rate, so the PricingCurrency family applies. Snyk has one billing account type, no regionally priced deployments or zones, and no capacity reservations; those columns are N/A and should exist as null. Feature levels follow the FOCUS v1.2 Content Constraints.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Snyk source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoices for credit pre-purchases, top-ups, and in-arrears overage; the Billable Events Log carries credits only, no dollar amounts | Deviation |
| EffectiveCost | Mandatory | Not available: needs the Order's per-credit price amortized across credits drawn, plus expiry of unused credits at term end | Missing: Mandatory |
| ListCost | Mandatory | Not exposed; rate card credits × quantity × $1 list price per credit | Missing: Mandatory |
| ContractedCost | Mandatory | Not exposed; rate card credits × quantity × the Order's per-credit price | Missing: Mandatory |
| BillingAccountId | Mandatory | Snyk Tenant ID | Present |
| BillingAccountName | Mandatory | Snyk Tenant name | Present |
| BillingCurrency | Mandatory | "USD" | Present |
| BillingPeriodStart | Mandatory | "Current Billing Period" start on the Your Plan page | Present |
| BillingPeriodEnd | Mandatory | Billing period end (exclusive) | Present |
| ChargePeriodStart | Mandatory | Billable Events Log day | Present |
| ChargePeriodEnd | Mandatory | Day plus one | Present |
| ChargeDescription | Mandatory | Not emitted; derive from capability and unit (e.g., "Snyk Code: Active Contributor-Day") | Deviation |
| ChargeCategory | Mandatory | Derive: "Purchase" for credit pre-purchases and top-ups; "Usage" for daily draw-down and on-demand overage; "Tax" if invoiced | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued charges | Present |
| InvoiceIssuerName | Mandatory | "Snyk Limited" for direct contracts; "Amazon Web Services" or "Google Cloud" for marketplace transactions (badge on Your Plan) | Present |
| ProviderName | Mandatory (dep. v1.3) | "Snyk" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Snyk" | Present |
| ServiceName | Mandatory | Capability: "Snyk Code", "Snyk Open Source", "Snyk Container", "Snyk IaC", "Snyk Secrets", "Snyk AI-SPM", "Snyk API and Web", "Snyk Coding Agent Security", "Snyk AI Pentesting" | Present |
| ServiceCategory | Mandatory | Derive: "Security" for all capabilities | Deviation |
| PricingQuantity | Mandatory | Daily count of billable units per capability; not documented as a log field, and deduplication is account-wide | Deviation |
| PricingUnit | Mandatory | Not emitted; normalize to "Contributor-Days", "Image-Days", "Target-Days", "Machine-Days", "Assessments" | Deviation |
| ConsumedQuantity | Conditional | Billable event count per day | Present |
| ConsumedUnit | Conditional | Implicit in the capability; normalize as for PricingUnit | Deviation |
| ListUnitPrice | Conditional | Not in data; public rate card credits × $1 | Missing: Conditional |
| ContractedUnitPrice | Conditional | Not exposed; rate card credits × the Order's per-credit price | Missing: Conditional |
| PricingCategory | Conditional | Derive: "Committed" for draw-down against prepaid credits; "Standard" for on-demand overage | Deviation |
| BillingAccountType | Conditional | N/A: one account type (Tenant) | N/A |
| SubAccountId | Conditional | Organization ID on each Billable Events Log row | Present |
| SubAccountName | Conditional | Organization name | Present |
| SubAccountType | Conditional | Not emitted; constant "Organization" | Deviation |
| ResourceId | Conditional | Not documented in the log; billed entity (contributor, image digest, target base URL, machine, or assessment) | Missing: Conditional |
| ResourceName | Conditional | Not documented; entity display name | Missing: Conditional |
| ResourceType | Conditional | Not documented; "Contributor", "Container Image", "Target", "Machine", "Assessment" | Missing: Conditional |
| SkuId | Conditional | Not exposed; capability × unit codes | Missing: Conditional |
| Tags | Conditional | Group is in the log and Project tags exist, but consumption is not attributed to Projects | Missing: Conditional |
| PricingCurrency | Conditional | Not emitted; "Credits" (Snyk's documented pricing unit for all capabilities) | Missing: Conditional |
| PricingCurrencyListUnitPrice | Conditional | Rate card credits per unit; public but not in data | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | Credits per unit from the versioned rate card linked in the Order | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | Credits drawn per row; shown in the UI but not documented in the CSV | Missing: Conditional |
| SkuMeter | Conditional | Implied by capability; no meter name emitted | Deviation |
| SkuPriceId | Conditional | Not exposed; the versioned rate card linked in each Order belongs here | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; unit definition (90-day contributor window, digest deduplication) belongs here | Missing: Conditional |
| RegionId | Conditional | N/A: no region appears in any pricing or billing surface | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | Prepaid credit balance per Order or top-up; not exported | Missing: Conditional |
| CommitmentDiscountName | Conditional | Not exposed | Missing: Conditional |
| CommitmentDiscountType | Conditional | Not exposed (e.g., "Snyk Credits") | Missing: Conditional |
| CommitmentDiscountCategory | Conditional | "Spend"; not exposed | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | "Used"/"Unused"; unused credits expire at term end but are not reported as rows | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | Credits drawn from the balance | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | "Credits" | Missing: Conditional |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number (invoice documents only; not in the Billable Events Log) | Present |
| ChargeFrequency | Recommended | Derive: "One-Time" or "Recurring" for credit purchases per the Order's payment schedule; "Usage-Based" for draw-down and overage | Deviation |
| ServiceSubcategory | Recommended | Not exposed; map each capability to an allowed v1.2 Security subcategory | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: Snyk operates the SaaS; zones are not customer-billed | N/A |

**Tally:** 16 Present, 11 Deviation, 3 Missing Mandatory, 20 Missing Conditional, 1 Missing Recommended, 6 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Tenant identity, USD billing, a public and precisely defined rate card, daily metering per capability, and a consumption log already mapped to Organization and Group. Snyk documents its units of measure (deduplication keys, rolling windows, partial-day rules) more rigorously than most SaaS vendors, which is the hard part of PricingQuantity.

**Substantive (1 of 3 Mandatory gaps):**

- **EffectiveCost.** Enterprise customers prepay credits at a negotiated per-credit price for the whole term; those credits are drawn down daily and expire unredeemed. EffectiveCost means amortizing each pre-purchase and top-up across the credits actually drawn, recording unused credits at expiry, and pricing overage at the contract rate. No documented surface carries a dollar figure at row level, let alone an amortized one.

**Trivial (2 of 3 Mandatory gaps):**

- **ListCost.** Daily quantity × rate card credits × $1. Rates are flat per unit, so the join is direct, provided the published rate card is used rather than the Order's version.
- **ContractedCost.** Daily quantity × the Order's rate card credits × the Order's per-credit price. Snyk's billing system already holds both; expose them per row.

**Substantive, beyond the column table:**

- **No documented data contract or API.** The Billable Events Log is a UI download with undocumented columns and no API. A FinOps platform cannot ingest it on a schedule without screen-level automation. This is the largest practical barrier, ahead of any single column.
- **Non-additive deduplication.** Contributors are counted once per account per day across every Organization they commit to, and images once per digest. Splitting a single billed contributor-day across three Organizations needs an allocation rule Snyk must define and document, or per-Organization rows will overstate the bill.
- **No Project-level attribution.** Chargeback in Snyk customers usually runs by application team, which maps to Projects and Project tags, not Organizations. Consumption stops at Organization.
- **Two billing models.** Free, Team, and legacy SKU-based Enterprise customers have no credit ledger at all, only test counts and contributing developers. A FOCUS export for them would be a monthly or annual Purchase row per SKU with license quantity, which is simpler but different.

### 1.5 Deviations to Fix

**BilledCost:** Emit Purchase rows for each credit pre-purchase and top-up, Usage rows for on-demand overage, and Tax rows where invoiced, so BilledCost summed per InvoiceId equals the invoice. Draw-down against prepaid credits carries BilledCost of zero.

**ChargeCategory and ChargeFrequency:** As in the table.

**ServiceCategory:** "Security" for every capability.

**PricingQuantity and PricingUnit:** One row per capability per day in the rate card's unit, using Snyk's own deduplication rules. Document the allocation rule when a contributor or image spans Organizations.

**ChargeDescription, SubAccountType, SkuMeter, ConsumedUnit, PricingCategory:** Derive from capability and purchase type.

**Already right:** USD billing, a flat published rate per unit, daily granularity, and a Tenant > Group > Organization hierarchy that maps directly to BillingAccount and SubAccount.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is a candidate release; its scope is on the FOCUS site. The v1.3 Contract Commitment dataset fits Snyk's term credit pre-purchases better than per-row CommitmentDiscount columns alone, and the v1.4 Invoice Detail dataset covers in-arrears overage invoices.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (single account type, no billed regions, zones, or reservations), the cross-Organization allocation rule, and the decision to model prepaid credits as a commitment discount.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Download one month of the Billable Events Log for a Platform Subscription tenant with an Order and an overage invoice. Document the CSV columns. Hand-build a v1.2 file and run it through the Validator. Settle the credit-as-commitment model and the cross-Organization allocation rule.

**Phase 1: Close Mandatory gaps.** Join the published rate card for ListCost and the Order's rate card and per-credit price for ContractedCost. Amortize pre-purchases and top-ups for EffectiveCost. Emit Purchase, overage Usage, and Tax rows so BilledCost reconciles to invoices.

**Phase 2: Fix deviations.** Derive ChargeCategory, ChargeFrequency, ServiceCategory, PricingCategory, SubAccountType, SkuMeter, and ChargeDescription; label units per capability.

**Phase 3: Conditional columns and delivery.** Populate the PricingCurrency family in credits; the CommitmentDiscount family for credit draw-down and expiry; the Resource family from the billed entity; SkuId, SkuPriceId (rate card version), and SkuPriceDetails; ListUnitPrice and ContractedUnitPrice; ServiceSubcategory; and Tags (Group, then Project tags once consumption reaches Projects). Deliver by REST API and scheduled push to object storage.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Contract Commitment and Invoice Detail datasets; extend the export to SKU-based and Team plans; certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **After Phase 1:** Invoice reconciliation, actuals-based budgeting, and amortized spend reporting for Snyk.
- **After Phase 2:** Security tooling spend by category alongside other providers, and mix analysis across Snyk capabilities.
- **After Phase 3:** Chargeback and showback by Group and Organization (and Project, if attribution extends); credit balance utilization and expiry-risk tracking; unit economics per contributor or per monitored image; anomaly detection on contributor and image growth; and comparison of credit-denominated and dollar-denominated cost.
- **Out of scope:** Capacity reservation management, regional cost analysis, and multi-currency billing analysis.

---

## Part 3: Immediate Next Steps

1. Reach the owners of Snyk's Platform Subscription billing and the Billable Events Log.
2. Obtain and document the Billable Events Log CSV columns, and ask whether a REST endpoint for it is planned.
3. Confirm how pre-purchases, top-ups, overage, marketplace transactions, and tax appear on invoices, and which entity issues them.
4. Ask how contributors and images that span Organizations are attributed, and whether Project-level attribution is feasible.
5. Build a v1.2 sample from one billing month and run it through the FOCUS Validator.
6. Open the RFI with `member-cert@finops.org` and confirm FinOps Foundation membership status.

---

## Confidence Summary

- **High:** Rate card, units of measure, daily draw-down, prepaid term credits, expiry without rollover, in-arrears overage, and 1 credit = $1 list come from Snyk's Credit-Based Billing policy (August 4, 2026) and pricing page.
- **High:** The Billable Events Log exists at the Tenant level, records events by day mapped to Organization and Group, exports to CSV, and shows credits rather than dollars, per Snyk's Platform Subscription docs.
- **High:** Feature levels match the bundled FOCUS v1.2 Content Constraints table (verified June 23, 2026); v1.4 remains the latest ratified version and v1.5 is a candidate release. A live spot-check through the FOCUS MCP was not run for this analysis.
- **Moderate:** No usage or billing REST API exists. None appears in the docs reviewed, but Snyk's full API reference was not searched endpoint by endpoint.
- **Moderate:** Present status for SubAccountId, SubAccountName, and ConsumedQuantity. The docs say rows map to Organization, but the CSV columns are unpublished.
- **Moderate:** Present status for invoice-sourced columns (InvoiceId, billing periods). Snyk publishes no invoice sample.
- **Moderate:** Treating prepaid credits as a spend commitment discount. If Snyk models them as simple prepayment, the seven CommitmentDiscount columns become N/A and the amortization moves entirely into EffectiveCost.
- **Moderate:** PricingCurrency as applicable. It rests on Snyk naming credits "the pricing unit for all capabilities" with a contract-specific dollar price per credit.
- **Low:** InvoiceIssuerName as "Snyk Limited." It is the entity named in site footers (registered in England and Wales); no public invoice confirms it, and US customers may be invoiced by a different Snyk entity.
- **Low:** RegionId as N/A. No billing surface shows region; if Snyk's regional hosting options carry different pricing, RegionId becomes applicable.

---

## Sources

- Snyk Credit-Based Billing policy: [snyk.io/policies/credit-based-billing/](https://snyk.io/policies/credit-based-billing/)
- Snyk Pricing: [snyk.io/pricing/](https://snyk.io/pricing/)
- Snyk Platform Subscription docs: [docs.snyk.io/platform-administration/snyk-platform-subscription](https://docs.snyk.io/platform-administration/snyk-platform-subscription)
- SKU-based licensing usage settings: [docs.snyk.io/platform-administration/snyk-hierarchy/usage-settings](https://docs.snyk.io/platform-administration/snyk-hierarchy/usage-settings)
- Snyk Learn, Review credit consumption for billing: [learn.snyk.io/lesson/review-credit-consumption-for-billing/](https://learn.snyk.io/lesson/review-credit-consumption-for-billing/)
- `snyk scm contributors count`: [docs.snyk.io](https://docs.snyk.io/developer-tools/snyk-cli/scan-and-maintain-projects-using-the-cli/cli-tools/snyk-scm-contributors-count)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
