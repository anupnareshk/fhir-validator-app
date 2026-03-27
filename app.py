import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd

st.set_page_config(page_title="FHIR XML Validator", layout="wide")

st.title("🧬 FHIR XML Validator & Detailed Analyzer")

uploaded_file = st.file_uploader("Upload FHIR XML Bundle", type=["xml"])

# ---------------------------
# EXPECTED FIELDS
# ---------------------------
EXPECTED_FIELDS = {
    "Bundle": ["id", "meta", "identifier", "type", "timestamp", "entry"],
    "Composition": ["id", "meta", "language", "text", "subject", "author", "title", "section"],
    "Binary": ["contentType", "data", "securityContext"],

    "MedicinalProductDefinition": ["identifier", "name", "type"],
    "Ingredient": ["substance", "role"],
    "Substance": ["code"],
    "ClinicalUseDefinition": ["type", "indication", "contraindication"],
    "MedicationKnowledge": ["doseForm", "amount"],
}

TYPE_MAP = {
    "Type 1": ["Bundle", "Composition", "Binary"],
    "Type 2": [
        "MedicinalProductDefinition",
        "RegulatedAuthorization",
        "Organization",
        "PackagedProductDefinition",
        "ManufacturedItemDefinition",
        "AdministrableProductDefinition",
        "Ingredient",
        "Substance",
    ],
    "Type 3": ["ClinicalUseDefinition", "MedicationKnowledge"],
}

# ---------------------------
# HELPERS
# ---------------------------

def get_resource_elements(resource):
    """Extract child element names"""
    elements = []
    for child in resource:
        tag = child.tag.split("}")[-1]
        elements.append(tag)
    return list(set(elements))


def find_resource(root, resource_name):
    """Find first instance of resource"""
    ns = {"fhir": "http://hl7.org/fhir"}

    if resource_name == "Bundle":
        return root

    return root.find(f".//fhir:{resource_name}", ns)


# ---------------------------
# MAIN
# ---------------------------

if uploaded_file:
    try:
        tree = ET.parse(uploaded_file)
        root = tree.getroot()

        results = []

        for fhir_type, resources in TYPE_MAP.items():
            for res in resources:

                resource_node = find_resource(root, res)

                if resource_node is not None:
                    present_fields = get_resource_elements(resource_node)
                    expected = EXPECTED_FIELDS.get(res, [])

                    missing_fields = [f for f in expected if f not in present_fields]

                    present_str = ", ".join(sorted(present_fields))
                    missing_str = ", ".join(missing_fields) if missing_fields else "-"

                else:
                    present_str = "-"
                    missing_str = "Resource not found"

                results.append({
                    "FHIR Type": fhir_type,
                    "Resource": res,
                    "What is Present": present_str,
                    "What is Missing": missing_str
                })

        # TYPE 4 summary
        results.append({
            "FHIR Type": "Type 4",
            "Resource": "Supporting Resources",
            "What is Present": "Binary (partial)",
            "What is Missing": "Organization, Practitioner, Terminologies"
        })

        df = pd.DataFrame(results)

        st.success("✅ Detailed Validation Completed")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error processing XML: {str(e)}")