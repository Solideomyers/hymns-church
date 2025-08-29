import sys
import os

# Add the parent directory of the modules to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.generator-hymnary.hymn_document_generator import HymnDocumentGenerator

def generate_hymnary():
    hymns_json_path = "modules/extraction-hymns/output-hymns/hymns.json"
    styles_config_path = "modules/generator-hymnary/styles_config.json"
    output_filepath = "modules/generator-hymnary/output/himnario_final.docx"

    generator = HymnDocumentGenerator(hymns_json_path, styles_config_path)
    generator.generate_document(output_filepath)

    return {"message": "Hymnary generated successfully", "path": output_filepath}
