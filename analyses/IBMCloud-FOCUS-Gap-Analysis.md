# IBM Cloud as a FOCUS Data Generator: Compliance Gap Analysis

*Analysis run: June 26, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: June 26, 2026
Subject: IBM Cloud IaaS/PaaS service usage billing (native FOCUS v1.2 export API)
Baseline: FOCUS v1.2 (certification baseline). Build target: v1.4 (latest ratified).
Feature levels verified against the FOCUS v1.2 specification on 2026-06-26.
IBM Cloud contacts: Kevin Jacoby, Brad Johnson, Sidhya Iyer

## Executive summary

IBM Cloud now provides a native FOCUS v1.2 export API (`GET https://billing.cloud.ibm.com/v4/accounts/{account_id}/focus/{month}`) that produces a compliant CSV or JSON billing dataset with all 21 mandatory columns and 23 conditional columns natively emitted — no external enrichment required. The API was documented on April 24, 2026 and resolves all of the previously identified derivation challenges: ListCost (from Global Catalog pricing), EffectiveCost (subscription credit amortization), ContractedCost (enterprise contracted rates), ChargeCategory (mapped from IBM charge type codes), ServiceCategory (mapped from IBM resource identifiers), Tags (parsed from `key:value` strings), and CommitmentDiscount identity fields for Flex Point subscription accounts.

What remains: 10 missing conditional columns (SubAccountId/Name/Type — enterprise member-account hierarchy not yet surfaced; PricingCurrencyContractedUnitPrice, PricingCurrencyEffectiveCost, PricingCurrencyListUnitPrice — cross-currency price fields not emitted; SkuPriceId, SkuPriceDetails — SKU price metadata absent; CommitmentDiscountStatus, CommitmentDiscountQuantity — per-charge commitment tracking not computed), 1 missing recommended column (InvoiceId), and 2 legitimate N/A columns (CapacityReservationId/Status — IBM Cloud has no per-resource capacity reservation construct).

Of 57 v1.2 columns: 44 Present, 0 Deviation, 10 Missing Conditional, 1 Missing Recommended, 2 N/A.

## Part 1: The conformance gap

### 1.1 The data source

**IBM Cloud FOCUS Export API** (`GET https://billing.cloud.ibm.com/v4/accounts/{account_id}/focus/{month}`): The primary billing feed for FOCUS-conformant data. Introduced April 24, 2026. Authentication uses IAM Bearer tokens via `Authorization: Bearer {iam_token}`. Path parameters: `account_id` (IBM Cloud account ID) and `month` (YYYY-MM format). Optional request header: `x-focus-version: 1.2` (default; specifies the FOCUS output version). Query parameters: `format` (json | csv; default: json) and `_limit` (pagination limit, max 250, default 200). The API returns a paginated JSON dataset or a full CSV suitable for direct import into FinOps platforms (Apptio Cloudability, CloudHealth, Kubecost) without transformation.

IBM publishes the following coverage:

**16 "Fully Supported" mandatory fields (per IBM documentation):** BilledCost, BillingCurrency, ChargeCategory, ChargeDescription, ChargePeriodEnd, ChargePeriodStart, EffectiveCost, ListUnitPrice, PricingCategory, PricingQuantity, PricingUnit, ProviderName, PublisherName, ResourceId, ResourceName, ServiceCategory, ServiceName, SkuId.

**Additional supported fields:** Account & Billing (BillingAccountId, BillingAccountName, BillingAccountType, BillingPeriodEnd, BillingPeriodStart, InvoiceIssuerName); Geographic (AvailabilityZone, RegionId, RegionName); Commitment & Discount (CommitmentDiscountCategory, CommitmentDiscountId, CommitmentDiscountName, CommitmentDiscountType, CommitmentDiscountUnit); Cost Breakdown (ContractedCost, ContractedUnitPrice, ListCost); Charge Details (ChargeClass, ChargeFrequency); Consumption (ConsumedQuantity, ConsumedUnit); Pricing (PricingCurrency, SkuMeter); Resource Metadata (ResourceType, ServiceSubcategory, Tags); IBM-Specific Extensions (x_DiscountId, x_DiscountName, x_DiscountQuantity, x_OfferId, x_OfferCredit).

Characteristics that matter for FOCUS:

- Monthly grain: the FOCUS API returns monthly granularity. ChargePeriodStart and ChargePeriodEnd span the billing month; no sub-monthly hourly granularity is available via this endpoint.
- Enterprise hierarchy: IBM Cloud Enterprise accounts contain Account Groups and Member Accounts. The FOCUS API emits BillingAccountId at the account level and BillingAccountType for the plan type (PAYG, Subscription, Enterprise), but does not yet surface Member Accounts as SubAccountId. This is the most significant structural gap for enterprise FinOps use cases.
- Subscription credits: IBM Cloud Flex Point subscriptions (spend-based commitment credits) surface via the CommitmentDiscount column family (Id, Name, Type = "Other", Category = "Spend", Unit). CommitmentDiscountStatus ("Used"/"Unused" per charge row) and CommitmentDiscountQuantity are not yet emitted.
- Tags: IBM Cloud user tags in `key:value` string format are natively parsed and emitted as FOCUS key-value pairs by the API. Bare-label tags (no colon) are handled by IBM's convention.
- ChargeCategory values: "Usage", "Purchase", "Tax", "Adjustment". The "Credit" value is absent from IBM's published list; promotional credits and billing credits appear to be represented as negative-cost "Adjustment" rows. This may differ from the FOCUS v1.2-specified "Credit" allowed value and requires confirmation with IBM contacts.
- CapacityReservations: IBM Cloud has no per-resource reserved capacity construct equivalent to AWS CapacityReservations. IBM reserved virtual server instances are modeled as CommitmentDiscount, not CapacityReservation.
- Resource identifiers: Cloud Resource Names (CRNs) — globally unique, machine-parseable, in the format `crn:v1:bluemix:public:{service}:{region}:{account}:{resource-type}:{resource-id}` — are emitted as ResourceId.

### 1.2 How conformance is judged

FOCUS conformance is column-driven. Each column carries a feature level: Mandatory (must exist and be populated where applicable), Conditional (must exist; populated when the provider's model triggers the condition, otherwise null), or Recommended. A conformant dataset presents the full column set under FOCUS column IDs, populates every Mandatory column, satisfies Conditional columns where applicable, and uses the correct types and allowed values. Provider-specific columns are allowed when prefixed `x_`.

### 1.3 Column-by-column status (all 57 FOCUS v1.2 columns)

Status legend: Present (natively emitted by the IBM Cloud FOCUS API); Missing: Conditional; Missing: Recommended; N/A: null valid (does not apply to IBM Cloud's model).

| FOCUS Column | Level (1.2) | IBM Cloud FOCUS API source | Status |
| --- | --- | --- | --- |
| BilledCost | Mandatory | Natively emitted — billed cost in BillingCurrency | Present |
| EffectiveCost | Mandatory | Natively emitted — amortized cost including Flex Point subscription credit allocation | Present |
| ListCost | Mandatory | Natively emitted — derived internally from IBM Global Catalog pricing | Present |
| ContractedCost | Mandatory | Natively emitted — equals ListCost for PAYG; contracted rates for enterprise accounts | Present |
| BillingAccountId | Mandatory | Natively emitted — IBM Cloud account ID | Present |
| BillingAccountName | Mandatory | Natively emitted — IBM Cloud account name | Present |
| BillingCurrency | Mandatory | Natively emitted — ISO 4217 currency code | Present |
| BillingPeriodStart | Mandatory | Natively emitted — first second of billing month | Present |
| BillingPeriodEnd | Mandatory | Natively emitted — last second of billing month | Present |
| ChargePeriodStart | Mandatory | Natively emitted — monthly granularity | Present |
| ChargePeriodEnd | Mandatory | Natively emitted — monthly granularity | Present |
| ChargeDescription | Mandatory | Natively emitted — resource name + plan name + metric description | Present |
| ChargeCategory | Mandatory | Natively emitted — values: "Usage", "Purchase", "Tax", "Adjustment"; "Credit" not documented (credits appear as negative-cost "Adjustment") | Present |
| ChargeClass | Mandatory (nullable) | Natively emitted — null for standard; "Correction" for billing corrections | Present |
| InvoiceIssuerName | Mandatory | Natively emitted — "IBM" | Present |
| ProviderName | Mandatory (dep. v1.3) | Natively emitted — "IBM" | Present |
| PublisherName | Mandatory (dep. v1.3) | Natively emitted — "IBM" for first-party; marketplace publisher name for third-party | Present |
| ServiceName | Mandatory | Natively emitted — e.g., "Cloud Object Storage", "Virtual Servers for VPC" | Present |
| ServiceCategory | Mandatory | Natively emitted — mapped internally from IBM service identifiers | Present |
| PricingQuantity | Mandatory | Natively emitted — metered quantity used in pricing | Present |
| PricingUnit | Mandatory | Natively emitted — e.g., "GIGABYTE-HOURS", "INSTANCE-HOURS" | Present |
| ConsumedQuantity | Conditional | Natively emitted — gross consumption before rateability adjustments | Present |
| ConsumedUnit | Conditional | Natively emitted — unit of consumption | Present |
| ListUnitPrice | Conditional | Natively emitted — list unit price from IBM Global Catalog | Present |
| ContractedUnitPrice | Conditional | Natively emitted — contracted unit rate | Present |
| PricingCategory | Conditional | Natively emitted — "Standard" for PAYG; "Committed" for Subscription accounts | Present |
| ChargeFrequency | Conditional | Natively emitted — "Usage-Based", "Recurring", or "One-Time" | Present |
| BillingAccountType | Conditional | Natively emitted — IBM account plan type (PAYG, Subscription, Enterprise) | Present |
| SubAccountId | Conditional | Not emitted — enterprise member accounts are not surfaced as SubAccountId | Missing: Conditional |
| SubAccountName | Conditional | Not emitted | Missing: Conditional |
| SubAccountType | Conditional | Not emitted | Missing: Conditional |
| ResourceId | Conditional | Natively emitted — Cloud Resource Name (CRN): crn:v1:bluemix:public:{service}:{region}:... | Present |
| ResourceName | Conditional | Natively emitted — resource instance name | Present |
| ResourceType | Conditional | Natively emitted — derived from CRN service segment (e.g., "Virtual Server", "Object Storage Bucket") | Present |
| SkuId | Conditional | Natively emitted — billing plan UUID identifying the plan within a service | Present |
| Tags | Conditional | Natively emitted — IBM `key:value` strings parsed to FOCUS key-value pairs by the API | Present |
| PricingCurrency | Conditional | Natively emitted — pricing currency (typically matches BillingCurrency) | Present |
| PricingCurrencyListUnitPrice | Conditional | Not emitted — cross-currency unit price fields absent from FOCUS API output | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | Not emitted | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | Not emitted | Missing: Conditional |
| SkuMeter | Conditional | Natively emitted — billing metric ID from IBM usage data | Present |
| SkuPriceId | Conditional | Not emitted — pricing plan rate identifier not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not emitted | Missing: Conditional |
| RegionId | Conditional | Natively emitted — e.g., "us-south", "eu-de", "jp-tok" | Present |
| RegionName | Conditional | Natively emitted — e.g., "US South", "Germany", "Japan - Tokyo" | Present |
| CommitmentDiscountId | Conditional | Natively emitted — Flex Point subscription ID | Present |
| CommitmentDiscountName | Conditional | Natively emitted — subscription term and name | Present |
| CommitmentDiscountType | Conditional | Natively emitted — "Other" (spend-based subscription model) | Present |
| CommitmentDiscountCategory | Conditional | Natively emitted — "Spend" (IBM subscriptions are spend-based credit pools) | Present |
| CommitmentDiscountStatus | Conditional | Not emitted — per-charge "Used"/"Unused" status not computed; IBM publishes x_DiscountQuantity extension instead | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | Not emitted — standard field absent; IBM provides x_DiscountQuantity extension | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | Natively emitted — unit of the commitment discount | Present |
| CapacityReservationId | Conditional | N/A — IBM Cloud has no per-resource capacity reservation construct; reserved VMs use CommitmentDiscount | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Not emitted — invoice number available via Invoices API but not included in FOCUS API output | Missing: Recommended |
| ServiceSubcategory | Recommended | Natively emitted — derived from IBM service classification | Present |
| AvailabilityZone | Recommended | Natively emitted — zone ID for VPC resources (e.g., "us-south-1"); null for PaaS and Classic Infrastructure | Present |

Tally: 44 Present, 0 Deviation, 10 Missing Conditional, 1 Missing Recommended, 2 N/A. All 21 Mandatory columns are natively emitted. The 14 columns previously requiring derivation or enrichment (ListCost, ContractedCost, EffectiveCost, ChargeCategory, ServiceCategory, PublisherName, ChargeFrequency, ListUnitPrice, ContractedUnitPrice, Tags, CommitmentDiscountStatus, PricingCurrencyListUnitPrice, PricingCurrencyContractedUnitPrice, PricingCurrencyEffectiveCost) are now handled internally by IBM's FOCUS API.

### 1.4 What's solved, and what remains

The IBM Cloud FOCUS Export API resolves all previously identified derivation and enrichment challenges:

Solved by the FOCUS API: ListCost and ListUnitPrice are computed from Global Catalog pricing and emitted directly. EffectiveCost reflects IBM's Flex Point subscription credit amortization — emitted correctly for both PAYG and subscription accounts. ContractedCost is available for enterprise accounts within the FOCUS API. ChargeCategory, ServiceCategory, ChargeFrequency, and PublisherName are mapped from IBM internal data and emitted as FOCUS-conformant enum values. Tags are parsed from IBM `key:value` strings into FOCUS key-value pairs. CommitmentDiscount identity fields (Id, Name, Type = "Other", Category = "Spend", Unit) are emitted for subscription accounts.

Remaining gaps fall into three areas:

First, enterprise sub-account hierarchy. IBM Cloud's enterprise structure (Enterprise → Account Groups → Member Accounts → Resource Groups) naturally maps Member Accounts to SubAccountId and SubAccountName. The FOCUS API emits BillingAccountId at the account level and BillingAccountType for the plan type, but does not surface Member Accounts as SubAccountId. Enterprise customers lose standard FOCUS sub-account attribution and must rely on IBM's x_ extensions or BillingAccountId alone. Confirm the roadmap for SubAccountId/Name/Type with Kevin Jacoby, Brad Johnson, and Sidhya Iyer.

Second, per-charge commitment tracking. The FOCUS API emits CommitmentDiscount identity fields but not CommitmentDiscountStatus ("Used"/"Unused" per charge row) or CommitmentDiscountQuantity. These are required for subscription waste analysis — identifying which charge rows were covered by Flex Point credits versus billed at PAYG rates within the commitment period. IBM currently provides x_DiscountQuantity as a non-standard extension; promote this to CommitmentDiscountQuantity and add CommitmentDiscountStatus at the charge-row level.

Third, PricingCurrency cross-currency and SKU price fields. IBM emits PricingCurrency but not PricingCurrencyListUnitPrice, PricingCurrencyContractedUnitPrice, or PricingCurrencyEffectiveCost. For accounts where PricingCurrency differs from BillingCurrency (non-USD accounts), these fields are required for multi-currency cost analysis. SkuPriceId and SkuPriceDetails are absent; SkuId and SkuMeter are present but the price-level granularity needed for rate validation is missing. InvoiceId is available via the Invoices API but not included in the FOCUS API output.

### 1.5 Known gaps to address

**SubAccountId for enterprise accounts:** IBM should map each enterprise member account's account ID to SubAccountId, the account name to SubAccountName, and "Account" to SubAccountType in the FOCUS API. For resource-group-level attribution, IBM could optionally nest resource groups as a second sub-account level. Confirm priority and timeline with IBM contacts.

**CommitmentDiscountStatus per charge row:** FOCUS v1.2 requires each charge row to carry CommitmentDiscountStatus = "Used" when covered by a commitment discount, or "Unused" when the commitment was available but not applied. IBM currently emits CommitmentDiscount identity at the row level but does not allocate credit drawdown per charge. Implement proportional or FIFO Flex Point credit allocation to individual usage rows and promote x_DiscountQuantity to the standard CommitmentDiscountQuantity field.

**ChargeCategory "Credit" value:** IBM's published ChargeCategory values are "Usage", "Purchase", "Tax", "Adjustment". The FOCUS v1.2 specification includes "Credit" as a distinct allowed value for rows representing credit issuance. Confirm with IBM contacts whether promotional credits, support credits, and billing adjustments are emitted as ChargeCategory = "Credit" rows or as negative-cost "Adjustment" rows. If the latter, this is a deviation from the FOCUS v1.2 specification.

**PricingCurrency cross-currency fields:** For IBM accounts billing in a non-USD currency where PricingCurrency differs from BillingCurrency, add PricingCurrencyListUnitPrice, PricingCurrencyContractedUnitPrice, and PricingCurrencyEffectiveCost to the FOCUS API output.

**InvoiceId:** The IBM Invoices API (`/v2/accounts/{accountId}/invoices`) provides invoice numbers. Add InvoiceId to the FOCUS export row to enable joining FOCUS rows to invoice-level detail and reconciling with IBM billing statements.

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Live versions: 1.1 (Nov 7, 2024), 1.2 (May 29, 2025, the current certification baseline), 1.3 (Dec 5, 2025), and 1.4 (June 4, 2026, adding Invoice Detail and billing-period datasets). IBM's FOCUS API currently targets v1.2. IBM's mandatory column coverage makes v1.2 certification achievable today. Build toward v1.4 as the next output target. Note that ProviderName and PublisherName are deprecated in v1.3 and removed in v1.4; plan to deprecate them in the v1.4 transition.

### 2.2 What certification requires

Certification for data generators runs through the FinOps Foundation. Contact `member-cert@finops.org` for the RFI. IBM Cloud's FOCUS API mandatory field coverage supports initiating the certification process immediately. Deliverables: a structurally conformant dataset under FOCUS column IDs, public sample data that passes the FOCUS Validator, a documented native-to-FOCUS mapping, and a Conformance Gap Report (this document is its seed). Membership is required for certification.

Tooling: the FOCUS Validator (validate the FOCUS API output against v1.2 requirements), the FOCUS Converter (IBM Cloud provider patterns could be contributed to the open-source project), and the FOCUS Requirements Model (authoritative machine-readable requirements).

### 2.3 Phased roadmap

Phase 1, certify at v1.2 now. Run a sample FOCUS API export through the FOCUS Validator. Confirm the ChargeCategory "Credit" handling with IBM contacts. Open the RFI with `member-cert@finops.org`. IBM's current output supports initiating certification with no additional API changes required for mandatory fields.

Phase 2, close the conditional gaps. Add SubAccountId, SubAccountName, SubAccountType for enterprise member accounts. Emit CommitmentDiscountStatus and CommitmentDiscountQuantity at the charge-row level. Add InvoiceId from the Invoices API. Emit PricingCurrencyListUnitPrice, PricingCurrencyContractedUnitPrice, and PricingCurrencyEffectiveCost for international accounts.

Phase 3, round out SKU price metadata and build to v1.4. Add SkuPriceId and SkuPriceDetails. Adopt the v1.4 column set (drop ProviderName, PublisherName). Validate against v1.4 spec. Contribute IBM Cloud provider mappings to the FOCUS Converter open-source project.

### 2.4 FOCUS Use Cases IBM Cloud customers unlock

Available now with the IBM Cloud FOCUS API: resource-level cost attribution by account and resource instance (ResourceId/Name/Type), multi-account cost consolidation, cost by region (RegionId/Name), cost by service (ServiceName, ServiceCategory, ServiceSubcategory), list-versus-effective cost comparison (negotiated savings identification), subscription credit identification (CommitmentDiscount identity fields), tag-based chargeback and showback, ChargeCategory-based filtering (usage vs. subscription purchases), and PricingCategory-based filtering (Standard vs. Committed).

Unlocked after Phase 2: enterprise member-account-level attribution (SubAccountId/Name), subscription waste analysis (CommitmentDiscountStatus = "Unused"), FOCUS-to-invoice reconciliation (InvoiceId), and cross-currency cost analysis (PricingCurrency* fields).

Out of scope: AvailabilityZone analysis for Classic Infrastructure and PaaS services (zone is null for non-VPC resources); capacity reservation use cases (IBM Cloud has no per-resource capacity reservation construct).

## Part 3: Immediate next steps

1. Confirm ChargeCategory "Credit" handling: does the FOCUS API emit ChargeCategory = "Credit" for promotional or billing credits, or are all credits represented as negative-cost "Adjustment" rows? Contact Kevin Jacoby, Brad Johnson, or Sidhya Iyer.
2. Confirm SubAccount roadmap: will IBM add SubAccountId/Name/Type for enterprise member accounts in the FOCUS API? This is the highest-priority structural gap for enterprise FinOps use cases.
3. Run the FOCUS API output through the FOCUS Validator to confirm v1.2 compliance and surface any issues not identified in this analysis.
4. Open the certification RFI with `member-cert@finops.org`. IBM's mandatory field coverage supports initiating v1.2 certification today.
5. Plan Phase 2 API additions: CommitmentDiscountStatus, CommitmentDiscountQuantity, InvoiceId, and PricingCurrency cross-currency fields. Prioritize CommitmentDiscountStatus for enterprise subscription customers who need subscription waste visibility.

## Confidence summary

- High: All 21 mandatory FOCUS v1.2 columns are natively emitted per IBM's published documentation (April 24, 2026). The 14 previously required derivations are handled internally by IBM's FOCUS API.
- High: CommitmentDiscount identity fields (Id, Name, Type = "Other", Category = "Spend", Unit) are emitted for Flex Point subscription accounts. EffectiveCost is amortized; subscription credit allocation is handled by IBM.
- High: Tags, ServiceCategory, PublisherName, ChargeFrequency, ListCost, EffectiveCost, ContractedCost confirmed as natively emitted per IBM documentation — no external enrichment required.
- Moderate: ChargeCategory "Credit" handling is ambiguous from published documentation. IBM's doc lists "Usage/Purchase/Tax/Adjustment" without "Credit"; whether credits are emitted as "Credit" or "Adjustment" rows requires confirmation with IBM contacts.
- Moderate: SubAccountId/SubAccountName are not in the FOCUS API. IBM's enterprise hierarchy has a natural mapping to these columns but whether IBM plans to add them requires confirmation.
- Moderate: PricingCurrency cross-currency fields may be present for non-USD accounts but are not documented. Scope requires confirmation for international IBM Cloud customers.
- Low: CommitmentDiscountStatus and CommitmentDiscountQuantity per-charge row require per-row credit allocation logic on IBM's side. Timeline for implementation is unknown.

## Sources

- IBM Cloud Docs, FOCUS Export Documentation (April 24, 2026): https://github.com/ibm-cloud-docs/account/blob/master/export-usage-focus-format.md
- IBM Cloud FOCUS Export API: https://billing.cloud.ibm.com/v4/accounts/{account_id}/focus/{month}
- IBM Cloud Docs, Usage Reports API v4: https://cloud.ibm.com/apidocs/metering-reporting
- IBM Cloud Docs, Enterprise Usage Reports API: https://cloud.ibm.com/apidocs/enterprise-apis/resource-usage-reports
- IBM Cloud Docs, Enterprise Billing Units API: https://cloud.ibm.com/apidocs/enterprise-apis/billing-unit
- IBM Cloud Docs, Invoices API: https://cloud.ibm.com/apidocs/billing
- IBM Cloud Docs, Account Management (enterprise hierarchy): https://cloud.ibm.com/docs/enterprise-management
- FOCUS Specification v1.2: https://focus.finops.org/focus-specification/v1-2/
- FinOps Certified FOCUS v1.2 Conformant: https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
