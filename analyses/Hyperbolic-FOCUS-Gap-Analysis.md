# Hyperbolic and FOCUS: Compliance Gap and Adoption Roadmap

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: 2026-07-01
Source analyzed: Hyperbolic public documentation at docs.hyperbolic.ai (Platform Overview, On-Demand GPU platform, Serverless Inference, Reserved Clusters, Managing Instances, Renting FAQ), the pricing pages, the billing and Organizations console descriptions, and public marketplace pages. No FOCUS-shaped billing export or documented usage-export schema was found; the programmatic instance API is enterprise-gated.
FOCUS baseline: v1.2 (current certification baseline). Build target: v1.4 (latest, ratified 2026-06-04).

## Executive summary

Hyperbolic is an open-access AI cloud that spans three products under one account and one balance: On-Demand GPUs (rent H100 and H200 by the hour with SSH access, no commitment), Serverless Inference (an OpenAI-compatible API across 25 or more open-source models, priced per token or per image), and Reserved Clusters (dedicated capacity on a 3 to 12 month term with volume discounts up to 40 percent). It also operates as a GPU marketplace: suppliers set prices within Hyperbolic's guidelines and Hyperbolic takes a 10 percent platform fee, and the platform brands itself as multi-provider. Billing is prepaid credits, funded by card or crypto, tracked in a console that shows recent transactions and usage, with formal invoices available by email request.

What Hyperbolic publishes today is a product and console experience, not a FOCUS-shaped billing dataset. There is no documented per-charge export, no FOCUS column IDs, and no public field schema for usage lines. The console tracks running time and cost per instance and per-token inference spend, which are the raw materials for the consumption side of FOCUS, but they are not emitted as a charge-level dataset with the full cost family (List, Billed, Effective, Contracted), key-value tags, or ISO-shaped periods. Three distinct charge shapes (hourly GPU, per-token or per-image inference, and reserved-term commitments) all need to land in one schema, and the marketplace and Organizations features add provider-attribution and sub-account questions that a conformant feed must answer.

Verdict: a real consumption substrate with a thin, undocumented published cost surface. Conformance is reachable but requires designing a charge-level dataset from scratch and reconciling prepaid-credit balances and any Reserved discounts back to usage lines.

Stat strip: 57 FOCUS columns (v1.2). Roughly 12 present or trivially derivable from what the console exposes. Of 6 substantive Mandatory gaps, 4 sit in the cost family. Several deviations to fix once a dataset exists (tags, enums, currency and rate shaping).

RAG readiness: Cost Gap, Granularity Partial, Allocation Partial, Coverage Gap, FOCUS shape Gap. Overall band: Not yet aligned (per public docs).

Recommendation: Treat the console's per-instance running cost, the per-token inference meter, and the prepaid-credit ledger as inputs to one FOCUS charge-level feed. Design that feed first (one row per resource per charge period), decide how the marketplace supplier maps to Provider and Publisher versus Hyperbolic as Invoice Issuer, and use Organizations as the SubAccount dimension.

## Part 1: The conformance gap

### 1.1 The data source

Hyperbolic exposes usage and cost primarily through its console (app.hyperbolic.ai) rather than a documented billing export. The relevant surfaces:

- On-Demand GPUs: instances carry a label, GPU type (H100 80GB, H200 141GB), quantity, region, optional InfiniBand, and storage. The console's instance list shows status, GPU type and configuration, region, and running time and costs. Billing runs only while an instance is in the Running state; Pending, Starting, Terminating, and Failed states are not billed, and charging begins when an instance comes online rather than at creation. Pricing is hourly (documented range roughly 1.39 to 1.99 US dollars per GPU-hour). Programmatic instance management is available to enterprise customers on request; most users manage through the Web UI.
- Serverless Inference: an OpenAI-compatible API across 25 or more text, image, vision, and audio models. Pricing is per token (from about 0.0001 US dollars per 1K tokens) or per image (for example 0.01 US dollars for a standard 1024x1024, 25-step generation). Usage is metered and pay-as-you-go.
- Reserved Clusters: dedicated GPU capacity on a 3 to 12 month term, billed monthly or annually, with volume discounts up to 40 percent. Terms and pricing are arranged with sales.
- Billing and account: prepaid credits topped up by credit card or crypto (USDC, USDT, DAI), a minimum top-up, a transactions and usage history in the console, and no charge for failed instances. Formal invoices are issued on request by email. Currency is US dollars.
- Organizations: a team construct that centralizes access, governance, and spend so teams share billing and usage without shared credentials. This is the natural SubAccount or cost-center dimension.

Marketplace structure: suppliers list capacity and set prices within Hyperbolic's guidelines; Hyperbolic takes a 10 percent platform fee and presents itself as multi-provider. For FOCUS this raises the same attribution question an aggregator faces: the underlying supplier is closer to the true Provider and Publisher, while Hyperbolic is the Invoice Issuer and billing account.

Key limitations for FOCUS: no documented per-charge billing export or usage-export schema is published; the console figures are operational running totals, not time-sliced charge records. There is no documented field carrying list price versus effective price after Reserved discounts or promotional credits, and invoices are generated on request rather than exposed as structured data. Tag or label support is limited to an instance name. Inference usage and GPU-rental usage are described as separate metering paths that a single FOCUS feed would need to unify.

### 1.2 How conformance is judged

FOCUS assigns each column a feature level: Mandatory (must be present and populated where applicable), Conditional (required when the provider's model triggers the condition), Recommended, or Optional. Conformance is evaluated column by column against the FOCUS Requirements Model. Feature levels in this report were verified against the FOCUS v1.2 specification Content Constraints tables (bundled cache stamp 2026-06-23, spot-checked live on 2026-07-01 against the v1.2 spec: ChargeClass Mandatory and present-required, ChargeFrequency Recommended, ServiceSubcategory Recommended, all confirmed).

### 1.3 Column-by-column status (FOCUS v1.2, all 57 columns)

Legend: Present / Present, deviation to fix / Missing: Mandatory / Missing: Recommended / Missing: Conditional / N/A: null valid.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No (region only) | Missing: Recommended |
| BilledCost | M | Partial (console running cost, not per-charge) | Missing: Mandatory |
| BillingAccountId | M | Implicit (Hyperbolic account) | Missing: Mandatory (derivable) |
| BillingAccountName | M | Implicit (account) | Missing: Mandatory (derivable) |
| BillingAccountType | C | No | Missing: Conditional |
| BillingCurrency | M | Implicit (USD) | Missing: Mandatory (derivable) |
| BillingPeriodEnd | M | No (credit ledger, no cycle) | Missing: Mandatory (derivable) |
| BillingPeriodStart | M | No (credit ledger, no cycle) | Missing: Mandatory (derivable) |
| CapacityReservationId | C | No | N/A: null valid |
| CapacityReservationStatus | C | No | N/A: null valid |
| ChargeCategory | M | No (implied Usage / Purchase) | Missing: Mandatory (derivable) |
| ChargeClass | M | No | Missing: Mandatory (nullable, plumbing) |
| ChargeDescription | M | Partial (GPU type / model name) | Missing: Mandatory (derivable) |
| ChargeFrequency | R | No (implied Usage-Based / Recurring) | Missing: Recommended |
| ChargePeriodEnd | M | Partial (running time / termination) | Missing: Mandatory (derivable) |
| ChargePeriodStart | M | Partial (instance came online) | Missing: Mandatory (derivable) |
| CommitmentDiscountCategory | C | Partial (Reserved Clusters) | Missing: Conditional |
| CommitmentDiscountId | C | Partial (Reserved Clusters) | Missing: Conditional |
| CommitmentDiscountName | C | Partial (Reserved Clusters) | Missing: Conditional |
| CommitmentDiscountQuantity | C | No | Missing: Conditional |
| CommitmentDiscountStatus | C | No | Missing: Conditional |
| CommitmentDiscountType | C | Partial (Reserved term) | Missing: Conditional |
| CommitmentDiscountUnit | C | No | Missing: Conditional |
| ConsumedQuantity | C | Partial (GPU-hours / tokens) | Missing: Conditional (derivable) |
| ConsumedUnit | C | No (implied hours / tokens) | Missing: Conditional (derivable) |
| ContractedCost | M | No | Missing: Mandatory |
| ContractedUnitPrice | C | Partial (Reserved rate) | Missing: Conditional |
| EffectiveCost | M | Partial (console cost) | Missing: Mandatory |
| InvoiceId | R | No (invoice on request) | Missing: Recommended (derivable) |
| InvoiceIssuerName | M | Implicit (Hyperbolic) | Missing: Mandatory (derivable) |
| ListCost | M | Partial (hourly rate x hours, per-token x volume) | Missing: Mandatory (derivable) |
| ListUnitPrice | C | Yes (hourly rate, per-token rate) | Present, deviation to fix |
| PricingCategory | C | No (on-demand / committed implied) | Missing: Conditional (derivable) |
| PricingCurrency | C | Implicit (USD) | Missing: Conditional (derivable) |
| PricingCurrencyContractedUnitPrice | C | No | N/A: null valid |
| PricingCurrencyEffectiveCost | C | No | N/A: null valid |
| PricingCurrencyListUnitPrice | C | No | N/A: null valid |
| PricingQuantity | M | Partial (derivable, flat-rate GPU) | Missing: Mandatory (derivable) |
| PricingUnit | M | No (implied hours / 1K tokens) | Missing: Mandatory (derivable) |
| ProviderName | M | Implicit (Hyperbolic or supplier) | Missing: Mandatory (derivable) |
| PublisherName | M | Implicit (Hyperbolic or supplier) | Missing: Mandatory (derivable) |
| RegionId | C | Yes (region) | Present, deviation to fix |
| RegionName | C | Partial (region) | Present, deviation to fix |
| ResourceId | C | Partial (instance id in console) | Missing: Conditional (derivable) |
| ResourceName | C | Yes (instance label) | Present |
| ResourceType | C | Partial (GPU type / model) | Present, deviation to fix |
| ServiceCategory | M | No (implied Compute / AI and ML) | Missing: Mandatory (derivable) |
| ServiceName | M | No (product name implied) | Missing: Mandatory (derivable) |
| ServiceSubcategory | R | No | Missing: Recommended |
| SkuId | C | Partial (GPU type / model id) | Missing: Conditional (derivable) |
| SkuMeter | C | No | Missing: Conditional |
| SkuPriceDetails | C | Partial (config / rate) | Missing: Conditional |
| SkuPriceId | C | No | Missing: Conditional |
| SubAccountId | C | Partial (Organizations) | Missing: Conditional (derivable) |
| SubAccountName | C | Partial (Organization name) | Missing: Conditional (derivable) |
| SubAccountType | C | No | Missing: Conditional |
| Tags | C | Partial (instance label only) | Missing: Conditional |

### 1.4 What's solved, and what remains

Reading the tally: of 57 columns, roughly 3 are present (some with deviations) and another 9 are trivially derivable from what the console already exposes, leaving the cost family and the FOCUS-shaping work as the real build. Excluding the legitimately N/A pricing-currency and capacity-reservation columns, coverage of applicable columns sits low, because there is no published charge-level dataset to begin from.

**Substantive gaps (real data not in the source as structured, per-charge fields):**

1. **BilledCost and EffectiveCost.** The console shows a running cost per instance and a per-token inference meter, but bills are settled against a prepaid credit balance and promotional credits exist (referral and hackathon credits are documented). Producing per-charge BilledCost and EffectiveCost requires reconciling credit draws and any credits or Reserved discounts back to individual usage lines. Because credits and discounts are applied against the balance rather than shown per line, treat both as substantive, not a copy of the console figure.
2. **ContractedCost and the commitment family.** Reserved Clusters carry negotiated rates and volume discounts up to 40 percent on a fixed term. That is a genuine commitment-discount mechanic, so ContractedCost and the CommitmentDiscount columns are in scope and must be sourced from the Reserved agreement, not derived from on-demand rates. This is real data that does not exist in any published field today.
3. **A charge-level dataset itself.** Unlike providers that publish an instance object with an accrued-cost field, Hyperbolic's public surface is a console view. The Mandatory period, account, and service columns are derivable in principle but require first constructing the per-charge feed that carries them.

**Trivial gaps (derivable once the feed exists, flat-rate on-demand and per-unit inference):**

- ListCost for on-demand GPUs = hourly rate x billed hours; for inference = per-unit rate x metered volume. On-demand GPU rental is flat-rate, so PricingQuantity equals consumed GPU-hours and ListUnitPrice is the published hourly rate.
- PricingQuantity, PricingUnit, ConsumedQuantity, ConsumedUnit: GPU-hours from running time (billed only in the Running state), or tokens/images from the inference meter.
- ChargePeriodStart/End: from the instance online and termination times; per-request or per-window for inference.
- ChargeCategory (Usage for consumption, Purchase for a Reserved commitment), ServiceCategory (Compute for GPU rental, AI and Machine Learning for inference), ServiceName, ChargeDescription: constant or derivable from the product and SKU.
- BillingAccountId/Name, BillingCurrency (USD), InvoiceIssuerName (Hyperbolic): account-level constants.
- ChargeClass: null except for corrections.

### 1.5 Deviations to fix (present and near-present columns)

- **Tags**: only an instance label exists, not key-value pairs; FOCUS represents tags as key-value pairs. This is closer to missing than to a format fix, since there is no structured tagging model to reshape.
- **ListUnitPrice**: the hourly and per-token rates are published as plain USD figures; confirm they land as decimals in the billing currency at the correct unit basis (per GPU-hour, per 1K tokens).
- **RegionId/RegionName**: a single region value serves both; split into an ID and a human-readable name.
- **ResourceType / SkuId**: GPU type strings (H100 80GB, H200 141GB) and model identifiers are native values; map to a stable FOCUS SKU representation.
- **ProviderName and PublisherName**: because Hyperbolic is a marketplace, decide whether the underlying supplier or Hyperbolic itself is Provider and Publisher; the on-demand H100/H200 fleet appears first-party, while marketplace-listed capacity is third-party. Note these two columns are deprecated in v1.3 and removed in v1.4.

What is already right: a per-instance running-cost figure and running time, a clean region dimension, an instance label usable as ResourceName, a metered inference path, and a genuine account and credit ledger. These give a real consumption base to build on, even though the FOCUS shaping is not yet started.

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline conformance against v1.2 (the current certification baseline) and build toward v1.4 (latest, ratified 2026-06-04). Because v1.3 deprecates and v1.4 removes ProviderName and PublisherName, design marketplace provider attribution so it does not depend on those columns long term; carry the underlying supplier as a first-class dimension that survives their removal. The Validator supports v1.3 today, with v1.4 support expected later in Q3 2026.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The current badge is "FinOps Certified FOCUS v1.2 Conformant" (contact member-cert@finops.org for the RFI). Membership is required for certification, though contributing to the spec is open and free. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Open tooling: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules).

### 2.3 Phased roadmap

**Phase 0: Validate and scope.** Define the FOCUS dataset as a charge-level feed (one row per resource per charge period), unifying three charge shapes: hourly GPU rental, per-token or per-image inference, and Reserved-term commitments. Confirm the v1.2 baseline and v1.4 build target. There is no existing export to validate, so the first milestone is a draft schema, then a sample run through the FOCUS Validator.

**Phase 1 (unlock): Build the charge-level feed and close the substantive Mandatory cost gaps.** Construct the per-charge dataset and the reconciliation that ties prepaid-credit draws, promotional credits, and Reserved discounts to usage lines to produce BilledCost, EffectiveCost, ListCost, and ContractedCost. In the same pass, emit the derivable Mandatory columns: PricingQuantity, PricingUnit, ChargePeriodStart/End, BillingPeriodStart/End, ChargeCategory, ServiceCategory, ServiceName, ChargeDescription, BillingAccount fields, BillingCurrency, InvoiceIssuerName, and ChargeClass.

**Phase 2: Fix format and value deviations.** Standardize ListUnitPrice to a currency decimal at the correct unit basis, split region into RegionId and RegionName, map GPU and model strings to stable SKU values, and resolve marketplace Provider and Publisher attribution.

**Phase 3: Round out applicable Conditional and Recommended columns.** Populate SubAccountId/Name from Organizations, ResourceId from the console instance identifier, ConsumedQuantity/Unit, ContractedUnitPrice and the CommitmentDiscount family from Reserved agreements, PricingCategory, PricingCurrency, InvoiceId, ChargeFrequency, ServiceSubcategory, and the SKU detail columns. Build a real key-value tagging model to replace the single label. Null the capacity-reservation and pricing-currency families with a note where they do not apply.

**Phase 4: Mature to v1.4 and certify.** Migrate provider attribution off ProviderName/PublisherName ahead of their removal, adopt the v1.4 Invoice Detail and billing-period datasets for cleaner credit-ledger reconciliation, re-validate, and pursue certification.

### 2.4 FOCUS Use Cases unlocked

- Unlocked once the charge-level feed with resource, Organization, and day-level data exists (Phase 1 to 3): cost allocation by team and project via Organizations, spend reporting split across GPU rental and inference, GPU-hour and token-consumption utilization analysis, anomaly detection, and showback (by resource and by Organization).
- Unlocked once the cost family reconciles (Phase 1): invoice reconciliation against the credit ledger, effective-cost reporting, and actuals-based budgeting.
- In scope once the Reserved data is exposed (Phase 3): commitment-discount coverage and utilization reporting for Reserved Clusters.
- Out of scope for the model: capacity-reservation use cases, since Hyperbolic's documented model is on-demand plus term commitments rather than pre-purchased capacity reservations.

## Part 3: Immediate next steps

1. Define the target FOCUS dataset as a charge-level feed keyed on resource and charge period, unifying GPU rental, inference, and Reserved commitments.
2. Decide the marketplace attribution: when the underlying supplier is Provider and Publisher versus when Hyperbolic is, with Hyperbolic always the Invoice Issuer and billing account.
3. Design the reconciliation from prepaid-credit draws, promotional credits, and Reserved discounts to per-charge BilledCost, EffectiveCost, and ContractedCost.
4. Emit the derivable Mandatory columns and build a key-value tagging model to replace the single instance label.
5. Run a sample through the FOCUS Validator and confirm the target representation against the Requirements Model.

## Confidence summary

- Business model and product structure (three products, marketplace with 10 percent fee, prepaid credits, Organizations, USD): high confidence, drawn directly from Hyperbolic's public documentation and pricing pages.
- Billing mechanics (billed only in the Running state, charging on come-online, hourly GPU and per-token inference, invoices on request, credits and promotional credits): medium-high confidence, from the docs and FAQ rather than a billing-export schema.
- The absence of a published per-charge billing export or usage-export schema: medium-high confidence; the programmatic instance API is enterprise-gated and no public field schema was found. If Hyperbolic offers an enterprise usage or billing export, coverage would improve and several Missing items would move toward Present.
- The commitment-family classification for Reserved Clusters: medium confidence; Reserved terms and discounts are documented but their per-line data representation is not, so the CommitmentDiscount columns are marked Missing: Conditional rather than N/A.
- Feature levels: high confidence, verified against the v1.2 spec with a live spot-check on 2026-07-01.
- Data quality for this analysis: provisional. The model is well documented, but the billing-line schema is not published, so the cost-family and dataset-shape findings rest on the documented billing mechanics rather than a field-level export.

## Sources

- Hyperbolic Platform Overview and product pages: https://docs.hyperbolic.ai/, https://www.hyperbolic.ai/
- On-Demand GPU platform, Managing Instances, Renting FAQ: https://docs.hyperbolic.xyz/docs/gpu-marketplace, https://docs.hyperbolic.ai/on-demand/managing-instances, https://docs.hyperbolic.xyz/docs/renting-faq
- Serverless Inference and pricing: https://docs.hyperbolic.xyz/docs/hyperbolic-pricing, https://huggingface.co/docs/inference-providers/en/providers/hyperbolic
- Billing and Organizations console: https://app.hyperbolic.ai/settings/billing, https://app.hyperbolic.ai/billing
- Marketplace structure and landscape: https://www.hyperbolic.ai/marketplace, https://www.hyperbolic.ai/blog/gpu-marketplace-landscape
- FOCUS Specification v1.2: https://focus.finops.org/focus-specification/v1-2/
- FOCUS project, tooling, and certification: https://focus.finops.org/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
