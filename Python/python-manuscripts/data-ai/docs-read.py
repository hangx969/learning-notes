from docx import Document

# 从模板生成一个简单的 Linux 运维报告，包含服务器名称、CPU 使用率、内存使用率等基本信息。

# 创建word文档对象
doc = Document()
# 添加一级标题
doc.add_heading("Linux Operation Report", level=1)
# 添加段落信息
doc.add_paragraph("Server Name: ")
doc.add_paragraph("CPU usage:")
doc.add_paragraph("Memory usage:")

# 保存文档
doc.save(r".\data-ai\report_template.docx")