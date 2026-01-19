import os
import xml.etree.ElementTree as ET
import json

def cvat_xml_to_labelme(xml_path, output_dir=None):
    """
    Convert CVAT XML to LabelMe JSON format
    
    Args:
        xml_path: Path to the CVAT XML file
        output_dir: Directory to save JSON files (optional, defaults to same directory as XML)
    
    Returns:
        tuple: (success: bool, message: str, files_created: list)
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Set default output directory if not provided
        if output_dir is None:
            output_dir = os.path.dirname(xml_path)
        
        os.makedirs(output_dir, exist_ok=True)

        # Counter to assign object_X names
        object_counter = 0
        files_created = []

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
                            print(f"Warning: Invalid point pair '{pair}' in image {image_name}")
                            continue

                if point_pairs:  # Only add shape if we have valid points
                    shape = {
                        "label": poly.attrib.get("label", f"object_{object_counter:04d}"),
                        "points": point_pairs,
                        "group_id": None,
                        "shape_type": "polygon",
                        "flags": {}
                    }

                    labelme_json["shapes"].append(shape)
                    object_counter += 1

            base_name = os.path.splitext(image_name)[0]
            output_file = os.path.join(output_dir, base_name + ".json")

            with open(output_file, "w") as f:
                json.dump(labelme_json, f, indent=2)

            files_created.append(output_file)
            print(f"Saved: {output_file}")

        return True, f"Successfully converted {len(files_created)} files", files_created
    
    except ET.ParseError as e:
        error_msg = f"Error parsing XML file: {str(e)}"
        print(error_msg)
        return False, error_msg, []
    except Exception as e:
        error_msg = f"Error processing file: {str(e)}"
        print(error_msg)
        return False, error_msg, []

# Run the script
if __name__ == "__main__":
    # Set your paths here
    xml_path = "C:/Users/sanje/Pictures/yolo2json/input/annotations.xml"
    output_dir = "C:/Users/sanje/Pictures/yolo2json/output"

    print("Starting CVAT XML to LabelMe JSON conversion...")
    success, message, files_created = cvat_xml_to_labelme(xml_path, output_dir)
    
    if success:
        print(f"\n✅ Conversion completed successfully!")
        print(f"📊 {message}")
        print(f"📁 Output directory: {output_dir}")
    else:
        print(f"\n❌ Conversion failed!")
        print(f"Error: {message}")
