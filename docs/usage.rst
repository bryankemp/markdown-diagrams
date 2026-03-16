Usage
=====

Prerequisites
-------------

Rendering requires the `Mermaid CLI <https://github.com/mermaid-js/mermaid-cli>`_:

.. code-block:: bash

   npm install -g @mermaid-js/mermaid-cli

Installation
------------

.. code-block:: bash

   pip install markdown-diagrams

Or install from source:

.. code-block:: bash

   git clone https://github.com/bryankemp/markdown-diagrams.git
   cd markdown-diagrams
   pip install -e .

CLI Commands
------------

Extract and Render
^^^^^^^^^^^^^^^^^^

Extract all diagrams from a Markdown file and render them as images:

.. code-block:: bash

   markdown-diagrams extract document.md

Specify an output directory:

.. code-block:: bash

   markdown-diagrams extract document.md -o ./output

Filter by diagram type:

.. code-block:: bash

   markdown-diagrams extract document.md -t mermaid -t flowchart

Choose output format (``png``, ``svg``, or ``pdf``):

.. code-block:: bash

   markdown-diagrams extract document.md -f svg

Set custom dimensions and theme:

.. code-block:: bash

   markdown-diagrams extract document.md -w 1000 -H 800 -T dark

Validate
^^^^^^^^

Check all diagrams in a file for syntax errors:

.. code-block:: bash

   markdown-diagrams validate document.md

Auto-fix common issues (whitespace, unquoted parentheses in labels):

.. code-block:: bash

   markdown-diagrams validate document.md --fix

Preview what would be fixed without writing changes:

.. code-block:: bash

   markdown-diagrams validate document.md --dry-run

Filename Strategy
-----------------

When rendering diagrams, ``markdown-diagrams`` derives output filenames from the
document structure.  The tool looks for a **bold-text title** (``**...**``)
immediately above each code fence and uses it as the filename.  If no bold title
is found, the nearest ``#``-heading is used instead.

For example, given this Markdown:

.. code-block:: markdown

   ### Diagrams

   **Flowchart – License Injection Process**

   ```mermaid
   flowchart TD
       A[Start] --> B[End]
   ```

The output file will be named ``flowchart_license_injection_process.png`` rather
than the generic ``diagrams.png``.

When multiple diagrams resolve to the same name, a numeric suffix is appended
(e.g. ``flowchart_1.png``, ``flowchart_2.png``).

Python API
----------

Extracting Diagrams
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pathlib import Path
   from markdown_diagrams import extract_diagrams

   diagrams = extract_diagrams(Path("document.md"))

   for diagram_type, items in diagrams.items():
       for item in items:
           print(f"[{diagram_type}] {item['heading']}: {len(item['content'])} chars")

Rendering Diagrams
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from markdown_diagrams import render_mermaid_diagram

   output_path = render_mermaid_diagram(
       mermaid_content="graph TD\n    A-->B",
       output_dir="./output",
       format_type="png",
       width=800,
       height=600,
       theme="default",
       name="my_diagram",
   )
   print(f"Rendered to: {output_path}")

Validating Diagrams
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from pathlib import Path
   from markdown_diagrams import validate_and_fix_diagrams

   results = validate_and_fix_diagrams(Path("document.md"))
   for r in results:
       status = "OK" if r.valid else "FAIL"
       print(f"  [{status}] Diagram {r.index}: {r.heading}")
       for err in r.errors:
           print(f"    {err}")
