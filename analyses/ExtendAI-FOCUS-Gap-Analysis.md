# Extend (ExtendAI) and FOCUS: Conformance Gap and Adoption Roadmap

*Analysis run: August 4, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Prepared:** 2026-08-04
**Provider and product in scope:** Extend, the LLM document-processing platform at extend.ai / extend.app (Parse, Extract, Classify, Split, Edit, Workflows, and the per-run usage/credit data it emits).
**Source analyzed:** Public product and developer documentation: the pricing page, the "How Credits Work" billing guide, and the API reference (the extract-run `usage` object).
**FOCUS baseline:** v1.2 (current certification baseline). **Build target:** v1.4 (ratified 2026-06-04).
**Data quality:** Provisional. This assessment is built from public documentation for a small startup, not from a customer billing export or a billing API contract. There is no formal FOCUS conformance claim.

---

## Disambiguation assumption (read first)

The name "Extend" maps to several distinct companies. This report analyzes **Extend, the AI document-processing company at extend.ai (also extend.app), handle @ExtendHQ, GitHub `extend-hq`, a Y Combinator company**. Its product is "document processing infrastructure for AI agents": LLM-based parsing, extraction, classification, splitting, and editing of documents, sold on a credit-based, per-page usage model.

This is not "Extend" the virtual-card / spend fintech (paywithextend.com), and not "Extend" the extended-warranty / product-protection company (extend.com). If the intended subject is either of those, this analysis does not apply and should be re-scoped. Everything below assumes the document-AI platform.

---

## Executive summary

Extend meters usage well and prices it in credits, but it does not yet publish a cost dataset in currency. Every processed run returns a structured, itemized `usage` object with per-page quantities, units, and an itemized `charges` array, timestamped in UTC, and usage can be tagged and grouped by workspace, API key, processor, and usage tag. That is a strong, granular usage foundation. The gap for FOCUS is the cost layer: the record carries **credits**, an internal billing unit, not a currency amount, and the FOCUS cost quartet (ListCost, BilledCost, EffectiveCost, ContractedCost) is absent. Converting credits to currency is a reconciliation against the plan rate card and any volume or annual-commitment terms, so the cost columns are a substantive gap, not a copy.

Of the 57 FOCUS v1.2 columns: 1 Present, 7 Present with a deviation to fix, 18 Missing Mandatory (4 of them substantive, all in the cost quartet; the other 14 trivial), 3 Missing Recommended, 16 Missing Conditional, and 12 N/A. The eight usable columns are the per-run usage fields (quantities, units, resource identity, tags, charge time) under Extend-native names and shapes.

**Readiness (data source reviewed, not a certification result):**

| Dimension | Rating |
|---|---|
| Cost | Gap |
| Granularity | Strong |
| Allocation | Partial |
| Coverage | Gap |
| FOCUS shape | Gap |
| **Overall band** | **Emerging** |

**Recommendation:** Publish a cost dataset that expresses each run in currency, not just credits. Multiply metered credits by the account's per-credit rate to produce ListCost, and reconcile volume discounts and annual-commitment burn-down into BilledCost and EffectiveCost. Emit the trivial Mandatory constants and derivations (provider and issuer names, service category, billing account identity, charge period boundaries), convert `extend:usage_tags` from a bare-string array to key-value Tags, and expose the workspace hierarchy as SubAccount columns. The granularity and usage detail already exceed most emerging feeds; the missing piece is a currency-denominated, FOCUS-shaped billing view.

---

## Part 1: The conformance gap

Extend sells document processing on a credit model: each run of a processor (Parse, Extract, Classify, Split, Edit, Form Detection) consumes a base number of credits per page, at a plan-specific per-credit rate, with optional surcharges and multipliers. The platform exposes this as a rich per-run usage object and a filterable usage dashboard. The gap is that this is usage metering, not a billing dataset: it is granular and itemized, but not expressed in currency and not FOCUS-shaped.

### 1.1 The data source

The analyzable surface is the per-run `usage` object on the processor-run API responses (documented on the extract-run endpoint) plus the credit model and dashboard described in "How Credits Work."

- **Grain:** one processor run (for example, an extract run `exr_...`) over one file, with `createdAt` and `updatedAt` as RFC 3339 UTC timestamps. Runs are event-level and effectively real time.
- **Usage object:** `usage.credits` (billed credits for the run), `usage.totalCredits` (rolls up work the run triggered, such as an automatic parse), and `usage.breakdown[]`, where each entry carries its own `credits` and a `charges[]` array. Each charge itemizes `product` (for example `extraction_performance`, `review_agent`, `agentic_text_correction`), `unit` (`page`), `quantity`, `credits`, and for page-scoped add-ons the exact `pages[]` that incurred the charge.
- **Pricing model:** credits are the universal billing unit. Base rates are per page by action and mode (Performance vs Light), with surcharges (Review Agent, agentic corrections) and multipliers (priority parsing 2x, large-array extraction 2x); advanced Excel parsing is billed per 1,000 cells. Dollar cost equals credits times the plan's per-credit rate.
- **Plans:** Pay As You Go ($0.0125 per credit, 10,000 credits free), Scale ($500 per month, 50,000 credits included, $0.01 per credit, volume discounts available), and Enterprise (custom per-credit pricing, multiple workspaces, advanced RBAC, SSO/SAML). Annual plans track usage against a prepaid balance or a dollar commitment.
- **Identity and hierarchy:** API keys are organization-scoped or workspace-scoped; the `x-extend-workspace-id` header targets a workspace, and Enterprise supports multiple workspaces. Runs reference a `file` (id, name, type, page count) and a dashboard URL.
- **Allocation dimensions:** runs accept `extend:usage_tags` (an array of bare strings) in run metadata; the dashboard filters and groups credit usage by Usage Tags, Processors, Workflows, API Keys, and Charge Types.

Key limitations for FOCUS:

- **No currency on the record:** cost is expressed only in credits. There is no per-line amount in a currency, and no `BillingCurrency` on the record (USD is implied by the published rates, not stated per row).
- **No billing-period or invoice dataset via API:** the dashboard Billing page shows annual usage to date against a plan, but there is no documented line-item cost export tied to an invoice or a billing period.
- **Tags are bare strings:** `extend:usage_tags` is an array of single strings, not key-value pairs.
- **Hierarchy is thin outside Enterprise:** multiple workspaces are an Enterprise feature; single-workspace accounts have no sub-account structure.
- **No commitment-discount mechanic in the FOCUS sense:** volume discounts and annual prepaid balances exist, but there is no per-line commitment-discount attribution.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory (must be present and populated), Conditional (required when the provider's model triggers the condition), Recommended (encouraged), or Optional. Conformance is judged column by column against the Requirements Model. A dataset conforms when every Mandatory column is present and correctly populated, every applicable Conditional column is handled, Tags are key-value pairs, enumerated columns carry valid members, and types, currency, and date formats follow the spec. Feature levels for this report were verified against the FOCUS v1.2 specification content-constraint tables.

### 1.3 Column-by-column status

Legend: Present; Present, deviation to fix; Missing: Mandatory; Missing: Recommended; Missing: Conditional; N/A: null valid.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No (SaaS, no zones) | N/A: null valid |
| BilledCost | M | No (credits only, needs rate reconciliation) | Missing: Mandatory |
| BillingAccountId | M | No (organization identity exists off-record) | Missing: Mandatory |
| BillingAccountName | M | No (account lookup) | Missing: Mandatory |
| BillingAccountType | C | No | Missing: Conditional |
| BillingCurrency | M | No (credits, not currency; USD implied) | Missing: Mandatory |
| BillingPeriodEnd | M | No (billing month derivable) | Missing: Mandatory |
| BillingPeriodStart | M | No (billing month derivable) | Missing: Mandatory |
| CapacityReservationId | C | No | N/A: null valid |
| CapacityReservationStatus | C | No | N/A: null valid |
| ChargeCategory | M | No (constant "Usage" for run feed) | Missing: Mandatory |
| ChargeClass | M | No (null; corrections not in feed) | Missing: Mandatory |
| ChargeDescription | M | No (derivable from product/processor) | Missing: Mandatory |
| ChargeFrequency | R | No (constant "Usage-Based") | Missing: Recommended |
| ChargePeriodEnd | M | No (derivable from run timestamps) | Missing: Mandatory |
| ChargePeriodStart | M | Partial (createdAt on the run) | Present, deviation to fix |
| CommitmentDiscountCategory | C | No (no per-line commitment mechanic) | N/A: null valid |
| CommitmentDiscountId | C | No | N/A: null valid |
| CommitmentDiscountName | C | No | N/A: null valid |
| CommitmentDiscountQuantity | C | No | N/A: null valid |
| CommitmentDiscountStatus | C | No | N/A: null valid |
| CommitmentDiscountType | C | No | N/A: null valid |
| CommitmentDiscountUnit | C | No | N/A: null valid |
| ConsumedQuantity | C | Yes (charges.quantity, e.g. pages) | Present, deviation to fix |
| ConsumedUnit | C | Yes (charges.unit = "page") | Present, deviation to fix |
| ContractedCost | M | No (credits only, needs rate reconciliation) | Missing: Mandatory |
| ContractedUnitPrice | C | No (per-credit rate lives in the plan) | Missing: Conditional |
| EffectiveCost | M | No (credits only, needs rate reconciliation) | Missing: Mandatory |
| InvoiceId | R | No | Missing: Recommended |
| InvoiceIssuerName | M | No (constant "Extend") | Missing: Mandatory |
| ListCost | M | No (credits times list per-credit rate) | Missing: Mandatory |
| ListUnitPrice | C | No (rate card, not on the run) | Missing: Conditional |
| PricingCategory | C | No (constant "On-Demand"/"Standard") | Missing: Conditional |
| PricingCurrency | C | No (constant USD once currency exists) | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | C | No | Missing: Conditional |
| PricingCurrencyEffectiveCost | C | No | Missing: Conditional |
| PricingCurrencyListUnitPrice | C | No | Missing: Conditional |
| PricingQuantity | M | Yes (charges.quantity) | Present, deviation to fix |
| PricingUnit | M | No (equals charges.unit = "page") | Missing: Mandatory |
| ProviderName | M (removed v1.4) | No (constant "Extend") | Missing: Mandatory |
| PublisherName | M (removed v1.4) | No (constant "Extend") | Missing: Mandatory |
| RegionId | C | No (SaaS, not region-scoped on record) | N/A: null valid |
| RegionName | C | No | N/A: null valid |
| ResourceId | C | Partial (run id or file id) | Present, deviation to fix |
| ResourceName | C | Partial (file name) | Present, deviation to fix |
| ResourceType | C | No (derivable, e.g. "Document"/"ExtractRun") | Missing: Conditional |
| ServiceCategory | M | No (constant "AI and Machine Learning") | Missing: Mandatory |
| ServiceName | M | Yes (the product/processor, e.g. "Extract") | Present |
| ServiceSubcategory | R | No | Missing: Recommended |
| SkuId | C | No (product + mode + plan is the effective SKU) | Missing: Conditional |
| SkuMeter | C | No (the billable metric, pages) | Missing: Conditional |
| SkuPriceDetails | C | No | Missing: Conditional |
| SkuPriceId | C | No | Missing: Conditional |
| SubAccountId | C | No (workspace id exists off-record; Enterprise) | Missing: Conditional |
| SubAccountName | C | No (workspace name; Enterprise) | Missing: Conditional |
| SubAccountType | C | No | Missing: Conditional |
| Tags | C | Yes (extend:usage_tags, bare-string array) | Present, deviation to fix |

**Reading the tally.** Of 57 v1.2 columns: 1 Present, 7 Present with a deviation, 18 Missing Mandatory, 3 Missing Recommended, 16 Missing Conditional, and 12 N/A. Of the 21 Mandatory columns, 3 carry usable data (ServiceName clean; ChargePeriodStart and PricingQuantity under native shapes) and 18 are missing. Of those 18, only 4 are substantive (the cost quartet: ListCost, BilledCost, EffectiveCost, ContractedCost). The other 14 are trivial constants or derivations.

### 1.4 What's solved, and what remains

**Solved or near-solved.** Extend already meters the hard part: a per-run, itemized usage object with quantities, units, per-product charges, and page-level attribution, timestamped in UTC. Consumed and pricing quantities and units are present as `charges.quantity` and `charges.unit`. Resource identity (run and file), a charge timestamp (`createdAt`), a service name (the processor product), and allocation tags all exist. Dates are ISO 8601. This is a genuinely granular, machine-readable usage feed.

**Substantive gaps.** The cost quartet is the real work. Each record carries credits, not currency. Producing FOCUS cost columns means:

- **ListCost:** metered credits times the account's list (Pay As You Go) per-credit rate. Derivable in principle, but the rate table lives outside the run record and varies by action, mode, and surcharge, so it is a join, not a field copy.
- **BilledCost and EffectiveCost:** these must reconcile the plan's actual economics: the Scale monthly platform fee and included-credit allotment, volume discounts, and annual prepaid or dollar-commitment burn-down. When an account draws down a prepaid balance or crosses a volume tier, BilledCost and EffectiveCost diverge from a naive credits-times-list-rate figure. This is a reconciliation against contract terms, the phrase that signals a substantive gap.
- **ContractedCost:** the negotiated-rate view, which for Enterprise custom per-credit pricing diverges from list.

Because the currency layer, the billing period, and the invoice association are all absent from the documented API, the cost columns cannot be treated as a trivial copy.

**Trivial gaps (plumbing, derivable from data already present or from constants).**

- Constants: `InvoiceIssuerName`, `ProviderName`, `PublisherName` are "Extend"; `ServiceCategory` is "AI and Machine Learning"; `ChargeCategory` is "Usage" for the run feed; `ChargeClass` is null; `PricingCategory` is "On-Demand".
- Derivations: `ChargeDescription` from the product/processor; `BillingAccountId` and `BillingAccountName` from the organization; `BillingPeriodStart` and `BillingPeriodEnd` from the billing cycle; `ChargePeriodEnd` from the run timestamps; `PricingUnit` equals `ConsumedUnit` ("page").
- `BillingCurrency` becomes a trivial constant ("USD") once the records are expressed in currency at all.

### 1.5 Deviations to fix

- **Tags:** `extend:usage_tags` is an array of bare strings, and FOCUS Tags must be key-value pairs. Emit them as keyed pairs (for example `environment=production`) rather than a flat list.
- **ConsumedQuantity, ConsumedUnit, PricingQuantity:** present inside the `charges[]` array as `quantity` and `unit`. Surface them as top-level FOCUS columns per charge line. For per-page products, PricingQuantity equals the page count; for advanced Excel parsing, which is billed per 1,000 cells, PricingQuantity is computed against the per-cell rate basis, not copied from a page count.
- **ChargePeriodStart:** `createdAt` is an instantaneous run timestamp. Emit it as `ChargePeriodStart` and derive `ChargePeriodEnd` (equal for an instantaneous charge, or the run's `updatedAt`).
- **ResourceId and ResourceName:** the run id and file identity carry the right meaning; emit them under the FOCUS column IDs, and decide whether the resource is the document or the run.
- **Credit convenience fields:** `usage.credits` and `usage.totalCredits` are internal units. Keep them as provider-specific columns prefixed `x_` (for example `x_UsageCredits`) alongside the currency cost columns, rather than mapping credits into a FOCUS cost column.

**Already done right:** ISO 8601 UTC timestamps, per-page quantities and units, an itemized per-product charge breakdown with page-level attribution, and a service name on every run.

---

## Part 2: The path forward

Baseline v1.2 for conformance and build toward v1.4. The sequence is: publish a currency cost view (the substantive work), add the trivial Mandatory constants and derivations, fix the tag and shaping deviations, then round out Conditional and Recommended columns and mature to the latest version.

### 2.1 Which FOCUS version to target

Baseline v1.2, the current certification version, for any conformance conversation, and build toward v1.4 (ratified 2026-06-04). Extend is already aligned with one v1.4 change: it emits no `ProviderName` or `PublisherName`, which v1.4 removes. Two v1.4 additions fit Extend's model well: the Invoice Detail and Billing Period datasets are the natural home for the monthly Scale platform fee, included-credit allotments, and top-up purchases, and they give a clean place to reconcile the credit usage to an invoice. A practical path shapes the transformation against v1.2 semantics, then layers the v1.3 and v1.4 additions.

### 2.2 What certification requires

FinOps Certified FOCUS conformance for data generators runs through the FinOps Foundation. The historical badge is "FinOps Certified FOCUS v1.2 Conformant"; confirm the current badge version on the program page. Contact `member-cert@finops.org` for the RFI. Membership is required for certification, though contributing to the spec is open and free. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report, which this analysis seeds. Open-source tooling includes the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST, SHOULD, and MAY rules). Extend does not appear on the FOCUS "get started" data-generator page and holds no FinOps Certified FOCUS designation; this report assesses readiness only.

### 2.3 Phased roadmap

**Phase 0: Validate and scope.** Assemble a sample of run `usage` objects across processors and modes, decide the charge grain (per run, or per charge line within a run), and confirm the v1.2 baseline and v1.4 build target. Establish the per-credit rate source (plan rate card plus any account-specific Enterprise rate) that the cost columns will join against.

**Phase 1: Publish cost in currency (the substantive work).** Add ListCost as metered credits times the list per-credit rate, and reconcile BilledCost and EffectiveCost against the plan's platform fee, included credits, volume discounts, and annual prepaid or commitment burn-down. Add ContractedCost for Enterprise negotiated rates. Add `BillingCurrency` ("USD"). Keep `x_UsageCredits` alongside.

**Phase 2: Trivial Mandatory columns.** Add the constants (`InvoiceIssuerName`, `ProviderName`, `PublisherName`, `ServiceCategory` = "AI and Machine Learning", `ChargeCategory` = "Usage", `ChargeClass` = null) and the derivations (`ChargeDescription`, `BillingAccountId`, `BillingAccountName`, `BillingPeriodStart`, `BillingPeriodEnd`, `ChargePeriodEnd`, `PricingUnit`).

**Phase 3: Fix deviations.** Convert `extend:usage_tags` to key-value Tags, surface `charges.quantity`/`charges.unit` as ConsumedQuantity/Unit and PricingQuantity/Unit, emit `createdAt` as ChargePeriodStart, map run/file identity to ResourceId/ResourceName, and prefix credit fields as `x_`.

**Phase 4: Conditional and Recommended.** Add unit prices (`ContractedUnitPrice`, `ListUnitPrice`), `PricingCategory`, the pricing-currency columns, the SKU family (`SkuId`, `SkuMeter`, `SkuPriceDetails`, `SkuPriceId`) built from product + mode + surcharges, `ResourceType`, the workspace-based SubAccount columns (Enterprise), and Recommended `ChargeFrequency`, `InvoiceId`, and `ServiceSubcategory`.

**Phase 5: Cover the full bill, mature, and certify.** Add the non-usage charges (the Scale platform fee and top-up purchases as `ChargeCategory` Purchase; any tax) and the invoice association, adopt v1.3 and v1.4 with the Invoice Detail and Billing Period datasets, and pursue certification.

### 2.4 FOCUS Use Cases unlocked

- **Unlocked now (granular itemized usage):** per-processor and per-workflow usage volume reporting, page-throughput trend and anomaly detection, and per-tag or per-API-key usage attribution, all in credits.
- **Unlocked with the cost columns filled (Phases 1 to 2):** unit-cost and cost-per-page metrics in currency, effective-cost views, showback and chargeback by workspace, tag, or customer, and usage-to-cost reconciliation.
- **Unlocked with tags and hierarchy fixed (Phases 3 to 4):** tag-based chargeback with key-value Tags, and workspace-level (SubAccount) allocation for Enterprise organizations.
- **Unlocked with the full bill and invoice datasets (Phase 5):** invoice reconciliation, virtual-currency (credit) lifecycle and burn-down analysis against prepaid balances, and budget tracking against annual commitments.
- **Out of scope for now:** commitment and capacity-reservation use cases (no per-line commitment-discount or reservation mechanic); region and availability-zone analysis (SaaS, not region-scoped on the record).

---

## Part 3: Immediate next steps

1. Confirm the disambiguation (extend.ai document-AI platform) and the charge grain (per run vs per charge line) for the FOCUS dataset.
2. Stand up the credit-to-currency mapping: join metered credits to the plan rate card to produce ListCost, then reconcile BilledCost and EffectiveCost against platform fees, volume discounts, and prepaid or annual commitments.
3. Add the trivial Mandatory constants and derivations, and set `BillingCurrency` to "USD".
4. Convert `extend:usage_tags` to key-value Tags and surface the in-`charges` quantities and units as FOCUS columns.
5. Run a sample through the FOCUS Validator against v1.2 to establish a baseline, and engage the FinOps Foundation conformance program for the RFI.

---

## Confidence summary

- **Disambiguation:** high confidence that the subject is the extend.ai / extend.app document-AI platform (product description, @ExtendHQ, GitHub `extend-hq`, YC). If the intended subject is the virtual-card fintech or the extended-warranty company, this analysis does not apply.
- **Data source structure** (per-run `usage` object, credit model, plans, tags, workspace scope): high confidence, from the current Extend developer documentation and pricing page, including a documented example `usage` payload on the extract-run endpoint.
- **Cost columns substantive rather than trivial:** high confidence. Records are denominated in credits, not currency, and BilledCost/EffectiveCost require reconciling plan fees, volume discounts, and prepaid or annual commitments, so producing the cost quartet is a reconciliation, not a copy.
- **Feature-level classifications:** high confidence. Levels were checked against the FOCUS v1.2 content-constraint reference; the bundled table (stamped 2026-06-23) was cache-validated on 2026-08-04 against the live FOCUS specification index, confirming v1.2 as the certification baseline and v1.4 (2026-06-04) as the latest ratified version, with no refresh needed.
- **Field-presence provisional:** moderate confidence. Field shapes were taken from the public docs and the extract-run example; whether organization and workspace identity, billing-period boundaries, and currency appear as run fields versus account context should be confirmed against a real customer export and the full API reference. This is why the data quality is marked provisional.
- **Overall readiness band (Emerging):** moderate-to-high confidence. Extend has strong, real-time, itemized usage and reasonable allocation dimensions, but no currency cost on any record, no FOCUS shaping, and low column coverage, which places it in Emerging rather than Structured.
- **Certification status:** Extend is not on the FOCUS data-generator "get started" page and holds no FinOps Certified FOCUS designation; this report assesses readiness only and is not a certification result.

---

## Sources

- Extend, Pricing (plans, credit rates, workspaces): https://www.extend.ai/pricing
- Extend Documentation, How Credits Work (credit model, usage tags, dashboard filters): https://docs.extend.ai/general/how-credits-work
- Extend Documentation, Get Extract Run (the `usage` object, workspace scoping, timestamps): https://docs.extend.ai/api-reference/endpoints/extract/get-extract-run
- Extend, product overview: https://www.extend.ai/
- FOCUS Specification (version index, v1.4 ratified 2026-06-04): https://focus.finops.org/focus-specification/
- FOCUS Specification v1.2 (certification baseline): https://focus.finops.org/focus-specification/v1-2/
- FOCUS Validator, FOCUS Converter, and FOCUS Requirements Model tooling.

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
