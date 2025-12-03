import os
import mimetypes
import stat
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Scope | Pentest Finder</title>
    <style>
        :root {
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --text-main: #e2e8f0;
            --text-muted: #94a3b8;
            --accent: #3b82f6;
            --accent-hover: #2563eb;
            --match-highlight: #f59e0b;
            --border: #334155;
            --font-mono: 'Consolas', 'Monaco', 'Courier New', monospace;
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }

        /* --- Header & Toolbar --- */
        header {
            background-color: var(--bg-card);
            border-bottom: 1px solid var(--border);
            padding: 1rem 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            z-index: 10;
        }

        .title-row {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            gap: 10px;
        }
        
        .logo-container {
            width: 50px;
            height: 50px;
            margin-right: 2px;
            margin-top: -6px;
        }
        
        .logo-text {
            font-weight: 800;
            font-size: 1.75rem;
            letter-spacing: -0.05em;
            display: flex;
            align-items: center;
            gap: 0;
            margin-top: -4px;
            margin-left: -6px;
        }
        
        .logo-text span:first-child {
            color: #003399;
        }
        
        .logo-text span:last-child {
            color: #00C8C8;
        }
        
        .logo { font-weight: 800; font-size: 1.25rem; letter-spacing: -0.05em; color: var(--accent); margin-right: 10px; }
        .logo span { color: #2CB4C5; }

        .search-grid {
            display: grid;
            grid-template-columns: 2fr 1.5fr 1fr auto;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
        }

        .advanced-filters {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: 10px;
            padding-top: 10px;
            border-top: 1px solid var(--border);
        }

        input[type="text"], input[type="number"], select {
            background-color: var(--bg-dark);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s;
            width: 100%;
            box-sizing: border-box;
        }

        input:focus { border-color: var(--accent); }

        .btn-primary {
            background-color: var(--accent);
            color: white;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            white-space: nowrap;
        }
        .btn-primary:hover { background-color: var(--accent-hover); }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

        .toggle-group {
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 0.85rem;
            color: var(--text-muted);
        }

        .toggle-label {
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            user-select: none;
        }

        input[type="checkbox"] { accent-color: var(--accent); width: auto; }
        
        label.input-label {
            display: block;
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-bottom: 4px;
            font-weight: 600;
        }


        main {
            flex: 1;
            overflow-y: auto;
            padding: 1.5rem;
        }

        .stats-bar {
            margin-bottom: 1rem;
            font-size: 0.85rem;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
        }

        .file-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 1rem;
            overflow: hidden;
        }

        .file-header {
            padding: 0.75rem 1rem;
            background-color: rgba(0,0,0,0.2);
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }
        
        .file-path { font-family: var(--font-mono); font-size: 0.9rem; color: var(--accent); word-break: break-all; }
        .file-meta { font-size: 0.75rem; color: var(--text-muted); margin-right: 10px; }
        .match-count { background: var(--bg-dark); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }

        .code-block {
            padding: 0;
            margin: 0;
            background-color: #0d1117;
            overflow-x: auto;
            display: none; /* Hidden by default */
        }
        .file-card.open .code-block { display: block; }

        .code-line {
            display: flex;
            font-family: var(--font-mono);
            font-size: 0.85rem;
            line-height: 1.5;
        }
        
        .code-line:hover { background-color: #161b22; }

        .line-num {
            width: 50px;
            text-align: right;
            padding-right: 10px;
            color: #4b5563;
            background-color: #161b22;
            user-select: none;
            flex-shrink: 0;
        }

        .line-content {
            padding-left: 10px;
            white-space: pre;
            color: #c9d1d9;
        }

        .highlight {
            background-color: rgba(245, 158, 11, 0.2);
            color: var(--match-highlight);
            font-weight: bold;
            border-bottom: 1px solid var(--match-highlight);
        }

        .loader {
            border: 3px solid var(--bg-card);
            border-top: 3px solid var(--accent);
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            display: none;
        }
        
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        

        .badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-right: 8px;
        }
        .badge-dir { background: #4f46e5; color: white; }
        .badge-file { background: #0ea5e9; color: white; }
        .badge-exe { background: #dc2626; color: white; }
        .badge-bin { background: #9333ea; color: white; }

    </style>
</head>
<body>

<header>
    <div class="title-row">
        <div class="logo-container">
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full h-full">
                <path d="M 30 65 A 28 28 0 1 1 78 45" stroke="#00C8C8" stroke-width="3" stroke-linecap="round" fill="none" />
                <path d="M 28 72 A 36 36 0 1 1 86 45" stroke="#003399" stroke-width="4" stroke-linecap="round" fill="none" />
                <path d="M 86 45 L 82 38 L 91 39 Z" fill="#003399" />
                <g>
                    <rect x="26" y="66" width="10" height="26" rx="5" transform="rotate(45 31 79)" fill="#003399" />
                    <rect x="29" y="68" width="4" height="20" rx="2" transform="rotate(45 31 79)" fill="#00C8C8" />
                    <circle cx="50" cy="45" r="18" stroke="#003399" stroke-width="5" fill="white" />
                </g>
                <g transform="translate(50, 45)">
                    <path d="M 8 -8 A 10 10 0 1 0 0 10 L 0 0 L 8 0" stroke="#00C8C8" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none" />
                </g>
            </svg>
        </div>
        <div class="logo-text"><span>G</span><span>Trace</span></div>
        <div class="loader" id="loader"></div>
    </div>

    <div class="search-grid">
        <input type="text" id="searchTerm" placeholder="Search string or Regex..." autofocus>
        <input type="text" id="rootPath" placeholder="Root Path (e.g. /var/www or C:\\Users)">
        
        <!-- Search Target -->
        <select id="searchTarget">
            <option value="all">Find in: All</option>
            <option value="content">Find in: File Content</option>
            <option value="filename">Find in: File Names</option>
            <option value="dirname">Find in: Directory Names</option>
        </select>
        
        <button class="btn-primary" onclick="startSearch()">SCAN</button>
    </div>

    <div class="advanced-filters">
        <!-- File Type Filter -->
        <div>
            <label class="input-label">File Type</label>
            <select id="fileType">
                <option value="any">All</option>
                <option value="text" selected>Text file (Default)</option>
                <option value="binary">Binary file</option>
                <option value="executable">Executable file</option>
            </select>
        </div>

        <!-- Extension Filter -->
        <div>
            <label class="input-label">Extensions (Optional)</label>
            <input type="text" id="extensions" placeholder="e.g. py, js, log">
        </div>

        <!-- Toggles -->
        <div class="toggle-group" style="grid-column: span 2; align-self: end; padding-bottom: 5px;">
            <label class="toggle-label">
                <input type="checkbox" id="useRegex"> Regex
            </label>
            <label class="toggle-label">
                <input type="checkbox" id="exactMatch"> Exact Match
            </label>
            <label class="toggle-label">
                <input type="checkbox" id="caseSensitive"> Case Sensitive
            </label>
            <div style="margin-left: auto; display: flex; align-items: center; gap: 5px;">
                Context: 
                <input type="number" id="contextLines" value="2" min="0" max="10" style="width: 40px; padding: 2px 5px;">
            </div>
        </div>
    </div>
</header>

<main id="resultsArea">
    <div style="text-align: center; margin-top: 3rem; color: var(--text-muted);">
        <h3>Ready to Scan</h3>
        <p>Configure your filters above and click SCAN.</p>
    </div>
</main>

<script>
    // Set default path to current directory on load
    document.getElementById('rootPath').value = ".";

    async function startSearch() {
        const term = document.getElementById('searchTerm').value;
        const path = document.getElementById('rootPath').value;
        const target = document.getElementById('searchTarget').value;
        const fileType = document.getElementById('fileType').value;
        const ext = document.getElementById('extensions').value;
        const useRegex = document.getElementById('useRegex').checked;
        const exactMatch = document.getElementById('exactMatch').checked;
        const caseSensitive = document.getElementById('caseSensitive').checked;
        const context = parseInt(document.getElementById('contextLines').value);

        if (!term) { alert("Please enter a search term"); return; }

        const resultsArea = document.getElementById('resultsArea');
        const loader = document.getElementById('loader');
        
        resultsArea.innerHTML = '';
        loader.style.display = 'block';
        document.querySelector('.btn-primary').disabled = true;

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    term, path, target, fileType, ext, useRegex, exactMatch, caseSensitive, context
                })
            });

            const data = await response.json();
            
            if (data.error) {
                resultsArea.innerHTML = `<div style="color: red; text-align: center;">Error: ${data.error}</div>`;
            } else {
                renderResults(data.results, data.stats);
            }
        } catch (e) {
            console.error(e);
            resultsArea.innerHTML = `<div style="color: red; text-align: center;">Connection Error</div>`;
        } finally {
            loader.style.display = 'none';
            document.querySelector('.btn-primary').disabled = false;
        }
    }

    function renderResults(items, stats) {
        const area = document.getElementById('resultsArea');
        
        if (items.length === 0) {
            area.innerHTML = `<div style="text-align: center; margin-top: 2rem;">No matches found.</div>`;
            return;
        }

        const statsHtml = `
            <div class="stats-bar">
                <span>Found ${items.length} matches</span>
                <span>Scanned: ${stats.scanned_count} items</span>
            </div>
        `;
        area.innerHTML = statsHtml;

        items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'file-card open'; 

            // Determine badge
            let badgeHtml = '';
            if (item.type === 'dir') badgeHtml = '<span class="badge badge-dir">DIR</span>';
            else if (item.is_exe) badgeHtml = '<span class="badge badge-exe">EXE</span>';
            else if (item.is_binary) badgeHtml = '<span class="badge badge-bin">BIN</span>';
            else badgeHtml = '<span class="badge badge-file">FILE</span>';

            // Match Logic
            let contentHtml = '';
            
            if (item.type === 'content_match') {
                // Render code blocks for content matches
                let codeHtml = '';
                item.matches.forEach(match => {
                     // Sort context lines
                     match.context.sort((a,b) => a.num - b.num);
                     
                     match.context.forEach(ctxLine => {
                        const isMatchLine = ctxLine.num === match.line;
                        const highlightClass = isMatchLine ? 'highlight' : '';
                        const safeContent = ctxLine.content
                            .replace(/&/g, "&amp;")
                            .replace(/</g, "&lt;")
                            .replace(/>/g, "&gt;");

                        codeHtml += `
                            <div class="code-line">
                                <div class="line-num">${ctxLine.num}</div>
                                <div class="line-content ${highlightClass}">${safeContent}</div>
                            </div>
                        `;
                    });
                    codeHtml += `<div style="height: 1px; background: #333; margin: 5px 0;"></div>`;
                });
                contentHtml = `<div class="code-block">${codeHtml}</div>`;
            } else {
                // Render simple view for Filename/Dirname matches
                const matchTypeLabel = item.type === 'dir' ? 'Directory Name' : 'Filename';
                contentHtml = `
                    <div style="padding: 10px; font-size: 0.85rem; color: #94a3b8;">
                        Match found in <strong>${matchTypeLabel}</strong>.
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="file-header" onclick="this.parentElement.classList.toggle('open')">
                    <div style="display:flex; align-items:center;">
                        ${badgeHtml}
                        <span class="file-path">${item.path}</span>
                    </div>
                    ${item.match_count ? `<span class="match-count">${item.match_count} matches</span>` : ''}
                </div>
                ${contentHtml}
            `;
            area.appendChild(card);
        });
    }
</script>

</body>
</html>
"""

# ==========================================
#  BACKEND LOGIC
# ==========================================

def get_context(lines, line_idx, context_range):
    """Extracts N lines before and after the match."""
    start = max(0, line_idx - context_range)
    end = min(len(lines), line_idx + context_range + 1)
    
    snippet = []
    for i in range(start, end):
        snippet.append({
            'num': i + 1,
            'content': lines[i].rstrip('\n')
        })
    return snippet

def is_executable(filepath):
    """Check if a file is executable."""
    if os.name == 'nt':
        return filepath.lower().endswith(('.exe', '.bat', '.cmd', '.ps1', '.vbs'))
    return os.access(filepath, os.X_OK)

def is_binary_mime(filepath):
    """Check if file is binary based on mime or basic heuristics."""
    mime, _ = mimetypes.guess_type(filepath)
    if mime and not mime.startswith('text') and mime not in ['application/json', 'application/javascript', 'application/xml']:
        return True
    return False

@app.route('/')
def home():
    return render_template_string(TEMPLATE)

@app.route('/api/search', methods=['POST'])
def search_files():
    data = request.json
    search_term = data.get('term', '')
    root_path = data.get('path', '.')
    search_target = data.get('target', 'content') # content, filename, dirname, all
    file_type_filter = data.get('fileType', 'text') # any, text, binary, executable
    extensions = data.get('ext', '')
    exact_match = data.get('exactMatch', False)
    case_sensitive = data.get('caseSensitive', False)
    context_lines = data.get('context', 2)

    if not search_term:
        return jsonify({'error': 'No search term provided'})

    # Prepare Extensions
    valid_exts = set()
    if extensions:
        valid_exts = {e.strip() if e.strip().startswith('.') else f'.{e.strip()}' for e in extensions.split(',')}

    # Prepare search term for matching
    search_lower = search_term.lower() if not case_sensitive else None
    
    def matches(text):
        if case_sensitive:
            if exact_match:
                return text == search_term
            return search_term in text
        else:
            text_lower = text.lower()
            if exact_match:
                return text_lower == search_lower
            return search_lower in text_lower

    results = []
    scanned_count = 0
    root_path = os.path.expanduser(root_path)

    if not os.path.exists(root_path):
        return jsonify({'error': 'Directory not found'})

    # Determine scope
    check_dirname = search_target in ['dirname', 'all']
    check_filename = search_target in ['filename', 'all']
    check_content = search_target in ['content', 'all']

    for root, dirs, files in os.walk(root_path):
        # Filter hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        # ---------------------------
        # DIRECTORY NAMES
        # ---------------------------
        if check_dirname:
            for d in dirs:
                if not check_dirname and search_target != 'all': 
                    # Optimization: scanned_count increments only if we actually check them
                    pass
                else:
                    # When target='all', we might count dirs as scanned items
                    pass
                
                if matches(d):
                    full_path = os.path.join(root, d)
                    results.append({
                        'path': full_path,
                        'type': 'dir',
                        'is_exe': False,
                        'is_binary': False,
                        'matches': []
                    })
        
        # If we are ONLY searching directories, skip files
        if search_target == 'dirname':
            scanned_count += len(dirs)
            continue

        # ---------------------------
        # FILE PROCESSING
        # ---------------------------
        for file in files:
            # Extension Filter
            if valid_exts:
                _, ext = os.path.splitext(file)
                if ext not in valid_exts:
                    continue

            file_path = os.path.join(root, file)
            scanned_count += 1

            is_exe = is_executable(file_path)
            is_bin = is_binary_mime(file_path)

            # --- TYPE FILTERS ---
            if file_type_filter == 'text':
                if is_bin: continue
            elif file_type_filter == 'binary':
                if not is_bin: continue
            elif file_type_filter == 'executable':
                if not is_exe: continue

            # --- CHECK FILENAME ---
            if check_filename:
                if matches(file):
                    results.append({
                        'path': file_path,
                        'type': 'file_name_match',
                        'is_exe': is_exe,
                        'is_binary': is_bin,
                        'matches': []
                    })
                    # If we matched the filename, and we are NOT in 'all' mode, we might stop here
                    # But if 'all', we should ALSO check content
                    if search_target == 'filename':
                        continue

            # --- CHECK CONTENT ---
            if check_content:
                # Content Skip Logic:
                if file_type_filter == 'text' and is_bin:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()

                    file_matches = []
                    for i, line in enumerate(lines):
                        if matches(line.rstrip('\n')):
                            file_matches.append({
                                'line': i + 1,
                                'context': get_context(lines, i, context_lines)
                            })

                    if file_matches:
                        results.append({
                            'path': file_path,
                            'type': 'content_match',
                            'match_count': len(file_matches),
                            'matches': file_matches,
                            'is_exe': is_exe,
                            'is_binary': is_bin
                        })

                except Exception:
                    continue
            
            if scanned_count > 10000: # Safety break
                break
        
        if scanned_count > 10000:
            break

    return jsonify({
        'results': results,
        'stats': {'scanned_count': scanned_count}
    })

if __name__ == '__main__':
    print("----------------------------------------------------------------")
    print(" SYSTEM SCOPE TOOL STARTED")
    print(" Open your browser to: http://127.0.0.1:5000")
    print(" Press CTRL+C to stop")
    print("----------------------------------------------------------------")
    app.run(debug=False, port=5000)
