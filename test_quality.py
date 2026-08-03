from pathlib import Path

import pandas as pd

from quality_assessment import quality_gate

# Test Images Folder

TEST_FOLDER = Path("data_fingerprint/")

results = []

# Process Every Image

for image_path in sorted(TEST_FOLDER.rglob("*")):

    if image_path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
        continue

    result = quality_gate(str(image_path))

    results.append({
        "Image": image_path.name,

        "Blur": "PASS" if not result["blur"]["is_blurry"] else "FAIL",

        "Brightness":
            "PASS"
            if (
                not result["brightness"]["is_too_dark"]
                and not result["brightness"]["is_too_bright"]
            )
            else "FAIL",

        "Glare":
            "PASS"
            if not result["glare"]["has_glare"]
            else "FAIL",

        "ROI":
            "PASS"
            if result["roi"]["roi_complete"]
            else "FAIL",

        "Ridge":
            "PASS"
            if result["ridge"]["ridges_clear"]
            else "FAIL",

        "Composite Score": result["composite_score"],

        "Overall":
            "PASS"
            if result["passed"]
            else "FAIL",

        "Guidance": result["guidance"]
    })

# -------------------------------------------------
# Display Table
# -------------------------------------------------

df = pd.DataFrame(results)

print("\n")
print("=" * 120)
print("FINGERPRINT QUALITY ASSESSMENT RESULTS")
print("=" * 120)

print(df.to_string(index=False))

print("=" * 120)

# Statistics

total = len(df)
passed = (df["Overall"] == "PASS").sum()
failed = total - passed

print(f"\nTotal Images : {total}")
print(f"Passed       : {passed}")
print(f"Failed       : {failed}")
print(f"Pass Rate    : {(passed/total)*100:.2f}%")


# Save CSV


output_file = "quality_results.csv"

df.to_csv(output_file, index=False)

print(f"\nResults saved to {output_file}")