#!/usr/bin/env python3.6
# -*- coding:UTF-8 -*-

"""
20170802    计划
    配置管理, 根据时间生成图片, 整合Django, 命令行参数.
    1.添加分组功能
    2.调整起点任务与子步骤的node样式,edge样式
20170803
    添加schedule等判断
    调整配色,红色是独立禁用的任务
20170918
    添加图片生成日期

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
__last_date__ = "2017.09.18"
__version__ = __last_date__

# for log >>
import logging
import os
from rundeck_graph.log4p import log4p

SCRIPT_NAME = os.path.basename(__file__)
pLogger = log4p.GetLogger(SCRIPT_NAME, logging.DEBUG).get_l()
config_file = os.path.dirname(os.path.abspath(__file__)) + '/config.ini'
pLogger.debug("\n"*50)
pLogger.debug("config file is {}".format(config_file))
# log end <<


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
pLogger.debug("{!r}, {!r}, {!r}, {!r}, {!r}".format(rundeck_server_ip, rundeck_server_port, rundeck_server_protocol, rundeck_project, rundeck_token))

font_size = '9'

today = datetime.date.fromtimestamp(time.time())
pLogger.info("today is : {!r}".format(today))


def get_jobs_export_xml_root():
    """
    curl -X GET  -H x-rundeck-auth-token:Orbv4nQJ6vXJboj9LKTguQg7j5taRJAx  http://192.168.1.228:4440/api/14/project/in-jobs/jobs/export
    :return:
    """
    jobs_url_api = '%s://%s:%s/api/14/project/%s/jobs/export' % (rundeck_server_protocol, rundeck_server_ip, rundeck_server_port, rundeck_project)
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
    **kwargs in : name=None, comment=None, filename=None, directory=None, format=None, engine=None, encoding=None, graph_attr=None, node_attr=None, edge_attr=None, body=None, strict=False
    """
    root = et_root
    rd_pic = Digraph(**kwargs)
    rd_pic.graph_attr['rankdir'] = 'LR'
    create_time = "Image create time : {} ".format(datetime.datetime.now().strftime('%Y-%m-%d,%H.%M'))
    rd_pic.graph_attr['label'] = create_time
    rd_pic.graph_attr['labelloc'] = 't'
    rd_pic.attr('node', shape='box', style='filled',
                # orientation='rotate',
                orientation='landscape',
                ratio='compress',
                fontsize=font_size,
                remincross='true', 
                concentrate='fase',
                compound='true',
                overlap='false',
                rank='source',
                constraint='false',
                clusterrank='none',
                center='false',
                imagepos='ml',
                height='.2')
    # rd_pic.node_attr.update(fillcolor='red', style='filled', labeltooltip="注意!此任务已经被禁用")
    rd_pic.edge_attr.update(splines='compound', concentrate='true')
    for job in root:
        # 1.获取任务名
        job_name = job.find("name").text

        # 2.禁用状态
        executionEnabled = job.find('executionEnabled').text
        pLogger.debug("job启用状态: %r", executionEnabled)
        if executionEnabled and executionEnabled == 'false':
            pLogger.info("job {!r} 已经被禁用".format(job_name))
            continue

        # 7.调度状态
        schedule = job.find('schedule')
        pLogger.debug("Job调度启用状态:%r, type: %r", schedule, type(schedule))

        # rd_pic.node(job_name)
        # 3.分组信息
        job_group = job.find('group').text  # .replace('/', '_')

        pLogger.debug("job group is : %r", job_group)
        pLogger.debug("job name is %r", job_name)
        cluster_name = '_'.join(["cluster", job_group])
        pLogger.debug("cluster_name is %r", cluster_name)
        with rd_pic.subgraph(name=cluster_name) as group:
            group.attr(style='filled', bgcolor='khaki')
            group.attr(label=job_group,
                       fontsize=font_size, labeljust='l')

            if schedule is None:
                group.node(job_name, fillcolor='orange:yellow', shape='box', style='filled',
                           # gradientangle='90'
                           )
                node_stats = 'end'
            else:
                group.node(job_name, fillcolor='green:yellow', shape='box', style='filled',
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
                    rd_pic.edge(job_name, runjob_jobref_name, "并行调用",
                                headlable=job_name, color='red', fontsize=font_size,
                                concentrate='true',
                                splines='compound'
                                )
                elif jobref_name == '基本数据拉取任务':
                    # runjob_jobref_name = jobref.find(".//arg").get('line')
                    runjob_jobref_name = jobref_name
                    pLogger.debug("基本数据拉取任务 is %r", runjob_jobref_name)
                    rd_pic.edge(job_name, runjob_jobref_name, "数据操作",
                                headlable=job_name, color='green', fontsize=font_size,
                                concentrate='true',
                                splines='compound'
                                )
                else:
                    rd_pic.edge(job_name, jobref_name,
                                label="串行子步骤",
                                labelfloat='true',
                                # headlabel="串行子步骤",
                                # taillabel="串行子步骤",
                                style='dashed',
                                color='blue',
                                fontsize=font_size,
                                concentrate='true',
                                splines='compound')
        # 5.jobrefs_rd_run
        job_ref_rd_runs = job.findall(".//exec")
        pLogger.debug("job_ref_rd_runs is %r", job_ref_rd_runs)
        if job_ref_rd_runs:
            for job_ref_rd_run in job_ref_rd_runs:
                if job_ref_rd_run.text.startswith('rd run'):
                    job_ref_rd_run_jobname = job_ref_rd_run.text.split('/')[-1]
                    pLogger.debug("%r has %r", job_ref_rd_run.text, job_ref_rd_run_jobname)
                    rd_pic.edge(job_name, job_ref_rd_run_jobname,
                                headlable=job_name, color='red', fontsize=font_size,
                                concentrate='true',
                                splines='compound'
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
                      format='gif',
                      engine='dot')
    graph_render(graph)
