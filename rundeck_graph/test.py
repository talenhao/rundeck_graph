import rundeck_graph as rg
root = rg.get_jobs_export_xml_root()
graph = rg.graph_dot(et_root=root, comment='rundeck graph', name='rd', filename='rundeck.gv', format='gif', engine='dot')
rg.graph_render(graph)
