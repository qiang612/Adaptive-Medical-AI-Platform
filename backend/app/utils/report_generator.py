from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime
from app.core.config import settings


# 注册中文字体（需要下载中文字体文件，这里使用系统默认或备用方案）
def register_fonts():
    font_paths = [
        # Windows
        "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        # Linux
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        # Mac
        "/System/Library/Fonts/PingFang.ttc",
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                return 'ChineseFont'
            except:
                continue
    return 'Helvetica'  # fallback


FONT_NAME = register_fonts()


class MedicalReportGenerator:
    def __init__(self, task_data, result_data):
        self.task = task_data
        self.result = result_data
        self.styles = getSampleStyleSheet()
        self._setup_chinese_styles()

    def _setup_chinese_styles(self):
        self.styles.add(ParagraphStyle(
            name='ChineseTitle',
            parent=self.styles['Heading1'],
            fontName=FONT_NAME,
            fontSize=18,
            spaceAfter=30,
            alignment=1  # 居中
        ))
        self.styles.add(ParagraphStyle(
            name='ChineseHeading',
            parent=self.styles['Heading2'],
            fontName=FONT_NAME,
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        self.styles.add(ParagraphStyle(
            name='ChineseNormal',
            parent=self.styles['Normal'],
            fontName=FONT_NAME,
            fontSize=10,
            spaceAfter=6
        ))
        self.styles.add(ParagraphStyle(
            name='ChineseSmall',
            parent=self.styles['Normal'],
            fontName=FONT_NAME,
            fontSize=8,
            textColor=colors.gray
        ))

    def generate(self, output_path):
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )

        story = []

        # 1. 报告标题
        story.append(Paragraph("自适应 AI 辅助医疗诊断报告", self.styles['ChineseTitle']))
        story.append(Spacer(1, 20))

        # 2. 患者信息
        story.append(Paragraph("一、患者信息", self.styles['ChineseHeading']))
        patient_data = [
            ["患者姓名", self.task.patient_name or "未填写"],
            ["患者ID", self.task.patient_id or "未填写"],
            ["检查时间", datetime.now().strftime("%Y年%m月%d日 %H:%M")],
            ["诊断模型", self.result.get('model_type', '未知')]
        ]
        patient_table = Table(patient_data, colWidths=[100, 300])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 20))

        # 3. 诊断结果
        story.append(Paragraph("二、诊断结果", self.styles['ChineseHeading']))

        # 风险评估（如果有）
        if 'risk_score' in self.result:
            risk_level = self.result.get('risk_level', '未知')
            risk_color = colors.green if risk_level == '低风险' else colors.orange if risk_level == '中风险' else colors.red

            story.append(Paragraph(f"风险等级: <font color='{risk_color}'><b>{risk_level}</b></font>",
                                   self.styles['ChineseNormal']))
            story.append(Paragraph(f"风险评分: {self.result['risk_score']:.2f}", self.styles['ChineseNormal']))
            story.append(Spacer(1, 10))

            story.append(Paragraph("影响因素权重:", self.styles['ChineseNormal']))
            weights = self.result.get('feature_weights', {})
            weight_data = [[k, f"{v:.2%}"] for k, v in weights.items()]
            weight_table = Table(weight_data, colWidths=[150, 100])
            weight_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(weight_table)
            story.append(Spacer(1, 10))

        # 影像检测结果（如果有）
        if 'detections' in self.result and self.result['detections']:
            story.append(
                Paragraph(f"检测到 {len(self.result['detections'])} 个异常区域:", self.styles['ChineseNormal']))
            det_data = [["序号", "类别", "置信度", "坐标"]]
            for i, det in enumerate(self.result['detections'], 1):
                det_data.append([
                    str(i),
                    det['class'],
                    f"{det['confidence']:.2%}",
                    str(det['bbox'])
                ])
            det_table = Table(det_data, colWidths=[50, 100, 80, 170])
            det_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(det_table)
            story.append(Spacer(1, 10))

            # 添加标注图片
            if 'annotated_image' in self.result:
                img_path = self.result['annotated_image']
                if os.path.exists(img_path):
                    story.append(Paragraph("AI标注影像:", self.styles['ChineseNormal']))
                    img = Image(img_path, width=400, height=300)
                    story.append(img)
                    story.append(Spacer(1, 10))

            # 🔥 新增：在 PDF 影像或表格下方直接附带详细的图像分析与诊断建议 🔥
            if 'image_analysis' in self.result:
                story.append(Spacer(1, 5))
                story.append(Paragraph("<b><font color='darkblue'>AI 影像辅助诊断与详细临床建议:</font></b>",
                                       self.styles['ChineseNormal']))
                analysis_lines = self.result['image_analysis'].split('\n')
                for line in analysis_lines:
                    if line.strip():
                        # 使用 &nbsp; 替换空格，以确保 PDF 渲染时保留左侧缩进，使排版更美观
                        formatted_line = line.replace('  ', '&nbsp;&nbsp;')

                        # 识别带【】的标题行为加粗显示
                        if '【' in formatted_line:
                            formatted_line = f"<b>{formatted_line}</b>"

                        story.append(Paragraph(formatted_line, self.styles['ChineseNormal']))
                story.append(Spacer(1, 10))

        # 4. 医疗建议
        story.append(Paragraph("三、医疗建议", self.styles['ChineseHeading']))
        recommendation = self.result.get('recommendation', '建议咨询专业医生')
        story.append(Paragraph(recommendation, self.styles['ChineseNormal']))
        story.append(Spacer(1, 30))

        # 5. 免责声明
        story.append(Spacer(1, 50))
        story.append(Paragraph("-" * 80, self.styles['ChineseSmall']))
        story.append(Paragraph("免责声明: 本报告仅供参考，不作为最终诊断依据。请务必咨询专业医生获取准确诊断。",
                               self.styles['ChineseSmall']))
        story.append(
            Paragraph(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['ChineseSmall']))

        doc.build(story)
        return output_path