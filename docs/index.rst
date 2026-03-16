markdown-diagrams
=================

Extract and render `Mermaid <https://mermaid.js.org/>`_ diagrams from Markdown
files to PNG, SVG, and PDF.

.. code-block:: bash

   pip install markdown-diagrams

.. code-block:: bash

   # Extract and render all diagrams
   markdown-diagrams extract document.md -o output/

   # Validate diagram syntax
   markdown-diagrams validate document.md

Features
--------

* Extract Mermaid diagrams from any Markdown file
* Render to PNG, SVG, and PDF formats
* Automatically name output files from bold-text titles or headings
* Support for 19 diagram types (flowchart, sequence, class, state, ER, gantt,
  pie, mindmap, gitGraph, journey, quadrant, requirement, C4, and more)
* Validate and auto-fix diagram syntax
* Python API for programmatic use

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   examples
   api
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
