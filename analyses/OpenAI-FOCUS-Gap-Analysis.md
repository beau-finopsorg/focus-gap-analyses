# OpenAI & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** OpenAI  
**Prepared:** June 25, 2026  
**Source:** OpenAI Usage API (`GET /v1/usage`); OpenAI billing dashboard  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 27 Present, 11 Deviation, 0 Missing Mandatory, 2 Missing Conditional, 1 Missing Recommended, 16 N/A

---

## Executive Summary

OpenAI bills by consumption unit across a diverse portfolio: LLM tokens (input, output, cached), audio minutes (Whisper), images (DALL-E), characters (TTS), and fine-tuning training tokens. Each service type has a distinct PricingUnit. All 21 Mandatory columns have source data. The 11 Deviations cover enum derivation, unit normalization, and enterprise ContractedCost. Sixteen columns are legitimately N/A: no per-request resource IDs, no regional routing, and no commitment discount model. The project-based hierarchy (OpenAI Projects) maps to SubAccount.

**Recommendation:** The key design decision is row granularity: one FOCUS row per model × service type × token type × project × day. OpenAI's Usage API provides per-project, per-model, per-day breakdowns. The public rate card handles ListUnitPrice. Implement LLM text (input/output/cached) first, then extend to audio, image, and TTS in a follow-on pass.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**OpenAI Usage API** (`GET /v1/usage`): Returns daily usage broken down by model, with token counts and cost. Projects provide usage isolation. The API returns input tokens, output tokens, and cached input tokens for LLM calls; audio seconds for Whisper; images by resolution for DALL-E.

**OpenAI Billing Dashboard**: Monthly invoices with line items by model and usage type. Invoice numbers are available here.

Key characteristics for FOCUS:

- **Multi-unit billing:** OpenAI bills by different units depending on the capability. LLM APIs: tokens. Audio transcription (Whisper): seconds or minutes. TTS: characters. Image generation (DALL-E): images by resolution. Fine-tuning: training tokens (one-time) + inference tokens. Embeddings: input tokens.
- **Project hierarchy:** OpenAI organizations contain Projects. Usage is tracked per project, mapping to FOCUS SubAccountId and SubAccountName.
- **Public rate card:** OpenAI publishes per-model, per-token-type pricing. ListCost and ListUnitPrice are derivable.
- **Cached tokens:** GPT-4o and select models offer prompt caching; cached input tokens are billed at 50% of the standard input token rate. These must be separate FOCUS rows.
- **No regional routing:** OpenAI's API does not expose region assignment to customers.
- **No commitment discounts:** OpenAI has no reserved capacity model. All usage is on-demand.
- **Enterprise agreements:** Large enterprise customers may have negotiated pricing not exposed via the Usage API.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Each column carries a feature level: Mandatory, Conditional, or Recommended. N/A is a valid FOCUS state for columns the provider's billing model genuinely does not produce.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | OpenAI source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item amount by model and usage type | Present |
| EffectiveCost | Mandatory | = BilledCost (no prepaid commitment amortization) | Present |
| ListCost | Mandatory | Public rate × PricingQuantity from OpenAI rate card | Present |
| ContractedCost | Mandatory | = ListCost for standard API; enterprise negotiated rates not exposed via API | Deviation |
| BillingAccountId | Mandatory | OpenAI organization account ID | Present |
| BillingAccountName | Mandatory | Organization name | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Start of aggregation period (day or month) | Present |
| ChargePeriodEnd | Mandatory | End of aggregation period | Present |
| ChargeDescription | Mandatory | Derive: model name + usage type (e.g., "gpt-4o · Input Tokens") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for all consumption charges | Deviation |
| ChargeClass | Mandatory (nullable) | null except for correction charges | Present |
| InvoiceIssuerName | Mandatory | "OpenAI, LLC" | Present |
| ProviderName | Mandatory (dep. v1.3) | "OpenAI" | Present |
| PublisherName | Mandatory (dep. v1.3) | "OpenAI" | Present |
| ServiceName | Mandatory | Derive: "OpenAI API" for LLM/embedding/audio/image; "OpenAI Fine-Tuning" for training | Deviation |
| ServiceCategory | Mandatory | Derive: "AI and Machine Learning" | Deviation |
| PricingQuantity | Mandatory | Depends on service type: token count (÷ 1M), audio minutes, image count, character count (÷ 1M) | Present |
| PricingUnit | Mandatory | Normalize: "1M Input Tokens", "1M Output Tokens", "Minutes", "Images", "1M Characters" per row | Deviation |
| ConsumedQuantity | Conditional | = PricingQuantity | Present |
| ConsumedUnit | Conditional | = PricingUnit | Present |
| ListUnitPrice | Conditional | Published rate for the model and usage type from OpenAI pricing page | Present |
| ContractedUnitPrice | Conditional | = ListUnitPrice for standard customers; enterprise rates require supplementary data | Deviation |
| PricingCategory | Conditional | Derive: "Standard" for on-demand | Deviation |
| ChargeFrequency | Conditional | Derive: "Usage-Based" | Deviation |
| BillingAccountType | Conditional | Derive from account tier (Pay-as-you-go, Enterprise) | Present |
| SubAccountId | Conditional | OpenAI Project ID | Present |
| SubAccountName | Conditional | Project name | Present |
| SubAccountType | Conditional | "Project" | Present |
| ResourceId | Conditional | N/A: billing aggregates have no per-request resource IDs | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | OpenAI model ID (e.g., "gpt-4o-2024-11-20") | Present |
| Tags | Conditional | N/A: OpenAI billing does not include request-level tags | N/A |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation because enterprise rates require supplementary data | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost | Present |
| SkuMeter | Conditional | Derive: "Input Tokens", "Output Tokens", "Cached Input Tokens", "Minutes", "Images", "Characters" | Deviation |
| SkuPriceId | Conditional | No pricing catalog rate ID exposed in OpenAI billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable (flat per-unit pricing by model) | Missing: Conditional |
| RegionId | Conditional | N/A: OpenAI API does not expose regional routing to customers | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: OpenAI has no reserved capacity or savings plan model | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from OpenAI billing dashboard | Present |
| ServiceSubcategory | Recommended | No native field; map from model type: "Large Language Models", "Image Generation", "Audio Transcription", "Text-to-Speech" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global API with no customer-visible zone assignment | N/A |

**Tally:** 27 Present, 11 Deviation, 0 Missing Mandatory, 2 Missing Conditional, 1 Missing Recommended, 16 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Usage quantities by model, project hierarchy, billing period, invoice numbers, and public pricing. All 21 Mandatory columns have source data.

**Remaining:** Enterprise ContractedCost requires supplementary pricing data. SkuPriceId and SkuPriceDetails are absent. Eleven Deviations are all derivation and normalization tasks. ServiceSubcategory requires a mapping table per model type.

### 1.5 Deviations to Fix

**PricingUnit normalization:** Each service type gets a distinct unit: LLM input tokens → "1M Input Tokens"; LLM output tokens → "1M Output Tokens"; cached input tokens → "1M Cached Input Tokens"; Whisper → "Minutes"; DALL-E → "Images"; TTS → "1M Characters". Each is a separate FOCUS row.

**ChargeCategory:** All consumption charges → "Usage". Fine-tuning training (one-time purchase) → "Purchase".

**SkuMeter:** Derive from usage type field in the Usage API: input_tokens → "Input Tokens", output_tokens → "Output Tokens", cached_tokens → "Cached Input Tokens", audio → "Minutes", images → "Images".

**ServiceName:** "OpenAI API" for LLM, embedding, audio, and image generation. "OpenAI Fine-Tuning" for training charges.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. The 16 N/A columns must be documented as legitimately not applicable for a stateless API billing model.

### 2.3 Phased Roadmap

**Phase 0:** Enable Usage API access. Pull one month of per-project, per-model usage data. Identify all active model types.

**Phase 1: LLM text transform.** Map input, output, and cached token rows for GPT-4o and other LLM models. Derive ChargeCategory, ServiceName, ServiceCategory, PricingCategory, ChargeFrequency, SkuMeter, PricingUnit.

**Phase 2: Non-LLM services.** Add Whisper (audio), DALL-E (image), TTS (character), and embedding rows with appropriate PricingUnit. Add fine-tuning training rows with ChargeCategory = "Purchase".

**Phase 3: Certify.** Add ServiceSubcategory mapping. Drop ProviderName, PublisherName (v1.4). Validate with FOCUS Validator. Submit for certification.

### 2.4 FOCUS Use Cases OpenAI Customers Unlock

**After Phase 1:** Per-model LLM cost breakdown by project. Input vs. output vs. cached token cost analysis. Cross-provider AI cost comparison.

**After Phase 2:** Full portfolio cost breakdown: LLM + audio + image + TTS + fine-tuning. Fine-tuning cost amortization via BilledCost vs. EffectiveCost.

---

## Part 3: Immediate Next Steps

1. Enable OpenAI Usage API access and pull one month of per-project, per-model usage data.
2. Build a rate card mapping model × usage type → ListUnitPrice from OpenAI's published pricing page.
3. Implement the Phase 1 LLM text transform. Run through the FOCUS Validator.
4. Design the multi-unit PricingUnit normalization strategy for Whisper, DALL-E, and TTS.
5. Open the RFI with `member-cert@finops.org` once Phase 1 data is validator-clean.

---

## Confidence Summary

- **High:** LLM token billing is structurally clear. Token count × rate = cost, with a public rate card. All 27 Present columns are grounded in OpenAI's Usage API and public pricing.
- **High:** Project hierarchy maps cleanly to SubAccountId and SubAccountName.
- **Moderate:** Multi-unit PricingUnit normalization. OpenAI's billing units vary by service type; the normalization table must cover all active model types.
- **Low:** Enterprise ContractedCost. OpenAI does not expose negotiated rates via the Usage API.

---

## Sources

- OpenAI API Documentation: [platform.openai.com/docs](https://platform.openai.com/docs)
- OpenAI Pricing: [openai.com/api/pricing](https://openai.com/api/pricing)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
