import rundeck_graph as rg
root = rg.get_jobs_export_xml_root()
graph = rg.graph_dot(et_root=root)
rg.graph_render(graph)
