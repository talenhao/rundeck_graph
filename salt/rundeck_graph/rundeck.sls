python_require_common_package:
  pkg.installed:
    - pkgs:
      - gcc
      - xz
      - zlib-devel
      - openssl-devel
      - graphviz-devel

rundeck_graph:
  file.recurse:
    - name: /usr/local/_rundeck_graph
    - source: salt://rundeck_graph/files/rundeck_graph

python_requirements:
  cmd.run:
    - name: /usr/local/_python3.6.1/bin/pip3 install --upgrade -r /usr/local/_rundeck_graph/requirements.txt --no-index --find-links=file:///usr/local/_rundeck_graph/pip_requirements/
    - cwd: /usr/local/_rundeck_graph
    - watch:
      - file: rundeck_graph

graph:
  cmd.run:
    - name: /usr/local/_python3.6.1/bin/python3.6 /usr/local/_python3.6.1/lib/python3.6/site-packages/rundeck_graph/test.py
    - cwd: /usr/local/_rundeck_graph
    - require:
      - cmd: python_requirements
