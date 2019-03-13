#!/usr/bin/env python3.6
# -*- coding:UTF-8 -*-

"""


"""
from graphviz import Digraph

import datetime
import requests
import sys
import time
import xml.etree.ElementTree as ET
import configparser

__author__ = "Talen Hao(天飞)<talenhao@gmail.com>"
__status__ = "product"
__create_date__ = "2017.08.01"

# for log >>
import logging
import os
import log4python

SCRIPT_NAME = os.path.basename(__file__)
pLogger = log4python.GetLogger(SCRIPT_NAME, logging.DEBUG).get_l()
config_file = os.path.dirname(os.path.abspath(__file__)) + '/config.ini'
pLogger.debug("\n" * 50)
pLogger.debug("config file is {}".format(config_file))
# log end <<

try:
    get_encode = sys.getdefaultencoding()
except:
    import sys
    get_encode = sys.getdefaultencoding()
finally:
    if get_encode == 'ascii':
        sys.setdefaultencoding('utf8')
        pLogger.info("getdefaultencoding is {!r}, convert to utf8.".format(get_encode))
    else:
        pLogger.info("getdefaultencoding is {!r}".format(get_encode))


def exception(e):
    pLogger.exception(e)
    sys.exit()


class RgvConfigParser:
    def __init__(self, config_file=config_file):
        self.config_file = config_file
        pLogger.debug("Use config file: {} ".format(self.config_file))

    def config_parser(self):
        # with open(self.config_file,mode='r') as self.fp:
        #     self.python_config_parser.read_file(self.fp)
        try:
            python_config_parser = configparser.ConfigParser()
            python_config_parser.read(self.config_file)
        except configparser.ParsingError:
            exception("正则匹配配置文件语法有误，检查配置文件！")
        else:
            return python_config_parser


pyconfig = RgvConfigParser().config_parser()
rundeck_server_ip = pyconfig.get('RUNDECK', 'rundeck_server_ip')
rundeck_server_port = pyconfig.get('RUNDECK', 'rundeck_server_port')
rundeck_server_protocol = pyconfig.get('RUNDECK', 'rundeck_server_protocol')
rundeck_project = pyconfig.get('RUNDECK', 'rundeck_project')
rundeck_token = pyconfig.get('RUNDECK', 'rundeck_token')
pLogger.debug("{!r}, {!r}, {!r}, {!r}, {!r}".format(
    rundeck_server_ip,
    rundeck_server_port,
    rundeck_server_protocol,
    rundeck_project,
    rundeck_token))

font_size = '9'

today = datetime.date.fromtimestamp(time.time())
pLogger.info("today is : {!r}".format(today))


def get_jobs_export_xml_root():
    """
    curl -X GET  -H x-rundeck-auth-token:Orbv4nQJ6vXJboj9LKTguQg7j5taRJAx\
      http://192.168.1.228:4440/api/14/project/in-jobs/jobs/export
    :return:
    """
    jobs_url_api = '{}://{}:{}/api/14/project/{}/jobs/export'.format(
        rundeck_server_protocol,
        rundeck_server_ip,
        rundeck_server_port,
        rundeck_project)
    jobs_url_api_headers = {'x-rundeck-auth-token': rundeck_token}
    jobs_url_api_params = {}
    try:
        jobs_export = requests.get(jobs_url_api, params=jobs_url_api_params, headers=jobs_url_api_headers)
        pLogger.info("Receive config.")
        # pLogger.info("Export jobs config :\n %r", jobs_export.text)
    except OSError:
        pLogger.info("Network connect error!")
        exit()
    else:
        jobs_xml_export = ET.fromstring(jobs_export.text)
        root = jobs_xml_export
        pLogger.debug("root tag: %r", root.tag)
        return root


def graph_dot(et_root, **kwargs):
    """
    **kwargs in : name=None, comment=None, filename=None, directory=None, format=None,\
     engine=None, encoding=None, graph_attr=None, node_attr=None, edge_attr=None, body=None, strict=False
    """
    root = et_root
    rd_pic = Digraph(**kwargs)
    create_time = "Image create time : {} ".format(datetime.datetime.now().strftime('%Y-%m-%d,%H.%M'))
    rd_pic.attr('graph',
                rankdir='LR',
                label=create_time,
                labelloc='t',
                bgcolor='azure',
                # compound='true',
                constraint='true',  # If false, the edge is not used in ranking the nodes.
                rank='source',  # 等级
                # concentrate='false',  # 共用线
                # clusterrank='local',
                overlap='true',
                # center='false',
                decorate='true',
                # imagepos='ml',
                ratio='auto',
                )
    rd_pic.attr('node',
                fontsize=str(int(font_size) + 2),
                fillcolor='yellowgreen',  # 填充颜色
                style='filled',  # 填充
                # shape='folder',  # node图标形状
                # orientation='rotate',
                fontname='DejaVu Sans Mono',  # 使用字体
                remincross='true',
                fixedsize='false',  # 固定大小
                # distortion='-100'
                # height='.4',
                # dim='10',  # Set the number of dimensions used for the layout. The maximum value allowed is 10.
                # dimen='10',  # Set the number of dimensions used for rendering. The maximum value allowed is 10.
                # splines='false',
                )
    # rd_pic.node_attr.update(fillcolor='red', style='filled', labeltooltip="注意!此任务已经被禁用")
    rd_pic.edge_attr.update(concentrate='true',
                            # decorate='true',  # 线标题加下划线,标注连接线.
                            penwidth='1.5',  # 线的粗细.
                            # minlen='5',  # 线的最小长度
                            fontsize=str(int(font_size) - 1),
                            fontname='DejaVu Sans Mono',  # 使用字体
                            labelfloat='true',
                            # labeldistance='false',
                            # labelangle='-25.0'
                            )
    for job in root:
        # 1.获取任务名
        job_name = job.find("name").text
        # 2.禁用状态
        executionEnabled = job.find('executionEnabled').text
        pLogger.debug("job enabled status: %r", executionEnabled)
        if executionEnabled and executionEnabled == 'false':
            pLogger.debug("job {!r} is disabled.".format(job_name))
            continue

        # 7.调度状态
        schedule = job.find('schedule')
        pLogger.debug("Job schedule :%r, type: %r", schedule, type(schedule))

        job_id = job.find('id').text
        pLogger.debug("job id is {}".format(job_id))
        node_url = '{}://{}:{}/project/in-jobs/job/show/{}'.format(
            rundeck_server_protocol,
            rundeck_server_ip,
            rundeck_server_port,
            job_id)
        rd_pic.node(name=job_name,
                    URL=node_url)
        # rd_pic.node(job_name)
        # 3.分组信息
        job_group = job.find('group').text  # .replace('/', '_')
        pLogger.debug("job group is : %r", job_group)
        pLogger.debug("job name is %r", job_name)

        cluster_name = '_'.join(["cluster", job_group])
        pLogger.debug("cluster_name is %r", cluster_name)
        with rd_pic.subgraph(name=cluster_name) as group:
            group.attr(style='filled',  # cluster外圈样式, dashed:虚线;filled:实线填充;rounded:环绕
                       bgcolor='cornsilk',  # 背景色
                       )
            group.attr(label=job_group,
                       fontsize=str(int(font_size) + 4),
                       fontname='DejaVu Sans Mono',  # 使用字体
                       labeljust='l')

            if schedule is None:
                group.node(job_name, fillcolor='orange', style='filled',
                           # gradientangle='90',
                           )
                node_stats = 'end'
            else:
                group.node(job_name, fillcolor='green', style='filled',
                           # gradientangle='90'
                           )
                node_stats = 'start'
            pLogger.debug('node_stats _____________________________ %r ', node_stats)
            pLogger.debug("group_subgraph is %r", group)
        # 4.子任务指向
        jobrefs = job.findall(".//jobref")
        pLogger.debug(jobrefs)
        if jobrefs:
            for jobref in jobrefs:
                pLogger.debug("jobref is : %r", jobref)
                pLogger.debug(jobref.attrib)
                pLogger.debug(jobref.attrib.get('name'))
                # 5.直接指向任务名
                jobref_name = jobref.attrib.get('name')
                if jobref_name == 'runjob':
                    # 6.间接指向任务名
                    runjob_jobref_name = jobref.find(".//arg").get('line').split('/')[-1]
                    pLogger.debug("runjob link to %r", runjob_jobref_name)
                    rd_pic.edge(job_name, runjob_jobref_name, "call",
                                headlabel=job_name,
                                color='red',
                                )
                elif jobref_name == '基本数据拉取任务':
                    # runjob_jobref_name = jobref.find(".//arg").get('line')
                    runjob_jobref_name = jobref_name
                    pLogger.debug("BaseData is %r", runjob_jobref_name)
                    rd_pic.edge(job_name, runjob_jobref_name, "transport data",
                                headlabel=job_name,
                                color='green',
                                )
                else:
                    rd_pic.edge(job_name, jobref_name,
                                label="substep",
                                labelfloat='true',
                                headlabel=job_name,
                                # style='dashed',
                                color='blue'
                                )
        # 5.jobrefs_rd_run
        job_ref_rd_runs = job.findall(".//exec")
        pLogger.debug("job_ref_rd_runs is %r", job_ref_rd_runs)
        if job_ref_rd_runs:
            for job_ref_rd_run in job_ref_rd_runs:
                if job_ref_rd_run.text.startswith('rd run'):
                    job_ref_rd_run_jobname = job_ref_rd_run.text.split('/')[-1]
                    pLogger.debug("%r has %r", job_ref_rd_run.text, job_ref_rd_run_jobname)
                    rd_pic.edge(job_name, job_ref_rd_run_jobname,
                                headlabel=job_name, color='red', fontsize=font_size,
                                concentrate='true',
                                splines='false'
                                )
                else:
                    pLogger.debug("%r has not rd run", job_ref_rd_run.text)
    rd_pic.node(name=create_time, shape='plaintext', pos="1, 1!", fontsize='10')
    return rd_pic


def graph_render(graph):
    pLogger.info("Collect over, graphing image...")
    graph.render()


if __name__ == "__main__":
    root = get_jobs_export_xml_root()
    graph = graph_dot(et_root=root,
                      comment='rundeck graph',
                      name='rd',
                      filename='rundeck.gv',
                      format='svg',
                      engine='dot')
    graph_render(graph)
