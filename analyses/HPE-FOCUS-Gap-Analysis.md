# HPE & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** HPE (Hewlett Packard Enterprise)  
**Prepared:** June 25, 2026  
**Source:** HPE GreenLake Platform API; HPE invoice system  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 29 Present, 10 Deviation, 0 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 10 N/A

---

## Executive Summary

HPE GreenLake delivers on-premises infrastructure as a pay-per-use service: customers meter actual consumption of compute, storage, and networking capacity and pay monthly based on usage above a committed minimum. This model gives HPE a billing data structure with clear PricingQuantity and PricingUnit per meter, and a workspace/tenant account hierarchy that maps to FOCUS SubAccount. All 21 Mandatory columns have source data. The 10 Deviations cover cost enrichment (list and contracted pricing are enterprise-negotiated), ChargeCategory and ServiceCategory derivation, and CommitmentDiscountStatus logic. Seven Missing Conditional columns are in the SKU price catalog and unit price families, which HPE's billing API does not expose for enterprise customers. Ten columns are N/A: the CommitmentDiscount family (HPE's minimum commitment is a pricing tier, not a per-resource discount) and CapacityReservation.

**Recommendation:** Build the GreenLake metered consumption transform first. HPE's per-meter billing, resource hierarchy, and workspace structure give a conformant structural foundation. Add list and contracted pricing from HPE's price book as a supplementary data step. Tag support and ServiceCategory mapping round out the dataset.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**HPE GreenLake Platform API**: HPE GreenLake exposes billing and usage data through the GreenLake Platform API and the HPE Consumption Analytics service. Endpoints provide monthly usage metrics per service, workspace, and resource. Key fields: `workspace_id`, `workspace_name`, `service_name`, `meter_name`, `quantity`, `unit`, `cost`, `currency`, `start_date`, `end_date`, `resource_id`, `resource_name`.

**HPE Invoice System**: Monthly invoices are generated per customer account. Invoice data includes: invoice number, billing period, line items per service and meter, totals.

Key characteristics for FOCUS:
- **Metered model:** HPE GreenLake bills per meter per service (compute: vCPU-hours, RAM GB-hours; storage: TB-hours). PricingQuantity and PricingUnit are present for all charge rows.
- **Enterprise pricing:** HPE GreenLake pricing is entirely enterprise-negotiated. No public API-accessible list price or rate card exists. ListUnitPrice and ContractedUnitPrice require supplementary price book data.
- **Workspace hierarchy:** HPE GreenLake organizes resources within Workspaces (and sometimes Tenants within Workspaces). This maps to FOCUS SubAccountId and SubAccountName.
- **On-premises deployment:** HPE GreenLake is deployed in customer or HPE data centers. The physical location maps to RegionId/RegionName but the concept of AvailabilityZone does not apply.
- **Tags:** HPE GreenLake supports resource-level tagging. Tag data is available via the GreenLake API.
- **Minimum commitment:** HPE GreenLake contracts include a minimum committed monthly payment. This is a pricing tier, not a per-resource CommitmentDiscount. Charges above the committed minimum are billed at a higher rate; charges at or below the committed level are billed at the committed rate.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Each column carries a feature level: Mandatory (must exist and be populated where applicable), Conditional (must exist; populated when the provider's model triggers the condition, otherwise null), or Recommended. A conformant dataset presents the full column set under FOCUS column IDs, populates every Mandatory column, satisfies Conditional columns where applicable, and uses the correct types and allowed values.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | HPE source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Monthly invoice amount per meter or line item | Present |
| EffectiveCost | Mandatory | For committed-tier usage, = BilledCost; for usage above committed minimum billed at overage rate, requires cost recalculation to reflect what the amortized commitment cost would have been | Deviation |
| ListCost | Mandatory | HPE list price × PricingQuantity; HPE's list price (MSRP) exists in the HPE price book but is not exposed via API; requires supplementary price book data | Deviation |
| ContractedCost | Mandatory | Enterprise-negotiated rate × PricingQuantity; not accessible via the billing API | Deviation |
| BillingAccountId | Mandatory | HPE customer account number | Present |
| BillingAccountName | Mandatory | Customer company name from HPE contract | Present |
| BillingCurrency | Mandatory | Invoice currency (USD, EUR, or regional currency per contract) | Present |
| BillingPeriodStart | Mandatory | Invoice period start date | Present |
| BillingPeriodEnd | Mandatory | Invoice period end date | Present |
| ChargePeriodStart | Mandatory | Meter period start (typically = BillingPeriodStart for monthly billing) | Present |
| ChargePeriodEnd | Mandatory | Meter period end | Present |
| ChargeDescription | Mandatory | Meter name + service label (e.g., "Compute - vCPU Hours", "Storage - Capacity TB Hours") | Present |
| ChargeCategory | Mandatory | Derive: "Usage" for metered consumption; "Recurring" charges are technically "Usage" in FOCUS terms; "Adjustment" for credits or corrections | Deviation |
| ChargeClass | Mandatory (nullable) | null except for correction charges | Present |
| InvoiceIssuerName | Mandatory | "Hewlett Packard Enterprise" | Present |
| ProviderName | Mandatory (dep. v1.3) | "HPE" | Present |
| PublisherName | Mandatory (dep. v1.3) | "HPE" for HPE services; third-party software publisher names for software-as-a-service layers | Present |
| ServiceName | Mandatory | HPE GreenLake service name (e.g., "HPE GreenLake for Compute", "HPE GreenLake for Block Storage") | Present |
| ServiceCategory | Mandatory | Map HPE service type to FOCUS enum: Compute services → "Compute"; Block/Object/File storage → "Storage"; Networking services → "Networking"; Database services → "Databases" | Deviation |
| PricingQuantity | Mandatory | Meter quantity (e.g., vCPU-hours, TB-hours, port-hours) | Present |
| PricingUnit | Mandatory | Meter unit (e.g., "vCPU-Hour", "TB-Hour", "Port-Hour") | Present |
| ConsumedQuantity | Conditional | Actual measured consumption; for HPE GreenLake, typically = PricingQuantity (metered at point of consumption) | Present |
| ConsumedUnit | Conditional | = PricingUnit | Present |
| ListUnitPrice | Conditional | HPE MSRP (list price) per meter unit; not exposed via billing API; requires HPE price book integration | Missing: Conditional |
| ContractedUnitPrice | Conditional | Enterprise-negotiated rate per meter unit; not exposed via billing API | Missing: Conditional |
| PricingCategory | Conditional | Derive: "Committed" for usage within the minimum commitment tier; "Standard" for overage usage above the committed minimum | Deviation |
| ChargeFrequency | Conditional | "Usage-Based" for metered consumption charges; "Recurring" for flat monthly fees (support, software licenses) | Deviation |
| BillingAccountType | Conditional | Derive from HPE customer agreement type (e.g., "Enterprise") | Present |
| SubAccountId | Conditional | HPE GreenLake Workspace ID | Present |
| SubAccountName | Conditional | HPE GreenLake Workspace name | Present |
| SubAccountType | Conditional | "Workspace" | Present |
| ResourceId | Conditional | HPE GreenLake resource identifier; format varies by service type (server IDs, volume IDs, etc.) | Deviation |
| ResourceName | Conditional | Resource display name from GreenLake API | Present |
| ResourceType | Conditional | HPE service resource type (e.g., "Virtual Machine", "Block Volume", "Network Port") | Present |
| SkuId | Conditional | HPE part number or service SKU from price book | Present |
| Tags | Conditional | HPE GreenLake resource tags; parse to FOCUS key-value format | Deviation |
| PricingCurrency | Conditional | = BillingCurrency | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice; Missing because ListUnitPrice requires price book integration | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Missing because ContractedUnitPrice requires enterprise pricing data | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost; Deviation because EffectiveCost requires commitment-tier logic | Deviation |
| SkuMeter | Conditional | Meter identifier exists in billing data but does not map to a FOCUS SkuMeter display name format | Missing: Conditional |
| SkuPriceId | Conditional | Price book rate identifier not exposed in billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Tiered pricing details not exposed in billing API; HPE GreenLake has committed vs. overage tiers | Missing: Conditional |
| RegionId | Conditional | HPE data center or customer site location code | Present |
| RegionName | Conditional | HPE data center display name (e.g., "HPE US East Data Center", "Customer Site - London") | Present |
| CommitmentDiscountId | Conditional | N/A: HPE's minimum commitment is a pricing tier, not a per-resource commitment discount in the FOCUS sense | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A: HPE on-premises hardware does not have a FOCUS CapacityReservation construct | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | HPE invoice number | Present |
| ServiceSubcategory | Recommended | No native field; requires mapping from HPE service names to subcategory labels | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: HPE GreenLake is deployed in physical data centers; the cloud AZ concept does not apply | N/A |

**Tally:** 29 Present, 10 Deviation, 0 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 10 N/A

### 1.4 What Is Solved, and What Remains

**Solved**

HPE GreenLake's metered consumption model provides clean PricingQuantity and PricingUnit for every charge row. The workspace hierarchy maps to FOCUS SubAccountId and SubAccountName. Resource identifiers, names, and types are available from the GreenLake API. RegionId and RegionName cover HPE data center locations. InvoiceId is available from the HPE invoice system.

**Remaining**

The main gap is unit pricing. HPE GreenLake pricing is enterprise-negotiated, and neither the list price (MSRP) nor the contracted rate is exposed via the billing API. ListUnitPrice and ContractedUnitPrice require integration with HPE's price book, which is typically delivered as a spreadsheet or customer portal document. ResourceId needs a consistent format mapping across HPE's diverse resource types.

The CommitmentDiscount family is N/A because HPE's minimum commitment is a pricing-tier mechanism, not a per-resource FOCUS CommitmentDiscount construct. Seven Missing Conditional columns are in the SKU price catalog and unit price families.

### 1.5 Deviations to Fix

**EffectiveCost**  
For usage within the committed minimum tier, EffectiveCost = BilledCost. For overage usage billed at the higher overage rate, FOCUS EffectiveCost should reflect what the amortized committed rate would have been, not the overage rate. This requires knowing the committed minimum amount and prorating it.

**ListCost and ContractedCost**  
Integrate HPE's MSRP price book for ListCost. ContractedCost requires the customer's negotiated rate, which HPE does not expose via the billing API. Until HPE provides a programmatic rate-card API, both require supplementary data files per customer.

**ChargeCategory**  
Derive from charge type: metered consumption → "Usage"; adjustment credits → "Credit"; one-time setup fees → "Purchase".

**ServiceCategory**  
Map HPE GreenLake service types: compute services → "Compute"; block, object, file storage → "Storage"; networking ports and switches → "Networking"; database services → "Databases"; Kubernetes and container services → "Compute".

**ResourceId**  
HPE GreenLake assigns resource IDs that vary by service type (server UUIDs, volume IDs, etc.). Define a consistent format convention for the FOCUS ResourceId column that normalizes across HPE's resource types.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2. ProviderName and PublisherName are deprecated in v1.3 and removed in v1.4.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. HPE's 0 Missing Mandatory makes the structural conformance bar achievable after Phase 1. The ListCost/ContractedCost supplementary data approach must be documented during certification.

### 2.3 Phased Roadmap

**Phase 0:** Confirm GreenLake Platform API access. Pull sample billing data for one month across compute, storage, and networking. Verify field availability for meter quantities, workspace IDs, and resource identifiers.

**Phase 1: Core metered consumption transform.** Map BilledCost, ChargePeriod, BillingAccount, SubAccount (workspace), ResourceId/Name/Type, RegionId/Name, ServiceName, SkuId, PricingQuantity/Unit, ConsumedQuantity/Unit, InvoiceId, ChargeClass, InvoiceIssuerName. Derive ChargeCategory and ServiceCategory from service type. Delivers conformant output for the 29 Present columns.

**Phase 2: Cost enrichment.** Integrate HPE price book (MSRP) for ListCost and ListUnitPrice. Add contracted rate file per customer for ContractedCost. Implement PricingCategory = "Committed" vs. "Standard" based on minimum commitment tier. Implement EffectiveCost logic for overage rows. Add Tags from GreenLake API.

**Phase 3: Finalize and certify.** Add ServiceSubcategory mapping. Drop ProviderName, PublisherName (v1.4). Validate with FOCUS Validator. Submit for certification.

### 2.4 FOCUS Use Cases HPE GreenLake Customers Unlock

**After Phase 1:** Cost by service and meter across all GreenLake workspaces. Resource-level cost attribution. Site/data-center cost comparison. Invoice reconciliation via InvoiceId.

**After Phase 2:** List vs. contracted vs. billed cost comparison to verify enterprise discount application. PricingCategory-based reporting to show committed vs. overage consumption cost. Tag-based chargeback by team or project.

**Out of scope:** CommitmentDiscount use cases (HPE's minimum commitment is a pricing tier, not a FOCUS CommitmentDiscount). AvailabilityZone analysis. Capacity reservation tracking.

---

## Part 3: Immediate Next Steps

1. Establish access to the HPE GreenLake Platform API and pull a sample monthly billing dataset across compute, storage, and networking meters.
2. Obtain the HPE MSRP price book (typically a spreadsheet from HPE) and map each meter unit to a list unit price. Design the programmatic price book integration.
3. Build the ServiceCategory and ChargeCategory mapping tables from HPE service type identifiers.
4. Define the ResourceId format convention to normalize resource IDs across HPE's diverse resource types.
5. Run the Phase 1 transform through the FOCUS Validator. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** HPE GreenLake's metered billing exposes per-meter quantity, unit, cost, workspace, and resource data. The 29 Present columns are grounded in documented GreenLake API fields.
- **High:** HPE GreenLake Workspace hierarchy maps cleanly to FOCUS SubAccountId and SubAccountName. Workspace IDs and names are available from the GreenLake account management API.
- **Moderate:** ServiceCategory and ChargeCategory mapping. HPE's service catalog is broad (compute, storage, networking, databases, containers). A comprehensive mapping requires reviewing the full GreenLake service catalog.
- **Low:** ListCost and ContractedCost from the HPE price book. The price book is typically a static document, not a machine-readable API. Automated integration requires either HPE publishing a pricing API or a manual ETL process per customer.
- **Unknown:** CommitmentDiscount applicability. If HPE introduces a per-resource commitment model (analogous to cloud reserved instances) in a future GreenLake release, the N/A status of the CommitmentDiscount family should be revisited.

---

## Sources

- HPE GreenLake Platform Documentation: [developer.greenlake.hpe.com](https://developer.greenlake.hpe.com)
- HPE GreenLake Consumption Analytics: [hpe.com/h20195/v2/GetPDF.aspx/a00120892enw.pdf](https://www.hpe.com/us/en/services/greenlake.html)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
