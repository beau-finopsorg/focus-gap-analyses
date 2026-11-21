# Naver Cloud Platform & FOCUS: Data Generator Gap Analysis

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** NAVER Cloud Corp. (Naver Cloud Platform, South Korea sovereign cloud)  
**Prepared:** July 1, 2026  
**Source:** Naver Cloud Platform Cost and Usage API (`/billing/v1/cost/getDemandCostList`, `getProductDemandCostList`, `getContractDemandCostList`, `getContractUsageList`, `getContractUsageListByDaily`, `getContractSummaryList`, `getCostRelationCodeList`); Cost Explorer; Sub Account and Organization services  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 13 Present, 25 Deviation, 2 Missing Mandatory, 2 Missing Recommended, 0 Missing Conditional, 15 N/A

---

## Executive Summary

Naver Cloud Platform (NCP) is the sovereign public cloud operated by NAVER Cloud Corp., serving the South Korean market with Classic and VPC platforms and a public-institution region. Billing and usage data are exposed through a RESTful Cost and Usage API on `billingapi.apigw.ntruss.com`. The data needed for FOCUS conformance is split across two surfaces that do not share a grain. The cost surface (`getDemandCostList`, `getProductDemandCostList`, `getContractDemandCostList`) is monthly and carries a full discount decomposition and net billed amount, but aggregates to member, product, or contract rather than to a resource per day. The usage surface (`getContractUsageListByDaily`) is daily and resource-level, carrying `instanceNo`, `instanceName`, `productCode`, `regionCode`, and metered quantities, but carries no cost. A conformant FOCUS row requires joining the two.

NCP's discount model is unusually well itemized for a native billing feed. The cost records break the reduction into `promiseDiscountAmount` (its committed-use, or "promise," discount), `promotionDiscountAmount`, `productDiscountAmount`, `creditDiscountAmount`, `customerDiscountAmount`, and `etcDiscountAmount`, with `useAmount` as the pre-discount list figure and `demandAmount` as the net. This means ListCost and EffectiveCost are reconstructable from data already present, once the discounts are joined down to the resource-day grain. The two genuinely substantive Mandatory gaps are producing BilledCost and EffectiveCost at daily resource granularity, because the itemized costs live only at the monthly product or contract aggregate today.

Fifteen columns are N/A under NCP's model as reflected in this API. The cost and usage feeds expose no resource tags (sub-account tagging exists but does not flow to billing lines), no capacity-reservation construct, and no SKU price-detail objects; the pricing-currency family collapses because billing and pricing are both KRW at an applied exchange rate of 1.

**Recommendation:** Build one FOCUS row per resource per day by joining `getContractUsageListByDaily` (instanceNo, productCode, regionCode, daily quantity, service dates) to the monthly `getProductDemandCostList`/`getContractDemandCostList` discount and amount fields, allocating the itemized discounts and net amount from the monthly aggregate down to the resource-day. SubAccountId from `memberNo` under an Organization, BillingAccountId from the master `memberNo`, ResourceId from `instanceNo`, RegionId from `regionCode`, currency KRW.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

NCP's billing and usage data lives in the Cost and Usage API at `https://billingapi.apigw.ntruss.com/billing/v1/`, called with GET or POST and authenticated with a timestamp, IAM access key, and HMAC-SHA256 signature. Responses are XML by default or JSON on request. The API separates cost from usage.

**Cost surface (monthly):**
- `getDemandCostList` returns one billing summary per `memberNo` per `demandMonth`: `useAmount` (pre-discount), a set of discount fields (`promiseDiscountAmount`, `promotionDiscountAmount`, `etcDiscountAmount`, `customerDiscountAmount`, `productDiscountAmount`, `creditDiscountAmount`, `rounddownDiscountAmount`, `currencyDiscountAmount`), `thisMonthDemandAmount` (net), VAT fields, `totalDemandAmount`, `payCurrency` (code KRW), and `thisMonthAppliedExchangeRate`.
- `getProductDemandCostList` breaks the month down by `productDemandType` (a code such as `NET_SVR` "Network - Server&LoadBalancer" plus a `regionCode`), with the same discount fields, `defaultAmount`, `useAmount`, and `demandAmount` per product line.
- `getContractDemandCostList` breaks the month down by contract, carrying `demandType`, `demandTypeDetail`, a nested `contract` (with `contractNo`, `contractType`, `contractStatus`, dates, `instanceName`, `regionCode`, and a `contractProductList` with `productCode`, `priceNo`, `promiseNo`, `instanceNo`, `productItemKind`), plus `unitUsageQuantity`, `usageUnit`, `productPrice`, `useAmount`, discount fields, and `demandAmount`.

**Usage surface (daily and monthly):**
- `getContractUsageListByDaily` returns daily service usage per resource: an `account` (`memberNo`), a `useDate` (`useStartDate`/`useEndDate` as ISO 8601 with +0900 offset), a `contract` block (`contractNo`, `contractType`, `contractStatus`, dates, `instanceName`, `regionCode`), a `contractProduct` block (`productCode`, `priceNo`, `promiseNo`, `instanceNo`, `productItemKind`, `productRatingType`, service dates, size/count), and a `usage` block (`meteringType`, `usageQuantity` with `unit`, and `userUsageQuantity` with `userUnit`, for example 44124 `USAGE_SEC` normalized to 12.256667 `HOUR`).
- `getContractUsageList` is the non-daily equivalent; `getContractSummaryList` returns the user contract summary; `getCostRelationCodeList` returns the code dictionary for the various code/codeName pairs.

Key characteristics:
- **Daily usage granularity:** `getContractUsageListByDaily` yields 24-hour usage blocks per resource, with quantities in both raw metering units and user-facing units.
- **Monthly cost granularity:** all three cost endpoints aggregate to the month at member, product, or contract grain. There is no daily cost line and no per-resource cost line in the cost feed.
- **Accounts and sub-accounts:** `memberNo` is the billing entity. The Organization service consolidates expenses across member accounts (queried with `isOrganization=true`, master only), and Sub Account provides IAM identities under a member. Partner accounts are queried with `isPartner=true`.
- **Committed-use discounts:** the "promise" mechanic (`promiseNo` on a contract product, `promiseDiscountAmount` on the cost line) is NCP's commitment discount. It is itemized in the cost feed but has no dedicated commitment object with an ID, term, or status in this API.
- **Currency:** `payCurrency` is KRW with `thisMonthAppliedExchangeRate` of 1 for domestic accounts, so billing currency and pricing currency are the same.
- **Regions:** `regionCode` (for example `KR`) is present on contract and usage lines. There is no availability-zone field in the cost or usage data.
- **Tags:** sub-accounts can be tagged in the Sub Account console, but resource tags do not appear in the cost or usage API records.

### 1.2 How Conformance Is Judged

FOCUS conformance is judged column by column against the feature level each column carries. Feature levels for this analysis were verified against the FOCUS v1.2 specification Content Constraints tables, not recalled from memory. NCP exposes no capacity-reservation construct, so both CapacityReservation columns are N/A. The cost and usage feeds carry no resource tags, so Tags is N/A. Billing and pricing currency are identical (KRW at exchange rate 1), so the four PricingCurrency columns are N/A. NCP has no dedicated commitment object (only an itemized promise discount and a `promiseNo` reference), so the seven-column CommitmentDiscount family cannot be populated from this API and is treated as N/A pending a commitment-detail source. SKU price-detail objects are absent, so SkuPriceId and SkuPriceDetails are N/A.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

Feature levels verified against the FOCUS Specification v1.2.

| FOCUS Column | Level (v1.2) | Naver Cloud source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Monthly demandAmount only, not per resource per day; substantive to produce at charge grain | Missing: Mandatory |
| EffectiveCost | Mandatory | Derive: useAmount minus itemized discounts, allocated to resource-day; monthly only today | Missing: Mandatory |
| ListCost | Mandatory | Derive: useAmount (pre-discount), allocated from monthly product/contract to resource-day | Deviation |
| ContractedCost | Mandatory | Derive: useAmount minus promiseDiscountAmount (committed rate), allocated to resource-day | Deviation |
| BillingAccountId | Mandatory | memberNo (master under an Organization) | Present |
| BillingAccountName | Mandatory | Account name (not in cost feed; from account profile) | Deviation |
| BillingCurrency | Mandatory | payCurrency.code (KRW) | Present |
| BillingPeriodStart | Mandatory | Derive: first day of demandMonth | Deviation |
| BillingPeriodEnd | Mandatory | Derive: first day of the following month (exclusive) | Deviation |
| ChargePeriodStart | Mandatory | useDate.useStartDate (daily usage) | Present |
| ChargePeriodEnd | Mandatory | useDate.useEndDate; normalize to exclusive-end | Deviation |
| ChargeDescription | Mandatory | Derive from productItemKind.codeName + instanceName | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for metered lines; "Credit" for creditDiscountAmount; "Tax" for VAT | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | Constant "NAVER Cloud Corp." | Deviation |
| ProviderName | Mandatory (dep. v1.3) | Constant "Naver Cloud Platform" | Deviation |
| PublisherName | Mandatory (dep. v1.3) | Constant "Naver Cloud Platform" | Deviation |
| ServiceName | Mandatory | Derive from productItemKind / productDemandType codeName | Deviation |
| ServiceCategory | Mandatory | Map productItemKind to a FOCUS ServiceCategory (Compute, Storage, Networking) | Deviation |
| PricingQuantity | Mandatory | usage.usageQuantity (or userUsageQuantity); flat-rate metered SKUs | Deviation |
| PricingUnit | Mandatory | Normalize usage.unit (USAGE_SEC, USAGE_DAY) or userUnit (HOUR) to FOCUS unit | Deviation |
| ConsumedQuantity | Conditional | usage.userUsageQuantity | Present |
| ConsumedUnit | Conditional | usage.userUnit.codeName (e.g., "Hour(s)"); normalize | Deviation |
| ListUnitPrice | Conditional | productPrice (contract cost feed) or List Price API getPriceList | Deviation |
| ContractedUnitPrice | Conditional | Derive: list unit price net of promise discount | Deviation |
| PricingCategory | Conditional | Derive: "Standard" on demand; "Committed" where promiseNo is set | Deviation |
| ChargeFrequency | Recommended | Derive: "Usage-Based" for metered; "Recurring" for monthly/promise contracts | Deviation |
| BillingAccountType | Conditional | Derive: "Billing Account" | Present |
| SubAccountId | Conditional | memberNo of the member account under an Organization | Present |
| SubAccountName | Conditional | Member account name (from account profile, not cost feed) | Deviation |
| SubAccountType | Conditional | Derive: "Organization Member Account" | Present |
| ResourceId | Conditional | contractProduct.instanceNo | Present |
| ResourceName | Conditional | contract.instanceName | Present |
| ResourceType | Conditional | Derive from productCode / productRatingType.codeName | Deviation |
| SkuId | Conditional | contractProduct.productCode | Present |
| Tags | Conditional | N/A: cost and usage feeds expose no resource tags | N/A |
| PricingCurrency | Conditional | N/A: pricing currency equals billing currency (KRW, exchange rate 1) | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A: single-currency billing | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A: single-currency billing | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A: single-currency billing | N/A |
| SkuMeter | Conditional | Derive: meteringType.codeName + unit (e.g., "Server Usage per second") | Deviation |
| SkuPriceId | Conditional | priceNo (contractProduct.priceNo) | Present |
| SkuPriceDetails | Conditional | N/A: no SKU price-detail object in the API | N/A |
| RegionId | Conditional | contract.regionCode (e.g., KR) | Present |
| RegionName | Conditional | Map regionCode to display name via getRegionList | Deviation |
| CommitmentDiscountId | Conditional | N/A: no commitment object; only promiseNo reference and itemized discount | N/A |
| CommitmentDiscountName | Conditional | N/A: no commitment object | N/A |
| CommitmentDiscountType | Conditional | N/A: no commitment object | N/A |
| CommitmentDiscountCategory | Conditional | N/A: no commitment object | N/A |
| CommitmentDiscountStatus | Conditional | N/A: no used/unused status exposed | N/A |
| CommitmentDiscountQuantity | Conditional | N/A: no committed quantity exposed | N/A |
| CommitmentDiscountUnit | Conditional | N/A: no committed unit exposed | N/A |
| CapacityReservationId | Conditional | N/A: no capacity reservation construct | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | demandNo (getDemandCostList) | Deviation |
| ServiceSubcategory | Recommended | Map from productItemKind / productRatingType | Missing: Recommended |
| AvailabilityZone | Recommended | Not exposed in cost or usage data | Missing: Recommended |

**Tally:** 13 Present, 25 Deviation, 2 Missing Mandatory, 2 Missing Recommended, 0 Missing Conditional, 15 N/A. The 15 N/A are Tags, the four PricingCurrency columns, the seven CommitmentDiscount columns, the two CapacityReservation columns, and SkuPriceDetails. There are no Missing Conditional columns: the CommitmentDiscount and CapacityReservation families are classified N/A rather than missing because NCP's model does not expose those constructs, which is the honest reading of the API. The two Missing Mandatory (BilledCost, EffectiveCost) are the substantive gaps; both stem from the same cause, cost living only at the monthly aggregate.

### 1.4 What Is Solved, and What Remains

**Solved:** Resource identity is native and clean: `instanceNo` (ResourceId), `instanceName` (ResourceName), `productCode` (SkuId), `priceNo` (SkuPriceId), `regionCode` (RegionId), and daily charge periods. The Organization model gives a real BillingAccountId and SubAccountId. Nineteen of the 21 Mandatory columns have a source; the two exceptions are the cost columns at daily resource grain.

**Substantive gaps (real data work, not plumbing):**
- **BilledCost and EffectiveCost at charge grain.** The net amount (`demandAmount`, `thisMonthDemandAmount`) and the full discount decomposition exist only in the monthly cost feed at member, product, or contract aggregate. Producing per-resource, per-day BilledCost and EffectiveCost requires allocating the monthly itemized amounts down to the resource-day usage lines. This is the join, and it is the real engineering.

**Trivial gaps (derivable from data present):** ListCost from `useAmount`; ContractedCost from `useAmount` minus `promiseDiscountAmount`; PricingQuantity and PricingUnit from the daily usage quantity and unit for flat-rate metered SKUs; ChargeCategory, ServiceCategory, ServiceName, ResourceType, BillingPeriodStart/End, and the constant issuer/provider columns. These are shape and derivation work, not missing data.

**Remaining Conditional/Recommended:** The CommitmentDiscount and CapacityReservation families cannot be populated from this API. ServiceSubcategory and AvailabilityZone are not emitted.

### 1.5 Deviations to Fix

**Cost columns:** allocate the monthly `useAmount`, itemized discounts, and `demandAmount` from `getProductDemandCostList`/`getContractDemandCostList` down to the daily resource lines. Set ListCost = allocated `useAmount`, ContractedCost = `useAmount` minus `promiseDiscountAmount`, EffectiveCost = net of all applicable discounts, BilledCost = allocated `demandAmount`. Do not collapse all four to one figure: the discount itemization is present and should be preserved.

**PricingUnit / ConsumedUnit:** normalize NCP metering units (`USAGE_SEC`, `USAGE_DAY`, `HOUR`) to FOCUS unit strings ("Hours", "Days"), reconciling raw `usageQuantity` against `userUsageQuantity`.

**ChargeCategory:** "Usage" for metered lines, "Credit" where `creditDiscountAmount` applies, "Tax" for the VAT lines in the demand summary.

**ServiceCategory / ServiceName:** map `productItemKind` and `productDemandType` codes (SVR, SW, NET_SVR) to FOCUS ServiceCategory members and readable service names using `getCostRelationCodeList`.

**RegionName:** resolve `regionCode` to a display name through `getRegionList`.

**InvoiceId:** map `demandNo` from the monthly demand record.

**Constants:** InvoiceIssuerName, ProviderName, and PublisherName are constants ("NAVER Cloud Corp." / "Naver Cloud Platform"); populate them explicitly.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2, the current certification baseline. For the v1.4 build, drop ProviderName and PublisherName (removed in v1.4) and adopt the Invoice Detail and billing-period datasets, which suit NCP's monthly demand records well.

### 2.2 What Certification Requires

The program is "FinOps Certified FOCUS v1.2 Conformant"; contact `member-cert@finops.org` for the RFI. Membership is required for certification, though contributing to the specification is open and free. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Document Tags, CapacityReservation, and the PricingCurrency family as not applicable to this API, and document the promise-discount handling. Validate with the FOCUS Validator and convert with the FOCUS Converter against the FOCUS Requirements Model.

### 2.3 Phased Roadmap

**Phase 0:** Confirm scope (Cost and Usage API, KRW, Classic and VPC) and version. Pull one month of `getContractUsageListByDaily` plus the matching `getProductDemandCostList` and `getContractDemandCostList`, and the `getCostRelationCodeList` code dictionary.

**Phase 1: Join and Mandatory close.** Build the resource-day to monthly-cost join and allocate itemized amounts down to charge lines. Populate the four cost columns (BilledCost, EffectiveCost, ListCost, ContractedCost) and the trivial Mandatory derivations (PricingQuantity, PricingUnit, ChargeCategory, ServiceCategory, ServiceName, BillingPeriod dates) plus core identity (ResourceId, SubAccountId, BillingAccountId, RegionId).

**Phase 2: Deviations.** Normalize units and enums, resolve RegionName and ServiceName from code lists, map InvoiceId from demandNo, set the constant issuer/provider columns.

**Phase 3: Conditional and Recommended.** Add ServiceSubcategory. Document the CommitmentDiscount and CapacityReservation families and the PricingCurrency family as not exposed. If a commitment-detail source becomes available, populate the CommitmentDiscount columns from the promise construct.

**Phase 4: Mature and certify.** Adopt v1.4 (drop ProviderName/PublisherName, add Invoice Detail dataset). Extend from KRW-domestic to any multi-currency partner accounts if applicable. Validate and certify.

### 2.4 FOCUS Use Cases Unlocked

- **As soon as Phase 1 lands (resource, region, day, cost):** cost reporting by service, region, and member account; resource-level cost visibility; chargeback by Organization member account; effective-cost and committed-cost trending.
- **After Phase 2/3 (clean enums, promise data):** promise-discount coverage analysis if a commitment source is added; anomaly detection on daily resource cost.
- **Out of scope for this API today:** tag-based allocation (no resource tags in the feed), capacity-reservation analysis (no reservation construct), and multi-currency pricing analysis (single-currency KRW).

---

## Part 3: Immediate Next Steps

1. Pull one month of `getContractUsageListByDaily` and the matching `getProductDemandCostList`/`getContractDemandCostList` for a member account that uses a promise (committed) contract.
2. Confirm how the monthly itemized discounts can be allocated down to daily resource lines, and implement the Phase 1 join and cost derivation.
3. Run the resulting sample through the FOCUS Validator to baseline conformance.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** NCP exposes daily resource-level usage (instanceNo, instanceName, productCode, regionCode, quantity, service dates) through `getContractUsageListByDaily`, and monthly itemized cost (useAmount, six-way discount breakdown, demandAmount, KRW currency) through `getDemandCostList`/`getProductDemandCostList`/`getContractDemandCostList`. Field names are grounded in the published API schema and sample responses.
- **High:** The two surfaces do not share a grain (daily resource usage versus monthly product/contract cost), so BilledCost and EffectiveCost at charge grain are a substantive join, not a rename. ListCost and ContractedCost are derivable from useAmount and promiseDiscountAmount.
- **Moderate:** The precise allocation method for pushing monthly product/contract discounts down to individual daily resource lines is not specified by NCP and would be defined during implementation; the choice affects EffectiveCost accuracy at the resource level.
- **Moderate:** The promise (committed-use) discount is itemized in cost but has no dedicated commitment object with ID, term, or status in this API, so the CommitmentDiscount family is classified N/A pending a commitment-detail source rather than as a build target. This is the item most likely to change if a commitment API exists that was not surfaced in the reviewed docs.
- **Moderate:** Tags are treated as N/A because resource tags do not appear in the cost or usage records reviewed; sub-account tagging exists but does not flow to billing lines. If NCP exposes resource tags elsewhere, Tags moves from N/A to a build target.
- **Low:** BillingAccountName and SubAccountName come from account profile rather than the cost feed and are treated as a light join. AvailabilityZone is assumed absent based on the reviewed schema.

The bundled FOCUS feature-level table (v1.2 baseline, stamped 2026-06-23) was spot-checked against the live specification; BilledCost and ContractedCost remain Mandatory and v1.4 remains the latest ratified version, so no cache refresh was required. This analysis reflects the data sources reviewed, not a formal certification result. Naver Cloud Platform does not hold the FinOps Certified FOCUS designation; the readiness band below is an assessment of the reviewed data, not a certification. Data quality for this analysis is solid.

---

## Sources

- Naver Cloud Platform Cost and Usage overview: [api.ncloud-docs.com/docs/en/platform-costandusage](https://api.ncloud-docs.com/docs/en/platform-costandusage)
- getDemandCostList: [api.ncloud-docs.com/docs/en/platform-costandusage-getdemandcostlist](https://api.ncloud-docs.com/docs/en/platform-costandusage-getdemandcostlist)
- getProductDemandCostList: [api.ncloud-docs.com/docs/en/platform-costandusage-getproductdemandcostlist](https://api.ncloud-docs.com/docs/en/platform-costandusage-getproductdemandcostlist)
- getContractDemandCostList: [api.ncloud-docs.com/docs/en/platform-costandusage-getcontractdemandcostlist](https://api.ncloud-docs.com/docs/en/platform-costandusage-getcontractdemandcostlist)
- getContractUsageListByDaily: [api.ncloud-docs.com/docs/en/platform-costandusage-getcontractusagelistbydaily](https://api.ncloud-docs.com/docs/en/platform-costandusage-getcontractusagelistbydaily)
- NCP Cost Explorer overview: [guide.ncloud-docs.com/docs/en/costexplorer-overview](https://guide.ncloud-docs.com/docs/en/costexplorer-overview)
- NCP Organization overview: [guide.ncloud-docs.com/docs/en/organization-overview](https://guide.ncloud-docs.com/docs/en/organization-overview)
- NCP Sub Account: [guide.ncloud-docs.com/docs/en/subaccount-use](https://guide.ncloud-docs.com/docs/en/subaccount-use)
- FOCUS Specification v1.2: [focus.finops.org/focus-specification/v1-2](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS Specification v1.4: [finops.org/insights/introducing-focus-1-4](https://www.finops.org/insights/introducing-focus-1-4/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
