# Supabase & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Supabase  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Supabase docs (About billing, Your monthly invoice, Billing FAQ, Control your costs, Manage Compute usage, Regions); Supabase Management API OpenAPI spec; August 2024 invoice changelog; Supabase pricing page; AWS Marketplace listing  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 13 Present, 17 Deviation, 4 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 15 N/A

---

## Executive Summary

Supabase is a managed Postgres platform. Each project is a dedicated Postgres instance with Auth, Storage, Edge Functions, Realtime, and logging attached. Billing is per organization: one plan (Free, Pro from $25, Team from $599, Enterprise custom), one billing cycle anchored to the organization's creation date, and one monthly invoice in USD. Compute is billed hourly per project; everything else is usage against organization-wide quotas, with overage billed in arrears.

**Public billing documentation is thin.** Supabase documents its invoice layout, quotas, and unit prices well, but documents no way to get billing data out other than reading it. There is no billing export, no CSV download, and no cost or invoice endpoint in the Management API. Invoices arrive by email and on the dashboard invoices page; the organization usage page shows a per-project daily breakdown on hover and nothing more. The Management API's only billing-adjacent surfaces are a per-project add-ons endpoint (selected compute size and add-ons with a list `price.amount`, no currency) and request-count analytics with no cost. This analysis therefore assesses what Supabase's invoice and data model could supply, not a dataset that exists today.

The invoice itself is better shaped than most. Since August 2024, most line items carry the project reference, quotas appear as explicit discounts, the $10 monthly compute credit appears as a discount, and tax is shown separately. Thirteen of 57 FOCUS v1.2 columns have a clean source and 17 of 21 Mandatory columns have one. The four missing Mandatory columns are the cost columns, and two of them (**BilledCost** and **EffectiveCost**) are substantive: quotas, compute credits, and prepaid credit top-ups are netted at the organization level and must be allocated back to project rows.

**Recommendation:** Publish a daily FOCUS export per organization with one row per project × line item (compute size, add-on variant, usage meter) × day, carrying project ref, region, and ListCost, BilledCost, EffectiveCost, and ContractedCost with quota and compute-credit discounts allocated to the projects that consumed them. Emit Purchase rows for the plan fee and fixed add-ons, Credit rows for top-ups and compute credits, and Tax rows. Deliver it through a Management API endpoint and a dashboard CSV download.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

- **Monthly invoice** (email and dashboard invoices page): One invoice per organization per billing cycle. It combines fixed fees for the current cycle (plan subscription, HIPAA, priority support; paid in advance) with usage fees for the previous cycle (paid in arrears). Most usage lines carry the project reference, quantity, quota, and amount, for example "Compute Hours Small" per project, Egress with a 250 GB quota and billed GB, and Custom Domain hours. Quotas and the $10 compute credit are shown as discounts. Tax is a separate line at the bottom. Supabase states its payment provider cannot regenerate past invoices.
- **Organization usage page** (dashboard only): Usage per line item for all projects or one selected project, with a daily breakdown on hover. Usage data is delayed up to one hour. No documented export.
- **Upcoming Invoice** (dashboard only): An estimate of the current cycle.
- **Management API** (`api.supabase.com/v1`): No billing, invoice, usage-cost, or spend endpoint. `GET /v1/projects` returns `ref`, `name`, `region`, `organization_slug`, `created_at`, and `status`. `GET /v1/organizations/{slug}` returns `name` and `plan`. `GET /v1/projects/{ref}/billing/addons` returns `selected_addons[]` with `type` (`compute_instance`, `custom_domain`, `pitr`, `ipv4`, `auth_mfa_phone`, `auth_mfa_web_authn`, `log_drain`, `etl_pipeline`) and a `variant` (`id` such as `ci_small` or `pitr_7`, `name`, and `price` with `type` fixed or usage, `interval` monthly or hourly, and `amount`). The `usage.api-counts` analytics endpoint returns request counts by service with no cost.

Key characteristics:

- **Compute:** Billed per project per hour, with partial hours rounded up. Micro $0.01344/hr (~$10/mo) through 16XL $5.12/hr (~$3,730/mo); larger sizes by sales. Nano is billed at the Micro rate on paid plans. Not covered by the Spend Cap.
- **Compute credits:** Paid plans include $10 per month, reset monthly, and do not cover Read Replica or Branching compute.
- **Usage items with organization-wide quotas (Pro/Team):** Egress 250 GB then $0.09/GB; cached egress 250 GB then $0.03/GB; disk 8 GB per project then $0.125/GB; MAU 100,000 then $0.00325; third-party MAU priced the same; SSO MAU 50 then $0.015; Storage 100 GB then $0.021/GB; image transformations 100 then $5 per 1,000; Edge Function invocations 2 million then $2 per million; Realtime messages 5 million then $2.50 per million; Realtime peak connections 500 then $10 per 1,000; log ingestion 20 GB then $0.50/GB.
- **Project add-ons:** Compute, Read Replicas, Disk (IOPS and throughput), PITR ($100 per month per 7 days of retention), Custom Domain ($10 per month), IPv4, Advanced MFA Phone, Log Drains ($60 per drain per month plus events and egress), Branching ($0.01344 per branch-hour), and Pipelines. Add-ons and storage are prorated to the hour.
- **Hierarchy:** Organization (billing), then projects (each with a `ref`), then branches and read replicas.
- **Regions:** 17 specific regions using AWS-style IDs (`us-east-1`, `eu-central-1`, `ap-southeast-1`, and others) plus three general regions (Americas, Europe, APAC). Project `region` is in the Management API, not on the invoice.
- **No tags:** No project tag or label feature appears in the billing or platform docs reviewed.
- **No commitment discounts:** No reserved compute or annual plans. Credit top-ups prepay future invoices and substitute for annual billing; they carry no rate benefit.
- **Invoicing:** USD only; credit card only, with alternatives for large upfront payments by ticket. The payment entity is in Singapore. Pro and Team are also sold through AWS Marketplace (for customers with AWS spend commitments) and Vercel Marketplace, where the marketplace handles tax. Sales tax, VAT, and GST roll out between May 1 and June 30, 2026.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Supabase deploys projects into named regions, so RegionId and RegionName apply. Supabase sells no commitment discounts or capacity reservations, exposes no availability zones, prices only in USD, and has no tags; those 15 columns are N/A and should exist as null. Because no machine-readable billing dataset exists, the source for each column below is the monthly invoice, joined to the Management API where noted. Feature levels follow the FOCUS v1.2 Content Constraints, spot-checked against the live spec on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Supabase source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line amounts only, on a PDF; quota and compute-credit discounts and credit top-ups are netted per organization, not allocated to project rows | Missing: Mandatory |
| EffectiveCost | Mandatory | Not available: needs the same allocation of quotas and compute credits, plus a treatment for prepaid credit top-ups | Missing: Mandatory |
| ListCost | Mandatory | Not in any dataset; gross quantity on the invoice × public unit price | Missing: Mandatory |
| ContractedCost | Mandatory | Not in any dataset; = ListCost for self-serve, Enterprise custom rates otherwise | Missing: Mandatory |
| BillingAccountId | Mandatory | Organization `slug` | Present |
| BillingAccountName | Mandatory | Organization `name` | Present |
| BillingCurrency | Mandatory | "USD" (all invoices are issued in USD) | Present |
| BillingPeriodStart | Mandatory | Invoice billing cycle start (anchored to organization creation date) | Present |
| BillingPeriodEnd | Mandatory | Invoice billing cycle end | Present |
| ChargePeriodStart | Mandatory | Not per line; current cycle for fixed fees, previous cycle for usage; daily detail exists only on the usage page | Deviation |
| ChargePeriodEnd | Mandatory | As ChargePeriodStart | Deviation |
| ChargeDescription | Mandatory | Invoice line item name (e.g., "Compute Hours Small", "Egress", "Custom Domain") | Present |
| ChargeCategory | Mandatory | Derive: "Usage" for metered items; "Purchase" for plan and fixed add-ons; "Credit" for compute credits and top-ups; "Tax" for the tax line | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for adjustments to prior cycles | Present |
| InvoiceIssuerName | Mandatory | Not named in docs (payment entity in Singapore); "Amazon Web Services" or "Vercel" for marketplace organizations | Deviation |
| ProviderName | Mandatory (dep. v1.3) | "Supabase" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Supabase" | Present |
| ServiceName | Mandatory | Invoice lines are meters, not services; map to "Supabase Database", "Supabase Auth", "Supabase Storage", "Supabase Edge Functions", "Supabase Realtime", "Supabase Logs" | Deviation |
| ServiceCategory | Mandatory | Derive: "Databases" for compute, disk, replicas, PITR, branching; "Identity" for Auth MAU and MFA; "Storage" for Storage; "Compute" for Edge Functions; "Networking" for egress, IPv4, custom domains; "Management and Governance" for logs and drains | Deviation |
| PricingQuantity | Mandatory | Billed quantity on invoice (hours, GB, MAU, invocations); must be expressed in each meter's rate block (per million, per 1,000) | Deviation |
| PricingUnit | Mandatory | Implied by line item; normalize to "Hours", "GB", "Users", "1000000 Invocations", "1000 Connections" | Deviation |
| ConsumedQuantity | Conditional | Invoice shows billed quantity and quota; total consumption must be reconstructed | Deviation |
| ConsumedUnit | Conditional | Implied; emit explicit FOCUS-format units | Deviation |
| ListUnitPrice | Conditional | Not in data; public pricing page and add-on `price.amount` | Missing: Conditional |
| ContractedUnitPrice | Conditional | Not in data; = ListUnitPrice for self-serve | Missing: Conditional |
| PricingCategory | Conditional | Derive: "Standard" (no committed pricing) | Deviation |
| BillingAccountType | Conditional | Not emitted; constant "Organization" | Deviation |
| SubAccountId | Conditional | Project `ref` on most invoice lines | Present |
| SubAccountName | Conditional | Project `name` | Present |
| SubAccountType | Conditional | Not emitted; constant "Project" | Deviation |
| ResourceId | Conditional | Project `ref` only; read replicas, branches, drains, and domains are not identified separately | Deviation |
| ResourceName | Conditional | Project name only; same limitation | Deviation |
| ResourceType | Conditional | Not emitted; derive from add-on `type` (`compute_instance`, `pitr`, `custom_domain`, and so on) | Deviation |
| SkuId | Conditional | Not on invoice; add-on variant IDs (`ci_small`, `pitr_7`) exist in the Management API | Missing: Conditional |
| SkuMeter | Conditional | Invoice line item names act as meters ("Compute Hours", "Egress", "Monthly Active Users", "Realtime Messages") | Present |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed for compute size, quota, and rate block | Missing: Conditional |
| RegionId | Conditional | Not on invoice; project `region` in the Management API | Missing: Conditional |
| RegionName | Conditional | Not on invoice; names on the Regions doc | Missing: Conditional |
| Tags | Conditional | N/A: no project tags or labels | N/A |
| PricingCurrency | Conditional | N/A: priced and billed in USD only | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: no commitment discounts; credit top-ups carry no rate benefit | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number on the dashboard invoices page | Present |
| ChargeFrequency | Recommended | Derive: "Recurring" for plan and fixed add-ons; "Usage-Based" for metered items; "One-Time" for credit top-ups | Deviation |
| ServiceSubcategory | Recommended | Not emitted; map each service to an allowed v1.2 value | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: zones are not exposed to customers | N/A |

**Tally:** 13 Present, 17 Deviation, 4 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 15 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Organization as billing account, project as sub-account on most invoice lines, USD billing, invoice numbers and cycles, meter-style line item names, explicit quota and credit discounts, separate tax, and a published price for every meter. The invoice is close to a FOCUS row set; it is just trapped in a PDF.

**Substantive (2 of 4 Mandatory gaps):**

- **BilledCost.** Quotas are organization-wide (egress, MAU, storage, invocations are summed across projects), and the $10 compute credit is one organization-level discount. Row-level BilledCost requires allocating those discounts to the projects that consumed them, plus Tax and Credit rows, so the rows sum to the invoice.
- **EffectiveCost.** Equals BilledCost once the allocation is done, except for credit top-ups: prepaid balances that pay future invoices and are taxed at purchase. Supabase must decide whether top-ups appear as a Purchase row with usage rows carrying their full cost, or as a balance applied at invoice time, and document it.

**Trivial (2 of 4 Mandatory gaps):**

- **ListCost.** Supabase owns the price list and the invoice already shows gross quantity and quota. Multiply the pre-quota quantity by the public unit price.
- **ContractedCost.** Equals ListCost for Free, Pro, and Team. Enterprise custom pricing needs the order-form rate.

**Substantive, beyond the column table:**

- **No delivery path.** There is no export, CSV, or API for billing data. Every FOCUS column depends on Supabase building one; this is the first gap, not the last.
- **Monthly grain.** The invoice is monthly. Daily per-project usage exists in the dashboard, so Supabase meters at least daily (usage is under one hour delayed), but it is not exposed.
- **Mixed periods on one invoice.** Each invoice combines current-cycle fixed fees with previous-cycle usage. Rows must carry their own ChargePeriod rather than inheriting the invoice cycle.
- **Sub-project resources.** Read replicas, branches, log drains, and custom domains roll up to the project `ref`; per-resource IDs are needed for ResourceId.

### 1.5 Deviations to Fix

**PricingQuantity, PricingUnit, ConsumedQuantity, ConsumedUnit:** Emit ConsumedQuantity as total usage before quota, and PricingQuantity in each meter's rate block (for example "1000000 Invocations" for Edge Functions, "1000000 Messages" for Realtime, "1000 Connections" for peak connections, "Hours" for compute). Keep billed-after-quota quantity as an `x_BilledQuantity` custom column.

**ServiceName and ServiceCategory:** Group meters into Supabase products. Use "Databases" for compute, disk, replicas, PITR, and branching; "Identity" for Auth; "Storage" for Storage; "Compute" for Edge Functions; "Networking" for egress, IPv4, and custom domains; and "Management and Governance" for logs and log drains.

**ChargePeriodStart and ChargePeriodEnd:** Use the previous cycle for usage rows and the current cycle for fixed fees, then move to daily rows.

**InvoiceIssuerName:** Emit the legal entity that issues direct invoices, and the marketplace for AWS and Vercel organizations.

**ResourceId, ResourceName, ResourceType:** Emit replica, branch, drain, and domain identifiers under their project; derive ResourceType from the add-on `type`.

**ChargeCategory, ChargeFrequency, PricingCategory, BillingAccountType, SubAccountType:** Derive as shown in the table.

**Already right:** Organization slug and name, project refs, USD, invoice numbers, line item names as meters, and separate quota, credit, and tax lines map cleanly.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is in release candidate with ratification scheduled for December 3, 2026. The v1.3 recency and completeness columns suit Supabase's near-real-time usage data, and the v1.4 Invoice Detail dataset fits its mixed-period invoice.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (no tags, zones, commitments, reservations, or alternate currencies) and the treatment of quotas, compute credits, and credit top-ups.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Take one month of invoices and usage-page data for a multi-project Pro organization. Hand-build a FOCUS file, run it through the Validator, and decide how quotas, compute credits, and top-ups allocate to projects.

**Phase 1: Export.** Ship a daily per-organization CSV and Management API endpoint at project × line item × day grain with BillingAccount, SubAccount, ChargePeriod, ChargeDescription, SkuMeter, ConsumedQuantity, ConsumedUnit, and RegionId. This is the prerequisite for everything else.

**Phase 2: Close Mandatory gaps.** Add ListCost and ListUnitPrice from the price list, ContractedCost and ContractedUnitPrice, and BilledCost and EffectiveCost with quota and credit discounts allocated. Add Purchase, Credit, and Tax rows so BilledCost reconciles to the invoice.

**Phase 3: Fix deviations and fill Conditional columns.** Derive ChargeCategory, ServiceName, ServiceCategory, ChargeFrequency, and PricingCategory; normalize pricing units; emit SkuId from add-on variant IDs, SkuPriceId, SkuPriceDetails, RegionName, per-resource IDs, InvoiceIssuerName, and ServiceSubcategory.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add recency and completeness columns and the Invoice Detail dataset; certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **Today, from the invoice:** Monthly spend by project for most line items, read by hand.
- **After Phase 1:** Daily usage trending, anomaly detection, and project inventory by region, in usage units.
- **After Phase 2:** Invoice reconciliation, chargeback and showback by project in dollars, and actuals-based budgeting and forecasting.
- **After Phase 3:** Cross-provider spend by service category, compute rightsizing by instance size, and unit economics per MAU or per invocation.
- **Out of scope:** Commitment utilization, capacity reservation management, availability zone analysis, and tag-based allocation (unless Supabase adds project labels).

---

## Part 3: Immediate Next Steps

1. Follow up with the Supabase contact from KubeCon NA 2026 to identify the owner of billing and the Management API.
2. Confirm whether daily per-project, per-meter usage can be exported from the system behind the usage page.
3. Confirm the legal entity on direct invoices, how Enterprise contracts are priced and invoiced, and whether any Enterprise contract includes commitments.
4. Confirm whether project tags or labels are planned.
5. Build a v1.2 sample from one month of a multi-project organization and run it through the FOCUS Validator.
6. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Supabase has no billing export, CSV download, or billing, invoice, or cost endpoint in the Management API. No doc reviewed mentions one, and the OpenAPI spec's billing paths cover add-on configuration only.
- **High:** Invoice structure (mixed fixed and usage periods, project refs on most lines, quotas and compute credits as discounts, separate tax), USD-only billing, hourly compute pricing, quotas, and unit prices, from Supabase docs and the pricing page.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints; spot-checked against the live spec on November 17, 2026, and v1.4 remains the latest ratified version.
- **Moderate:** Supabase has no tags. No tag feature appears in the docs reviewed; the organization response has an undocumented `opt_in_tags` field that does not appear to be resource tagging.
- **Moderate:** CommitmentDiscount N/A. True for self-serve plans and top-ups; Enterprise contract terms are not public and could include commitments.
- **Moderate:** Management API field lists for projects, organizations, and add-on analytics were read partly from a summary of the OpenAPI spec; the add-ons response and analytics response shapes were read directly.
- **Low:** InvoiceIssuerName. Docs name only a payment entity in Singapore, not the invoicing legal entity.
- **Low:** Which invoice lines lack a project ref. Supabase says "the majority" carry one; organization-level lines (plan fee, MAU, likely others) must be allocated or left with a null SubAccountId.

---

## Sources

- About billing on Supabase: [supabase.com/docs/guides/platform/billing-on-supabase](https://supabase.com/docs/guides/platform/billing-on-supabase)
- Your monthly invoice: [supabase.com/docs/guides/platform/your-monthly-invoice](https://supabase.com/docs/guides/platform/your-monthly-invoice)
- Billing FAQ: [supabase.com/docs/guides/platform/billing-faq](https://supabase.com/docs/guides/platform/billing-faq)
- Control your costs: [supabase.com/docs/guides/platform/cost-control](https://supabase.com/docs/guides/platform/cost-control)
- Manage Compute usage: [supabase.com/docs/guides/platform/manage-your-usage/compute](https://supabase.com/docs/guides/platform/manage-your-usage/compute)
- Improved invoices and more timely usage data (changelog): [supabase.com/changelog/28480](https://supabase.com/changelog/28480-improved-invoices-and-more-timely-usage-data)
- Regions: [supabase.com/docs/guides/platform/regions](https://supabase.com/docs/guides/platform/regions)
- Management API OpenAPI spec: [api.supabase.com/api/v1-json](https://api.supabase.com/api/v1-json)
- Supabase Pricing: [supabase.com/pricing](https://supabase.com/pricing)
- Supabase on AWS Marketplace: [aws.amazon.com/marketplace/pp/prodview-zjciuce2qsb3q](https://aws.amazon.com/marketplace/pp/prodview-zjciuce2qsb3q)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
