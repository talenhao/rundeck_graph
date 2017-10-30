import rundeck_graph as rg
root = rg.get_jobs_export_xml_root()
graph3 = rg.graph_dot(et_root=root, comment='rundeck graph', name='rd', filename='rundeck.gv', format='svg', engine='dot', directory='/var/lib/rundeck/exp/webapp/images/')
rg.graph_render(graph3)
