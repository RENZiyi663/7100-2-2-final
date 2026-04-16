"""
为Results_Final.docx添加显著性星标标注 - 增强版
更强大的表格识别和星标添加
"""

from docx import Document
from docx.shared import Pt, RGBColor
import re

# 打开文档
doc_path = '/workspaces/7100-2-2-final/Output/1104开写/Results_Final.docx'
doc = Document(doc_path)

def get_numeric_value(text):
    """从文本中提取数值"""
    match = re.search(r'([\d.]+|<\.001)', text)
    if match:
        return match.group(1)
    return None

def add_significance_mark(cell_text):
    """根据p值添加星标"""
    # 检查是否已有星标
    if cell_text.endswith(('*', 'ns', 'ns)')) or '***' in cell_text or '**' in cell_text or '*' in cell_text:
        return cell_text
    
    # 提取p值
    if '<.001' in cell_text.lower() or '< .001' in cell_text.lower():
        return f"{cell_text}***"
    elif '<.01' in cell_text.lower() or '< .01' in cell_text.lower():
        return f"{cell_text}**"
    
    # 提取数值并判断
    try:
        match = re.search(r'([\d.]+)', cell_text)
        if match:
            p_val = float(match.group(1))
            if p_val < 0.001:
                return f"{cell_text}***"
            elif p_val < 0.01:
                return f"{cell_text}**"
            elif p_val < 0.05:
                return f"{cell_text}*"
    except:
        pass
    
    return cell_text

# 遍历所有表格
table_count = 0
total_modified = 0

for table in doc.tables:
    table_count += 1
    print(f"\n【表格 {table_count}】")
    
    rows = len(table.rows)
    cols = len(table.columns) if rows > 0 else 0
    
    if rows == 0 or cols == 0:
        print("  表格为空，跳过")
        continue
    
    # 打印表格头信息
    header_row = table.rows[0]
    header_cells = [cell.text[:15] for cell in header_row.cells]
    print(f"  表头: {header_cells}")
    
    # 逐行遍历表格数据
    for row_idx in range(1, rows):
        row = table.rows[row_idx]
        
        for col_idx in range(cols):
            try:
                cell = row.cells[col_idx]
                cell_text = cell.text.strip()
                
                # 查找包含p值的单元格（p值通常是小数或<.001形式）
                if cell_text and any(char in cell_text for char in ['.', '<', '>']):
                    # 检查是否为p值格式
                    if re.search(r'[\d.]', cell_text) or '<.' in cell_text or '> .' in cell_text:
                        old_text = cell_text
                        new_text = add_significance_mark(cell_text)
                        
                        if new_text != old_text and ('*' in new_text and '*' not in old_text):
                            cell.text = new_text
                            print(f"    [行{row_idx},列{col_idx}] {old_text} → {new_text}")
                            total_modified += 1
            except Exception as e:
                pass

print(f"\n{'='*60}")
print("【修改统计】")
print(f"  总表格数: {table_count}")
print(f"  已添加星标: {total_modified} 个单元格")
print(f"\n【显著性星标说明】")
print("  * p < 0.05 (显著)")
print("  ** p < 0.01 (非常显著)")
print("  *** p < 0.001 (极其显著)")
print(f"{'='*60}")

# 检查并添加说明
found_note = False
for para in doc.paragraphs:
    if '显著性' in para.text or 'significance' in para.text.lower() or '***' in para.text:
        found_note = True
        break

if not found_note:
    doc.add_paragraph('')
    note_para = doc.add_paragraph('注：* p < 0.05, ** p < 0.01, *** p < 0.001')
    note_para.style = 'Normal'

# 保存修改
doc.save(doc_path)
print(f"\n✓ 已成功保存: {doc_path}")
