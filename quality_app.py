import tempfile
import streamlit as st

from quality_assessment import quality_gate

st.set_page_config(
    page_title="Fingerprint Quality Assessment",
    page_icon="🖐",
    layout="wide"
)

# Sidebar

st.sidebar.title("⚙ Quality Thresholds")

blur_threshold = st.sidebar.slider(
    "Blur Threshold",
    min_value=1.0,
    max_value=100.0,
    value=10.0
)

dark_threshold = st.sidebar.slider(
    "Dark Brightness",
    min_value=0,
    max_value=120,
    value=50
)

bright_threshold = st.sidebar.slider(
    "Bright Brightness",
    min_value=150,
    max_value=255,
    value=200
)

glare_threshold = st.sidebar.slider(
    "Glare Pixel Threshold",
    min_value=200,
    max_value=255,
    value=240
)

roi_threshold = st.sidebar.slider(
    "Minimum ROI Fraction",
    min_value=0.05,
    max_value=0.50,
    value=0.15,
    step=0.01
)

ridge_threshold = st.sidebar.slider(
    "Ridge Threshold",
    min_value=10.0,
    max_value=50000.0,
    value=100.0
)

st.title("🖐 Fingerprint Quality Assessment")

st.write("Upload a contactless fingerprint image to evaluate its quality.")

uploaded_file = st.file_uploader("Upload fingerprint Image", type = ["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(
        uploaded_file,
        caption="Uploaded Fingerprint",
        width=250
    )

    #save the image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(uploaded_file.read())
        image_path = temp_file.name

    result = quality_gate(
    image_path,
    blur_threshold=blur_threshold,
    dark_threshold=dark_threshold,
    bright_threshold=bright_threshold,
    glare_threshold=glare_threshold,
    roi_threshold=roi_threshold,
    ridge_threshold=ridge_threshold
    )

    st.subheader("Quality Assessment Results")
    st.subheader("Overall Result")

    if result["passed"]:
        st.success("✅ IMAGE PASSED QUALITY CHECK")
    else:
        st.error("❌ IMAGE FAILED QUALITY CHECK")

    st.metric(
    "Composite Score",
    f"{result['composite_score']:.2f}/100"
    )
    st.progress(result["composite_score"] / 100)

    st.subheader("Quality Metrics")

    metric_col1, metric_col2 = st.columns(2)

    with metric_col1:

        if result["blur"]["is_blurry"]:
            st.error("❌ Blur")
        else:
            st.success("✅ Blur")

        if (
            result["brightness"]["is_too_dark"]
            or result["brightness"]["is_too_bright"]
        ):
            st.error("❌ Brightness")
        else:
            st.success("✅ Brightness")

        if result["glare"]["has_glare"]:
            st.error("❌ Glare")
        else:
            st.success("✅ Glare")

    with metric_col2:

        if result["roi"]["roi_complete"]:
            st.success("✅ ROI")
        else:
            st.error("❌ ROI")

        if result["ridge"]["ridges_clear"]:
            st.success("✅ Ridge")
        else:
            st.error("❌ Ridge")

    st.subheader("Guidance")

    st.info(result["guidance"])

    st.markdown("---")

    st.subheader("Raw Metric Values")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Blur Score", result["blur"]["blur_score"])
        st.metric("Brightness", result["brightness"]["brightness"])

    with c2:
        st.metric("Glare Fraction", result["glare"]["glare_fraction"])
        st.metric("ROI Fraction", result["roi"]["roi_fraction"])

    with c3:
        st.metric("Ridge Score", result["ridge"]["ridge_score"])

