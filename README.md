# FYP
## 1 Introduction
本仓库作为作者本科毕业论文——**《新创企业的空间分布特征及其驱动因子探究》** 内容与数据共享平台, fyp即 Final-Year Paper 的缩写。如果您具有 **工商局企业注册数据库**，那么您可以使用本仓库`\code`文件夹中代码完成数据获取内容并用于科学研究，包括且不限于**1979-2018年**最小至**县级单元**的**区分企业法人单位与所有制类型**的新创企业成立数(某些年份某些省份因为经纬度数据**缺失较多**仅能通过其他方法获取并精确到地级市层面，这一部分数据会在代码运行中**声明**)。如果您没有该数据库, 但是出于**科学研究目的**想要对此题目有所了解，可以在文档最后的链接中下载本文所用数据，文责自负。

## 2 Usage

### 2.1 准备工作
#### *2.1.1 Installation*

`git clone https://github.com/yottahub/fyp.git`

#### *2.1.2 预装库*

`os`  `time`  `json`  `pandas`  `numpy`  `tqdm`  `xlsxwriter`
####  2.2 功能介绍
**Version: Python 3.8**

#### *2.2.1 Class*

```python
class project(object):
	def __init__(self, directory, period, region, outfolder):
	'''项目初始化
    	param: directory <数据库地址>>, str
    	   eg:'D:\\database' or 'd:\database'
    	param: period <研究时间>, list
    	   eg. [2008, 2018] NOTES:表示2008-2018年这一区间
    	param: region <研究区域>, list
    	   eg. ['北京', '天津', '河北', '山西', '内蒙古']
    	param: outfolder <项目地址>, str
    	   eg. 'C:\\document\\MyProject', NOTES:'MyProject'将被视为项目名
    	param: classification <分类文件地址>, str
    	   eg.'C:\\document\\MyProject\\classification.txt'
	'''
    
   	def selfcheck(self):
    	'''核实项目状态
    	----------------------------------------------------------------
    	param	: null
    	desc	: 检查项目进度，项目初始化时会自动执行一次;selfcheck与cp.json捆
    		  绑，请不要擅自移动与修改cp.json文件;
   	NOTES	: 暂不支持热插拔
    	----------------------------------------------------------------
    	OUT	: 打印'项目当前状态:'
    		eg: {'项目名称': 'MyTrial',
 		     '保存位置': 'E:\\FYP',
 		     '创建时间': '2021年06月13日 14:13:23',
 		     '数据库地址': 'E:\\database',
 		     '研究时间': '2018年',
 		     '研究区域': ['辽宁', '吉林', '黑龙江'],
 		     '项目进度': 'E:\\database\\csv_data\\辽宁\\2018.csv',
		     '修改时间': '2021年06月13日 15:15:09',
 		     '分类结果': 'E:\\FYP\\MyTrial\\classification.txt',
 		     '输出类型': {'法人单位': 'y', '所有制类型': 'f'}}
    	'''
	def run(self, loss_rate=1):
    	'''运行项目
    	----------------------------------------------------------------
    	param	: loss_rate, optional, float	default: loss_rate=1
    	desc	: 如果需要区分法人单位和所有制类型，先进行分类；默认先提取经纬度，
    		  获得每个新企业的点坐标，若某省数据缺失率超过给定loss_rate，根据
    		  'city'栏获取企业所在城市(数据缺失少，但潜在错误多)
    	----------------------------------------------------------------
    	OUT	: a. 如果尚未进行分类, generate '\classification.txt', 文本
    		  文档包含enterprise_type, entity, ownership, sum 三列, 分
    		  别为数据库中企业类型, 是否为法人单位(y: 企业法人, n: 非法人单位
    		  , u: 不确定), 所有制类型(p: 私营企业, f: 外资企业,s: 国有企业
    		  , c: 集体企业), 若发现分类异常可以手动更正.
    		  ------------------------------------------------------
    		  b. generate '{year}\coordinates_{year}.txt', 存储符合要求
    		  的点坐标如"'输出类型': {'法人单位': 'y', '所有制类型': 'f'}}"
    		  , 则点坐标为法人单位外资企业.
    		  ------------------------------------------------------
    		  c. generate '{year}\report_{year}.xslx', 工作表"输出结果"
    		  包含提取省份, 缺失率, 提取有效值, 额外工作表"{province}"为缺失
    		  率较高省份,根据'city'列提取的有效新创企业数以及该省该方法缺失率.
    	'''
	def classifer(self):
    	'''识别是否为法人单位与所有制类型
    	----------------------------------------------------------------
    	OUT	: generate '\classification.txt'
    	'''
    	@property
    	def directory(self):

    	@directory.setter
    	def directory(self, directory):

    	@property
    	def period(self):

    	@period.setter
    	def period(self, period):

    	@property
    	def region(self):

    	@region.setter
    	def region(self, region):

    	@property
    	def outfolder(self):

    	@outfolder.setter
    	def outfolder(self, outfolder):

    	@property
    	def classification(self):

    	@classification.setter
    	def classification(self, classification):
    	'''
    	param: classification, str	eg. 'E:\\FYP\\MyTrial\\classification.txt'
    	'''
```

#### *2.2.2 Modules*

```python
def set_directory():
    '''设置数据库地址'''
    
def set_period():
    '''设置研究时间'''

def set_region():
    '''设置研究区域'''
    
def set_outfolder():
    '''设置输出位置'''
    
def timenow():
    '''获取当前时间
    ----------------------------------------------------------------
    OUT		: 2021年06月13日 15:15:09
    '''
def main():
    '''使用示例'''
    prj = project(set_directory, set_period, set_region, set_outfolder)
    prj.run()
```

#### *2.2.3 使用*

`python fyp.py` or `import fyp as *`

## 3 License
> MIT License

项目中代码并不是从网上随意复制粘贴的产品，而是根据数据库真实情况原创编写并不断调试得到的。因此如需引用或修改本仓库内容, 请署名并以相同方式共享, 谢谢！

## 4 Others

### 4.1 更新计划

- [ ] 利用多线程和多进程，提高代码的运行效率
- [ ] 支持运行中断后将项目恢复至上次运行位置

### 4.2 论文数据

文章与数据下载
