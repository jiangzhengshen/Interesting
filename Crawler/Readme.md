# Python实现的简单爬虫

注意：

代码为crawler_enhanced.py。

使用命令举例：
```shell
python crawler_enhanced.py -a http://www.baidu.com -d 1 -o ./output/
```

crawler_deprecated.py为原始实现，现已弃用。

## 实现思路
所谓“爬虫”，主要功能在于从一个基本url列表出发，递归的挖掘网页中的url，并从url对应的网页中提取需要的信息。

网络上很多称为爬虫的程序，没有挖掘url这一步，只有从网页中提取信息的部分。这种程序其实不能称为爬虫，而应该称为网页分析程序。

此脚本实现了递归挖掘网页url的功能，而把具体的网页内容提取留给调用者实现。

crawler_enhanced.py的流程为：
1. 输入初始url列表，并构建url队列
2. 对url队列中的每个url，根据url获得对应的html
3. 使用**用户自定义**的方法保存html中需要的信息
4. 从html中提取出所有包含的url
5. 有些url会自动跳转，因此要根据原始url获得跳转后的url
6. 使用**用户自定义**的过滤方法对提取出的url进行筛选
7. 将筛选后的url加入队列

## crawler_enhanced.py代码说明
最主要的类为Crawler类，实现了递归挖掘url的方法。

具体的，使用了广度优先搜索，使用队列来实现（深度优先则使用栈来实现）。

使用时，需要先继承Crawler类，并按需重载save\_content方法和filter\_url方法。

代码中给出了两个示例：
- URLCrawler子类：保留所有网址的根目录
- ImageCrawler子类：保留所有网页中的图片（img标签中的src属性对应的内容）
