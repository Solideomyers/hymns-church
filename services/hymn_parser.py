import re

def _process_hymn_content(lines, hymn_number):
    if not lines:
        return []

    has_explicit_stanza_nums = False
    if hymn_number != 176:
        for line in lines:
            if re.match(r'^\s*\d+\s*$', line.strip()):
                has_explicit_stanza_nums = True
                break

    content = []
    current_stanza_lines = []
    current_type = 'estrofa'
    current_stanza_num = 1

    def save_current_stanza():
        nonlocal current_stanza_num
        if not current_stanza_lines:
            return
        
        block = {"tipo": current_type}
        if current_type == 'estrofa':
            block["estrofa_num"] = current_stanza_num
            block["texto"] = current_stanza_lines
            current_stanza_num += 1
        else:
            block["texto"] = current_stanza_lines
        
        content.append(block)

    for line in lines:
        stripped_line = line.strip()
        
        if not stripped_line:
            if not has_explicit_stanza_nums and current_stanza_lines:
                save_current_stanza()
                current_stanza_lines = []
                current_type = 'estrofa'
            continue

        stanza_match = None
        if hymn_number == 176:
            stanza_match = re.match(r'^(\d+)\.\s*(.*)', stripped_line)
        elif has_explicit_stanza_nums:
            stanza_match = re.match(r'^(\d+)\s*$', stripped_line)

        if stanza_match:
            if current_stanza_lines:
                save_current_stanza()
            
            current_stanza_lines = []
            current_type = 'estrofa'
            current_stanza_num = int(stanza_match.group(1))
            
            if hymn_number == 176 and stanza_match.group(2):
                current_stanza_lines.append(stanza_match.group(2).strip())

        elif stripped_line.upper().startswith('CORO'):
            if current_stanza_lines:
                save_current_stanza()
            current_stanza_lines = []
            current_type = 'coro'
        else:
            current_stanza_lines.append(stripped_line)

    if current_stanza_lines:
        save_current_stanza()

    return content

def parse_hymns_from_text(all_text: str):
    print("Parsing extracted text to find hymns...")
    all_lines = all_text.split('\n')
    hymns = []
    current_hymn_info = None
    current_hymn_lines = []
    
    hymn_title_regex = re.compile(r'^\s*(\d+)\.\s+([A-ZÁÉÍÓÚÑ\s-]{5,})', re.IGNORECASE)

    for line in all_lines:
        match = hymn_title_regex.search(line)
        
        if match:
            if current_hymn_info and current_hymn_info['numero'] == 176:
                current_hymn_lines.append(line.lower())
                continue

            if current_hymn_info:
                current_hymn_info['contenido'] = _process_hymn_content(current_hymn_lines, current_hymn_info['numero'])
                hymns.append(current_hymn_info)

            hymn_number = int(match.group(1))
            hymn_title = match.group(2).strip().lower()
            current_hymn_info = {'numero': hymn_number, 'titulo': hymn_title}
            current_hymn_lines = []
        
        elif current_hymn_info:
            current_hymn_lines.append(line.lower())

    if current_hymn_info:
        current_hymn_info['contenido'] = _process_hymn_content(current_hymn_lines, current_hymn_info['numero'])
        hymns.append(current_hymn_info)
    
    print(f"Parsing finished. Found {len(hymns)} hymns.")
    return hymns
