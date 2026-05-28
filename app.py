"""
The BRJS Historical Research Database
HTML + CSS + JavaScript + Python Flask + SQLite

How to run:
1. Save this file as app.py
2. Open Terminal in the same folder
3. Install Flask: pip install flask
4. Run: python app.py
5. Open your browser at: http://127.0.0.1:5000
"""

from flask import Flask, render_template_string, request, redirect, url_for, jsonify, Response
import sqlite3
import csv
import io
from datetime import datetime

app = Flask(__name__)
DATABASE = "historical_sources.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            creator TEXT,
            source_date TEXT,
            location TEXT,
            source_type TEXT,
            repository TEXT,
            url TEXT,
            tags TEXT,
            citation TEXT,
            notes TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>The BRJS Historical Research Database</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: Georgia, 'Times New Roman', serif;
            background: #f4efe6;
            color: #2b2118;
            line-height: 1.6;
        }

        header {
            background: linear-gradient(rgba(30, 20, 12, 0.85), rgba(30, 20, 12, 0.85)),
                        url('https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=1600&q=80');
            background-size: cover;
            background-position: center;
            color: white;
            text-align: center;
            padding: 4rem 8%;
        }

        header h1 {
            font-size: 2.8rem;
            margin-bottom: 0.6rem;
            letter-spacing: 1px;
        }

        header p {
            max-width: 850px;
            margin: auto;
            color: #f0ddb9;
            font-size: 1.1rem;
        }

        nav {
            background: #3b2a1d;
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            flex-wrap: wrap;
            padding: 1rem 8%;
        }

        nav a {
            color: #fff3d9;
            text-decoration: none;
            font-weight: bold;
        }

        nav a:hover {
            color: #d8a84e;
        }

        main {
            width: 92%;
            max-width: 1250px;
            margin: 2rem auto;
        }

        section {
            background: #fffaf1;
            border: 1px solid #e4d3b5;
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 18px rgba(50, 35, 20, 0.12);
        }

        h2 {
            color: #4a2f1b;
            border-bottom: 2px solid #c89b3c;
            padding-bottom: 0.4rem;
            margin-bottom: 1rem;
        }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 1rem;
        }

        .card {
            background: #f8eddc;
            border-left: 5px solid #8a5a32;
            border-radius: 12px;
            padding: 1rem;
        }

        .card h3 {
            color: #4a2f1b;
            margin-bottom: 0.3rem;
        }

        .number {
            font-size: 2rem;
            font-weight: bold;
            color: #6b4226;
        }

        form {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }

        label {
            display: block;
            font-weight: bold;
            margin-bottom: 0.35rem;
            color: #3b2a1d;
        }

        input,
        select,
        textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #cbb89a;
            border-radius: 8px;
            background: white;
            color: #2b2118;
            font-size: 1rem;
            font-family: Georgia, 'Times New Roman', serif;
        }

        textarea {
            min-height: 115px;
            resize: vertical;
        }

        .full-width {
            grid-column: 1 / -1;
        }

        button,
        .button-link {
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 0.95rem;
        }

        .primary-btn {
            background: #6b4226;
            color: white;
        }

        .primary-btn:hover {
            background: #8a5a32;
        }

        .secondary-btn {
            background: #d8bd84;
            color: #2b2118;
        }

        .danger-btn {
            background: #8f2d24;
            color: white;
        }

        .toolbar {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 1rem;
            margin-bottom: 1rem;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            margin-top: 1rem;
        }

        th,
        td {
            padding: 0.85rem;
            text-align: left;
            vertical-align: top;
            border-bottom: 1px solid #e5d6bd;
        }

        th {
            background: #4a2f1b;
            color: #fff8ea;
        }

        tr:hover {
            background: #fbf3e6;
        }

        .tag {
            display: inline-block;
            background: #e8d2a6;
            color: #3b2a1d;
            padding: 0.2rem 0.5rem;
            border-radius: 999px;
            font-size: 0.85rem;
            margin: 0.1rem;
        }

        .actions {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
        }

        .small-btn {
            padding: 0.45rem 0.65rem;
            font-size: 0.85rem;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            padding: 2rem;
            overflow: auto;
        }

        .modal-content {
            background: #fffaf1;
            max-width: 760px;
            margin: 2rem auto;
            padding: 2rem;
            border-radius: 16px;
            border: 1px solid #e4d3b5;
        }

        .close {
            float: right;
            font-size: 1.8rem;
            cursor: pointer;
            color: #8f2d24;
        }

        footer {
            text-align: center;
            padding: 2rem;
            background: #3b2a1d;
            color: #fff3d9;
            margin-top: 3rem;
        }

        @media (max-width: 850px) {
            header h1 {
                font-size: 2rem;
            }

            .toolbar {
                grid-template-columns: 1fr;
            }

            table,
            thead,
            tbody,
            th,
            td,
            tr {
                display: block;
            }

            thead {
                display: none;
            }

            tr {
                margin-bottom: 1rem;
                border: 1px solid #e5d6bd;
                border-radius: 10px;
                overflow: hidden;
            }

            td::before {
                content: attr(data-label);
                display: block;
                font-weight: bold;
                color: #6b4226;
                margin-bottom: 0.2rem;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>The BRJS Historical Research Database</h1>
        <p>A Python-powered digital archive for organizing historical sources, metadata, citations, research notes, and archival records.</p>
    </header>

    <nav>
        <a href="#dashboard">Dashboard</a>
        <a href="#add-source">Add Source</a>
        <a href="#database">Database</a>
        <a href="#guide">Metadata Guide</a>
    </nav>

    <main>
        <section id="dashboard">
            <h2>Research Dashboard</h2>
            <div class="dashboard">
                <div class="card">
                    <h3>Total Sources</h3>
                    <p class="number">{{ total_sources }}</p>
                </div>
                <div class="card">
                    <h3>Primary Sources</h3>
                    <p class="number">{{ primary_sources }}</p>
                </div>
                <div class="card">
                    <h3>Secondary Sources</h3>
                    <p class="number">{{ secondary_sources }}</p>
                </div>
                <div class="card">
                    <h3>Database Type</h3>
                    <p><strong>SQLite</strong></p>
                    <p>Saved through Python, not only the browser.</p>
                </div>
            </div>
        </section>

        <section id="add-source">
            <h2>{{ 'Edit Historical Source' if edit_source else 'Add a Historical Source' }}</h2>
            <form method="POST" action="{{ url_for('update_source', source_id=edit_source['id']) if edit_source else url_for('add_source') }}">
                <div>
                    <label for="title">Title / Document Name</label>
                    <input type="text" id="title" name="title" required value="{{ edit_source['title'] if edit_source else '' }}" placeholder="Example: Letter from Thomas Brother, 1924" />
                </div>

                <div>
                    <label for="creator">Creator / Author</label>
                    <input type="text" id="creator" name="creator" value="{{ edit_source['creator'] if edit_source else '' }}" placeholder="Example: Unknown photographer, Adam Hochschild" />
                </div>

                <div>
                    <label for="source_date">Date / Year</label>
                    <input type="text" id="source_date" name="source_date" value="{{ edit_source['source_date'] if edit_source else '' }}" placeholder="Example: 1910, March 5, 1924, c. 1890" />
                </div>

                <div>
                    <label for="location">Historical Location</label>
                    <input type="text" id="location" name="location" value="{{ edit_source['location'] if edit_source else '' }}" placeholder="Example: Escondido, Mexico City, Congo Free State" />
                </div>

                <div>
                    <label for="source_type">Source Type</label>
                    <select id="source_type" name="source_type">
                        {% for type in source_types %}
                            <option value="{{ type }}" {% if edit_source and edit_source['source_type'] == type %}selected{% endif %}>{{ type }}</option>
                        {% endfor %}
                    </select>
                </div>

                <div>
                    <label for="repository">Archive / Repository</label>
                    <input type="text" id="repository" name="repository" value="{{ edit_source['repository'] if edit_source else '' }}" placeholder="Example: Escondido History Center, Library of Congress" />
                </div>

                <div>
                    <label for="url">URL or File Location</label>
                    <input type="text" id="url" name="url" value="{{ edit_source['url'] if edit_source else '' }}" placeholder="https://... or local folder path" />
                </div>

                <div>
                    <label for="tags">Tags / Keywords</label>
                    <input type="text" id="tags" name="tags" value="{{ edit_source['tags'] if edit_source else '' }}" placeholder="Mexico, Revolution, Catholicism, Escondido" />
                </div>

                <div class="full-width">
                    <label for="citation">Citation</label>
                    <textarea id="citation" name="citation" placeholder="Chicago-style citation or archival citation">{{ edit_source['citation'] if edit_source else '' }}</textarea>
                </div>

                <div class="full-width">
                    <label for="notes">Research Notes / Historical Significance</label>
                    <textarea id="notes" name="notes" placeholder="Explain what this source reveals, how it supports your argument, and what questions it raises.">{{ edit_source['notes'] if edit_source else '' }}</textarea>
                </div>

                <div class="full-width">
                    <button type="submit" class="primary-btn">{{ 'Update Source' if edit_source else 'Save Source' }}</button>
                    {% if edit_source %}
                        <a class="button-link secondary-btn" href="{{ url_for('index') }}">Cancel Edit</a>
                    {% else %}
                        <button type="reset" class="secondary-btn">Clear Form</button>
                    {% endif %}
                </div>
            </form>
        </section>

        <section id="database">
            <h2>Historical Source Database</h2>
            <div class="toolbar">
                <input type="text" id="searchInput" placeholder="Search title, creator, location, tags, notes..." oninput="filterTable()" />
                <select id="typeFilter" onchange="filterTable()">
                    <option value="All">All Source Types</option>
                    {% for type in source_types %}
                        <option value="{{ type }}">{{ type }}</option>
                    {% endfor %}
                </select>
                <a class="button-link secondary-btn" href="{{ url_for('export_csv') }}">Export CSV</a>
            </div>

            <table id="sourceTable">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Creator</th>
                        <th>Date</th>
                        <th>Type</th>
                        <th>Location</th>
                        <th>Tags</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% if sources %}
                        {% for source in sources %}
                            <tr data-type="{{ source['source_type'] }}">
                                <td data-label="Title">
                                    <strong>{{ source['title'] }}</strong><br />
                                    {% if source['url'] %}
                                        <a href="{{ source['url'] }}" target="_blank">Open Source</a>
                                    {% endif %}
                                </td>
                                <td data-label="Creator">{{ source['creator'] }}</td>
                                <td data-label="Date">{{ source['source_date'] }}</td>
                                <td data-label="Type">{{ source['source_type'] }}</td>
                                <td data-label="Location">{{ source['location'] }}</td>
                                <td data-label="Tags">
                                    {% if source['tags'] %}
                                        {% for tag in source['tags'].split(',') %}
                                            <span class="tag">{{ tag.strip() }}</span>
                                        {% endfor %}
                                    {% endif %}
                                </td>
                                <td data-label="Actions">
                                    <div class="actions">
                                        <button class="small-btn secondary-btn" onclick='openModal({{ source|tojson }})'>View</button>
                                        <a class="button-link small-btn primary-btn" href="{{ url_for('edit_source', source_id=source['id']) }}#add-source">Edit</a>
                                        <form method="POST" action="{{ url_for('delete_source', source_id=source['id']) }}" onsubmit="return confirm('Delete this source?');">
                                            <button class="small-btn danger-btn" type="submit">Delete</button>
                                        </form>
                                    </div>
                                </td>
                            </tr>
                        {% endfor %}
                    {% else %}
                        <tr>
                            <td colspan="7">No sources added yet. Use the form above to begin your database.</td>
                        </tr>
                    {% endif %}
                </tbody>
            </table>
        </section>

        <section id="guide">
            <h2>Metadata Guide</h2>
            <div class="dashboard">
                <div class="card">
                    <h3>Title</h3>
                    <p>Use the official title if available. If not, create a short descriptive title.</p>
                </div>
                <div class="card">
                    <h3>Creator</h3>
                    <p>Name the author, photographer, organization, speaker, or creator. Use “Unknown” when necessary.</p>
                </div>
                <div class="card">
                    <h3>Date</h3>
                    <p>Use exact dates when possible. Use “c.” for approximate dates, such as c. 1910.</p>
                </div>
                <div class="card">
                    <h3>Repository</h3>
                    <p>Record where the source came from: archive, museum, library, database, website, or personal collection.</p>
                </div>
            </div>
        </section>
    </main>

    <div id="sourceModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <h2 id="modalTitle"></h2>
            <p><strong>Creator:</strong> <span id="modalCreator"></span></p>
            <p><strong>Date:</strong> <span id="modalDate"></span></p>
            <p><strong>Location:</strong> <span id="modalLocation"></span></p>
            <p><strong>Type:</strong> <span id="modalType"></span></p>
            <p><strong>Repository:</strong> <span id="modalRepository"></span></p>
            <p><strong>URL/File:</strong> <span id="modalURL"></span></p>
            <br />
            <h3>Citation</h3>
            <p id="modalCitation"></p>
            <br />
            <h3>Research Notes</h3>
            <p id="modalNotes"></p>
        </div>
    </div>

    <footer>
        <p>&copy; 2026 The BRJS Historical Research. Built with HTML, CSS, JavaScript, Python Flask, and SQLite.</p>
    </footer>

    <script>
        function filterTable() {
            const searchInput = document.getElementById('searchInput').value.toLowerCase();
            const typeFilter = document.getElementById('typeFilter').value;
            const rows = document.querySelectorAll('#sourceTable tbody tr');

            rows.forEach(row => {
                const rowText = row.innerText.toLowerCase();
                const rowType = row.getAttribute('data-type');
                const matchesSearch = rowText.includes(searchInput);
                const matchesType = typeFilter === 'All' || rowType === typeFilter;

                row.style.display = matchesSearch && matchesType ? '' : 'none';
            });
        }

        function openModal(source) {
            document.getElementById('modalTitle').innerText = source.title || 'Untitled Source';
            document.getElementById('modalCreator').innerText = source.creator || 'Unknown';
            document.getElementById('modalDate').innerText = source.source_date || 'No date listed';
            document.getElementById('modalLocation').innerText = source.location || 'No location listed';
            document.getElementById('modalType').innerText = source.source_type || 'No type listed';
            document.getElementById('modalRepository').innerText = source.repository || 'No repository listed';
            document.getElementById('modalURL').innerText = source.url || 'No URL or file path listed';
            document.getElementById('modalCitation').innerText = source.citation || 'No citation added';
            document.getElementById('modalNotes').innerText = source.notes || 'No notes added';
            document.getElementById('sourceModal').style.display = 'block';
        }

        function closeModal() {
            document.getElementById('sourceModal').style.display = 'none';
        }

        window.onclick = function(event) {
            const modal = document.getElementById('sourceModal');
            if (event.target === modal) {
                closeModal();
            }
        };
    </script>
</body>
</html>
"""


SOURCE_TYPES = [
    "Primary Source",
    "Secondary Source",
    "Photograph",
    "Newspaper",
    "Book",
    "Academic Article",
    "Map",
    "Oral History",
    "Website",
    "Archive Record",
]


@app.route("/")
def index():
    conn = get_db_connection()
    sources = [
    dict(row) for row in conn.execute(
        "SELECT * FROM sources ORDER BY id DESC"
    ).fetchall()]
    total_sources = conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    primary_sources = conn.execute("SELECT COUNT(*) FROM sources WHERE source_type = 'Primary Source'").fetchone()[0]
    secondary_sources = conn.execute("SELECT COUNT(*) FROM sources WHERE source_type = 'Secondary Source'").fetchone()[0]
    conn.close()

    return render_template_string(
        HTML_TEMPLATE,
        sources=sources,
        source_types=SOURCE_TYPES,
        total_sources=total_sources,
        primary_sources=primary_sources,
        secondary_sources=secondary_sources,
        edit_source=None,
    )


@app.route("/add", methods=["POST"])
def add_source():
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO sources
        (title, creator, source_date, location, source_type, repository, url, tags, citation, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            request.form.get("title"),
            request.form.get("creator"),
            request.form.get("source_date"),
            request.form.get("location"),
            request.form.get("source_type"),
            request.form.get("repository"),
            request.form.get("url"),
            request.form.get("tags"),
            request.form.get("citation"),
            request.form.get("notes"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index") + "#database")


@app.route("/edit/<int:source_id>")
def edit_source(source_id):
    conn = get_db_connection()
    sources = [
    dict(row) for row in conn.execute(
        "SELECT * FROM sources ORDER BY id DESC"
    ).fetchall()]
    edit_source = conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
    total_sources = conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    primary_sources = conn.execute("SELECT COUNT(*) FROM sources WHERE source_type = 'Primary Source'").fetchone()[0]
    secondary_sources = conn.execute("SELECT COUNT(*) FROM sources WHERE source_type = 'Secondary Source'").fetchone()[0]
    conn.close()

    return render_template_string(
        HTML_TEMPLATE,
        sources=sources,
        source_types=SOURCE_TYPES,
        total_sources=total_sources,
        primary_sources=primary_sources,
        secondary_sources=secondary_sources,
        edit_source=edit_source,
    )


@app.route("/update/<int:source_id>", methods=["POST"])
def update_source(source_id):
    conn = get_db_connection()
    conn.execute(
        """
        UPDATE sources
        SET title = ?, creator = ?, source_date = ?, location = ?, source_type = ?,
            repository = ?, url = ?, tags = ?, citation = ?, notes = ?
        WHERE id = ?
        """,
        (
            request.form.get("title"),
            request.form.get("creator"),
            request.form.get("source_date"),
            request.form.get("location"),
            request.form.get("source_type"),
            request.form.get("repository"),
            request.form.get("url"),
            request.form.get("tags"),
            request.form.get("citation"),
            request.form.get("notes"),
            source_id,
        ),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index") + "#database")


@app.route("/delete/<int:source_id>", methods=["POST"])
def delete_source(source_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM sources WHERE id = ?", (source_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index") + "#database")


@app.route("/export")
def export_csv():
    conn = get_db_connection()
    sources = [
    dict(row) for row in conn.execute(
        "SELECT * FROM sources ORDER BY id DESC"
    ).fetchall()]
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID",
        "Title",
        "Creator",
        "Date",
        "Location",
        "Source Type",
        "Repository",
        "URL/File",
        "Tags",
        "Citation",
        "Notes",
        "Created At",
    ])

    for source in sources:
        writer.writerow([
            source["id"],
            source["title"],
            source["creator"],
            source["source_date"],
            source["location"],
            source["source_type"],
            source["repository"],
            source["url"],
            source["tags"],
            source["citation"],
            source["notes"],
            source["created_at"],
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=historical_research_database.csv"},
    )


@app.route("/api/sources")
def api_sources():
    conn = get_db_connection()
    sources = [
    dict(row) for row in conn.execute(
        "SELECT * FROM sources ORDER BY id DESC"
    ).fetchall()]
    conn.close()
    return jsonify([dict(source) for source in sources])


if __name__ == "__main__":
    create_database()
    app.run(host=0.0.0.0, port=5000, debug=True)
