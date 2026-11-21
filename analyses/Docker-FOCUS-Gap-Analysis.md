# Docker & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Docker, Inc.  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Docker Home billing (Invoices, Costs, Usage, and Credits pages with CSV export); Docker Hub pull usage CSV; Docker Hub API (2-beta); Docker pricing page and plan docs  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 19 Present, 8 Deviation, 2 Missing Mandatory, 14 Missing Conditional, 1 Missing Recommended, 13 N/A

---

## Executive Summary

Docker sells per-user subscriptions (Personal, Pro, Team, Business) billed monthly or annually, plus usage-based products: Docker Build Cloud minutes, Testcontainers Cloud minutes, and the pay-as-you-go Docker Agentic Platform (which includes Docker Offload). Add-ons such as Docker Hardened Images are billed annually per repository. All charges are in USD.

Docker already has most of the raw material for FOCUS. The Costs page groups each billing period's charges by product and exports CSV; the Usage page breaks usage-based charges down by product and meter and also exports CSV; invoices carry line items with description, quantity, unit price, and amount. Nineteen of 57 FOCUS v1.2 columns map directly, and 19 of 21 Mandatory columns have a source.

Two Mandatory columns are missing, and one of them is substantive. **EffectiveCost** is the real gap: annual plans and prepaid minute blocks are paid up front, and credits are applied only at the end of the billing period, so no current export shows amortized, credit-adjusted cost per charge. **ListCost** is plumbing: Docker owns the price book and needs only to join it to each line.

The larger problems sit outside the column table. Docker has no public billing or cost API; the CSV exports are UI-only and their column names are undocumented. Sales-managed accounts see only an Overview page and must request invoices from their rep. Agentic Platform usage bills to the individual account even when the user belongs to an organization, so an organization-scoped export misses that spend. Cost allocation is weak: there are no billing tags, and the Costs CSV is grouped by product, not by resource, team, or user.

**Recommendation:** Publish a monthly FOCUS export per organization (and per company, where consolidated billing applies) with one row per product × meter × billing period for usage, one Purchase row per subscription or prepaid block, and separate Tax and Credit rows so the dataset reconciles to the invoice. Expose it through an API, not only the Docker Home UI.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

Docker publishes no billing API. All billing data lives in Docker Home under **Billing**:

- **Invoices:** Issued whenever a subscription renews or changes, and monthly in arrears for on-demand usage. Fields: invoice number, date of issue, due date, bill-to, line items (description, quantity where applicable, unit price, amount), subtotal before discounts, total, and amount due in USD. PDF download.
- **Costs:** Charges for one billing period grouped by product in a **Resource** column, with period status, amounts excluding tax, cost to date, subtotal, and credits. CSV export. Docker notes that the invoice total can differ because the invoice adds tax and credits.
- **Usage:** Charts of usage-based charges, filterable by period, product, and meter, covering Build Cloud minutes, Testcontainers Cloud minutes, and Agentic Platform compute. CSV export.
- **Credits:** Balances per product and each grant's remaining amount. Credits apply at the end of the billing period.
- **Docker Hub pull usage CSV:** Hourly pulls per repository (`datehour`, `user_name`, `repository`, `access_token_name`, `ips`, `repository_privacy`, `tag`, `digest`, `version_checks`, `pulls`). It carries no cost data.
- **Docker Hub API (2-beta):** Covers organizations, groups (teams), repositories, members, access tokens, and audit logs. It has no billing, invoice, subscription, or usage endpoints.

Key characteristics:

- **Seat subscriptions:** Pro ($9 annual, $11 monthly), Team ($15 annual, $16 monthly), and Business ($24 annual) per user per month. Seats added mid-cycle are prorated; removed seats take effect at the next cycle.
- **Usage-based products:** Testcontainers Cloud on demand at $4 per 100 minutes, billed monthly in arrears. Agentic Platform metered in seconds by sandbox runtime and vCPU plus memory configuration. Build Cloud minutes beyond the plan allocation are bought in blocks.
- **Prepaid blocks:** Build Cloud minutes and Testcontainers Cloud minutes ($3 per 100 minutes, sold through sales) are purchased up front and expire at the end of the billing period. Business customers can also prepay Scout repositories and Hub consumption.
- **Negotiated pricing:** Business volume pricing through sales from 25 seats.
- **Hierarchy:** Company > Organization > Team. Billing applies to the individual account or organization. Only Business customers can create a company.
- **No tags, no regions:** No billing labels exist, and nothing is priced by region.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Docker's prepaid, expiring minute blocks behave like a usage-based commitment discount (sold below the on-demand rate, drawn down, unused balance forfeited), so this analysis treats the CommitmentDiscount family as applicable. Docker has no capacity reservations, regions, alternate pricing currencies, or billing tags; those columns are N/A and should exist as null. Feature levels below follow the FOCUS v1.2 Content Constraints, spot-checked against the live spec on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Docker source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Costs CSV amount per product (excludes tax and credits); invoice line amount | Deviation |
| EffectiveCost | Mandatory | Not available: needs amortization of annual plans and prepaid blocks plus end-of-period credit allocation | Missing: Mandatory |
| ListCost | Mandatory | Not in exports; join Docker price book × PricingQuantity | Missing: Mandatory |
| ContractedCost | Mandatory | Invoice unit price × quantity (reflects negotiated Business rates) | Present |
| BillingAccountId | Mandatory | Organization or personal account namespace that owns the billing | Present |
| BillingAccountName | Mandatory | Organization name or account username | Present |
| BillingCurrency | Mandatory | "USD" | Present |
| BillingPeriodStart | Mandatory | Billing period start on the Costs page (anchored to subscription date) | Present |
| BillingPeriodEnd | Mandatory | Billing period end on the Costs page | Present |
| ChargePeriodStart | Mandatory | Billing period start (Costs and Usage are period-level) | Present |
| ChargePeriodEnd | Mandatory | Billing period end | Present |
| ChargeDescription | Mandatory | Invoice line item description | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for seats, annual add-ons, and prepaid blocks; "Usage" for on-demand minutes and Agentic Platform; "Tax" and "Credit" rows from invoice | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for any re-issued charges | Present |
| InvoiceIssuerName | Mandatory | "Docker, Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "Docker" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Docker" | Present |
| ServiceName | Mandatory | Costs CSV Resource (e.g., "Docker Business", "Docker Build Cloud", "Testcontainers Cloud", "Docker Agentic Platform", "Docker Hardened Images") | Present |
| ServiceCategory | Mandatory | Derive: "Developer Tools" for subscriptions, Build Cloud, and Testcontainers Cloud; "Compute" for Agentic Platform and Offload; "Security" for Scout and Hardened Images | Deviation |
| PricingQuantity | Mandatory | Invoice quantity "if applicable"; must be non-null on every non-Tax row | Deviation |
| PricingUnit | Mandatory | Normalize: "Users", "Minutes", "Repositories"; define a single rate basis for Agentic Platform's vCPU plus memory meter | Deviation |
| ConsumedQuantity | Conditional | Usage CSV meter quantity | Present |
| ConsumedUnit | Conditional | Usage CSV meter unit; normalize to FOCUS unit format | Deviation |
| ListUnitPrice | Conditional | Not in exports; public price page for plans, internal rate card for Agentic Platform | Missing: Conditional |
| ContractedUnitPrice | Conditional | Invoice unit price | Present |
| PricingCategory | Conditional | Derive: "Standard" for seats and on-demand usage; "Committed" for usage drawn from prepaid blocks | Deviation |
| BillingAccountType | Conditional | "Organization" or "Personal" | Present |
| SubAccountId | Conditional | N/A: billing is per organization; teams are not billing entities | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | Not exposed: Costs CSV is product-level; candidates are seat (user), repository, builder, and sandbox IDs | Missing: Conditional |
| ResourceName | Conditional | Not exposed | Missing: Conditional |
| ResourceType | Conditional | Not exposed | Missing: Conditional |
| SkuId | Conditional | Not exposed; internal plan and product codes | Missing: Conditional |
| Tags | Conditional | N/A: no billing tags or labels | N/A |
| PricingCurrency | Conditional | N/A: priced and billed in USD only | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Usage page meter (e.g., Build Cloud minutes, Testcontainers Cloud minutes, Agentic Platform compute) | Present |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed for monthly vs. annual and prepaid vs. on-demand price points | Missing: Conditional |
| RegionId | Conditional | N/A: no region-based pricing or billing | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | Prepaid minute block or prepaid Hub consumption ID; not exposed | Missing: Conditional |
| CommitmentDiscountName | Conditional | Not exposed | Missing: Conditional |
| CommitmentDiscountType | Conditional | Not exposed (e.g., "Prepaid Minutes") | Missing: Conditional |
| CommitmentDiscountCategory | Conditional | "Usage" for minute blocks; not exposed | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | "Used"/"Unused"; unused minutes expire at period end | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | Minutes drawn from the block | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | "Minutes" | Missing: Conditional |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number | Present |
| ChargeFrequency | Recommended | Derive: "Recurring" for seats and annual add-ons; "One-Time" for prepaid blocks; "Usage-Based" for on-demand minutes | Deviation |
| ServiceSubcategory | Recommended | Not exposed; map each product to an allowed v1.2 ServiceSubcategory value | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: no zones | N/A |

**Tally:** 19 Present, 8 Deviation, 2 Missing Mandatory, 14 Missing Conditional, 1 Missing Recommended, 13 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Billing account, currency, billing periods, product-level cost, invoice line descriptions, contracted unit prices, invoice numbers, and usage meters already exist in Docker Home.

**Substantive (1 of 2 Mandatory gaps):**

- **EffectiveCost.** Annual plans and Hardened Images are paid up front; prepaid minute blocks are bought before use; credits apply only at period end. Producing EffectiveCost means amortizing purchases across the service term and allocating credits back to the charges they offset. No current export does this.

**Trivial (1 of 2 Mandatory gaps):**

- **ListCost.** Docker owns the price book. Join list unit price by plan, billing cadence, and meter, then multiply by PricingQuantity.

**Substantive, beyond the column table:**

- **No API.** CSV exports are UI-only with undocumented columns. A FOCUS dataset that FinOps tools can ingest needs a programmatic delivery path (API or scheduled object-storage drop).
- **Sales-managed accounts.** These see only Overview and request invoices from their rep, so the largest Business customers have the least self-serve billing data.
- **Agentic Platform scope.** Usage bills to the individual account even when the user is in an organization. An organization-scoped FOCUS export will miss it unless Docker either moves billing to the organization or includes member usage with a SubAccount or Resource attribution.
- **Allocation.** The Costs CSV is product-level. Without ResourceId (seat, repository, builder, sandbox) or tags, customers cannot charge back Docker spend to teams.

### 1.5 Deviations to Fix

**BilledCost:** The Costs CSV excludes tax and credits, and the invoice applies discounts below the subtotal. Emit Tax rows and Credit rows (and Credit or Adjustment rows for invoice-level discounts) so that the sum of BilledCost per InvoiceId equals the invoice total.

**ChargeCategory:** "Purchase" for seat subscriptions, annual add-ons, and prepaid blocks; "Usage" for on-demand and drawn-down minutes and Agentic Platform compute; "Tax" and "Credit" as above.

**ServiceCategory:** "Developer Tools" for subscriptions, Build Cloud, and Testcontainers Cloud; "Compute" for Agentic Platform and Offload; "Security" for Scout and Hardened Images.

**PricingQuantity and PricingUnit:** Every non-Tax row needs a quantity. Use "Users" for seats, "Minutes" for Build Cloud and Testcontainers Cloud, and "Repositories" for Hardened Images and Scout. The Agentic Platform meter combines runtime with a vCPU plus memory configuration, so PricingQuantity must be computed against the rate basis rather than copied from runtime seconds.

**ChargeFrequency and PricingCategory:** Derive from product type as shown in the table.

**Already right:** USD-only billing, invoice numbers, explicit unit prices on invoice lines, and a meter dimension on the Usage page. These map cleanly.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is in release candidate with ratification scheduled for December 3, 2026; its Invoice Detail and billing-period datasets (introduced in v1.4) suit Docker's invoice-centric model.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (no regions, reservations, tags, or alternate currencies) and the decision on modeling prepaid blocks as commitment discounts.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Export one billing period of Costs and Usage CSV for a self-serve Business organization and a sales-managed one. Run a hand-built FOCUS file through the Validator. Decide whether prepaid minute blocks are modeled as commitment discounts.

**Phase 1: Close Mandatory gaps.** Join the price book for ListCost and ListUnitPrice. Build amortization for annual and prepaid purchases and allocate end-of-period credits to produce EffectiveCost. Add Tax and Credit rows so BilledCost reconciles to the invoice.

**Phase 2: Fix deviations.** Derive ChargeCategory, ServiceCategory, ChargeFrequency, and PricingCategory; normalize PricingUnit and ConsumedUnit; populate PricingQuantity on every non-Tax row.

**Phase 3: Allocation and Conditional columns.** Add ResourceId, ResourceName, and ResourceType (seat, repository, builder, sandbox); SkuId, SkuPriceId, and SkuPriceDetails; the CommitmentDiscount family for prepaid blocks; and ServiceSubcategory. Bring Agentic Platform member usage into the organization export. Ship an API or scheduled export.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Invoice Detail dataset; certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **After Phase 1:** Invoice reconciliation, actuals-based budgeting and forecasting, and amortized spend reporting.
- **After Phase 2:** Spend by service category across providers, and usage-versus-subscription mix analysis.
- **After Phase 3:** Chargeback and showback by team or repository, unit economics per build or test minute, prepaid block utilization, and anomaly detection on metered products.
- **Out of scope:** Region-based analysis, capacity reservation management, and tag-based allocation (unless Docker adds labels).

---

## Part 3: Immediate Next Steps

1. Confirm with Docker billing which CSV columns the Costs and Usage exports emit today.
2. Confirm the invoicing legal entity and whether company-level consolidated billing exists.
3. Build a v1.2 sample from one billing period and run it through the FOCUS Validator.
4. Agree on the prepaid-block commitment model and the Agentic Platform rate basis.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Docker has no public billing API; the Hub API has no billing, invoice, or usage endpoints. Billing is USD-only. Invoice fields and the Costs, Usage, and Credits page descriptions are taken from Docker's docs.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints; the bundled table was spot-checked against the live spec on November 17, 2026, and v1.4 remains the latest ratified version.
- **Moderate:** Present status for columns sourced from the Costs and Usage CSVs. Docker does not document those column names, so presence is inferred from the UI fields.
- **Moderate:** Treating prepaid minute blocks as commitment discounts. If Docker models them as plain Purchases with no rate benefit, the seven CommitmentDiscount columns become N/A.
- **Moderate:** Agentic Platform PricingUnit. Docker publishes no rates for it, so the rate basis is unknown.
- **Low:** InvoiceIssuerName as "Docker, Inc." No page names the invoicing entity; non-US contracting entities may exist.
- **Low:** Build Cloud plan allocations and overage pricing. Current docs and the pricing page no longer publish them, and older FAQ figures may be stale.

---

## Sources

- Docker Subscription and Billing: [docs.docker.com/subscription-billing/](https://docs.docker.com/subscription-billing/)
- Docker Manage Billing (Invoices, Costs, Usage, Credits): [docs.docker.com/subscription-billing/manage/](https://docs.docker.com/subscription-billing/manage/)
- Docker Invoices and Billing History: [docs.docker.com/billing/history/](https://docs.docker.com/billing/history/)
- Docker Payment Methods: [docs.docker.com/billing/payment-method/](https://docs.docker.com/billing/payment-method/)
- Docker Plans: [docs.docker.com/subscription/plans/docker/](https://docs.docker.com/subscription/plans/docker/)
- Docker Manage Seats: [docs.docker.com/subscription/manage-seats/](https://docs.docker.com/subscription/manage-seats/)
- Docker Agentic Platform Billing: [docs.docker.com/subscription-billing/plans/docker-agentic-platform/](https://docs.docker.com/subscription-billing/plans/docker-agentic-platform/)
- Docker Hub Pull Usage: [docs.docker.com/docker-hub/usage/pulls/](https://docs.docker.com/docker-hub/usage/pulls/)
- Docker Company Management: [docs.docker.com/admin/company/](https://docs.docker.com/admin/company/)
- Docker Hub API: [docs.docker.com/reference/api/hub/latest/](https://docs.docker.com/reference/api/hub/latest/)
- Docker Pricing and FAQ: [docker.com/pricing/](https://www.docker.com/pricing/), [docker.com/pricing/faq/](https://www.docker.com/pricing/faq/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
