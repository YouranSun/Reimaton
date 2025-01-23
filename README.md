# *Reimaton*: A GUI reimbursement helper

## About

*Reimaton* is a GUI programme that helps you generate a valid reimbursement application based on your Fapiao and other documents.

It aims to improve the efficiency of the reimbursement process for the University's XCPC team, especially avoiding the back-and-forth caused by mistakes in the reimbursement materials.

<table><tr>
<td><img src="wechat1.jpg" alt="wechat1" /></td>

<td><img src="wechat2.jpg" alt="wechat2" /></td>

<td><img src="wechat3.jpg" alt="wechat3" /></td>
</tr><table>

## Dependencies & Declaration

*Reimaton* uses:

* Third-party libraries, which can be found in [requirements.txt](https://github.com/YouranSun/Reimaton/blob/main/requirements.txt).
* **Tesseract** for OCR under the [Apache license](http://www.apache.org/licenses/LICENSE-2.0).

The project is for non-commercial use. Author(s) of this project don't take any responsibility for the content generated with the programme.

## Installing & Running *Reimaton*

The project is still in progress. Currently *Reimaton* can be run as a Python programme on Windows.

1. ```bash
   git clone https://github.com/YouranSun/Reimaton
   cd Reimaton
   pip install -r requirements.txt
   ```
   
2. Install Tesseract [here](https://github.com/UB-Mannheim/tesseract/wiki). Make sure it is added to your system paths. Check it by:

   ```bash
   tesseract --version
   ```

3. Download [chi_sim.traineddata](https://github.com/tesseract-ocr/tessdata/blob/main/chi_sim.traineddata) and [eng_traineddata](https://github.com/tesseract-ocr/tessdata/blob/main/eng.traineddata) under the current directory `Reimaton/` for Chinese and English OCR.
4. Run `python main.py`.

## Reimbursement Rules

*Part of this section is in Chinese for clarification.*

### “发票-证明文件-说明” Diagram

*Reimaton* follows a “发票-证明文件-说明” diagram for reimbursement items. “发票” is the basic element in the reimbursement application. Each piece of 发票 is uniquely assigned an amount of money, and the total amount of the reimbursement is the sum of the amount from each piece of 发票.

Each piece of 发票 is related to some 证明文件, indicating the corresponding consumption of the 发票 and giving evidence that it is under the University's standard.

Other than 证明文件, it is necessary to attach some 说明 to help the school staff better understand the reimbursement items.

### Types of reimbursement items and their formats

| 报销款项 | 发票种类                   | 证明文件                                               | 说明                                           |
| -------- | -------------------------- | ------------------------------------------------------ | ---------------------------------------------- |
| 交通     | 电子发票（飞机）           | 舱位截图（包含金额、乘机人姓名、行程起终点、舱位类型） | 行程说明（出行人、行程起终点），扣除的附加费用 |
|          | 航空运输电子客票行程单     | /                                                      | 行程说明（出行人、行程起终点）                 |
|          | 电子发票（打车）           | 行程单（包含金额、行程信息）                           | 出行人                                         |
| 住宿     | 电子发票                   | 酒店水单**原件**                                       | 住宿人、住宿天数                               |
| 报名费   | 电子发票                   | 参赛手册                                               |                                                |
| 纸质发票 | 火车报销凭证               | /                                                      | 行程说明（出行人、行程起终点）                 |
|          | 纸质发票（路桥费、打车等） | /                                                      | 行程说明（出行人、行程起终点）                 |

### Types of Mistakes

Here are some frequent mistakes. *Reimaton* can now detect a part of them ([?] means no guaranteed accuracy):

* [ ] 发票的类型应为 “普通发票”，开成 “专用发票”（To-do）
* [x] 发票/航空运输电子客票行程单的购买方名称（“发票抬头”，应为大学）错漏
* [x] 发票/航空运输电子客票行程单的纳税人识别号（“税号”）错漏
* **?**  发票缺少全国统一发票监制章
* [x] 发票金额未扣除行程的附加费用（保险等）
* [x] 证明文件的总金额不能覆盖发票的金额
* [x] 发票重复
* [x] 同一证明文件成为不同发票的证明
* [x] 同一行程出现在不同发票的说明中
* **?**  证明文件中没有包含说明所指定行程的信息
* [x] 舱位截图不能证明乘经济舱出行
* [x] 发票实际金额与报销表格陈述不符
* [x] 文件命名方式与报销表格陈述不符
* [x] 报销总金额与发票金额总和不等
* [ ] 缺少参赛手册或排名文件证明参赛（To-do）
* [ ] 缺少代收款委托书（To-do）
* [ ] 酒店价格超过报销标准
* [ ] 火车座位超过报销标准
* [ ] 纸质发票缺少原件
* [ ] 酒店水单缺少原件
* [ ] 小于A4的纸质报销材料没有粘贴在A4纸上提交

## Functionalities

*Reimaton* helps with **real** reimbursement materials. It is not *Reimaton*'s work to deal with other files.

Here are currently supported functionalities:

* Edit the 参赛选手 and 举办城市 of a contest.
* Attach a 电子发票 file to 交通，住宿 or 报名费; Attach a 航空运输电子客票行程单 file to 交通.
* Attach a 舱位截图 file to some 电子发票.
* Add a record of 纸质发票, including its 金额 and 说明.
* Attach a 行程说明 to some 发票.
* Detecting 附加费用 in a 电子发票 and subtracting it automatically from the amount.
* Remove any file from the reimbursement scheme.
* Validate the current reimbursement scheme with potential [mistakes](#Types of mistakes) and provide **errors** and **warnings**.
* Generate a directory that contains well-renamed documents and a `.xlsx` file indicating the corresponding relationships of these documents according to the current reimbursement scheme.

## To-dos

* Detect more [mistakes](#Types of mistakes).
* Support persistence (read and write reimbursement scheme from/to an existing file).
* Validate the execution on different platforms (mainly on macOS).
* Provide an auto-install script.
* Improve the robustness, especially on non-existent or unrecognizable files.
* Improve the GUI.
