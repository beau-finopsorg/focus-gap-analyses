# Ola Krutrim (Krutrim Cloud) and FOCUS: Conformance Gap Analysis

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: 2026-07-01
Source analyzed: Krutrim Cloud public documentation (docs.cloud.olakrutrim.com): billing for compute, billing for AI Studio, billing models, usage and transactions, IAM, account management, pricing pages.
FOCUS baseline: v1.2 (current certification baseline). Build target: v1.4 (latest ratified).

## Executive summary

Krutrim Cloud is Ola Krutrim's India sovereign AI cloud, offering GPU compute (VMs, AI Pods, GPU Baremetals), storage, networking, managed Kubernetes, databases, and an AI Studio model catalogue, all priced and billed in Indian rupees. Cost visibility today is a credits-based console experience: a Usage Metrics dashboard that shows total credits consumed with a breakdown by service over a selected date range, plus a Transactions ledger of payments, credit top-ups, refunds, and service charges. AI Studio adds a per-service Export button for usage data, and the platform exposes usage summaries via API and SDK.

Judged against FOCUS (the FinOps Open Cost and Usage Specification), the reviewed data source is at an early stage. The documented artifacts are service-level aggregates and a financial-transaction ledger, not a line-item cost and usage record shaped around resources, charge periods, and a full cost ladder. The information needed to build FOCUS clearly exists inside the platform (fine-grained 15-minute metering, per-resource pricing, regions, projects, credits, and enterprise committed bundles), but the documentation does not describe a granular, per-line export carrying it. The largest gaps are substantive: the cost columns and the per-line charge dimensions are not present in the reviewed source.

Stat strip:
- 57 FOCUS columns (v1.2)
- Present or trivially derivable: 10
- Substantive Mandatory data gaps: 8 of the 21 Mandatory columns
- Deviations to fix on present fields: 2

Recommendation: treat this as a build, not a cleanup. The priority is to expose a usage-line-level export (one row per resource per charge period) that carries a cost ladder and time windows. Everything else follows from that.

## Part 1: The conformance gap

### 1.1 The data source

What the Krutrim Cloud documentation describes:

- Billing model: prepaid credits. Pay-as-you-go (on-demand, per-unit rates shown on the console) and Enterprise Usage (committed bundles at custom rates, quoted by sales). Free-tier quotas were also offered (services free until Diwali 2025 during launch).
- Metering: fine-grained. Compute is metered in 15-minute intervals (per-hour rates displayed, rounded up to the nearest 15 minutes, minimum 15 minutes). Storage is metered hourly. AI Studio bills per token, per audio minute, or per GPU-hour depending on the model.
- Currency: INR only. Pricing explicitly avoids forex and hidden egress charges.
- Usage Metrics dashboard: remaining balance, total credits used, breakdown by service (Core Infrastructure, AI Studio, AI Solutions), date-range filter.
- Transactions ledger: transaction ID, date and time, type (service payment or credit purchase), description, service category, amount, status (Completed, Pending, Failed, Refunded), with downloadable receipts.
- AI Studio: a per-sub-tab Export button (Model Catalogue, Fine Tuning, Deployment, Evaluation) to download usage data, with a date filter.
- Programmatic access: usage summaries via API and SDK; alerts and usage reports configurable by account or project.
- Structure: accounts are Individual or Organization type; IAM is RBAC (Users, Policies, Roles, Groups); resources live in VPCs and regions (pricing varies by region and VM flavor).

Key limitations for FOCUS:

- The documented outputs are service-level aggregates (credits by service) and a payment ledger, not a per-resource, per-charge-period line-item record.
- No documented cost export carrying list price, effective cost after credits and discounts, and billed cost joined to the usage lines that produced them.
- Resource identity (resource IDs), region per line, and resource tags or labels are not described as billing dimensions. IAM has no documented resource-tagging feature that flows to billing.
- Zones are not documented (regions only).
- The AI Studio Export exists but its column set is not published, so its FOCUS value cannot be confirmed from the documentation.

Because the field-level schema of the console exports is not published, this analysis is provisional. It reflects what the documentation describes, not a sample export or an API response payload.

### 1.2 How conformance is judged

FOCUS defines 57 columns for v1.2, each carrying a feature level: Mandatory, Conditional, Recommended, or Optional. Conformance is judged column by column against the FOCUS Requirements Model. A conformant dataset must include and correctly populate every Mandatory column, populate Conditional columns when the provider's business model triggers the condition, and may null Conditional or Recommended columns that do not apply (the column must still exist). Feature levels for this analysis were verified against the bundled v1.2 reference (validated 2026-06-23) and the live FOCUS specification.

### 1.3 Column-by-column status

Status legend: Present (emitted and aligned); Present, deviation to fix (emitted, wrong format or invalid value); Missing: Mandatory (required, absent, blocks conformance); Missing: Recommended; Missing: Conditional (condition applies, absent); N/A: null valid (does not apply to this model, should exist and be null).

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No zones documented (regions only) | N/A: null valid |
| BilledCost | M | No (credits debited; aggregates only) | Missing: Mandatory (substantive) |
| BillingAccountId | M | Account ID exists | Present (trivial to surface) |
| BillingAccountName | M | Account / organization name | Present (trivial to surface) |
| BillingCurrency | M | INR | Present (constant) |
| BillingPeriodEnd | M | Statement / date-range boundary | Present (trivial to derive) |
| BillingPeriodStart | M | Statement / date-range boundary | Present (trivial to derive) |
| BillingAccountType | C | Individual or Organization account type | Present (trivial to map) |
| CapacityReservationId | C | Not documented | N/A: null valid |
| CapacityReservationStatus | C | Not documented | N/A: null valid |
| ChargeCategory | M | Transaction type exists, not the FOCUS enum | Missing: Mandatory (substantive) |
| ChargeClass | M | No correction flag documented | Missing: Mandatory (trivial, nullable) |
| ChargeDescription | M | Transaction description / service line | Present, deviation to fix |
| ChargeFrequency | R | Usage-based and committed models exist | Missing: Recommended |
| ChargePeriodEnd | M | Not exposed per line (metered internally) | Missing: Mandatory (substantive) |
| ChargePeriodStart | M | Not exposed per line (metered internally) | Missing: Mandatory (substantive) |
| CommitmentDiscountCategory | C | Enterprise committed bundles exist | Missing: Conditional |
| CommitmentDiscountId | C | Enterprise committed bundles exist | Missing: Conditional |
| CommitmentDiscountName | C | Enterprise committed bundles exist | Missing: Conditional |
| CommitmentDiscountQuantity | C | Enterprise committed bundles exist | Missing: Conditional |
| CommitmentDiscountStatus | C | Enterprise committed bundles exist | Missing: Conditional |
| CommitmentDiscountType | C | Enterprise committed bundles exist | Missing: Conditional |
| CommitmentDiscountUnit | C | Enterprise committed bundles exist | Missing: Conditional |
| ConsumedQuantity | C | Metered internally (hours, tokens, GB, minutes) | Missing: Conditional (substantive to expose) |
| ConsumedUnit | C | Unit types defined per service and model | Missing: Conditional (trivial once quantity exposed) |
| ContractedCost | M | No (credits / custom bundles not reconciled to lines) | Missing: Mandatory (substantive) |
| ContractedUnitPrice | C | Custom enterprise rates exist, not per line | Missing: Conditional |
| EffectiveCost | M | No (credits and refunds applied at account level) | Missing: Mandatory (substantive) |
| InvoiceId | R | Transaction / receipt IDs exist | Missing: Recommended (derivable) |
| InvoiceIssuerName | M | Krutrim as issuer | Present (constant) |
| ListCost | M | Published list rates, not joined to usage lines | Missing: Mandatory (substantive) |
| ListUnitPrice | C | Published per-unit rates by SKU | Missing: Conditional (derivable from rate card) |
| PricingCategory | C | On-demand vs committed distinction exists | Missing: Conditional |
| PricingCurrency | C | INR | Missing: Conditional (trivial; equals billing currency) |
| PricingCurrencyContractedUnitPrice | C | INR context | Missing: Conditional |
| PricingCurrencyEffectiveCost | C | INR context | Missing: Conditional |
| PricingCurrencyListUnitPrice | C | INR context | Missing: Conditional |
| PricingQuantity | M | Metered internally, not exposed per line | Missing: Mandatory (substantive) |
| PricingUnit | M | Unit types defined, not exposed per line | Missing: Mandatory (trivial once quantity exposed) |
| ProviderName | M | Krutrim | Present (constant) |
| PublisherName | M | Krutrim (and model authors in AI Studio) | Present (constant) |
| RegionId | C | Regions exist (pricing varies by region) | Missing: Conditional |
| RegionName | C | Regions exist | Missing: Conditional |
| ResourceId | C | Resources exist (VMs, pods) but not in billing lines | Missing: Conditional (substantive to expose) |
| ResourceName | C | Resource names exist in console | Missing: Conditional |
| ResourceType | C | VM flavor, pod, baremetal, model | Missing: Conditional |
| ServiceCategory | M | Service breakdown exists, not FOCUS enum | Present, deviation to fix |
| ServiceName | M | Service breakdown (Compute, Storage, AI Studio, etc.) | Present |
| ServiceSubcategory | R | Sub-service detail exists (Model Catalogue, Fine Tuning) | Missing: Recommended |
| SkuId | C | VM flavor / model identifiers exist | Missing: Conditional |
| SkuMeter | C | Per-model billing mode (input tokens, minutes) | Missing: Conditional |
| SkuPriceDetails | C | Rate card exists | Missing: Conditional |
| SkuPriceId | C | Rate card exists | Missing: Conditional |
| SubAccountId | C | Projects exist (usage reports by project) | Missing: Conditional |
| SubAccountName | C | Project names exist | Missing: Conditional |
| SubAccountType | C | Project construct | Missing: Conditional |
| Tags | C | No billing tags documented | Missing: Conditional |

Reading the tally: of the 21 Mandatory columns, 8 are missing as substantive data gaps (BilledCost, ChargeCategory, ChargePeriodStart, ChargePeriodEnd, ContractedCost, EffectiveCost, ListCost, PricingQuantity), 2 are present with deviations to fix (ChargeDescription, ServiceCategory), and the remainder are present or trivially derivable (the account, currency, billing-period, issuer, provider, publisher, and service-name columns, plus PricingUnit and ChargeClass as trivial adds once the line-level export exists). Roughly 10 of the 57 columns are present or a trivial lift today; the rest require a line-item export that the documentation does not describe.

### 1.4 What's solved, and what remains

Solved or near-solved:

- Identity and header columns: BillingAccountId, BillingAccountName, BillingAccountType, BillingCurrency (INR), InvoiceIssuerName, ProviderName, PublisherName, and the billing-period boundaries are all present or a trivial mapping from account and statement data.
- Service naming: ServiceName maps directly from the console's per-service breakdown.

Substantive gaps (real data that the reviewed source does not carry):

- The cost ladder: ListCost, ContractedCost, BilledCost, and EffectiveCost. This is the central gap. Krutrim bills against a prepaid credit balance and applies credits, refunds, free-tier quotas, and enterprise committed-bundle rates. Because discounts and credits exist and are handled at the account and ledger level rather than on usage lines, the cost columns are a substantive reconciliation problem, not a trivial copy of a list figure. List rates are published on the pricing pages but are not joined to the usage lines that consumed them.
- Per-line charge dimensions: ChargePeriodStart, ChargePeriodEnd, PricingQuantity, ConsumedQuantity, and ResourceId. The platform meters at 15-minute granularity internally and knows the resource, but the documented outputs are aggregates, so these dimensions have to be surfaced onto an exportable line record.
- ChargeCategory: the Transactions ledger records a transaction type, but not the FOCUS per-charge classification (Usage, Purchase, Tax, Credit, Adjustment) on usage lines.

Trivial once the line-level export exists: PricingUnit and ConsumedUnit (unit types are already defined per service and model), ChargeClass (nullable, populated only for corrections), the pricing-currency columns (all INR, equal to the billing currency), and ListUnitPrice (derivable from the published rate card).

### 1.5 Deviations to fix

Two present columns carry the right idea in a non-conformant shape:

- ServiceCategory: the console groups spend by service (Core Infrastructure, AI Studio, AI Solutions) and by service name, but these are not the FOCUS ServiceCategory enum (AI and Machine Learning, Compute, Storage, Networking, Databases, and so on). The values need mapping to the allowed set.
- ChargeDescription: transaction descriptions and service-line labels exist, but they describe payments and credit events, not the per-usage-line charge that FOCUS expects. The description needs to attach to a usage line, not only to a ledger entry.

Not yet applicable: AvailabilityZone (regions only, no zones documented) and the capacity-reservation family are null-valid for this model. The commitment-discount family is not applicable to on-demand usage but does apply to Enterprise Usage committed bundles, so it should be populated for those customers rather than nulled globally.

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline the build on v1.2, the current certification baseline, and design the export so it extends cleanly to v1.4 (the latest ratified version, which removes ProviderName and PublisherName and adds invoice-detail and billing-period datasets for reconciliation). Since Krutrim is building the line-item export largely from scratch, adopting the v1.4 column shape from the start avoids rework, while certifying against v1.2 while that remains the badge version.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The current program is "FinOps Certified FOCUS v1.2 Conformant" (contact member-cert@finops.org for the RFI). Membership is required to certify, though contributing to the spec is open and free. The deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Open-source tooling: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules).

### 2.3 Phased roadmap

Phase 0: validate scope and confirm the internal data. Confirm that 15-minute metering, resource identity, region, project, and applied credits are all retrievable per usage event from the internal billing pipeline. Pull the AI Studio Export and any API usage payload and inspect their real fields against FOCUS.

Phase 1 (unlocks the most): build a usage-line export. Emit one row per resource per charge period carrying ChargePeriodStart/End, ResourceId, ServiceName, PricingQuantity, ConsumedQuantity, and the header columns already available. Populate the cost ladder: ListCost from the rate card, then BilledCost, EffectiveCost, and ContractedCost by reconciling credits, refunds, free-tier quotas, and committed-bundle rates back to the lines. Add ChargeCategory with the FOCUS enum, plus the trivial adds (PricingUnit, ConsumedUnit, ChargeClass, pricing-currency columns).

Phase 2: fix the deviations. Map service groupings to the FOCUS ServiceCategory enum and attach ChargeDescription to usage lines.

Phase 3: round out applicable Conditional and Recommended columns. RegionId/RegionName, SubAccountId/Name/Type from the project construct, the SKU family from the rate card and VM flavors and model identifiers, ServiceSubcategory, InvoiceId, ChargeFrequency, and a key-value Tags column if resource tagging is added. Populate the commitment-discount family for Enterprise Usage customers.

Phase 4: mature to v1.4, drop ProviderName and PublisherName, add the invoice-detail and billing-period datasets, and pursue certification.

### 2.4 FOCUS Use Cases unlocked

- Available after Phase 1: cost reporting and trending by service and resource, showback by project once SubAccount columns land, effective-cost analysis, and reconciliation against the credit ledger.
- Available after Phase 3: allocation and chargeback by tag, region-level cost analysis, SKU-level rate analysis, and committed-bundle utilization reporting for Enterprise Usage customers.
- Out of scope for the current model: commitment use cases apply only to Enterprise Usage committed bundles, not on-demand usage; capacity-reservation and availability-zone use cases do not apply as documented.

## Part 3: Immediate next steps

1. Confirm the real field set of the AI Studio Export and the usage API against FOCUS; this determines how much of Phase 1 already exists internally.
2. Confirm whether 15-minute metering, resource ID, region, and applied credits are all retrievable per usage event from the billing pipeline.
3. Decide the certification target (v1.2 badge) and the build shape (v1.4), and register for the RFI if pursuing certification.
4. Prototype a single-service FOCUS export (compute is the cleanest, with flat hourly rates) and run it through the FOCUS Validator.
5. Design the cost-ladder reconciliation for credits, refunds, free-tier quotas, and committed bundles, which is the hardest and highest-value piece.

## Confidence summary

- Moderate confidence: the description of Krutrim's billing model (credits-based, INR, 15-minute compute metering, pay-as-you-go and enterprise committed bundles, service-level usage dashboard, transactions ledger, AI Studio per-service Export). Sourced directly from the public Krutrim Cloud documentation.
- Lower confidence, provisional: every column classification that depends on the field-level schema of the console exports and usage API. The documentation does not publish those schemas or a sample row, so the analysis reflects the documented artifacts (aggregates and a ledger), not a confirmed export. A real sample export or API payload would likely move several Conditional columns from "missing" to "present" if the internal pipeline already carries resource, region, and project on each line.
- Moderate confidence: the substantive cost-column gap. Because credits, refunds, and committed-bundle rates exist and are applied at the account and ledger level rather than on usage lines, the list-cost trap applies and BilledCost, EffectiveCost, and ContractedCost are substantive, not trivial.
- Feature levels verified against the bundled v1.2 reference (validated 2026-06-23) and the live FOCUS specification; no cache refresh was required.
- Pending: a FOCUS Validator run on a real Krutrim export is the single largest open item and the objective arbiter of the classifications above.

## Sources

- Krutrim Cloud documentation: Billing for Compute, Billing for AI Studio, Billing Models, Usage and Transactions, Identity Access Management, Managing your Krutrim Cloud Account, Pricing (docs.cloud.olakrutrim.com).
- FOCUS Specification v1.2 and v1.4 (focus.finops.org/focus-specification).
- FOCUS tooling: Validator, Converter, Requirements Model.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org and is licensed under CC BY 4.0.

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
