# 绘制rundeck任务流程图
=====
使用rundeck任务周期性调用salt执行
- 20170802
-    配置管理, 根据时间生成图片, 整合Django, 命令行参数.
-    1.添加分组功能
-    2.调整起点任务与子步骤的node样式,edge样式
- 20170803
-    添加schedule等判断
-    调整配色,红色是独立禁用的任务
- 20170918
-    添加图片生成日期
- 20171030
-    图片node新增超链接,支持点击图片节点跳转到相应的任务界面.
-    节点连线显示上一层父任务名称,鼠标放在线上可以显示任务流向.

----
![image](https://github.com/talenhao/rundeck_graph/blob/master/rundeck_graph/images/img1.png?raw=true)
![image](https://github.com/talenhao/rundeck_graph/blob/master/rundeck_graph/images/img2.png?raw=true)
![image](https://github.com/talenhao/rundeck_graph/blob/master/rundeck_graph/images/img3.png?raw=true)
----
