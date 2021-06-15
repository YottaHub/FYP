'''
>>------------------------Yotta©----------------------------<<
拥有者: Yottas
仓库地址: https://github.com/yottahub/fyp.git
简介: 本脚本可用于操作工商局企业登记注册数据库
原创声明: 代码与所得数据仅供科学研究使用, 文责自负；如需引用或者修
改本代码，请署名或保留本段注释.
>>--------------------------Hub-----------------------------<<
'''


import os
import time
import json
import pandas as pd
import numpy as np
from tqdm import tqdm
from xlsxwriter import Workbook


def set_directory():
    '''设置数据库地址'''
    while True:
        directory = str(input("输入数据库地址(e.g. 'D:\...\Database'):"))
        try:
            with open(directory + '\\json_statistic.csv', 'r') as f:
                return directory
        except FileNotFoundError:
            print('似乎输入了错误的地址')


def set_period():
    '''设置研究时间'''
    while True:
        firstyear = int(input('起始年: '))
        lastyear = int(input('结束年: ')) + 1
        firstyear, lastyear = (
            lastyear, firstyear) if lastyear < firstyear else (firstyear,
                                                               lastyear)
        if (lastyear > 2020) | (firstyear < 1900):
            print('SORRY!数据库暂未收录这些年份')
            continue
        else:
            return [firstyear, lastyear]


def set_region():
    '''设置研究区域'''
    mainland = [
        '北京', '天津', '河北', '山西', '内蒙古', '上海', '江苏', '浙江', '安徽', '福建', '江西',
        '山东', '广东', '广西', '海南', '重庆', '四川', '贵州', '云南', '西藏', '辽宁', '吉林',
        '黑龙江', '陕西', '甘肃', '青海', '宁夏', '新疆', '河南', '湖北', '湖南'
    ]
    northeast = ['辽宁', '吉林', '黑龙江']
    east = ['上海', '江苏', '浙江', '安徽', '福建', '江西', '山东']
    north = ['北京', '天津', '河北', '山西', '内蒙古']
    central = ['河南', '湖北', '湖南']
    south = ['广东', '广西', '海南']
    southwest = ['重庆', '四川', '贵州', '云南', '西藏']
    northwest = ['陕西', '甘肃', '青海', '宁夏', '新疆']
    # SAZ = ['香港', '澳门', '台湾']
    print('Please choose the study region(s):')
    print(
        '1. 大陆  2. 华北  3. 华东  4. 华南\n5. 西南  6. 东北  7. 西北  8. 华中'  # + '\n9. 港澳台'
    )
    select = str(input('选择研究区域（可多选）:\n'))
    region = []
    if '2' in select:
        region += north
    if '3' in select:
        region += east
    if '4' in select:
        region += south
    if '5' in select:
        region += southwest
    if '6' in select:
        region += northeast
    if '7' in select:
        region += northwest
    if '8' in select:
        region += central
    if '1' in select:  # | region == mainland:
        region = mainland
    '''
    if '9' in select:
        region += SAZ
    '''
    return region


def set_outfolder():
    '''设置输出位置'''
    outpath = os.path.abspath(os.path.dirname(os.getcwd()))
    if 'n' == input('生成文件将保存在目录 {} (y/n?)'.format(outpath)):
        outpath = input('手动输入保存位置：')
    '''项目命名'''
    while True:
        prjname = input('请给本项目命名：')
        outfolder = outpath + '\\' + prjname
        if os.path.exists(outfolder):
            if 'y' == input('该项目已存在，是否为数据恢复(y/n?)'):
                return outfolder
        else:
            mkdir(outfolder)
            return outfolder


def timenow():
    '''获取时间'''
    year = time.strftime('%Y年', time.localtime(time.time()))
    date = time.strftime('%m月%d日', time.localtime(time.time()))
    date.replace('0', '')
    clock = time.strftime(' %H:%M:%S', time.localtime(time.time()))
    return year + date + clock


def mkdir(path):
    '''创建新目录'''
    if not os.path.exists(path):
        os.mkdir(path)


class project(object):
    '''项目标准化


    param: directory    数据库地址    type: str
    param: period    研究时间    type: list eg. [2008, 2018]
    param: region    研究区域    type: list eg. ['北京', '天津', '河北', '山西', '内蒙古']
    param: outfolder    项目地址    type: str eg. 'C:\\document\\MyProject'    MyProject将被视为项目名
    param: classification 分类文件地址 type: str eg.'C:\\document\\MyProject\\classification.txt'


    func: selfcheck
    param: null    
    desc: 
    检查项目进度，项目初始化时会自动执行一次;
    selfcheck与cp.json捆绑，请不要擅自移动与修改cp.json文件;
    NOTES: 暂不支持热插拔
    
    func: run    
    param: loss_rate    type: float    default: loss_rate = 1
    desc: 
    如果需要区分法人单位和所有制类型，先进行分类；
    默认先提取经纬度，获得每个新企业的点坐标，若某省缺失率超过给定loss_rate，根据'city'栏获取企业所在城市

    func: classifier
    param: null
    desc: 对所有研究时间与研究区域对应文件的企业类型进行分类

    func: new_cp
    param: null
    desc: checkpoint here!
    '''
    def __init__(self, directory, period, region, outfolder):
        print('项目初始化中...')
        self._database = directory
        self._period = period
        self._range = range(self._period[0], self._period[1])
        self._region = region
        self._outfolder = outfolder
        self._dirname = os.path.dirname(self._outfolder)
        self._name = self._outfolder.replace(self._dirname, '')
        self._name = self._name.replace('\\', '')
        self._csvfiles = self.gen_csvfiles()
        self.if_classify()
        self._classification = ''
        self._ref = ''
        self._dic = {}
        self._creationtime = timenow()
        self.selfcheck()

    def run(self, loss_rate=1):
        if self._classification != '':
            for index, col in self._ref.iterrows():
                self._dic.update(
                    {col['enterprise_type']: {
                         'entity': col['entity']
                     }})
                self._dic[
                    col['enterprise_type']]['ownership'] = col['ownership']
        elif self._flag:
            self.classifer()
            # self._ref = pd.read_csv(self._outfolder + '\\classification.txt',
            # sep='\t',
            # encoding='utf-8')
        # return self._ref
        for cursor in range(self._cursor, len(self._csvfiles)):
            year = self._csvfiles[cursor].split('\\')[-1].split('.')[0]
            province = self._csvfiles[cursor].split('\\')[-2]
            if self._row_cursor == 0 | ((self._process != '初始化') & (self._process != '分类完成')):
                # 初始化工作表
                xlsxfile = Workbook(self._outfolder +
                                    '\\{}\\report_{}.xlsx'.format(year, year))
                result = xlsxfile.add_worksheet('项目结果')
                result.write(self._row_cursor, 0, '省份')
                result.write(self._row_cursor, 1, '缺失率(%)')
                result.write(self._row_cursor, 2, '有效值')
                self._row_cursor += 1
            csvfile = pd.read_csv(self._csvfiles[cursor],
                                  usecols=[2, 17, 25],
                                  encoding='utf-8',
                                  low_memory=False)
            csvfile['enterprise_type'].fillna('个体工商户', inplace=True)
            total, loss, valid = len(csvfile), 0, 0
            mkdir(self._outfolder + '\\{}'.format(year))
            with open(self._outfolder + '\\{}\\coordinates_{}.txt'.format(year, year),
                      mode='a',
                      encoding='utf-8') as c:
                for index, col in tqdm(csvfile.iterrows(),
                                       total=total,
                                       desc='{} {}'.format(year, province)):
                    # if self._index_cursor > index:
                        # continue
                    if col['lnglat'] is np.nan:
                        loss += 1
                        continue
                    else:
                        if len(col['enterprise_type']) > 30:
                            loss += 1
                            continue
                        else:
                            if ((self._type['法人单位'] == 'n') |
                                (self._dic[col['enterprise_type']]['entity']
                                 == self._type['法人单位'])) & (
                                     (self._type['所有制类型'] == 'a') |
                                     (self._dic[col['enterprise_type']]
                                      ['ownership'] == self._type['所有制类型'])):
                                c.write(col['lnglat'] + '\n')
                                valid += 1
            lossrate = round(float(loss) / total * 100, 2)
            result.write(self._row_cursor, 0, province)
            result.write(self._row_cursor, 1, lossrate)
            result.write(self._row_cursor, 2, valid)
            self._row_cursor += 1
            self._row_cursor %= len(self._region) + 1
            if lossrate > loss_rate:
                print('{}缺失率为{}%，需要重提取'.format(province, lossrate))
                ws = xlsxfile.add_worksheet(province)
                ws.write(0, 0, '城市')
                ws.write(0, 1, '新创企业')
                dic, loss_c, r = {}, 0, 1
                for index, col in tqdm(csvfile.iterrows(),
                                       total=total,
                                       desc='* {} {}'.format(year, province)):
                    if len(col['enterprise_type']) > 30:
                        loss_c += 1
                        continue
                    if ((self._type['法人单位'] == 'n') |
                        (self._dic[col['enterprise_type']]['entity']
                         == self._type['法人单位'])) & (
                             (self._type['所有制类型'] == 'a') |
                             (self._dic[col['enterprise_type']]['ownership']
                              == self._type['所有制类型'])):
                        if col['city'] is np.nan:
                            loss_c += 1
                            continue
                        elif province in col['city']:
                            if col['city'] == province:
                                dic[col['city']] = dic.get(col['city'], 0) + 1
                            else:
                                col['city'] = col['city'][len(province):]
                                dic[col['city']] = dic.get(col['city'], 0) + 1
                        else:
                            loss_c += 1
                            continue
                for city, firms in dic.items():
                    if (city.endswith('区') | city.endswith('盟')
                            | city.endswith('自治州')):
                        pass
                    else:
                        city = city + '市'
                    ws.write(r, 0, city)
                    ws.write(r, 1, firms)
                    r += 1
                ws.write(r, 0, '缺失率(%)')
                ws.write(r, 1, round(float(loss_c) / total * 100, 2))
            if self._row_cursor == 0:
                # 遍历该年份所有数据后将结果写入xlsx并关闭文件
                xlsxfile.close()
                print('{}年已提取完成.'.format(year))
            self._process = self._csvfiles[cursor]
            self.new_cp()
        print('项目已完成.')

    def revive(self):
        # revive at the middle flag!
        try:
            self._cursor = self._csvfiles.index(self._process) + 1
            self._row_cursor = (self._cursor % len(self._region) + 1) if (
                self._cursor % len(self._region) != 0) else 0
        except ValueError:
            self._cursor = 0
            self._row_cursor = 0

    def if_classify(self):
        self._flag = 'y' == input('是否要区分法人单位与所有制类型(y/n?)')
        if self._flag:
            self._type = {
                '法人单位': input('仅保留企业法人单位(y/n?)'),
                '所有制类型': input('保留所有制类型(单选):\na:全部\tp:私有\tf:外资\ts:国有\tc:集体\n')
            }
        else:
            self._type = {'法人单位': 'n', '所有制类型': 'a'}

    def selfcheck(self):
        '''核实项目状态'''
        self._json = self._outfolder + '\\cp.json'
        try:
            with open(self._json, encoding='utf-8') as f:
                self._cp = json.load(f)
                self._creationtime = self._cp['创建时间']
                if self._cp['数据库地址'] != self._database:
                    if 'n' == input('项目数据库地址变化，是否更新 (y/n?)'):
                        self._database = self._cp['数据库地址']
                # if self._cp['研究时间'] != '{}年'.format(self._period[0]) if self._period[0] == self._period[1] - 1 else '{}年-{}年'.format(self._period[0], self._period[1] - 1):
                # if 'n' == input('项目研究时间变化，是否更新 (y/n?)'):
                # self._period = self._cp['研究时间']
                # self._range = range(self._period[0], self._period[1])
                if self._cp['研究区域'] != self._region:
                    if 'n' == input('项目研究区域变化，是否更新 (y/n?)'):
                        self._region = self._cp['研究区域']
                if self._cp['输出类型'] != self._type:
                    if 'n' == input('项目输出类型变化，是否更新 (y/n?)'):
                        self._type = self._cp['输出类型']
                self._process = self._cp['项目进度']
                if os.path.exists(self._cp['分类结果']) | os.path.exists(
                        'classification.txt'):
                    if 'y' == input(
                            '项目已包含分类文件，是否读取 (y/n?)\nNOTES:请确保研究时间与研究区域相同！\n'):
                        self._classification = self._cp['分类结果']
                        self._ref = pd.read_csv(self._cp['分类结果'],
                                                sep='\t',
                                                encoding='utf-8')
        except FileNotFoundError:
            self._process = '初始化'
        self.new_cp()
        self.revive()
        print('当前项目状态:\n{}'.format(self._cp))

    def classifer(self):
        '''识别是否为法人单位与所有制类型'''
        legal_entity = {
            'unincorporated': {
                'judgement':
                ['合伙', '个体工商户', '非法人', '分公司', '分支机构', '个体', '个人', '代表机构'],
                'entity':
                'n'
            },
            'unsure': {
                'judgement': ['联营'],
                'entity': 'u'
            }
        }
        ownership = {
            'state': {
                'judgement': ['国有', '全民'],
                'ownership': 's'
            },
            'collective': {
                'judgement': ['合作', '集体', '农'],
                'ownership': 'c'
            },
            'foreign': {
                'judgement': ['外', '港', '澳', '台'],
                'ownership': 'f'
            },
            'private': {
                'judgement': ['低于25'],
                'ownership': 'p'
            }
        }
        print('项目{}正在分类中，请等待...'.format(self._name))
        dic_sum = {}
        dic_entity = {}
        dic_ownership = {}
        for csvfile in self._csvfiles:
            data = pd.read_csv(csvfile,
                               usecols=[17],
                               encoding='utf-8',
                               low_memory=False)
            data['enterprise_type'].fillna('个体工商户', inplace=True)
            enterprise_types = data.enterprise_type.tolist()
            # 去除过长异常值
            for enterprise_type in enterprise_types:
                if len(enterprise_type) > 30:
                    enterprise_types.remove(enterprise_type)
            # 统计不同企业类型描述出现次数
            for enterprise_type in enterprise_types:
                dic_sum[enterprise_type] = dic_sum.get(enterprise_type, 0) + 1
            # 判断是否为企业法人单位，区分所有制类型
            for enterprise_type in dic_sum.keys():
                # 默认企业为法人单位
                dic_entity[enterprise_type] = 'y'
                for key in legal_entity.keys():
                    for statement in legal_entity[key]['judgement']:
                        if statement in enterprise_type:
                            dic_entity[enterprise_type] = legal_entity[key][
                                'entity']
                # 默认企业为私有制
                dic_ownership[enterprise_type] = 'p'
                for key in ownership:
                    for statement in ownership[key]['judgement']:
                        if statement in enterprise_type:
                            dic_ownership[enterprise_type] = ownership[key][
                                'ownership']
            # 用dic作为容器存储结果
            for enterprise_type in enterprise_types:
                self._dic.update(
                    {enterprise_type: {
                        'sum': dic_sum[enterprise_type]
                    }})
                self._dic[enterprise_type]['entity'] = dic_entity[
                    enterprise_type]
                self._dic[enterprise_type]['ownership'] = dic_ownership[
                    enterprise_type]
        # 将分类结果保存至classification.txt文件中
        self._classification = self._outfolder + '\\classification.txt'
        outfile = open(self._classification, 'w', encoding='utf-8')
        # outfile.write(
        #     'y for legal entity, n for unincorporated, u for unsure\np for private,
        #      s for state-own, c for collective, f for foreign\n'
        # )
        outfile.write('enterprise_type\tentity\townership\tsum\n')
        for enterprise_type in self._dic.keys():
            outfile.write('{}\t{}\t{}\t{}\n'.format(
                enterprise_type, self._dic[enterprise_type]['entity'],
                self._dic[enterprise_type]['ownership'],
                self._dic[enterprise_type]['sum']))
        self._process = '分类完成'
        self.new_cp()
        print('分类结束 :)')

    def gen_csvfiles(self):
        '''所有待处理文件名'''
        csvfiles = []
        for year in self._range:
            for province in self._region:
                csvfiles.append(
                    self._database +
                    '\\csv_data\\{}\\{}.csv'.format(province, year))
        # print(csvfiles)
        return csvfiles

    def new_cp(self):
        self._checktime = timenow()
        self._cp = {
            '项目名称':
            self._name,
            '保存位置':
            self._dirname,
            '创建时间':
            self._creationtime,
            '数据库地址':
            self._database,
            '研究时间':
            '{}年'.format(self._period[0])
            if self._period[0] == self._period[1] -
            1 else '{}年-{}年'.format(self._period[0], self._period[1] - 1),
            '研究区域':
            self._region,
            '项目进度':
            self._process,
            '修改时间':
            self._checktime,
            '分类结果':
            self._classification,
            '输出类型': {
                '法人单位': self._type['法人单位'],
                '所有制类型': self._type['所有制类型']
            }
        }
        with open(self._json, 'w') as f:
            f.write(json.dumps(self._cp, indent=4, separators=(',', ': ')))

    @property
    def directory(self):
        return self._directory

    @directory.setter
    def directory(self, directory):
        self._directory = directory

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, period):
        self._period = period

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, region):
        self._region = region

    @property
    def outfolder(self):
        return self._outfolder

    @outfolder.setter
    def outfolder(self, outfolder):
        self._outfolder = outfolder

    @property
    def classification(self):
        return self._classification

    @classification.setter
    def classification(self, classification):
        self._classification = classification
        self.new_cp()


def main():
    prj = project(set_directory(), set_period(), set_region(), set_outfolder())
    prj.run()


if __name__ == "__main__":
    main()
