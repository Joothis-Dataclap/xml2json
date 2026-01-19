import streamlit as st
import xml.etree.ElementTree as ET
import json
import zipfile
from io import BytesIO

st.set_page_config(page_title="XML to JSON Converter", page_icon="🔄")

def clear_app_state():
    """Clear cache and session state"""
    st.cache_data.clear()
    for k in ["processed_files", "last_file"]:
        if k in st.session_state:
            del st.session_state[k]

@st.cache_data
def process_xml(xml_content: bytes):
    """Convert XML to JSON format"""
    try:
        root = ET.fromstring(xml_content)
        json_files = {}
        object_counter = 0
        
        for image_tag in root.findall("image"):
            image_name = image_tag.attrib.get("name", "unknown.jpg")
            image_width = int(image_tag.attrib.get("width", 0))
            image_height = int(image_tag.attrib.get("height", 0))

            labelme_json = {
                "version": "5.2.1",
                "flags": {},
                "shapes": [],
                "imagePath": image_name,
                "imageData": None,
                "imageHeight": image_height,
                "imageWidth": image_width,
            }

            for poly in image_tag.findall("polygon"):
                points_str = poly.attrib.get("points", "")
                point_pairs = []
                
                for pair in points_str.strip().split(";"):
                    if pair:
                        try:
                            x_str, y_str = pair.split(",")
                            point_pairs.append([float(x_str), float(y_str)])
                        except ValueError:
                            continue

                if point_pairs:
                    shape = {
                        "label": poly.attrib.get("label", f"object_{object_counter:04d}"),
                        "points": point_pairs,
                        "group_id": None,
                        "shape_type": "polygon",
                        "flags": {}
                    }
                    labelme_json["shapes"].append(shape)
                    object_counter += 1

            base_name = image_name.split('.')[0]
            json_filename = base_name + ".json"
            json_files[json_filename] = json.dumps(labelme_json, indent=2)
        
        return json_files
        
    except:
        return None

def create_download_zip(json_files):
    """Create a ZIP file containing all JSON files"""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in json_files.items():
            zip_file.writestr(filename, content)
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def main():
    st.title("🔄 XML to JSON Converter")

    # Put uploader in a form so it clears after submit
    with st.form("upload_form", clear_on_submit=True):
        uploaded_file = st.file_uploader("Upload XML file", type=["xml"])
        submitted = st.form_submit_button("Convert")

    if submitted and uploaded_file is not None:
        current_file = f"{uploaded_file.name}_{uploaded_file.size}"
        if "last_file" in st.session_state and st.session_state.last_file != current_file:
            clear_app_state()
        st.session_state.last_file = current_file

        xml_content = uploaded_file.read()
        json_files = process_xml(xml_content)

        if json_files:
            st.session_state.processed_files = json_files
            st.success(f"✅ Converted {len(json_files)} files")
        else:
            st.error("❌ Failed to process XML file")

    # Only show download + success if processed_files exists
    if "processed_files" in st.session_state:
        zip_data = create_download_zip(st.session_state.processed_files)
        st.download_button(
            label="📥 Download JSON Files",
            data=zip_data,
            file_name="annotations.zip",
            mime="application/zip",
        )

    if st.button("Clear Cache"):
        clear_app_state()
        st.rerun()  
        
if __name__ == "__main__":
    main()
