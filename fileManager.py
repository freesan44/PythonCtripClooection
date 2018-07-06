import xlrd
import xlwt
from xlutils.copy import copy
import os

class ExcelFileManager:
    def creatExcelFile(fileName,sheetName,headRowList):
        # 获取项目所在目录
        filePath = os.getcwd() + '/' + fileName + '.xls'
        #如果不存在就新增
        try:
            oldFile = xlrd.open_workbook(filePath)
            file = copy(oldFile)
        except:
            file = xlwt.Workbook()
            print("新建文件")

        #如果不存在就新增
        try:
            sheet1 = file.add_sheet(sheetName,cell_overwrite_ok=True)
        except:
            sheet1 = file.get_sheet(sheetName)
        #设置style样式
        head_style = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',num_format_str='#,##0.00')
        row0 = headRowList
        for i in range(0,len(row0)):
            sheet1.write(0,i,row0[i],head_style)


        print(filePath)
        file.save(filePath)

    def addDataToExcelFile(fileName,sheetName,dataList):
        filePath = os.getcwd()+'/'+fileName+'.xls'
        file = xlrd.open_workbook(filePath)
        #已存在的行数
        newRows = file.sheet_by_name(sheetName).nrows
        new_File = copy(file)
        sheet = new_File.get_sheet(sheetName)
        try:
            for i in range(0,len(dataList)):
                for j in  range(0,len(dataList[i])):
                    sheet.write(i+newRows,j,dataList[i][j])
        except Exception as e:
            print(e)

        new_File.save(filePath)


if __name__ == '__main__':
    headRowList = ['1111','2222','3333']
    ExcelFileManager.creatExcelFile('test','jiangmen1',headRowList)


    dataList1 = ['1','2','3']
    dataList2 = ['4','5','6']
    dataList = [dataList1,dataList2]
    ExcelFileManager.addDataToExcelFile('test','jiangmen',dataList)