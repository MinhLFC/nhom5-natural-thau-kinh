import os
import sys
import subprocess
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, 'doc_images')
LOGO_PATH = os.path.join(BASE_DIR, 'assets', 'logo-hcmue.png')
DOCX_OUT = os.path.join(BASE_DIR, 'Huong-Dan-Mo-Phong-Thi-Nghiem-Thau-Kinh-Natural.docx')
DOCX_ALT = os.path.join(BASE_DIR, 'Huong-Dan-Mo-Phong-Thi-Nghiem-Thau-Kinh-Natural-MoiNhat.docx')
HTML_OUT = os.path.join(BASE_DIR, 'document_preview.html')
PDF_OUT = os.path.join(BASE_DIR, 'Huong-Dan-Mo-Phong-Thi-Nghiem-Thau-Kinh-Natural.pdf')
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def set_cell_border(cell, **kwargs):
    """Set cell borders."""
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = 'w:{}'.format(edge)
            element = OxmlElement(tag)
            element.set(qn('w:val'), edge_data.get('val', 'single'))
            element.set(qn('w:sz'), str(edge_data.get('sz', 4)))
            element.set(qn('w:space'), '0')
            element.set(qn('w:color'), edge_data.get('color', 'auto'))
            tcBorders.append(element)
    tcPr.append(tcBorders)

def set_cell_shading(cell, color_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def build_docx():
    doc = Document()

    # Set page margins A4: Top 2cm, Bottom 2cm, Left 2.5cm, Right 2cm
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(0.98)
        section.right_margin = Inches(0.79)

    # Base style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(13)
    normal_style.font.color.rgb = RGBColor(0x11, 0x18, 0x27)
    normal_style.paragraph_format.line_spacing = 1.2
    normal_style.paragraph_format.space_after = Pt(4)

    # Header with Logo and Institution
    if os.path.exists(LOGO_PATH):
        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        tbl.columns[0].width = Inches(2.2)
        tbl.columns[1].width = Inches(4.5)
        
        # Cell 1: Logo
        c1 = tbl.cell(0, 0)
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.line_spacing = 1.0
        run_logo = p1.add_run()
        run_logo.add_picture(LOGO_PATH, width=Inches(2.1))
        
        # Cell 2: School & Group Info
        c2 = tbl.cell(0, 1)
        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p2.paragraph_format.space_after = Pt(2)
        p2.paragraph_format.line_spacing = 1.15
        
        r_sch = p2.add_run("TRƯỜNG ĐẠI HỌC SƯ PHẠM TP. HỒ CHÍ MINH\n")
        r_sch.bold = True
        r_sch.font.size = Pt(11)
        r_sch.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)
        
        r_grp = p2.add_run("NHÓM NATURAL · KHOA HỌC TỰ NHIÊN 9\n")
        r_grp.bold = True
        r_grp.font.size = Pt(10.5)
        r_grp.font.color.rgb = RGBColor(0xd6, 0x3a, 0x3f)

        r_mem = p2.add_run("Nguyễn Thị Ý Như · Đỗ Văn Nhật Minh\nNguyễn Huyền Trang · Nguyễn Khánh Linh")
        r_mem.font.size = Pt(9.5)
        r_mem.font.color.rgb = RGBColor(0x55, 0x66, 0x77)

        # Clear borders of header table
        for row in tbl.rows:
            for cell in row.cells:
                set_cell_border(cell, top={'val': 'none'}, bottom={'val': 'none'}, left={'val': 'none'}, right={'val': 'none'})

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_after = Pt(8)

    # Document Title
    p_t1 = doc.add_paragraph()
    p_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t1.paragraph_format.space_after = Pt(4)
    r_t1 = p_t1.add_run("BÁO CÁO HỌC LIỆU SỐ & MÔ PHỎNG THÍ NGHIỆM")
    r_t1.bold = True
    r_t1.font.size = Pt(16)
    r_t1.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)

    p_t2 = doc.add_paragraph()
    p_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t2.paragraph_format.space_after = Pt(4)
    r_t2 = p_t2.add_run("BÀI 8: THẤU KÍNH (KHTN 9)")
    r_t2.bold = True
    r_t2.font.size = Pt(17)
    r_t2.font.color.rgb = RGBColor(0xd6, 0x3a, 0x3f)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("Học liệu số trực tuyến kết hợp đánh giá theo các mô hình TPACK, SAMR và TRIPLE E\nThời gian thực hiện: 2 tiết")
    r_sub.italic = True
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = RGBColor(0x33, 0x44, 0x55)

    def add_part_title(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(15)
        r.font.color.rgb = RGBColor(0xb9, 0x1c, 0x1c)
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(14)
        r.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(13)
        r.font.color.rgb = RGBColor(0x10, 0x23, 0x3a)
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(13)
        return p

    def add_step(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(13)
        r.font.color.rgb = RGBColor(0xb9, 0x1c, 0x1c)
        return p

    def add_bullet(text, bold_prefix="", indent=0.25):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(indent)
        p.paragraph_format.space_after = Pt(3)
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.bold = True
        p.add_run(text)
        return p

    def add_pic(fname, width_inch=5.8, caption=""):
        p_img = os.path.join(IMG_DIR, fname)
        if os.path.exists(p_img):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            r = p.add_run()
            r.add_picture(p_img, width=Inches(width_inch))

            if caption:
                p_c = doc.add_paragraph()
                p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_c.paragraph_format.space_after = Pt(6)
                rc = p_c.add_run(caption)
                rc.italic = True
                rc.font.size = Pt(10.5)
                rc.font.color.rgb = RGBColor(0x55, 0x66, 0x77)

    # ==================== PHẦN I ====================
    add_part_title("PHẦN I: HƯỚNG DẪN THỰC HÀNH MÔ PHỎNG THÍ NGHIỆM")

    add_h1("1. Thí nghiệm tìm hiểu đường truyền của các tia sáng đặc biệt qua thấu kính.")
    add_h2("1.1. Mục tiêu:")
    add_bullet("Trình bày và mô tả được đường truyền của 3 tia sáng đặc biệt (tia tới đi qua quang tâm O, tia tới song song với trục chính cho tia ló đi qua F' hoặc có đường kéo dài qua F', tia tới đi qua F hoặc có đường kéo dài hướng tới F cho tia ló song song trục chính) khi qua thấu kính hội tụ và thấu kính phân kì thông qua quan sát mô phỏng.")
    add_bullet("Rút ra được quy luật hội tụ của chùm tia ló đối với thấu kính hội tụ và tính chất phân kì của chùm tia ló đối với thấu kính phân kì khi chùm tia tới song song với trục chính.")

    add_h2("1.2. Dụng cụ, thiết bị và các bước tiến hành.")
    add_h3("1.2.1. Dụng cụ, thiết bị và giải thích về công cụ hỗ trợ.")
    add_bullet("Máy tính để bàn, máy tính xách tay hoặc điện thoại thông minh có kết nối Internet.", "- Thiết bị phần cứng: ")
    add_bullet("Phần mềm mô phỏng Thấu kính trực tuyến (Nhóm Natural - KHTN 9, Trường ĐHSP TP.HCM).", "- Phần mềm mô phỏng: ")
    
    p_gc1 = doc.add_paragraph()
    p_gc1.paragraph_format.space_before = Pt(4)
    p_gc1.paragraph_format.space_after = Pt(2)
    r_gc1 = p_gc1.add_run("★ Phân tích điểm khó của nội dung kiến thức trong bài học:")
    r_gc1.bold = True
    r_gc1.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)

    add_bullet("Trong thực tế phòng thí nghiệm phổ thông, đường truyền của các tia sáng trong không khí rất mờ nhạt, tán xạ yếu và cực kì khó quan sát nếu phòng học không đủ tối. Việc bố trí nguồn sáng, căn chỉnh góc nghiêng và lắp đặt khe hẹp để tạo chùm tia laser/halogen phẳng mất rất nhiều thời gian tiết học.", "• ", 0.3)
    add_bullet("Đặc biệt đối với thấu kính phân kì, khái niệm \"tiêu điểm ảo F\" và \"đường kéo dài của tia ló\" là một rào cản nhận thức rất lớn đối với học sinh lớp 9. Trong thí nghiệm thật, mắt học sinh không thể nhìn thấy đường kéo dài nét đứt cắt nhau tại tiêu điểm ở phía trước thấu kính, dẫn đến việc các em phải học vẹt định nghĩa trừu tượng mà không hiểu được bản chất hiện tượng vật lí.", "• ", 0.3)

    p_gc2 = doc.add_paragraph()
    p_gc2.paragraph_format.space_before = Pt(4)
    p_gc2.paragraph_format.space_after = Pt(2)
    r_gc2 = p_gc2.add_run("★ Vai trò và lý do lựa chọn công cụ mô phỏng tương tác (Khắc phục hạn chế của video/thí nghiệm thường):")
    r_gc2.bold = True
    r_gc2.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)

    add_bullet("Mô phỏng tương tác không đơn thuần chỉ để minh họa tĩnh hay thay thế bằng một đoạn video xem thụ động: Học sinh được trực tiếp cầm nắm, kéo rê nguồn sáng S đến bất kì toạ độ nào trong không gian, lập tức nhận thấy đường truyền tia sáng và tia ló biến đổi tương ứng theo thời gian thực (real-time visual feedback).", "• ", 0.3)
    add_bullet("Trực quan hóa \"cái vô hình\": Công cụ mô phỏng cho phép hiển thị các đường kéo dài tia sáng bằng nét đứt sắc nét, giúp học sinh tận mắt chứng kiến giao điểm ảo của chùm tia phân kì tại tiêu điểm F, giải quyết triệt để điểm nghẽn nhận thức của bài học.", "• ", 0.3)

    p_gc3 = doc.add_paragraph()
    p_gc3.paragraph_format.space_before = Pt(4)
    p_gc3.paragraph_format.space_after = Pt(2)
    r_gc3 = p_gc3.add_run("★ Giải thích chi tiết các công cụ hỗ trợ trên giao diện mô phỏng thí nghiệm 1:")
    r_gc3.bold = True
    r_gc3.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)

    add_bullet("Hiệu ứng âm thanh đa giác quan (Web Audio API): Tích hợp phản hồi âm thanh chuẩn mực khi bật/tắt tia sáng, âm thanh chuyển động của tia sáng và âm thanh chúc mừng khi hoàn thành, tạo môi trường học tập sống động, kích thích sự tập trung và hứng thú của học sinh.", "• ", 0.3)
    add_bullet("Chế độ hiển thị Sáng / Tối (Light / Dark mode): Nút chuyển đổi linh hoạt chế độ sáng (phù hợp khi giáo viên trình chiếu trên máy chiếu lớp học) và chế độ tối quang học (tạo cảm giác như đang ở trong phòng thí nghiệm quang học chuyên nghiệp, chống mỏi mắt khi học sinh tự học trên điện thoại cá nhân).", "• ", 0.3)
    add_bullet("Nút \"▶ Chiếu tia sáng\" (Play Animation): Tạo hoạt họa chùm photon chuyển động từ nguồn phát tới thấu kính rồi mới khúc xạ thành tia ló. Công cụ này giúp học sinh nhận thức sâu sắc quan hệ nhân quả vật lí: có tia tới đến thấu kính trước, sau đó mới sinh ra tia ló sau thấu kính.", "• ", 0.3)
    add_bullet("Nút \"Hiện kết luận\" (Đối chiếu sư phạm): Ban đầu kết luận được ẩn đi để học sinh tự thảo luận và rút ra quy tắc; chỉ khi học sinh đã nêu ý kiến thì giáo viên mới mở nút này để cả lớp cùng đối chiếu, khắc phục lỗi tiếp nhận thụ động.", "• ", 0.3)
    add_bullet("Áp dụng chu trình POE (Dự đoán - Quan sát - Giải thích): Nhằm tránh lỗi \"Hỏi sau khi đã thấy kết quả\", trước khi bật từng tia sáng trên mô phỏng, giáo viên luôn yêu cầu học sinh làm bước Dự đoán (P) xem tia ló sẽ đi đâu, sau đó mới bấm chọn tia trên mô phỏng để Quan sát (O) và Giải thích (E).", "• ", 0.3)

    add_h3("1.2.2. Các bước tiến hành.")
    add_step("Bước 1: Truy cập trang web mô phỏng và mở tab \"TN1: Tia sáng\"")
    add_bullet("https://minhlfc.github.io/nhom5-natural-thau-kinh/#tn1", "- Đường link truy cập: ")
    add_bullet("Sau khi truy cập vào đường link, nhấp chọn mục \"TN1: Tia sáng\" trên thanh menu ngang để hiển thị giao diện phòng thí nghiệm ảo chuẩn bị thực hiện mô phỏng.", "- ")
    
    p_cap1 = doc.add_paragraph()
    p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap1 = p_cap1.add_run("Giao diện của mô phỏng thí nghiệm 1 (Tia sáng)")
    r_cap1.bold = True
    r_cap1.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)
    add_pic("01_tn1_overview.png", 5.8, "Hình 1.1: Toàn cảnh giao diện thí nghiệm đường truyền các tia sáng đặc biệt qua thấu kính")

    add_bullet("Cần nắm rõ các phần trong giao diện mô phỏng thí nghiệm:")
    add_bullet("Khu vực sân khấu quang học: Thể hiện trục chính thấu kính, quang tâm O, các tiêu điểm F và F', nguồn sáng điểm S và đường truyền tia sáng màu rực rỡ.", "● ", 0.4)
    add_bullet("Khu vực lựa chọn loại thấu kính: Có thể chuyển đổi nhanh giữa \"Hội tụ\" và \"Phân kì\".", "● ", 0.4)
    add_pic("02_tn1_controls.png", 4.2, "Hình 1.2: Bảng điều khiển chọn loại thấu kính, bật/tắt tia sáng và điều chỉnh tiêu cự f")
    add_bullet("Khu vực chọn tia tới đặc biệt: Cho phép bật/tắt độc lập hoặc đồng thời 3 tia sáng (Tia qua quang tâm O - màu cam vàng, Tia song song trục chính - màu lam, Tia qua tiêu điểm - màu lục).", "● ", 0.4)
    add_bullet("Thanh chỉnh tiêu cự f: Thay đổi tiêu cự từ 6 cm đến 20 cm để khảo sát sự thay đổi vị trí tiêu điểm F, F'.", "● ", 0.4)
    add_bullet("Các nút thao tác nhanh: \"▶ Chiếu tia sáng\" (hiệu ứng tia sáng di chuyển), \"↺ Đặt lại\" (khôi phục mặc định), \"Hiện kết luận\" (đối chiếu kiến thức đã rút ra).", "● ", 0.4)

    add_step("Bước 2: Thực hiện quan sát đường truyền của các tia sáng đặc biệt qua Thấu kính hội tụ.")
    add_bullet("Tại thanh điều khiển, nhấp chọn loại thấu kính là \"Hội tụ\". Đặt nguồn sáng S phía trước thấu kính và lần lượt quan sát từng tia sáng:")
    
    add_bullet("Tia tới đi qua quang tâm O: Tích chọn duy nhất ô \"Tia đi qua quang tâm O\". Quan sát thấy tia ló tiếp tục truyền thẳng theo phương của tia tới mà không bị đổi hướng.", "1. ")
    add_pic("03_tn1_ht_ray_o.png", 5.4, "Hình 1.3: Tia tới đi qua quang tâm O của thấu kính hội tụ truyền thẳng")

    add_bullet("Tia tới song song với trục chính: Tích chọn ô \"Tia song song với trục chính\". Quan sát thấy tia ló bị khúc xạ gập xuống và đi qua tiêu điểm chính F' ở phía sau thấu kính.", "2. ")
    add_pic("04_tn1_ht_ray_p.png", 5.4, "Hình 1.4: Tia tới song song với trục chính cho tia ló đi qua tiêu điểm chính F'")

    add_bullet("Tia tới đi qua tiêu điểm chính F: Tích chọn ô \"Tia đi qua tiêu điểm chính F\". Quan sát thấy tia ló sau khi qua thấu kính trở nên song song với trục chính.", "3. ")
    add_pic("05_tn1_ht_ray_f.png", 5.4, "Hình 1.5: Tia tới đi qua tiêu điểm vật chính F cho tia ló song song trục chính")

    add_bullet("Chiếu đồng thời cả 3 tia sáng đặc biệt: Tích chọn cả 3 tia sáng, kéo rê nguồn sáng S đến các vị trí khác nhau. Quan sát thấy cả 3 tia ló đều cùng cắt nhau tại một điểm duy nhất S' (ảnh thật của điểm sáng S).", "4. ")
    add_pic("06_tn1_ht_all_rays.png", 5.4, "Hình 1.6: Cả 3 tia ló của thấu kính hội tụ cùng hội tụ tại điểm ảnh S'")

    add_step("Bước 3: Thực hiện quan sát đường truyền của các tia sáng đặc biệt qua Thấu kính phân kì.")
    add_bullet("Tại thanh điều khiển, nhấp chọn loại thấu kính là \"Phân kì\". Lần lượt khảo sát đường truyền của 3 tia sáng đặc biệt:")
    
    add_bullet("Tia tới đi qua quang tâm O: Tích chọn ô \"Tia đi qua quang tâm O\". Quan sát thấy tia ló tiếp tục truyền thẳng, tương tự như thấu kính hội tụ.", "1. ")
    add_pic("07_tn1_pk_ray_o.png", 5.4, "Hình 1.7: Tia tới đi qua quang tâm O của thấu kính phân kì truyền thẳng")

    add_bullet("Tia tới song song với trục chính: Tích chọn ô \"Tia song song với trục chính\". Quan sát thấy tia ló bị loe rộng ra (phân kì), đường kéo dài của tia ló (nét đứt) đi qua tiêu điểm ảnh chính F' ở phía trước thấu kính.", "2. ")
    add_pic("08_tn1_pk_ray_p.png", 5.4, "Hình 1.8: Tia tới song song trục chính cho tia ló có đường kéo dài đi qua tiêu điểm ảnh F'")

    add_bullet("Tia tới có đường kéo dài hướng tới tiêu điểm vật chính F: Tích chọn ô \"Tia có đường kéo dài qua tiêu điểm F\". Quan sát thấy tia ló sau khi qua thấu kính trở nên song song với trục chính.", "3. ")
    add_pic("09_tn1_pk_ray_f.png", 5.4, "Hình 1.9: Tia tới hướng tới tiêu điểm vật F ở sau thấu kính cho tia ló song song trục chính")

    add_bullet("Chiếu đồng thời cả 3 tia sáng đặc biệt qua thấu kính phân kì: Quan sát thấy chùm tia ló loe rộng ra, các đường kéo dài của chúng cắt nhau tại điểm ảnh ảo S' ở phía trước thấu kính.", "4. ")
    add_pic("10_tn1_pk_all_rays.png", 5.4, "Hình 1.10: Chùm tia ló phân kì có các đường kéo dài cắt nhau tại ảnh ảo S'")

    # Thí nghiệm 2
    add_h1("2. Thí nghiệm mô phỏng về sự tạo ảnh của vật qua thấu kính.")
    add_h2("2.1. Mục tiêu.")
    add_bullet("Thực hiện thí nghiệm mô phỏng quan sát quá trình dựng ảnh của một vật sáng AB (đoạn thẳng vuông góc với trục chính, A nằm trên trục chính) qua thấu kính hội tụ và thấu kính phân kì.")
    add_bullet("Khảo sát, xác định và ghi nhận được đặc điểm của ảnh A'B' (ảnh thật hay ảnh ảo, cùng chiều hay ngược chiều với vật, lớn hơn hay nhỏ hơn vật) ứng với các khoảng cách khác nhau từ vật đến thấu kính (d > 2f, d = 2f, f < d < 2f, d = f, d < f).")

    add_h2("2.2. Dụng cụ, thiết bị và các bước tiến hành.")
    add_h3("2.2.1. Dụng cụ, thiết bị và giải thích về công cụ hỗ trợ.")
    add_bullet("Máy tính hoặc điện thoại có kết nối Internet.", "- Thiết bị phần cứng: ")
    add_bullet("Phần mềm mô phỏng Thấu kính trực tuyến (Nhóm Natural - KHTN 9, Trường ĐHSP TP.HCM).", "- Phần mềm mô phỏng: ")

    p_gc4 = doc.add_paragraph()
    p_gc4.paragraph_format.space_before = Pt(4)
    p_gc4.paragraph_format.space_after = Pt(2)
    r_gc4 = p_gc4.add_run("★ Phân tích điểm khó của nội dung kiến thức trong bài học:")
    r_gc4.bold = True
    r_gc4.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)

    add_bullet("Khảo sát sự tạo ảnh của thấu kính (đặc biệt là mối liên hệ phụ thuộc giữa vị trí vật d và tính chất ảnh d', h') đòi hỏi sự thay đổi liên tục của vật trên trục chính. Trong thí nghiệm thật, việc dịch chuyển nến/đèn, dịch chuyển thấu kính và màn hứng trên giá quang học rất lề mề, dễ làm lệch trục quang học, ảnh trên màn bị mờ hoặc nhòe khiến học sinh khó xác định ranh giới ảnh rõ nét nhất.", "• ", 0.3)
    add_bullet("Vấn đề nan giải về ẢNH ẢO: Đối với thấu kính phân kì và trường hợp d < f của thấu kính hội tụ, ảnh tạo bởi thấu kính là ảnh ảo. Ảnh ảo hoàn toàn không hứng được trên màn chắn. Trong giờ học thực tế, học sinh nhìn qua thấu kính chỉ thấy ảnh lơ lửng, không thể đo được khoảng cách d' hay chiều cao h', không xác định được ảnh ảo nằm trước hay sau thấu kính. Đây là một điểm nghẽn nhận thức lớn nhất của học sinh THCS.", "• ", 0.3)

    p_gc5 = doc.add_paragraph()
    p_gc5.paragraph_format.space_before = Pt(4)
    p_gc5.paragraph_format.space_after = Pt(2)
    r_gc5 = p_gc5.add_run("★ Vai trò và lý do lựa chọn công cụ mô phỏng tương tác (Khắc phục hạn chế của video/thí nghiệm thường):")
    r_gc5.bold = True
    r_gc5.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)

    add_bullet("Vượt trội hoàn toàn so với video thụ động: Thay vì ngồi xem giáo viên thao tác mẫu, từng học sinh được tự do kéo thả đỉnh B của vật sáng AB sang trái/phải, lên/xuống liên tục; ảnh A'B' di chuyển và biến đổi tương ứng theo thời gian thực. Mối quan hệ giữa vật và ảnh trở thành một quy luật liên tục, trực quan thay vì các trường hợp rời rạc học vẹt.", "• ", 0.3)
    add_bullet("Giải quyết trọn vẹn khái niệm ảnh ảo: Mô phỏng hiển thị đồng thời cả vật thật, ảnh thật (nét liền màu cam), ảnh ảo (nét đứt màu cam) cùng với các đường kéo dài của tia ló, giúp học sinh thấy rõ bản chất tạo ảnh ảo là do đường kéo dài của chùm tia ló cắt nhau.", "• ", 0.3)

    p_gc6 = doc.add_paragraph()
    p_gc6.paragraph_format.space_before = Pt(4)
    p_gc6.paragraph_format.space_after = Pt(2)
    r_gc6 = p_gc6.add_run("★ Giải thích chi tiết các công cụ hỗ trợ trên giao diện mô phỏng thí nghiệm 2:")
    r_gc6.bold = True
    r_gc6.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)

    add_bullet("Thước đo quang học và hệ toạ độ tự động: Trục chính được chia vạch cm rõ ràng, tự động đánh dấu quang tâm O, các tiêu điểm F, F', các vị trí đặc biệt 2F, 2F' giúp học sinh định lượng chính xác khoảng cách.", "• ", 0.3)
    add_bullet("Các nút chọn nhanh vị trí chuẩn trong SGK (d > 2f, d = 2f, f < d < 2f, d = f, d < f): Giúp giáo viên và học sinh chuyển đổi ngay lập tức đến các vị trí trọng tâm của chương trình để khảo sát mà không mất thời gian căn chỉnh thủ công.", "• ", 0.3)
    add_bullet("Bảng đo đạc & tính chất ảnh tức thời (Readout Card): Đóng vai trò như một \"trợ lí số thông minh\", tự động tính toán khoảng cách ảnh d', chiều cao ảnh h', độ phóng đại k, đồng thời hiển thị huy hiệu phân loại ảnh (Ảnh thật / Ảnh ảo, Cùng chiều / Ngược chiều, Lớn hơn / Nhỏ hơn / Bằng vật) với màu sắc nổi bật, giúp học sinh tức thời đối chiếu và củng cố kết quả vẽ ảnh.", "• ", 0.3)
    add_bullet("Áp dụng chu trình POE (Dự đoán - Quan sát - Giải thích): Trước khi nhấp nút vị trí nhanh hoặc kéo vật, giáo viên yêu cầu học sinh ghi nhận dự đoán về đặc điểm ảnh (thật/ảo, chiều, độ lớn), sau đó mới quan sát ảnh trên mô phỏng và giải thích nguyên nhân.", "• ", 0.3)

    add_h3("2.2.2. Các bước tiến hành.")
    add_step("Bước 1: Truy cập trang web mô phỏng và mở tab \"TN2: Vẽ ảnh\"")
    add_bullet("https://minhlfc.github.io/nhom5-natural-thau-kinh/#tn2", "- Đường link truy cập: ")
    add_bullet("Nhấp chọn mục \"TN2: Vẽ ảnh\" trên thanh điều hướng để mở không gian thí nghiệm tạo ảnh.", "- ")

    p_cap2 = doc.add_paragraph()
    p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap2 = p_cap2.add_run("Giao diện của mô phỏng thí nghiệm 2 (Vẽ ảnh)")
    r_cap2.bold = True
    r_cap2.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)
    add_pic("11_tn2_overview.png", 5.8, "Hình 2.1: Toàn cảnh giao diện thí nghiệm vẽ ảnh của vật qua thấu kính")

    add_bullet("Cần nắm rõ các phần trong giao diện mô phỏng thí nghiệm:")
    add_bullet("Vùng quang học trực quan: Vật sáng AB (mũi tên màu xanh), ảnh A'B' (mũi tên màu cam, vẽ nét đứt nếu là ảnh ảo), quang tâm O, trục chính, các tiêu điểm F và F'. Người học có thể dùng chuột kéo thả trực tiếp đỉnh B của vật sang trái/phải hoặc lên/xuống.", "● ", 0.4)
    add_bullet("Khu vực bảng điều khiển thông số:", "● ", 0.4)
    add_pic("12_tn2_controls.png", 4.2, "Hình 2.2: Bảng điều khiển thấu kính, thanh trượt d, f, h và các nút chọn vị trí nhanh")
    add_bullet("Chọn loại thấu kính: \"Hội tụ\" hoặc \"Phân kì\".", "  - ", 0.6)
    add_bullet("Thanh trượt tiêu cự f (5 - 18 cm) và chiều cao vật h (2 - 10 cm).", "  - ", 0.6)
    add_bullet("Các nút chọn vị trí nhanh của vật: d > 2f, d = 2f, f < d < 2f, d = f, d < f giúp quan sát chuẩn xác từng trường hợp chuẩn trong SGK.", "  - ", 0.6)
    add_bullet("Bảng đo đạc & tính chất ảnh tức thời: Tự động cập nhật khoảng cách ảnh d', chiều cao ảnh h' và hiển thị rõ huy hiệu Ảnh thật/Ảnh ảo, Cùng chiều/Ngược chiều, Độ lớn so với vật.", "● ", 0.4)

    add_step("Bước 2: Khảo sát sự tạo ảnh qua Thấu kính hội tụ khi vật ở các khoảng cách khác nhau.")
    add_bullet("Chọn loại thấu kính là \"Hội tụ\", cố định tiêu cự f = 10 cm, chiều cao vật h = 5 cm. Tiến hành khảo sát lần lượt 4 trường hợp vị trí của vật:")

    add_bullet("Trường hợp 1: Vật đặt rất xa / ngoài khoảng 2f (d > 2f, chọn d = 25 cm):", "a) ")
    add_bullet("Nhấp nút vị trí nhanh \"d > 2f\" (hoặc kéo đỉnh B tới hoành độ x = -25 cm). Quan sát hai tia ló xuất phát từ B cắt nhau tại điểm B' ở phía sau thấu kính. Hạ vuông góc xuống trục chính được ảnh A'B'.", "- ", 0.4)
    add_bullet("Kết quả ghi nhận: Ảnh A'B' là ảnh thật, ngược chiều với vật và nhỏ hơn vật (d' = 16,7 cm; h' = 3,3 cm).", "- ", 0.4)
    add_pic("13_tn2_ht_case1_d_greater_2f.png", 5.4, "Hình 2.3: Vật đặt ngoài khoảng 2f (d > 2f) qua TKHT cho ảnh thật, ngược chiều, nhỏ hơn vật")

    add_bullet("Trường hợp 2: Vật đặt cách thấu kính đúng bằng 2 lần tiêu cự (d = 2f = 20 cm):", "b) ")
    add_bullet("Nhấp nút vị trí nhanh \"d = 2f\". Quan sát vị trí ảnh A'B' trên thước đo.", "- ", 0.4)
    add_bullet("Kết quả ghi nhận: Ảnh A'B' là ảnh thật, ngược chiều với vật và có độ cao đúng bằng vật (d' = 20 cm = 2f; h' = 5 cm = h).", "- ", 0.4)
    add_pic("14_tn2_ht_case2_d_equal_2f.png", 5.4, "Hình 2.4: Vật đặt tại vị trí d = 2f qua TKHT cho ảnh thật, ngược chiều, bằng vật")

    add_bullet("Trường hợp 3: Vật đặt trong khoảng giữa tiêu cự và 2 lần tiêu cự (f < d < 2f, chọn d = 15 cm):", "c) ")
    add_bullet("Nhấp nút vị trí nhanh \"f < d < 2f\". Quan sát ảnh A'B' dịch chuyển ra xa thấu kính.", "- ", 0.4)
    add_bullet("Kết quả ghi nhận: Ảnh A'B' là ảnh thật, ngược chiều với vật và lớn hơn vật (d' = 30 cm; h' = 10 cm).", "- ", 0.4)
    add_pic("15_tn2_ht_case3_f_d_2f.png", 5.4, "Hình 2.5: Vật đặt trong khoảng f < d < 2f qua TKHT cho ảnh thật, ngược chiều, lớn hơn vật")

    add_bullet("Trường hợp 4: Vật đặt trong khoảng tiêu cự (d < f, chọn d = 5 cm):", "d) ")
    add_bullet("Nhấp nút vị trí nhanh \"d < f\". Quan sát hai tia ló loe rộng ra không thể cắt nhau ở phía sau thấu kính. Tích chọn ô \"Hiện đường kéo dài\" để thấy hai đường kéo dài nét đứt cắt nhau tại B' ở phía trước thấu kính.", "- ", 0.4)
    add_bullet("Kết quả ghi nhận: Ảnh A'B' là ảnh ảo (nét đứt), cùng chiều với vật và lớn hơn vật (d' = -10 cm; h' = 10 cm). Đây chính là nguyên lý của kính lúp cầm tay.", "- ", 0.4)
    add_pic("16_tn2_ht_case4_d_less_f.png", 5.4, "Hình 2.6: Vật đặt trong khoảng tiêu cự (d < f) qua TKHT cho ảnh ảo, cùng chiều, lớn hơn vật")

    add_step("Bước 3: Khảo sát sự tạo ảnh của vật qua Thấu kính phân kì.")
    add_bullet("Tại thanh điều khiển, chuyển sang chọn loại thấu kính là \"Phân kì\". Cố định tiêu cự f = 10 cm, thay đổi vị trí của vật sáng AB ở các khoảng cách khác nhau (d = 20 cm, d = 25 cm, d = 10 cm...):")
    add_bullet("Thực hiện kéo rê vật AB dọc theo trục chính để quan sát chùm tia ló và vị trí ảnh A'B'.", "- ", 0.4)
    add_bullet("Kết quả ghi nhận: Với mọi vị trí của vật sáng đặt trước thấu kính phân kì, ảnh A'B' luôn luôn là ảnh ảo, cùng chiều với vật, nhỏ hơn vật và luôn nằm trong khoảng tiêu cự của thấu kính (nằm giữa quang tâm O và tiêu điểm F).", "- ", 0.4)
    add_pic("17_tn2_pk_case.png", 5.4, "Hình 2.7: Thấu kính phân kì luôn cho ảnh ảo, cùng chiều, nhỏ hơn vật và nằm trong khoảng tiêu cự")

    # Bảng tổng kết đặc điểm ảnh
    add_h2("2.3. Bảng tổng kết đặc điểm ảnh của vật qua thấu kính:")
    p_tbl_note = doc.add_paragraph()
    r_tn = p_tbl_note.add_run("Bảng 1.1: Đối chiếu đặc điểm ảnh qua Thấu kính hội tụ và Thấu kính phân kì")
    r_tn.italic = True
    r_tn.font.size = Pt(11)

    table = doc.add_table(rows=6, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    col_widths = [Inches(1.5), Inches(1.2), Inches(1.1), Inches(1.3), Inches(1.4)]
    for row in table.rows:
        for i, w in enumerate(col_widths):
            row.cells[i].width = w

    headers = ["Loại thấu kính", "Vị trí của vật (d)", "Ảnh thật / ảo", "Chiều của ảnh", "Độ lớn của ảnh"]
    data = [
        ["Thấu kính hội tụ", "d > 2f", "Ảnh thật", "Ngược chiều", "Nhỏ hơn vật"],
        ["Thấu kính hội tụ", "d = 2f", "Ảnh thật", "Ngược chiều", "Bằng vật"],
        ["Thấu kính hội tụ", "f < d < 2f", "Ảnh thật", "Ngược chiều", "Lớn hơn vật"],
        ["Thấu kính hội tụ", "d < f", "Ảnh ảo", "Cùng chiều", "Lớn hơn vật"],
        ["Thấu kính phân kì", "Mọi vị trí (d > 0)", "Ảnh ảo", "Cùng chiều", "Nhỏ hơn vật"],
    ]

    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)
        set_cell_shading(cell, "F1F5F9")
        set_cell_border(cell, top={'val': 'single', 'sz': 8, 'color': '0d4a7a'},
                              bottom={'val': 'single', 'sz': 8, 'color': '0d4a7a'},
                              left={'val': 'single', 'sz': 4, 'color': 'cbd5e1'},
                              right={'val': 'single', 'sz': 4, 'color': 'cbd5e1'})

    for i, row_data in enumerate(data):
        for j, val in enumerate(row_data):
            cell = table.cell(i + 1, j)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j > 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(10.5)
            if j == 2:
                r.bold = True
                r.font.color.rgb = RGBColor(0x16, 0xa3, 0x4a) if "thật" in val else RGBColor(0xd9, 0x77, 0x06)
            set_cell_border(cell, top={'val': 'single', 'sz': 4, 'color': 'cbd5e1'},
                                  bottom={'val': 'single', 'sz': 4, 'color': 'cbd5e1'},
                                  left={'val': 'single', 'sz': 4, 'color': 'cbd5e1'},
                                  right={'val': 'single', 'sz': 4, 'color': 'cbd5e1'})

    # ==================== PHẦN II ====================
    add_part_title("PHẦN II: PHÂN TÍCH VÀ ĐÁNH GIÁ HỌC LIỆU SỐ MÔ PHỎNG THEO CÁC MÔ HÌNH TPACK, SAMR VÀ TRIPLE E")

    add_h1("1. Giới thiệu chung về học liệu số mô phỏng")
    p_gt = doc.add_paragraph()
    p_gt.paragraph_format.space_after = Pt(4)
    p_gt.add_run(
        "Hiện nay, việc ứng dụng công nghệ thông tin vào dạy học ngày càng phổ biến, đặc biệt trong bối cảnh chuyển đổi số giáo dục "
        "và triển khai Chương trình GDPT 2018. Công nghệ không chỉ hỗ trợ giáo viên trình bày kiến thức mà còn tạo điều kiện để học sinh "
        "chủ động tìm hiểu, quan sát và khám phá nội dung bài học. Đối với môn Khoa học tự nhiên lớp 9, phần Vật lí, cụ thể là chủ đề Quang học "
        "(Bài 8: Thấu kính), có những nội dung rất trừu tượng: đường truyền ánh sáng vô hình trong không khí, tiêu điểm ảo, đường kéo dài của tia ló "
        "và mối quan hệ biến đổi liên tục giữa vị trí vật và tính chất ảnh. Nếu chỉ sử dụng phấn trắng bảng đen hoặc hình vẽ tĩnh trong SGK, học sinh "
        "rất dễ rơi vào tình trạng học vẹt, khó ghi nhớ bản chất hiện tượng.\n\n"
        "Từ thực tế đó, học liệu số mô phỏng thí nghiệm Thấu kính do Nhóm Natural (Trường ĐHSP TP.HCM) phát triển tại địa chỉ "
        "https://minhlfc.github.io/nhom5-natural-thau-kinh/ ra đời nhằm cung cấp môi trường thí nghiệm ảo tương tác cao. Học liệu bao gồm 2 mô phỏng cốt lõi: "
        "Thí nghiệm 1 (Đường truyền của ba tia sáng đặc biệt) và Thí nghiệm 2 (Sự tạo ảnh của vật qua thấu kính). Dưới đây là phần phân tích, đánh giá chuyên sâu "
        "về chất lượng và mức độ chuyển đổi sư phạm của học liệu số theo 3 khung lý thuyết giáo dục quốc tế uy tín: TPACK, SAMR và Triple E."
    )

    add_h1("2. Phân tích học liệu số theo mô hình TPACK")
    p_tp1 = doc.add_paragraph()
    p_tp1.add_run(
        "Mô hình TPACK (Technological Pedagogical Content Knowledge - Mishra & Koehler, 2006) xem xét sự tích hợp hài hòa giữa 3 thành phần kiến thức cốt lõi: "
        "Kiến thức Nội dung (CK), Kiến thức Sư phạm (PK) và Kiến thức Công nghệ (TK), cùng các vùng giao thoa giữa chúng."
    )

    add_h2("2.1. Phân tích các thành phần cốt lõi:")
    add_bullet("Bám sát tuyệt đối nội dung Yêu cầu cần đạt của Bài 8: Thấu kính trong Chương trình GDPT 2018 môn KHTN 9. Thể hiện chuẩn xác đường truyền 3 tia sáng đặc biệt của cả thấu kính hội tụ và phân kì, sự hình thành ảnh thật, ảnh ảo, chiều và độ lớn của ảnh ở các khoảng cách khác nhau.", "• Về Kiến thức Nội dung (CK): ")
    add_bullet("Thiết kế theo định hướng dạy học tích cực, chuyển từ dạy học thuyết giảng truyền thụ sang dạy học khám phá (Inquiry-based learning). Giáo viên tổ chức hoạt động theo chu trình POE (Dự đoán - Quan sát - Giải thích), kết hợp câu hỏi định hướng để học sinh tự kiến tạo kiến thức.", "• Về Kiến thức Sư phạm (PK): ")
    add_bullet("Xây dựng dưới dạng Single Page Application (SPA) trên nền tảng Web tiêu chuẩn (HTML5, CSS3, JavaScript hiện đại, Web Audio API). Không cần cài đặt, không phụ thuộc Flash/Java, tương thích mượt mà trên máy tính, máy tính bảng và điện thoại thông minh; đồ họa Canvas sắc nét và phản hồi tương tác tức thời (< 16ms).", "• Về Kiến thức Công nghệ (TK): ")

    add_h2("2.2. Phân tích các vùng giao thoa và hạt nhân TPACK:")
    add_bullet("Giáo viên lựa chọn câu hỏi định hướng, thiết kế các tình huống có vấn đề (như sự tạo ảnh khi vật ở tiêu điểm hoặc trường hợp d < f) để giúp học sinh giải quyết những nhận niệm sai lầm thường gặp trong quang học.", "• PCK (Sư phạm - Nội dung): ")
    add_bullet("Mô phỏng sử dụng thuật toán quang hình học chính xác để trực quan hóa quy tắc khúc xạ, biến các khái niệm trừu tượng như \"tiêu điểm ảo F\" hay \"đường kéo dài tia ló nét đứt\" thành hình ảnh nhìn thấy được.", "• TCK (Công nghệ - Nội dung): ")
    add_bullet("Khai thác tối đa các công cụ tương tác: kéo rê nguồn S, kéo đỉnh B của vật, thanh trượt f, d, h, nút chiếu tia, nút ẩn/hiện kết luận, chuyển đổi chế độ Sáng/Tối để biến bài giảng thành hoạt động tương tác sinh động.", "• TPK (Công nghệ - Sư phạm): ")
    add_bullet("Học liệu đạt tới đỉnh cao TPACK khi công nghệ mô phỏng được nhúng trực tiếp vào tiến trình sư phạm để giải quyết triệt để các rào cản nhận thức của nội dung bài học mà phương pháp truyền thống không thể làm được.", "• TPACK (Hạt nhân tích hợp): ")

    # Bảng Ma trận TPACK
    p_tpack_note = doc.add_paragraph()
    r_tpn = p_tpack_note.add_run("Bảng 2.1: Ma trận đánh giá học liệu số theo mô hình TPACK")
    r_tpn.italic = True
    r_tpn.font.size = Pt(11)

    t_tpack = doc.add_table(rows=8, cols=4)
    t_tpack.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_tpack.autofit = False
    col_w_tp = [Inches(1.2), Inches(2.2), Inches(2.2), Inches(1.1)]
    for row in t_tpack.rows:
        for idx, w in enumerate(col_w_tp):
            row.cells[idx].width = w

    tp_headers = ["Thành tố TPACK", "Biểu hiện trong học liệu", "Minh chứng thực tế trên Website", "Mức độ đáp ứng"]
    tp_data = [
        ["CK (Nội dung)", "Đúng chuẩn kiến thức quang hình học KHTN 9", "3 tia sáng đặc biệt, 5 trường hợp tạo ảnh chuẩn SGK", "Xuất sắc (5/5)"],
        ["PK (Sư phạm)", "Phương pháp khám phá, chu trình POE", "Hệ thống câu hỏi gợi mở, ẩn kết luận để đối chiếu", "Tốt (4.5/5)"],
        ["TK (Công nghệ)", "Công nghệ Web hiện đại, Canvas HTML5, Web Audio", "Chạy mượt trên mọi thiết bị, có âm thanh và Dark mode", "Xuất sắc (5/5)"],
        ["PCK", "Sư phạm hóa các điểm khó của nội dung quang học", "Giải quyết rào cản tiêu điểm ảo và bản chất ảnh ảo", "Xuất sắc (5/5)"],
        ["TCK", "Công nghệ biểu diễn chính xác quy luật vật lí", "Thuật toán traceRay vẽ tia tới, tia ló, đường kéo dài", "Xuất sắc (5/5)"],
        ["TPK", "Công nghệ hỗ trợ tổ chức hoạt động học tích cực", "Nút Play tia sáng, kéo thả tương tác, hộp chọn vị trí", "Xuất sắc (5/5)"],
        ["TPACK Toàn diện", "Tích hợp nhuần nhuyễn Công nghệ - Sư phạm - Nội dung", "Học sinh tự làm thí nghiệm, tự rút ra quy luật tạo ảnh", "Xuất sắc (5/5)"],
    ]
    for j, h in enumerate(tp_headers):
        cell = t_tpack.cell(0, j)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)
        set_cell_shading(cell, "F1F5F9")
        set_cell_border(cell, top={'val': 'single', 'sz': 8, 'color': '0d4a7a'}, bottom={'val': 'single', 'sz': 8, 'color': '0d4a7a'}, left={'val': 'single', 'sz': 4, 'color': 'cbd5e1'}, right={'val': 'single', 'sz': 4, 'color': 'cbd5e1'})

    for i, row_data in enumerate(tp_data):
        for j, val in enumerate(row_data):
            cell = t_tpack.cell(i + 1, j)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (j == 0 or j == 3) else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.size = Pt(10)
            if j == 3:
                r.bold = True
                r.font.color.rgb = RGBColor(0x16, 0xa3, 0x4a)
            set_cell_border(cell, top={'val': 'single', 'sz': 4, 'color': 'cbd5e1'}, bottom={'val': 'single', 'sz': 4, 'color': 'cbd5e1'}, left={'val': 'single', 'sz': 4, 'color': 'cbd5e1'}, right={'val': 'single', 'sz': 4, 'color': 'cbd5e1'})

    # Mô hình SAMR
    add_h1("3. Phân tích học liệu số theo mô hình SAMR")
    p_samr_intro = doc.add_paragraph()
    p_samr_intro.add_run(
        "Mô hình SAMR (Puentedura, 2006) đánh giá mức độ công nghệ làm thay đổi bản chất của hoạt động dạy học qua 4 cấp độ: "
        "Thay thế (Substitution) -> Tăng cường (Augmentation) -> Điều chỉnh (Modification) -> Tái định nghĩa (Redefinition). "
        "Đối với học liệu mô phỏng của Nhóm Natural, mức độ chuyển đổi sư phạm không cố định mà có thể đạt từ cấp độ 1 lên đến cấp độ 4 tùy thuộc vào cách tổ chức của giáo viên:"
    )

    add_bullet("Công nghệ đóng vai trò thay thế công cụ truyền thống mà không có sự thay đổi chức năng. Ví dụ: Giáo viên dùng máy chiếu mở website mô phỏng chiếu hình ảnh thấu kính lên màn hình thay cho việc vẽ phấn trên bảng. Học sinh vẫn quan sát thụ động.", "• Cấp độ 1: Thay thế (Substitution) - ")
    add_bullet("Công nghệ thay thế trực tiếp nhưng có sự cải tiến chức năng quan trọng. Mô phỏng cho phép người học trực tiếp tương tác: bật/tắt từng tia sáng, đổi thấu kính hội tụ/phân kì, kéo thay đổi tiêu cự f và vị trí vật d để nhận kết quả tức thời. Đường nét đứt kéo dài của tia ló giúp học sinh thấy rõ điều mà bảng phấn hay hình vẽ tĩnh không thể hiện được.", "• Cấp độ 2: Tăng cường (Augmentation) - ")
    add_bullet("Công nghệ cho phép tái thiết kế đáng kể nhiệm vụ học tập. Thay vì giáo viên giảng giải quy tắc tạo ảnh, học sinh làm việc nhóm thực hiện chu trình POE: dự đoán -> dùng mô phỏng kiểm chứng -> thảo luận giải thích quy luật. Học sinh tự phát hiện quy luật thấu kính phân kì luôn cho ảnh ảo nhỏ hơn vật, biến giờ học thành buổi nghiên cứu khoa học thực thụ.", "• Cấp độ 3: Điều chỉnh (Modification) - ")
    add_bullet("Công nghệ tạo ra những nhiệm vụ học tập hoàn toàn mới mà trước đây không thể thực hiện được trong lớp học truyền thống. Học sinh có thể ghi hình lại màn hình thao tác mô phỏng kèm giọng thuyết minh giải thích hiện tượng quang học để nộp sản phẩm số; hệ thống Phiếu học tập điện tử cho phép đồng bộ dữ liệu bài nộp theo thời gian thực về máy giáo viên.", "• Cấp độ 4: Tái định nghĩa (Redefinition) - ")

    # Bảng Ma trận SAMR
    p_samr_note = doc.add_paragraph()
    r_sn = p_samr_note.add_run("Bảng 2.2: Đánh giá cấp độ chuyển đổi sư phạm của học liệu số theo mô hình SAMR")
    r_sn.italic = True
    r_sn.font.size = Pt(11)

    t_samr = doc.add_table(rows=5, cols=4)
    t_samr.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_samr.autofit = False
    col_w_sm = [Inches(1.2), Inches(1.5), Inches(2.2), Inches(1.8)]
    for row in t_samr.rows:
        for idx, w in enumerate(col_w_sm):
            row.cells[idx].width = w

    sm_headers = ["Cấp độ SAMR", "Mục tiêu chuyển đổi", "Hoạt động dạy học tương ứng", "Minh chứng trên Website"]
    sm_data = [
        ["1. Substitution (Thay thế)", "Thay thế bảng vẽ truyền thống", "Giáo viên trình chiếu đường truyền tia sáng và ảnh vật thay cho vẽ bảng phấn", "Hình ảnh quang học chuẩn xác, màu sắc rõ ràng"],
        ["2. Augmentation (Tăng cường)", "Tăng cường tính tương tác trực quan", "Học sinh tự tay kéo thả nguồn S, chỉnh f, d, h; quan sát đường nét đứt của ảnh ảo", "Phản hồi động tức thời, thước đo cm, Readout thông số"],
        ["3. Modification (Điều chỉnh)", "Tái thiết kế nhiệm vụ học tập", "Tổ chức hoạt động nhóm theo chu trình POE, học sinh tự khám phá và so sánh TKHT vs TKPK", "Hộp vị trí nhanh (d>2f, d=2f...), nút ẩn/hiện kết luận"],
        ["4. Redefinition (Tái định nghĩa)", "Tạo ra nhiệm vụ học tập số mới", "Học sinh xây dựng video thuyết minh hiện tượng quang học, nộp bài kiểm tra trực tuyến thời gian thực", "Kênh nộp bài Real-time Cloud, trạm QR Code điện tử"],
    ]
    for j, h in enumerate(sm_headers):
        cell = t_samr.cell(0, j)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)
        set_cell_shading(cell, "F1F5F9")
        set_cell_border(cell, top={'val': 'single', 'sz': 8, 'color': '0d4a7a'}, bottom={'val': 'single', 'sz': 8, 'color': '0d4a7a'}, left={'val': 'single', 'sz': 4, 'color': 'cbd5e1'}, right={'val': 'single', 'sz': 4, 'color': 'cbd5e1'})

    for i, row_data in enumerate(sm_data):
        for j, val in enumerate(row_data):
            cell = t_samr.cell(i + 1, j)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j == 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.size = Pt(10)
            if j == 0:
                r.bold = True
                r.font.color.rgb = RGBColor(0xb9, 0x1c, 0x1c)
            set_cell_border(cell, top={'val': 'single', 'sz': 4, 'color': 'cbd5e1'}, bottom={'val': 'single', 'sz': 4, 'color': 'cbd5e1'}, left={'val': 'single', 'sz': 4, 'color': 'cbd5e1'}, right={'val': 'single', 'sz': 4, 'color': 'cbd5e1'})

    # Mô hình Triple E
    add_h1("4. Phân tích học liệu số theo khung đánh giá TRIPLE E (Lượng hóa điểm số)")
    p_eee_intro = doc.add_paragraph()
    p_eee_intro.add_run(
        "Khung đánh giá Triple E Framework do TS. Liz Kolb (Đại học Michigan, 2017) phát triển nhằm đánh giá hiệu quả thực chất của công nghệ đối với "
        "kết quả học tập của học sinh, tập trung vào 3 yếu tố then chốt: Gắn kết (Engagement) -> Nâng cao (Enhancement) -> Mở rộng (Extension). "
        "Mỗi yếu tố được đánh giá qua 3 câu hỏi định lượng (mỗi câu tối đa 2 điểm, tổng thang đo 18 điểm)."
    )

    add_h2("4.1. Gắn kết học tập (Engagement) - Đạt 6/6 điểm:")
    add_bullet("Học sinh có tập trung vào mục tiêu bài học không? (2/2 điểm) -> Công cụ tập trung tuyệt đối vào đường truyền tia sáng và quy luật tạo ảnh, không có quảng cáo, pop-up hay các yếu tố gây xao nhãng.", "• ")
    add_bullet("Công nghệ có giúp giảm thiểu xao nhãng và gia tăng chú ý không? (2/2 điểm) -> Hiệu ứng âm thanh tinh tế và giao diện tối quang học giữ trọn vẹn sự chú ý của học sinh vào màn hình thí nghiệm.", "• ")
    add_bullet("Học sinh có chuyển dịch từ tiếp nhận thụ động sang học tập chủ động không? (2/2 điểm) -> Học sinh đóng vai trò nhà nghiên cứu, trực tiếp cầm nắm vật sáng và điều khiển các thông số thí nghiệm.", "• ")

    add_h2("4.2. Nâng cao hiệu quả học tập (Enhancement) - Đạt 6/6 điểm:")
    add_bullet("Công nghệ có hỗ trợ học sinh phát triển tư duy bậc cao và hiểu sâu khái niệm trừu tượng không? (2/2 điểm) -> Giúp học sinh phân tích, so sánh và giải quyết trọn vẹn rào cản nhận thức về ảnh ảo và tiêu điểm ảo.", "• ")
    add_bullet("Công nghệ có cung cấp các hỗ trợ/giàn giáo học tập mà phương tiện truyền thống không làm được không? (2/2 điểm) -> Hệ thống đo đạc tự động (Readout card) hiển thị tức thời d, d', h, h' và tự động phân loại tính chất ảnh giúp học sinh tự kiểm chứng và đối chiếu.", "• ")
    add_bullet("Công nghệ có giúp học sinh kết nối kiến thức để vận dụng vào kỹ năng dựng hình thực tế không? (2/2 điểm) -> Mô phỏng bám sát quy tắc vẽ ảnh trong SGK, giúp học sinh tự tin chuyển giao kiến thức sang bài vẽ trên giấy.", "• ")

    add_h2("4.3. Mở rộng học tập (Extension) - Đạt 5/6 điểm:")
    add_bullet("Công nghệ có tạo cơ hội để học sinh học tập ngoài lớp học không? (2/2 điểm) -> Trang web triển khai trên đám mây GitHub Pages, học sinh có thể tự học, làm lại thí nghiệm mọi lúc mọi nơi trên điện thoại.", "• ")
    add_bullet("Công nghệ có kết nối kiến thức với đời sống thực tế không? (2/2 điểm) -> Trường hợp d < f kết nối trực tiếp với kính lúp; trường hợp d > 2f kết nối với máy ảnh kỹ thuật số.", "• ")
    add_bullet("Công nghệ có giúp xây dựng kỹ năng mềm và kỹ năng số không? (1/2 điểm) -> Cần có sự tổ chức nhiệm vụ nhóm của giáo viên để phát triển kỹ năng giao tiếp và cộng tác số hoàn thiện hơn.", "• ")

    # Bảng Ma trận Triple E
    p_eee_note = doc.add_paragraph()
    r_en = p_eee_note.add_run("Bảng 2.3: Bảng lượng hóa điểm số chi tiết học liệu theo khung Triple E Framework (Liz Kolb)")
    r_en.italic = True
    r_en.font.size = Pt(11)

    t_eee = doc.add_table(rows=13, cols=4)
    t_eee.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_eee.autofit = False
    col_w_ee = [Inches(1.3), Inches(2.3), Inches(2.3), Inches(0.8)]
    for row in t_eee.rows:
        for idx, w in enumerate(col_w_ee):
            row.cells[idx].width = w

    ee_headers = ["Thành tố Triple E", "Câu hỏi đánh giá chuẩn của Liz Kolb", "Minh chứng trong học liệu của Nhóm Natural", "Điểm số"]
    ee_data = [
        ["Engagement (E1)", "Tập trung học sinh vào mục tiêu học tập?", "Giao diện không quảng cáo, tập trung hoàn toàn vào thí nghiệm", "2 / 2"],
        ["Engagement (E2)", "Giảm thiểu yếu tố gây xao nhãng?", "Âm thanh phản hồi trực quan, chế độ nền tối chuyên nghiệp", "2 / 2"],
        ["Engagement (E3)", "Chuyển từ học thụ động sang chủ động?", "Tự tay kéo thả đỉnh B của vật, đổi tiêu cự và vị trí nguồn sáng", "2 / 2"],
        ["Tổng Engagement", "Mức độ Gắn kết của học sinh với bài học", "Đạt mức gắn kết tối đa", "6 / 6"],
        ["Enhancement (E1)", "Hiểu sâu sắc khái niệm trừu tượng?", "Trực quan hóa tiêu điểm ảo F và đường kéo dài nét đứt", "2 / 2"],
        ["Enhancement (E2)", "Cung cấp giàn giáo học tập ưu việt?", "Bảng Readout tức thời tự động tính d', h', phân loại ảnh", "2 / 2"],
        ["Enhancement (E3)", "Hỗ trợ kết nối và vận dụng kiến thức?", "Kết nối trực tiếp quy tắc mô phỏng với kỹ năng dựng hình SGK", "2 / 2"],
        ["Tổng Enhancement", "Mức độ Nâng cao hiệu quả bài học", "Đạt mức nâng cao tối đa", "6 / 6"],
        ["Extension (E1)", "Cơ hội học tập ngoài giờ lên lớp?", "Web online chạy 24/7 trên máy tính, điện thoại qua GitHub Pages", "2 / 2"],
        ["Extension (E2)", "Kết nối với hiện tượng thực tế đời sống?", "Giải thích nguyên lý kính lúp (d<f), máy ảnh (d>2f)", "2 / 2"],
        ["Extension (E3)", "Phát triển kỹ năng mềm và kỹ năng số?", "Học sinh thực hành thao tác số, cần thêm hướng dẫn nhóm của GV", "1 / 2"],
        ["TỔNG ĐIỂM TRIPLE E", "XẾP LOẠI TOÀN DIỆN (Thang điểm 18)", "MỨC ĐỘ CAO NHẤT: EXCEPTIONAL CONNECTION TO LEARNING", "17 / 18"],
    ]
    for j, h in enumerate(ee_headers):
        cell = t_eee.cell(0, j)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)
        set_cell_shading(cell, "F1F5F9")
        set_cell_border(cell, top={'val': 'single', 'sz': 8, 'color': '0d4a7a'}, bottom={'val': 'single', 'sz': 8, 'color': '0d4a7a'}, left={'val': 'single', 'sz': 4, 'color': 'cbd5e1'}, right={'val': 'single', 'sz': 4, 'color': 'cbd5e1'})

    for i, row_data in enumerate(ee_data):
        is_summary = (i in [3, 7, 11])
        for j, val in enumerate(row_data):
            cell = t_eee.cell(i + 1, j)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (j == 0 or j == 3) else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.size = Pt(9.5)
            if is_summary:
                r.bold = True
                set_cell_shading(cell, "FEF3C7" if i == 11 else "F3F4F6")
                if j == 3:
                    r.font.color.rgb = RGBColor(0xb9, 0x1c, 0x1c)
            elif j == 3:
                r.bold = True
                r.font.color.rgb = RGBColor(0x16, 0xa3, 0x4a)
            set_cell_border(cell, top={'val': 'single', 'sz': 4, 'color': 'cbd5e1'}, bottom={'val': 'single', 'sz': 4, 'color': 'cbd5e1'}, left={'val': 'single', 'sz': 4, 'color': 'cbd5e1'}, right={'val': 'single', 'sz': 4, 'color': 'cbd5e1'})

    # Quy trình tổ chức dạy học 4 bước
    add_h1("5. Đề xuất quy trình tổ chức hoạt động dạy học 4 bước chuẩn mực sư phạm")
    p_qt = doc.add_paragraph()
    p_qt.add_run(
        "Nhằm khai thác tối đa tiềm năng của học liệu số và khắc phục triệt để 4 lỗi thường gặp trong đổi mới phương pháp dạy học, "
        "nhóm đề xuất tiến trình dạy học gồm 4 bước dựa trên chu trình POE kết hợp hoạt động nhóm:"
    )

    add_bullet("Giáo viên nêu tình huống có vấn đề: \"Khi một tia sáng tới song song với trục chính chiếu qua thấu kính phân kì, tia ló sẽ đi như thế nào?\" Học sinh suy nghĩ độc lập và ghi dự đoán vào Phiếu học tập trước khi mở mô phỏng.", "• Bước 1: Dự đoán (Predict) - ")
    add_bullet("Học sinh truy cập mô phỏng trên thiết bị, tự tay kích hoạt từng tia sáng hoặc kéo thả vị trí vật sáng, đối chiếu hiện tượng diễn ra với dự đoán ban đầu, ghi nhận các số liệu và đặc điểm ảnh.", "• Bước 2: Quan sát mô phỏng và thu thập số liệu (Observe) - ")
    add_bullet("Các nhóm học sinh thảo luận, so sánh hiện tượng giữa thấu kính hội tụ và phân kì, giải thích vì sao ảnh ảo lại cùng chiều và nhỏ hơn vật. Đại diện nhóm trình bày, giáo viên chuẩn hóa kiến thức.", "• Bước 3: Thảo luận và rút ra kết luận (Explain) - ")
    add_bullet("Học sinh vận dụng quy tắc vừa học để vẽ ảnh của vật sáng AB trên giấy kẻ ô; làm bài tập liên hệ thực tế về kính lúp, máy ảnh hoặc hoàn thành Phiếu học tập điện tử.", "• Bước 4: Vận dụng và đánh giá (Apply & Assess) - ")

    # Kết luận chung
    add_h1("6. Kết luận và khuyến nghị sư phạm")
    p_kl = doc.add_paragraph()
    p_kl.add_run(
        "Học liệu số mô phỏng Bài 8: Thấu kính do Nhóm Natural phát triển là một công cụ hỗ trợ dạy học có giá trị cao, được thiết kế đồng bộ "
        "về cả nội dung khoa học, phương pháp sư phạm và kỹ thuật lập trình hiện đại. Kết quả đánh giá cho thấy học liệu đáp ứng xuất sắc mô hình TPACK, "
        "có khả năng nâng cấp hoạt động học lên cấp độ Modification và Redefinition trong thang SAMR, và đạt 17/18 điểm (Exceptional connection to learning) "
        "theo thang Triple E.\n\n"
        "Khuyến nghị đối với giáo viên: Không nên biến buổi học thành giờ trình chiếu thụ động. Giáo viên cần thiết kế phiếu học tập định hướng rõ ràng, "
        "luôn duy trì bước Dự đoán (P) trước khi cho học sinh thao tác trên mô phỏng, và kết hợp hài hòa giữa thực hành ảo với kỹ năng vẽ hình thực tế trên giấy "
        "để đạt hiệu quả giáo dục toàn diện nhất."
    )

    # Tài liệu tham khảo
    add_h1("TÀI LIỆU THAM KHẢO")
    add_bullet("Bộ Giáo dục và Đào tạo. (2018). Chương trình Giáo dục phổ thông 2018 - Môn Khoa học tự nhiên. Hà Nội.", "1. ")
    add_bullet("Kolb, L. (2017). Learning first, technology second: The educator's guide to the Triple E Framework. International Society for Technology in Education (ISTE).", "2. ")
    add_bullet("Mishra, P., & Koehler, M. J. (2006). Technological pedagogical content knowledge: A framework for teacher knowledge. Teachers College Record, 108(6), 1017-1054.", "3. ")
    add_bullet("Nhóm Natural. (2026). Website mô phỏng thí nghiệm tương tác Bài 8: Thấu kính (KHTN 9). https://minhlfc.github.io/nhom5-natural-thau-kinh/", "4. ")
    add_bullet("Puentedura, R. R. (2006). Transformation, technology, and education. Presentation at the Maine Department of Education.", "5. ")
    add_bullet("University of Calgary, Taylor Institute for Teaching and Learning. (2022). SAMR and TPACK: Two models to help with integrating technology into courses.", "6. ")

    # Save DOCX
    saved_paths = []
    try:
        doc.save(DOCX_OUT)
        saved_paths.append(DOCX_OUT)
        print(f"DOCX created: {DOCX_OUT}")
    except PermissionError:
        print(f"DOCX chính đang bị khóa bởi Word.")

    try:
        doc.save(DOCX_ALT)
        saved_paths.append(DOCX_ALT)
        print(f"DOCX bản mới nhất lưu tại: {DOCX_ALT}")
    except PermissionError:
        pass

def build_html_for_pdf():
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Báo Cáo Học Liệu Số & Mô Phỏng Thí Nghiệm - Bài 8: Thấu Kính - Nhóm Natural</title>
  <style>
    @page {{
      size: A4;
      margin: 18mm 16mm 18mm 18mm;
      @bottom-center {{
        content: counter(page);
        font-family: 'Times New Roman', serif;
        font-size: 11pt;
        color: #555;
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      font-family: 'Times New Roman', Times, serif;
      font-size: 13pt;
      line-height: 1.25;
      color: #111827;
      margin: 0;
      padding: 0;
      background: #fff;
    }}
    .header-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 12px;
    }}
    .header-table td {{
      vertical-align: middle;
      border: none;
      padding: 0;
    }}
    .logo-img {{
      max-width: 220px;
      height: auto;
      display: block;
    }}
    .school-info {{
      text-align: right;
    }}
    .school-name {{
      font-size: 11pt;
      font-weight: bold;
      color: #0d4a7a;
      text-transform: uppercase;
    }}
    .group-name {{
      font-size: 11pt;
      font-weight: bold;
      color: #d63a3f;
      margin-top: 2px;
    }}
    .members {{
      font-size: 9.5pt;
      color: #556677;
      margin-top: 2px;
    }}
    .title-box {{
      text-align: center;
      margin: 14px 0 16px 0;
    }}
    .main-title {{
      font-size: 16pt;
      font-weight: bold;
      color: #0d4a7a;
      text-transform: uppercase;
      margin: 0 0 4px 0;
    }}
    .lesson-title {{
      font-size: 18pt;
      font-weight: bold;
      color: #d63a3f;
      text-transform: uppercase;
      margin: 0 0 4px 0;
    }}
    .meta-title {{
      font-size: 12pt;
      font-style: italic;
      color: #334455;
      margin: 0;
    }}
    .part-title {{
      font-size: 15pt;
      font-weight: bold;
      color: #b91c1c;
      text-transform: uppercase;
      border-bottom: 2px solid #b91c1c;
      padding-bottom: 4px;
      margin: 22px 0 12px 0;
      page-break-after: avoid;
    }}
    h1 {{
      font-size: 14pt;
      font-weight: bold;
      color: #0d4a7a;
      margin: 16px 0 6px 0;
      page-break-after: avoid;
    }}
    h2 {{
      font-size: 13pt;
      font-weight: bold;
      color: #10233a;
      margin: 10px 0 4px 0;
      page-break-after: avoid;
    }}
    h3 {{
      font-size: 13pt;
      font-weight: bold;
      color: #111827;
      margin: 8px 0 4px 0;
      page-break-after: avoid;
    }}
    .step-title {{
      font-size: 13pt;
      font-weight: bold;
      color: #b91c1c;
      margin: 12px 0 4px 0;
      page-break-after: avoid;
    }}
    p {{
      margin: 0 0 5px 0;
      text-align: justify;
    }}
    ul {{
      margin: 4px 0 6px 20px;
      padding: 0;
    }}
    li {{
      margin-bottom: 4px;
      text-align: justify;
    }}
    .img-wrap {{
      text-align: center;
      margin: 8px 0 10px 0;
      page-break-inside: avoid;
    }}
    .img-wrap img {{
      max-width: 90%;
      height: auto;
      border: 1px solid #cbd5e1;
      border-radius: 4px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }}
    .img-wrap.small img {{
      max-width: 65%;
    }}
    .caption {{
      font-size: 10.5pt;
      font-style: italic;
      color: #556677;
      margin-top: 4px;
      text-align: center;
    }}
    table.data-table {{
      width: 100%;
      border-collapse: collapse;
      margin: 8px 0 14px 0;
      page-break-inside: avoid;
    }}
    table.data-table th, table.data-table td {{
      border: 1px solid #cbd5e1;
      padding: 6px 8px;
      font-size: 10.5pt;
    }}
    table.data-table th {{
      background: #f1f5f9;
      color: #0d4a7a;
      font-weight: bold;
      text-align: center;
    }}
    .text-center {{ text-align: center; }}
    .badge-real {{ color: #16a34a; font-weight: bold; }}
    .badge-virt {{ color: #d97706; font-weight: bold; }}
    .highlight-score {{ color: #b91c1c; font-weight: bold; }}
    .summary-row {{ background: #fef3c7; font-weight: bold; }}
    .link-code {{
      background: #f3f4f6;
      padding: 1px 4px;
      border-radius: 3px;
      font-family: Consolas, monospace;
      font-size: 11pt;
      color: #0d4a7a;
    }}
  </style>
</head>
<body>

  <!-- Header -->
  <table class="header-table">
    <tr>
      <td style="width: 38%;">
        <img src="{LOGO_PATH}" class="logo-img" alt="Logo HCMUE">
      </td>
      <td style="width: 62%;" class="school-info">
        <div class="school-name">Trường Đại học Sư phạm TP. Hồ Chí Minh</div>
        <div class="group-name">Nhóm Natural · Khoa học tự nhiên 9</div>
        <div class="members">Nguyễn Thị Ý Như · Đỗ Văn Nhật Minh · Nguyễn Huyền Trang · Nguyễn Khánh Linh</div>
      </td>
    </tr>
  </table>

  <!-- Title -->
  <div class="title-box">
    <div class="main-title">Báo Cáo Học Liệu Số & Mô Phỏng Thí Nghiệm</div>
    <div class="lesson-title">Bài 8: Thấu Kính (KHTN 9)</div>
    <div class="meta-title">Học liệu số trực tuyến kết hợp đánh giá theo các mô hình TPACK, SAMR và TRIPLE E — Thời gian: 2 tiết</div>
  </div>

  <!-- PHẦN I -->
  <div class="part-title">PHẦN I: HƯỚNG DẪN THỰC HÀNH MÔ PHỎNG THÍ NGHIỆM</div>

  <h1>1. Thí nghiệm tìm hiểu đường truyền của các tia sáng đặc biệt qua thấu kính.</h1>
  
  <h2>1.1. Mục tiêu:</h2>
  <ul>
    <li>Trình bày và mô tả được đường truyền của 3 tia sáng đặc biệt (tia tới đi qua quang tâm O, tia tới song song với trục chính cho tia ló đi qua F' hoặc có đường kéo dài qua F', tia tới đi qua F hoặc có đường kéo dài hướng tới F cho tia ló song song trục chính) khi qua thấu kính hội tụ và thấu kính phân kì thông qua quan sát mô phỏng.</li>
    <li>Rút ra được quy luật hội tụ của chùm tia ló đối với thấu kính hội tụ và tính chất phân kì của chùm tia ló đối với thấu kính phân kì khi chùm tia tới song song với trục chính.</li>
  </ul>

  <h2>1.2. Dụng cụ, thiết bị và các bước tiến hành.</h2>
  <h3>1.2.1. Dụng cụ, thiết bị và giải thích về công cụ hỗ trợ.</h3>
  <ul>
    <li><b>Thiết bị phần cứng:</b> Máy tính để bàn, máy tính xách tay hoặc điện thoại thông minh có kết nối Internet.</li>
    <li><b>Phần mềm mô phỏng:</b> Phần mềm mô phỏng Thấu kính trực tuyến (Nhóm Natural - KHTN 9, Trường ĐHSP TP.HCM).</li>
  </ul>

  <p><b>★ Phân tích điểm khó của nội dung kiến thức trong bài học:</b></p>
  <ul>
    <li>Trong thực tế phòng thí nghiệm phổ thông, đường truyền của các tia sáng trong không khí rất mờ nhạt, tán xạ yếu và cực kì khó quan sát nếu phòng học không đủ tối. Việc bố trí nguồn sáng, căn chỉnh góc nghiêng và lắp đặt khe hẹp để tạo chùm tia laser/halogen phẳng mất rất nhiều thời gian tiết học.</li>
    <li>Đặc biệt đối với thấu kính phân kì, khái niệm <i>"tiêu điểm ảo F"</i> và <i>"đường kéo dài của tia ló"</i> là một rào cản nhận thức rất lớn đối với học sinh lớp 9. Trong thí nghiệm thật, mắt học sinh không thể nhìn thấy đường kéo dài nét đứt cắt nhau tại tiêu điểm ở phía trước thấu kính, dẫn đến việc các em phải học vẹt định nghĩa trừu tượng mà không hiểu được bản chất hiện tượng vật lí.</li>
  </ul>

  <p><b>★ Vai trò và lý do lựa chọn công cụ mô phỏng tương tác (Khắc phục hạn chế của video/thí nghiệm thường):</b></p>
  <ul>
    <li>Mô phỏng tương tác không đơn thuần chỉ để minh họa tĩnh hay thay thế bằng một đoạn video xem thụ động: Học sinh được trực tiếp cầm nắm, kéo rê nguồn sáng S đến bất kì toạ độ nào trong không gian, lập tức nhận thấy đường truyền tia sáng và tia ló biến đổi tương ứng theo thời gian thực (real-time visual feedback).</li>
    <li>Trực quan hóa "cái vô hình": Công cụ mô phỏng cho phép hiển thị các đường kéo dài tia sáng bằng nét đứt sắc nét, giúp học sinh tận mắt chứng kiến giao điểm ảo của chùm tia phân kì tại tiêu điểm F, giải quyết triệt để điểm nghẽn nhận thức của bài học.</li>
  </ul>

  <p><b>★ Giải thích chi tiết các công cụ hỗ trợ trên giao diện mô phỏng thí nghiệm 1:</b></p>
  <ul>
    <li><b>Hiệu ứng âm thanh đa giác quan (Web Audio API):</b> Tích hợp phản hồi âm thanh chuẩn mực khi bật/tắt tia sáng, âm thanh chuyển động của tia sáng và âm thanh chúc mừng khi hoàn thành, tạo môi trường học tập sống động, kích thích sự tập trung và hứng thú của học sinh.</li>
    <li><b>Chế độ hiển thị Sáng / Tối (Light / Dark mode):</b> Nút chuyển đổi linh hoạt chế độ sáng (phù hợp khi giáo viên trình chiếu trên máy chiếu lớp học) và chế độ tối quang học (tạo cảm giác như đang ở trong phòng thí nghiệm quang học chuyên nghiệp, chống mỏi mắt khi học sinh tự học trên điện thoại cá nhân).</li>
    <li><b>Nút "▶ Chiếu tia sáng" (Play Animation):</b> Tạo hoạt họa chùm photon chuyển động từ nguồn phát tới thấu kính rồi mới khúc xạ thành tia ló. Công cụ này giúp học sinh nhận thức sâu sắc quan hệ nhân quả vật lí: có tia tới đến thấu kính trước, sau đó mới sinh ra tia ló sau thấu kính.</li>
    <li><b>Nút "Hiện kết luận" (Đối chiếu sư phạm):</b> Ban đầu kết luận được ẩn đi để học sinh tự thảo luận và rút ra quy tắc; chỉ khi học sinh đã nêu ý kiến thì giáo viên mới mở nút này để cả lớp cùng đối chiếu, khắc phục lỗi tiếp nhận thụ động.</li>
    <li><b>Áp dụng chu trình POE (Dự đoán - Quan sát - Giải thích):</b> Nhằm tránh lỗi <i>"Hỏi sau khi đã thấy kết quả"</i>, trước khi bật từng tia sáng trên mô phỏng, giáo viên luôn yêu cầu học sinh làm bước Dự đoán (P) xem tia ló sẽ đi đâu, sau đó mới bấm chọn tia trên mô phỏng để Quan sát (O) và Giải thích (E).</li>
  </ul>

  <h3>1.2.2. Các bước tiến hành.</h3>
  <div class="step-title">Bước 1: Truy cập trang web mô phỏng và mở tab "TN1: Tia sáng"</div>
  <ul>
    <li>Đường link truy cập: <span class="link-code">https://minhlfc.github.io/nhom5-natural-thau-kinh/#tn1</span></li>
    <li>Sau khi truy cập vào đường link, nhấp chọn mục <b>"TN1: Tia sáng"</b> trên thanh menu ngang để hiển thị giao diện phòng thí nghiệm ảo chuẩn bị thực hiện mô phỏng.</li>
  </ul>

  <div class="img-wrap">
    <img src="doc_images/01_tn1_overview.png" alt="Giao diện TN1">
    <div class="caption">Hình 1.1: Toàn cảnh giao diện thí nghiệm đường truyền các tia sáng đặc biệt qua thấu kính</div>
  </div>

  <p><b>Cần nắm rõ các phần trong giao diện mô phỏng thí nghiệm:</b></p>
  <ul>
    <li><b>Khu vực sân khấu quang học:</b> Thể hiện trục chính thấu kính, quang tâm O, các tiêu điểm F và F', nguồn sáng điểm S và đường truyền tia sáng màu sắc trực quan.</li>
    <li><b>Khu vực lựa chọn loại thấu kính:</b> Có thể chuyển đổi linh hoạt giữa <i>"Hội tụ"</i> và <i>"Phân kì"</i>.</li>
  </ul>

  <div class="img-wrap small">
    <img src="doc_images/02_tn1_controls.png" alt="Bảng điều khiển TN1">
    <div class="caption">Hình 1.2: Bảng điều khiển chọn loại thấu kính, bật/tắt tia sáng và điều chỉnh tiêu cự f</div>
  </div>

  <ul>
    <li><b>Khu vực chọn tia tới đặc biệt:</b> Cho phép bật/tắt độc lập hoặc đồng thời 3 tia sáng (Tia qua quang tâm O - màu cam, Tia song song trục chính - màu lam, Tia qua tiêu điểm - màu lục).</li>
    <li><b>Thanh chỉnh tiêu cự f:</b> Thay đổi tiêu cự từ 6 cm đến 20 cm để khảo sát sự dịch chuyển của các tiêu điểm.</li>
    <li><b>Các nút thao tác nhanh:</b> Nút <i>"▶ Chiếu tia sáng"</i> (chạy hoạt họa tia sáng), <i>"↺ Đặt lại"</i> (khôi phục trạng thái ban đầu), <i>"Hiện kết luận"</i> (đối chiếu quy tắc).</li>
  </ul>

  <div class="step-title">Bước 2: Thực hiện quan sát đường truyền của các tia sáng đặc biệt qua Thấu kính hội tụ.</div>
  <p>Tại bảng điều khiển, chọn loại thấu kính là <b>"Hội tụ"</b>. Đặt nguồn sáng S phía trước thấu kính và lần lượt quan sát từng tia sáng:</p>
  <ul>
    <li><b>1. Tia tới đi qua quang tâm O:</b> Tích chọn duy nhất ô <i>"Tia đi qua quang tâm O"</i>. Quan sát thấy tia ló tiếp tục truyền thẳng theo phương của tia tới mà không hề bị đổi hướng.</li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/03_tn1_ht_ray_o.png" alt="Tia qua quang tâm O - TKHT">
    <div class="caption">Hình 1.3: Tia tới đi qua quang tâm O của thấu kính hội tụ truyền thẳng</div>
  </div>

  <ul>
    <li><b>2. Tia tới song song với trục chính:</b> Tích chọn ô <i>"Tia song song với trục chính"</i>. Quan sát thấy tia ló bị khúc xạ gập xuống và đi qua tiêu điểm chính F' ở phía sau thấu kính.</li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/04_tn1_ht_ray_p.png" alt="Tia song song trục chính - TKHT">
    <div class="caption">Hình 1.4: Tia tới song song với trục chính cho tia ló đi qua tiêu điểm chính F'</div>
  </div>

  <ul>
    <li><b>3. Tia tới đi qua tiêu điểm chính F:</b> Tích chọn ô <i>"Tia đi qua tiêu điểm chính F"</i>. Quan sát thấy tia ló sau khi qua thấu kính trở nên song song với trục chính.</li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/05_tn1_ht_ray_f.png" alt="Tia qua tiêu điểm F - TKHT">
    <div class="caption">Hình 1.5: Tia tới đi qua tiêu điểm vật chính F cho tia ló song song trục chính</div>
  </div>

  <ul>
    <li><b>4. Chiếu đồng thời cả 3 tia sáng đặc biệt:</b> Tích chọn cả 3 tia sáng, kéo thay đổi vị trí nguồn sáng S hoặc thay đổi tiêu cự f. Quan sát thấy cả 3 tia ló đều cùng cắt nhau tại điểm ảnh thật S' của điểm sáng S.</li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/06_tn1_ht_all_rays.png" alt="Cả 3 tia sáng - TKHT">
    <div class="caption">Hình 1.6: Cả 3 tia ló của thấu kính hội tụ cùng hội tụ tại điểm ảnh S'</div>
  </div>

  <div class="step-title">Bước 3: Thực hiện quan sát đường truyền của các tia sáng đặc biệt qua Thấu kính phân kì.</div>
  <p>Tại thanh điều khiển, chuyển sang chọn loại thấu kính là <b>"Phân kì"</b>. Lần lượt khảo sát đường truyền của 3 tia sáng đặc biệt:</p>
  <ul>
    <li><b>1. Tia tới đi qua quang tâm O:</b> Tích chọn ô <i>"Tia đi qua quang tâm O"</i>. Tia ló tiếp tục truyền thẳng, tương tự như thấu kính hội tụ.</li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/07_tn1_pk_ray_o.png" alt="Tia qua quang tâm O - TKPK">
    <div class="caption">Hình 1.7: Tia tới đi qua quang tâm O của thấu kính phân kì truyền thẳng</div>
  </div>

  <ul>
    <li><b>2. Tia tới song song với trục chính:</b> Tích chọn ô <i>"Tia song song với trục chính"</i>. Quan sát thấy tia ló bị loe rộng ra (phân kì), đường kéo dài của tia ló (nét đứt) đi qua tiêu điểm ảnh chính F' ở phía trước thấu kính.</li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/08_tn1_pk_ray_p.png" alt="Tia song song trục chính - TKPK">
    <div class="caption">Hình 1.8: Tia tới song song trục chính cho tia ló có đường kéo dài đi qua tiêu điểm ảnh F'</div>
  </div>

  <ul>
    <li><b>3. Tia tới có đường kéo dài hướng tới tiêu điểm vật chính F:</b> Tích chọn ô <i>"Tia có đường kéo dài qua tiêu điểm F"</i>. Tia ló sau khi qua thấu kính trở nên song song với trục chính.</li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/09_tn1_pk_ray_f.png" alt="Tia hướng tới tiêu điểm F - TKPK">
    <div class="caption">Hình 1.9: Tia tới hướng tới tiêu điểm vật F ở sau thấu kính cho tia ló song song trục chính</div>
  </div>

  <ul>
    <li><b>4. Chiếu đồng thời cả 3 tia sáng đặc biệt qua thấu kính phân kì:</b> Quan sát thấy chùm tia ló loe rộng ra, các đường kéo dài của chúng cắt nhau tại điểm ảnh ảo S' ở phía trước thấu kính.</li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/10_tn1_pk_all_rays.png" alt="Cả 3 tia sáng - TKPK">
    <div class="caption">Hình 1.10: Chùm tia ló phân kì có các đường kéo dài cắt nhau tại ảnh ảo S'</div>
  </div>

  <!-- Thí nghiệm 2 -->
  <h1>2. Thí nghiệm mô phỏng về sự tạo ảnh của vật qua thấu kính.</h1>
  
  <h2>2.1. Mục tiêu.</h2>
  <ul>
    <li>Thực hiện thí nghiệm mô phỏng quan sát quá trình dựng ảnh của một vật sáng AB (đoạn thẳng vuông góc với trục chính, A nằm trên trục chính) qua thấu kính hội tụ và thấu kính phân kì.</li>
    <li>Khảo sát, xác định và ghi nhận được đặc điểm của ảnh A'B' (ảnh thật hay ảnh ảo, cùng chiều hay ngược chiều với vật, lớn hơn hay nhỏ hơn vật) ứng với các khoảng cách khác nhau từ vật đến thấu kính (d &gt; 2f, d = 2f, f &lt; d &lt; 2f, d = f, d &lt; f).</li>
  </ul>

  <h2>2.2. Dụng cụ, thiết bị và các bước tiến hành.</h2>
  <h3>2.2.1. Dụng cụ, thiết bị và giải thích về công cụ hỗ trợ.</h3>
  <ul>
    <li><b>Thiết bị phần cứng:</b> Máy tính để bàn, máy tính xách tay hoặc điện thoại có kết nối Internet.</li>
    <li><b>Phần mềm mô phỏng:</b> Phần mềm mô phỏng Thấu kính trực tuyến (Nhóm Natural - KHTN 9, Trường ĐHSP TP.HCM).</li>
  </ul>

  <p><b>★ Phân tích điểm khó của nội dung kiến thức trong bài học:</b></p>
  <ul>
    <li>Khảo sát sự tạo ảnh của thấu kính (đặc biệt là mối liên hệ phụ thuộc giữa vị trí vật d và tính chất ảnh d', h') đòi hỏi sự thay đổi liên tục của vật trên trục chính. Trong thí nghiệm thật, việc dịch chuyển nến/đèn, dịch chuyển thấu kính và màn hứng trên giá quang học rất lề mề, dễ làm lệch trục quang học, ảnh trên màn bị mờ hoặc nhòe khiến học sinh khó xác định ranh giới ảnh rõ nét nhất.</li>
    <li><b>Vấn đề nan giải về ẢNH ẢO:</b> Đối với thấu kính phân kì và trường hợp d &lt; f của thấu kính hội tụ, ảnh tạo bởi thấu kính là ảnh ảo. Ảnh ảo hoàn toàn không hứng được trên màn chắn. Trong giờ học thực tế, học sinh nhìn qua thấu kính chỉ thấy ảnh lơ lửng, không thể đo được khoảng cách d' hay chiều cao h', không xác định được ảnh ảo nằm trước hay sau thấu kính. Đây là một điểm nghẽn nhận thức lớn nhất của học sinh THCS.</li>
  </ul>

  <p><b>★ Vai trò và lý do lựa chọn công cụ mô phỏng tương tác (Khắc phục hạn chế của video/thí nghiệm thường):</b></p>
  <ul>
    <li><b>Vượt trội hoàn toàn so với video thụ động:</b> Thay vì ngồi xem giáo viên thao tác mẫu, từng học sinh được tự do kéo thả đỉnh B của vật sáng AB sang trái/phải, lên/xuống liên tục; ảnh A'B' di chuyển và biến đổi tương ứng theo thời gian thực. Mối quan hệ giữa vật và ảnh trở thành một quy luật liên tục, trực quan thay vì các trường hợp rời rạc học vẹt.</li>
    <li><b>Giải quyết trọn vẹn khái niệm ảnh ảo:</b> Mô phỏng hiển thị đồng thời cả vật thật, ảnh thật (nét liền màu cam), ảnh ảo (nét đứt màu cam) cùng với các đường kéo dài của tia ló, giúp học sinh thấy rõ bản chất tạo ảnh ảo là do đường kéo dài của chùm tia ló cắt nhau.</li>
  </ul>

  <p><b>★ Giải thích chi tiết các công cụ hỗ trợ trên giao diện mô phỏng thí nghiệm 2:</b></p>
  <ul>
    <li><b>Thước đo quang học và hệ toạ độ tự động:</b> Trục chính được chia vạch cm rõ ràng, tự động đánh dấu quang tâm O, các tiêu điểm F, F', các vị trí đặc biệt 2F, 2F' giúp học sinh định lượng chính xác khoảng cách.</li>
    <li><b>Các nút chọn nhanh vị trí chuẩn trong SGK (d &gt; 2f, d = 2f, f &lt; d &lt; 2f, d = f, d &lt; f):</b> Giúp giáo viên và học sinh chuyển đổi ngay lập tức đến các vị trí trọng tâm của chương trình để khảo sát mà không mất thời gian căn chỉnh thủ công.</li>
    <li><b>Bảng đo đạc & tính chất ảnh tức thời (Readout Card):</b> Đóng vai trò như một <i>"trợ lí số thông minh"</i>, tự động tính toán khoảng cách ảnh d', chiều cao ảnh h', độ phóng đại k, đồng thời hiển thị huy hiệu phân loại ảnh (Ảnh thật / Ảnh ảo, Cùng chiều / Ngược chiều, Lớn hơn / Nhỏ hơn / Bằng vật) với màu sắc nổi bật, giúp học sinh tức thời đối chiếu và củng cố kết quả vẽ ảnh.</li>
    <li><b>Áp dụng chu trình POE (Dự đoán - Quan sát - Giải thích):</b> Trước khi nhấp nút vị trí nhanh hoặc kéo vật, giáo viên yêu cầu học sinh ghi nhận dự đoán về đặc điểm ảnh (thật/ảo, chiều, độ lớn), sau đó mới quan sát ảnh trên mô phỏng và giải thích nguyên nhân.</li>
  </ul>

  <h3>2.2.2. Các bước tiến hành.</h3>
  <div class="step-title">Bước 1: Truy cập trang web mô phỏng và mở tab "TN2: Vẽ ảnh"</div>
  <ul>
    <li>Đường link truy cập: <span class="link-code">https://minhlfc.github.io/nhom5-natural-thau-kinh/#tn2</span></li>
    <li>Nhấp chọn mục <b>"TN2: Vẽ ảnh"</b> trên thanh menu để mở không gian thí nghiệm tạo ảnh.</li>
  </ul>

  <div class="img-wrap">
    <img src="doc_images/11_tn2_overview.png" alt="Giao diện TN2">
    <div class="caption">Hình 2.1: Toàn cảnh giao diện thí nghiệm vẽ ảnh của vật qua thấu kính</div>
  </div>

  <p><b>Cần nắm rõ các phần trong giao diện mô phỏng thí nghiệm:</b></p>
  <ul>
    <li><b>Vùng quang học tương tác:</b> Vật sáng AB (mũi tên xanh), ảnh A'B' (mũi tên cam, vẽ nét đứt nếu là ảnh ảo), quang tâm O, tiêu điểm F, F', các tia sáng dựng ảnh xuất phát từ đỉnh B. Học sinh có thể dùng chuột kéo thả trực tiếp đỉnh B của vật sang trái/phải hoặc lên/xuống.</li>
    <li><b>Khu vực bảng điều khiển thông số:</b></li>
  </ul>

  <div class="img-wrap small">
    <img src="doc_images/12_tn2_controls.png" alt="Bảng điều khiển TN2">
    <div class="caption">Hình 2.2: Bảng điều khiển thấu kính, thanh trượt d, f, h và các nút chọn vị trí nhanh</div>
  </div>

  <ul>
    <li>Chọn loại thấu kính: <i>"Hội tụ"</i> hoặc <i>"Phân kì"</i>.</li>
    <li>Thanh trượt tiêu cự f (5 - 18 cm) và chiều cao vật h (2 - 10 cm).</li>
    <li>Các nút chọn vị trí nhanh của vật: <code>d &gt; 2f</code>, <code>d = 2f</code>, <code>f &lt; d &lt; 2f</code>, <code>d = f</code>, <code>d &lt; f</code> giúp quan sát chuẩn xác từng trường hợp trong SGK.</li>
    <li><b>Bảng đo đạc & tính chất ảnh tức thời:</b> Tự động cập nhật khoảng cách ảnh d', chiều cao ảnh h' và hiển thị rõ huy hiệu Ảnh thật/Ảnh ảo, Cùng chiều/Ngược chiều, Độ lớn so với vật.</li>
  </ul>

  <div class="step-title">Bước 2: Khảo sát sự tạo ảnh qua Thấu kính hội tụ khi vật ở các khoảng cách khác nhau.</div>
  <p>Chọn loại thấu kính là <b>"Hội tụ"</b>, cố định tiêu cự f = 10 cm, chiều cao vật h = 5 cm. Tiến hành khảo sát lần lượt 4 trường hợp vị trí của vật:</p>

  <ul>
    <li><b>a) Trường hợp 1: Vật đặt rất xa / ngoài khoảng 2f (d &gt; 2f, chọn d = 25 cm):</b>
      <br>Nhấp nút vị trí nhanh <i>"d &gt; 2f"</i>. Hai tia ló xuất phát từ B cắt nhau tại điểm B' ở phía sau thấu kính. Hạ vuông góc xuống trục chính được ảnh A'B'.
      <br><b>Kết quả ghi nhận:</b> Ảnh A'B' là <b>ảnh thật, ngược chiều với vật và nhỏ hơn vật</b> (d' = 16,7 cm; h' = 3,3 cm).
    </li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/13_tn2_ht_case1_d_greater_2f.png" alt="TKHT d > 2f">
    <div class="caption">Hình 2.3: Vật đặt ngoài khoảng 2f (d &gt; 2f) qua TKHT cho ảnh thật, ngược chiều, nhỏ hơn vật</div>
  </div>

  <ul>
    <li><b>b) Trường hợp 2: Vật đặt cách thấu kính đúng bằng 2 lần tiêu cự (d = 2f = 20 cm):</b>
      <br>Nhấp nút vị trí nhanh <i>"d = 2f"</i>. Quan sát vị trí ảnh A'B' trên thước đo.
      <br><b>Kết quả ghi nhận:</b> Ảnh A'B' là <b>ảnh thật, ngược chiều với vật và có độ cao đúng bằng vật</b> (d' = 20 cm = 2f; h' = 5 cm = h).
    </li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/14_tn2_ht_case2_d_equal_2f.png" alt="TKHT d = 2f">
    <div class="caption">Hình 2.4: Vật đặt tại vị trí d = 2f qua TKHT cho ảnh thật, ngược chiều, bằng vật</div>
  </div>

  <ul>
    <li><b>c) Trường hợp 3: Vật đặt trong khoảng giữa tiêu cự và 2 lần tiêu cự (f &lt; d &lt; 2f, chọn d = 15 cm):</b>
      <br>Nhấp nút vị trí nhanh <i>"f &lt; d &lt; 2f"</i>. Quan sát ảnh A'B' dịch chuyển ra xa thấu kính.
      <br><b>Kết quả ghi nhận:</b> Ảnh A'B' là <b>ảnh thật, ngược chiều với vật và lớn hơn vật</b> (d' = 30 cm; h' = 10 cm).
    </li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/15_tn2_ht_case3_f_d_2f.png" alt="TKHT f < d < 2f">
    <div class="caption">Hình 2.5: Vật đặt trong khoảng f &lt; d &lt; 2f qua TKHT cho ảnh thật, ngược chiều, lớn hơn vật</div>
  </div>

  <ul>
    <li><b>d) Trường hợp 4: Vật đặt trong khoảng tiêu cự (d &lt; f, chọn d = 5 cm):</b>
      <br>Nhấp nút vị trí nhanh <i>"d &lt; f"</i>. Chùm tia ló loe rộng ra không thể cắt nhau ở phía sau thấu kính. Hai đường kéo dài nét đứt cắt nhau tại B' ở phía trước thấu kính.
      <br><b>Kết quả ghi nhận:</b> Ảnh A'B' là <b>ảnh ảo (nét đứt), cùng chiều với vật và lớn hơn vật</b> (d' = -10 cm; h' = 10 cm). Đây chính là nguyên lý của kính lúp.
    </li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/16_tn2_ht_case4_d_less_f.png" alt="TKHT d < f">
    <div class="caption">Hình 2.6: Vật đặt trong khoảng tiêu cự (d &lt; f) qua TKHT cho ảnh ảo, cùng chiều, lớn hơn vật</div>
  </div>

  <div class="step-title">Bước 3: Khảo sát sự tạo ảnh của vật qua Thấu kính phân kì.</div>
  <p>Tại thanh điều khiển, chuyển sang chọn loại thấu kính là <b>"Phân kì"</b>. Cố định tiêu cự f = 10 cm, thay đổi vị trí của vật sáng AB ở các khoảng cách khác nhau (d = 20 cm, d = 25 cm, d = 10 cm...):</p>
  <ul>
    <li>Thực hiện kéo rê vật AB dọc theo trục chính để quan sát chùm tia ló và vị trí ảnh A'B'.</li>
    <li><b>Kết quả ghi nhận:</b> Với mọi vị trí của vật sáng đặt trước thấu kính phân kì, ảnh A'B' <b>luôn luôn là ảnh ảo, cùng chiều với vật, nhỏ hơn vật và luôn nằm trong khoảng tiêu cự của thấu kính</b> (nằm giữa quang tâm O và tiêu điểm F).</li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/17_tn2_pk_case.png" alt="TKPK tạo ảnh">
    <div class="caption">Hình 2.7: Thấu kính phân kì luôn cho ảnh ảo, cùng chiều, nhỏ hơn vật và nằm trong khoảng tiêu cự</div>
  </div>

  <h2>2.3. Bảng tổng kết đặc điểm ảnh của vật qua thấu kính:</h2>
  <table class="data-table">
    <thead>
      <tr>
        <th>Loại thấu kính</th>
        <th>Vị trí của vật (d)</th>
        <th>Ảnh thật / ảo</th>
        <th>Chiều của ảnh</th>
        <th>Độ lớn của ảnh</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Thấu kính hội tụ</td>
        <td class="text-center">d &gt; 2f</td>
        <td class="text-center badge-real">Ảnh thật</td>
        <td class="text-center">Ngược chiều</td>
        <td class="text-center">Nhỏ hơn vật</td>
      </tr>
      <tr>
        <td>Thấu kính hội tụ</td>
        <td class="text-center">d = 2f</td>
        <td class="text-center badge-real">Ảnh thật</td>
        <td class="text-center">Ngược chiều</td>
        <td class="text-center">Bằng vật</td>
      </tr>
      <tr>
        <td>Thấu kính hội tụ</td>
        <td class="text-center">f &lt; d &lt; 2f</td>
        <td class="text-center badge-real">Ảnh thật</td>
        <td class="text-center">Ngược chiều</td>
        <td class="text-center">Lớn hơn vật</td>
      </tr>
      <tr>
        <td>Thấu kính hội tụ</td>
        <td class="text-center">d &lt; f</td>
        <td class="text-center badge-virt">Ảnh ảo</td>
        <td class="text-center">Cùng chiều</td>
        <td class="text-center">Lớn hơn vật</td>
      </tr>
      <tr>
        <td>Thấu kính phân kì</td>
        <td class="text-center">Mọi vị trí (d &gt; 0)</td>
        <td class="text-center badge-virt">Ảnh ảo</td>
        <td class="text-center">Cùng chiều</td>
        <td class="text-center">Nhỏ hơn vật</td>
      </tr>
    </tbody>
  </table>

  <!-- PHẦN II -->
  <div class="part-title">PHẦN II: PHÂN TÍCH VÀ ĐÁNH GIÁ HỌC LIỆU SỐ MÔ PHỎNG THEO CÁC MÔ HÌNH TPACK, SAMR VÀ TRIPLE E</div>

  <h1>1. Giới thiệu chung về học liệu số mô phỏng</h1>
  <p>Hiện nay, việc ứng dụng công nghệ thông tin vào dạy học ngày càng phổ biến, đặc biệt trong bối cảnh chuyển đổi số giáo dục và triển khai Chương trình GDPT 2018. Công nghệ không chỉ hỗ trợ giáo viên trình bày kiến thức mà còn tạo điều kiện để học sinh chủ động tìm hiểu, quan sát và khám phá nội dung bài học. Đối với môn Khoa học tự nhiên lớp 9, phần Vật lí, cụ thể là chủ đề Quang học (Bài 8: Thấu kính), có những nội dung rất trừu tượng: đường truyền ánh sáng vô hình trong không khí, tiêu điểm ảo, đường kéo dài của tia ló và mối quan hệ biến đổi liên tục giữa vị trí vật và tính chất ảnh. Nếu chỉ sử dụng phấn trắng bảng đen hoặc hình vẽ tĩnh trong SGK, học sinh rất dễ rơi vào tình trạng học vẹt, khó ghi nhớ bản chất hiện tượng.</p>
  <p>Từ thực tế đó, học liệu số mô phỏng thí nghiệm Thấu kính do Nhóm Natural (Trường ĐHSP TP.HCM) phát triển tại địa chỉ <b>https://minhlfc.github.io/nhom5-natural-thau-kinh/</b> ra đời nhằm cung cấp môi trường thí nghiệm ảo tương tác cao. Học liệu bao gồm 2 mô phỏng cốt lõi: Thí nghiệm 1 (Đường truyền của ba tia sáng đặc biệt) và Thí nghiệm 2 (Sự tạo ảnh của vật qua thấu kính). Dưới đây là phần phân tích, đánh giá chuyên sâu về chất lượng và mức độ chuyển đổi sư phạm của học liệu số theo 3 khung lý thuyết giáo dục quốc tế uy tín: TPACK, SAMR và Triple E.</p>

  <h1>2. Phân tích học liệu số theo mô hình TPACK</h1>
  <p>Mô hình TPACK (Technological Pedagogical Content Knowledge - Mishra & Koehler, 2006) xem xét sự tích hợp hài hòa giữa 3 thành phần kiến thức cốt lõi: Kiến thức Nội dung (CK), Kiến thức Sư phạm (PK) và Kiến thức Công nghệ (TK), cùng các vùng giao thoa giữa chúng.</p>

  <h2>2.1. Phân tích các thành phần cốt lõi:</h2>
  <ul>
    <li><b>Về Kiến thức Nội dung (CK):</b> Bám sát tuyệt đối nội dung Yêu cầu cần đạt của Bài 8: Thấu kính trong Chương trình GDPT 2018 môn KHTN 9. Thể hiện chuẩn xác đường truyền 3 tia sáng đặc biệt của cả thấu kính hội tụ và phân kì, sự hình thành ảnh thật, ảnh ảo, chiều và độ lớn của ảnh ở các khoảng cách khác nhau.</li>
    <li><b>Về Kiến thức Sư phạm (PK):</b> Thiết kế theo định hướng dạy học tích cực, chuyển từ dạy học thuyết giảng truyền thụ sang dạy học khám phá (Inquiry-based learning). Giáo viên tổ chức hoạt động theo chu trình POE (Dự đoán - Quan sát - Giải thích), kết hợp câu hỏi định hướng để học sinh tự kiến tạo kiến thức.</li>
    <li><b>Về Kiến thức Công nghệ (TK):</b> Xây dựng dưới dạng Single Page Application (SPA) trên nền tảng Web tiêu chuẩn (HTML5, CSS3, JavaScript hiện đại, Web Audio API). Không cần cài đặt, không phụ thuộc Flash/Java, tương thích mượt mà trên máy tính, máy tính bảng và điện thoại thông minh; đồ họa Canvas sắc nét và phản hồi tương tác tức thời (&lt; 16ms).</li>
  </ul>

  <h2>2.2. Phân tích các vùng giao thoa và hạt nhân TPACK:</h2>
  <ul>
    <li><b>PCK (Sư phạm - Nội dung):</b> Giáo viên lựa chọn câu hỏi định hướng, thiết kế các tình huống có vấn đề (như sự tạo ảnh khi vật ở tiêu điểm hoặc trường hợp d &lt; f) để giúp học sinh giải quyết những nhận niệm sai lầm thường gặp trong quang học.</li>
    <li><b>TCK (Công nghệ - Nội dung):</b> Mô phỏng sử dụng thuật toán quang hình học chính xác để trực quan hóa quy tắc khúc xạ, biến các khái niệm trừu tượng như "tiêu điểm ảo F" hay "đường kéo dài tia ló nét đứt" thành hình ảnh nhìn thấy được.</li>
    <li><b>TPK (Công nghệ - Sư phạm):</b> Khai thác tối đa các công cụ tương tác: kéo rê nguồn S, kéo đỉnh B của vật, thanh trượt f, d, h, nút chiếu tia, nút ẩn/hiện kết luận, chuyển đổi chế độ Sáng/Tối để biến bài giảng thành hoạt động tương tác sinh động.</li>
    <li><b>TPACK (Hạt nhân tích hợp):</b> Học liệu đạt tới đỉnh cao TPACK khi công nghệ mô phỏng được nhúng trực tiếp vào tiến trình sư phạm để giải quyết triệt để các rào cản nhận thức của nội dung bài học mà phương pháp truyền thống không thể làm được.</li>
  </ul>

  <p><i>Bảng 2.1: Ma trận đánh giá học liệu số theo mô hình TPACK</i></p>
  <table class="data-table">
    <thead>
      <tr>
        <th>Thành tố TPACK</th>
        <th>Biểu hiện trong học liệu</th>
        <th>Minh chứng thực tế trên Website</th>
        <th>Mức độ đáp ứng</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="text-center"><b>CK (Nội dung)</b></td>
        <td>Đúng chuẩn kiến thức quang hình học KHTN 9</td>
        <td>3 tia sáng đặc biệt, 5 trường hợp tạo ảnh chuẩn SGK</td>
        <td class="text-center badge-real">Xuất sắc (5/5)</td>
      </tr>
      <tr>
        <td class="text-center"><b>PK (Sư phạm)</b></td>
        <td>Phương pháp khám phá, chu trình POE</td>
        <td>Hệ thống câu hỏi gợi mở, ẩn kết luận để đối chiếu</td>
        <td class="text-center badge-real">Tốt (4.5/5)</td>
      </tr>
      <tr>
        <td class="text-center"><b>TK (Công nghệ)</b></td>
        <td>Công nghệ Web hiện đại, Canvas HTML5, Web Audio</td>
        <td>Chạy mượt trên mọi thiết bị, có âm thanh và Dark mode</td>
        <td class="text-center badge-real">Xuất sắc (5/5)</td>
      </tr>
      <tr>
        <td class="text-center"><b>PCK</b></td>
        <td>Sư phạm hóa các điểm khó của nội dung quang học</td>
        <td>Giải quyết rào cản tiêu điểm ảo và bản chất ảnh ảo</td>
        <td class="text-center badge-real">Xuất sắc (5/5)</td>
      </tr>
      <tr>
        <td class="text-center"><b>TCK</b></td>
        <td>Công nghệ biểu diễn chính xác quy luật vật lí</td>
        <td>Thuật toán traceRay vẽ tia tới, tia ló, đường kéo dài</td>
        <td class="text-center badge-real">Xuất sắc (5/5)</td>
      </tr>
      <tr>
        <td class="text-center"><b>TPK</b></td>
        <td>Công nghệ hỗ trợ tổ chức hoạt động học tích cực</td>
        <td>Nút Play tia sáng, kéo thả tương tác, hộp chọn vị trí</td>
        <td class="text-center badge-real">Xuất sắc (5/5)</td>
      </tr>
      <tr>
        <td class="text-center"><b>TPACK Toàn diện</b></td>
        <td>Tích hợp nhuần nhuyễn Công nghệ - Sư phạm - Nội dung</td>
        <td>Học sinh tự làm thí nghiệm, tự rút ra quy luật tạo ảnh</td>
        <td class="text-center badge-real">Xuất sắc (5/5)</td>
      </tr>
    </tbody>
  </table>

  <h1>3. Phân tích học liệu số theo mô hình SAMR</h1>
  <p>Mô hình SAMR (Puentedura, 2006) đánh giá mức độ công nghệ làm thay đổi bản chất của hoạt động dạy học qua 4 cấp độ: Thay thế (Substitution) -> Tăng cường (Augmentation) -> Điều chỉnh (Modification) -> Tái định nghĩa (Redefinition). Đối với học liệu mô phỏng của Nhóm Natural, mức độ chuyển đổi sư phạm không cố định mà có thể đạt từ cấp độ 1 lên đến cấp độ 4 tùy thuộc vào cách tổ chức của giáo viên:</p>

  <ul>
    <li><b>Cấp độ 1: Thay thế (Substitution) - </b> Công nghệ đóng vai trò thay thế công cụ truyền thống mà không có sự thay đổi chức năng. Ví dụ: Giáo viên dùng máy chiếu mở website mô phỏng chiếu hình ảnh thấu kính lên màn hình thay cho việc vẽ phấn trên bảng. Học sinh vẫn quan sát thụ động.</li>
    <li><b>Cấp độ 2: Tăng cường (Augmentation) - </b> Công nghệ thay thế trực tiếp nhưng có sự cải tiến chức năng quan trọng. Mô phỏng cho phép người học trực tiếp tương tác: bật/tắt từng tia sáng, đổi thấu kính hội tụ/phân kì, kéo thay đổi tiêu cự f và vị trí vật d để nhận kết quả tức thời. Đường nét đứt kéo dài của tia ló giúp học sinh thấy rõ điều mà bảng phấn hay hình vẽ tĩnh không thể hiện được.</li>
    <li><b>Cấp độ 3: Điều chỉnh (Modification) - </b> Công nghệ cho phép tái thiết kế đáng kể nhiệm vụ học tập. Thay vì giáo viên giảng giải quy tắc tạo ảnh, học sinh làm việc nhóm thực hiện chu trình POE: dự đoán -> dùng mô phỏng kiểm chứng -> thảo luận giải thích quy luật. Học sinh tự phát hiện quy luật thấu kính phân kì luôn cho ảnh ảo nhỏ hơn vật, biến giờ học thành buổi nghiên cứu khoa học thực thụ.</li>
    <li><b>Cấp độ 4: Tái định nghĩa (Redefinition) - </b> Công nghệ tạo ra những nhiệm vụ học tập hoàn toàn mới mà trước đây không thể thực hiện được trong lớp học truyền thống. Học sinh có thể ghi hình lại màn hình thao tác mô phỏng kèm giọng thuyết minh giải thích hiện tượng quang học để nộp sản phẩm số; hệ thống Phiếu học tập điện tử cho phép đồng bộ dữ liệu bài nộp theo thời gian thực về máy giáo viên.</li>
  </ul>

  <p><i>Bảng 2.2: Đánh giá cấp độ chuyển đổi sư phạm của học liệu số theo mô hình SAMR</i></p>
  <table class="data-table">
    <thead>
      <tr>
        <th>Cấp độ SAMR</th>
        <th>Mục tiêu chuyển đổi</th>
        <th>Hoạt động dạy học tương ứng</th>
        <th>Minh chứng trên Website</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="text-center"><b>1. Substitution (Thay thế)</b></td>
        <td>Thay thế bảng vẽ truyền thống</td>
        <td>Giáo viên trình chiếu đường truyền tia sáng và ảnh vật thay cho vẽ bảng phấn</td>
        <td>Hình ảnh quang học chuẩn xác, màu sắc rõ ràng</td>
      </tr>
      <tr>
        <td class="text-center"><b>2. Augmentation (Tăng cường)</b></td>
        <td>Tăng cường tính tương tác trực quan</td>
        <td>Học sinh tự tay kéo thả nguồn S, chỉnh f, d, h; quan sát đường nét đứt của ảnh ảo</td>
        <td>Phản hồi động tức thời, thước đo cm, Readout thông số</td>
      </tr>
      <tr>
        <td class="text-center"><b>3. Modification (Điều chỉnh)</b></td>
        <td>Tái thiết kế nhiệm vụ học tập</td>
        <td>Tổ chức hoạt động nhóm theo chu trình POE, học sinh tự khám phá và so sánh TKHT vs TKPK</td>
        <td>Hộp vị trí nhanh (d&gt;2f, d=2f...), nút ẩn/hiện kết luận</td>
      </tr>
      <tr>
        <td class="text-center"><b>4. Redefinition (Tái định nghĩa)</b></td>
        <td>Tạo ra nhiệm vụ học tập số mới</td>
        <td>Học sinh xây dựng video thuyết minh hiện tượng quang học, nộp bài kiểm tra trực tuyến thời gian thực</td>
        <td>Kênh nộp bài Real-time Cloud, trạm QR Code điện tử</td>
      </tr>
    </tbody>
  </table>

  <h1>4. Phân tích học liệu số theo khung đánh giá TRIPLE E (Lượng hóa điểm số)</h1>
  <p>Khung đánh giá Triple E Framework do TS. Liz Kolb (Đại học Michigan, 2017) phát triển nhằm đánh giá hiệu quả thực chất của công nghệ đối với kết quả học tập của học sinh, tập trung vào 3 yếu tố then chốt: Gắn kết (Engagement) -> Nâng cao (Enhancement) -> Mở rộng (Extension). Mỗi yếu tố được đánh giá qua 3 câu hỏi định lượng (mỗi câu tối đa 2 điểm, tổng thang đo 18 điểm).</p>

  <h2>4.1. Gắn kết học tập (Engagement) - Đạt 6/6 điểm:</h2>
  <ul>
    <li><b>Học sinh có tập trung vào mục tiêu bài học không? (2/2 điểm):</b> Công cụ tập trung tuyệt đối vào đường truyền tia sáng và quy luật tạo ảnh, không có quảng cáo, pop-up hay các yếu tố gây xao nhãng.</li>
    <li><b>Công nghệ có giúp giảm thiểu xao nhãng và gia tăng chú ý không? (2/2 điểm):</b> Hiệu ứng âm thanh tinh tế và giao diện tối quang học giữ trọn vẹn sự chú ý của học sinh vào màn hình thí nghiệm.</li>
    <li><b>Học sinh có chuyển dịch từ tiếp nhận thụ động sang học tập chủ động không? (2/2 điểm):</b> Học sinh đóng vai trò nhà nghiên cứu, trực tiếp cầm nắm vật sáng và điều khiển các thông số thí nghiệm.</li>
  </ul>

  <h2>4.2. Nâng cao hiệu quả học tập (Enhancement) - Đạt 6/6 điểm:</h2>
  <ul>
    <li><b>Công nghệ có hỗ trợ học sinh phát triển tư duy bậc cao và hiểu sâu khái niệm trừu tượng không? (2/2 điểm):</b> Giúp học sinh phân tích, so sánh và giải quyết trọn vẹn rào cản nhận thức về ảnh ảo và tiêu điểm ảo.</li>
    <li><b>Công nghệ có cung cấp các hỗ trợ/giàn giáo học tập mà phương tiện truyền thống không làm được không? (2/2 điểm):</b> Hệ thống đo đạc tự động (Readout card) hiển thị tức thời d, d', h, h' và tự động phân loại tính chất ảnh giúp học sinh tự kiểm chứng và đối chiếu.</li>
    <li><b>Công nghệ có giúp học sinh kết nối kiến thức để vận dụng vào kỹ năng dựng hình thực tế không? (2/2 điểm):</b> Mô phỏng bám sát quy tắc vẽ ảnh trong SGK, giúp học sinh tự tin chuyển giao kiến thức sang bài vẽ trên giấy.</li>
  </ul>

  <h2>4.3. Mở rộng học tập (Extension) - Đạt 5/6 điểm:</h2>
  <ul>
    <li><b>Công nghệ có tạo cơ hội để học sinh học tập ngoài lớp học không? (2/2 điểm):</b> Trang web triển khai trên đám mây GitHub Pages, học sinh có thể tự học, làm lại thí nghiệm mọi lúc mọi nơi trên điện thoại.</li>
    <li><b>Công nghệ có kết nối kiến thức với đời sống thực tế không? (2/2 điểm):</b> Trường hợp d &lt; f kết nối trực tiếp với kính lúp; trường hợp d &gt; 2f kết nối với máy ảnh kỹ thuật số.</li>
    <li><b>Công nghệ có giúp xây dựng kỹ năng mềm và kỹ năng số không? (1/2 điểm):</b> Cần có sự tổ chức nhiệm vụ nhóm của giáo viên để phát triển kỹ năng giao tiếp và cộng tác số hoàn thiện hơn.</li>
  </ul>

  <p><i>Bảng 2.3: Bảng lượng hóa điểm số chi tiết học liệu theo khung Triple E Framework (Liz Kolb)</i></p>
  <table class="data-table">
    <thead>
      <tr>
        <th>Thành tố Triple E</th>
        <th>Câu hỏi đánh giá chuẩn của Liz Kolb</th>
        <th>Minh chứng trong học liệu của Nhóm Natural</th>
        <th>Điểm số</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Engagement (E1)</b></td>
        <td>Tập trung học sinh vào mục tiêu học tập?</td>
        <td>Giao diện không quảng cáo, tập trung hoàn toàn vào thí nghiệm</td>
        <td class="text-center badge-real">2 / 2</td>
      </tr>
      <tr>
        <td><b>Engagement (E2)</b></td>
        <td>Giảm thiểu yếu tố gây xao nhãng?</td>
        <td>Âm thanh phản hồi trực quan, chế độ nền tối chuyên nghiệp</td>
        <td class="text-center badge-real">2 / 2</td>
      </tr>
      <tr>
        <td><b>Engagement (E3)</b></td>
        <td>Chuyển từ học thụ động sang chủ động?</td>
        <td>Tự tay kéo thả đỉnh B của vật, đổi tiêu cự và vị trí nguồn sáng</td>
        <td class="text-center badge-real">2 / 2</td>
      </tr>
      <tr style="background: #f3f4f6; font-weight: bold;">
        <td>Tổng Engagement</td>
        <td>Mức độ Gắn kết của học sinh với bài học</td>
        <td>Đạt mức gắn kết tối đa</td>
        <td class="text-center badge-real">6 / 6</td>
      </tr>
      <tr>
        <td><b>Enhancement (E1)</b></td>
        <td>Hiểu sâu sắc khái niệm trừu tượng?</td>
        <td>Trực quan hóa tiêu điểm ảo F và đường kéo dài nét đứt</td>
        <td class="text-center badge-real">2 / 2</td>
      </tr>
      <tr>
        <td><b>Enhancement (E2)</b></td>
        <td>Cung cấp giàn giáo học tập ưu việt?</td>
        <td>Bảng Readout tức thời tự động tính d', h', phân loại ảnh</td>
        <td class="text-center badge-real">2 / 2</td>
      </tr>
      <tr>
        <td><b>Enhancement (E3)</b></td>
        <td>Hỗ trợ kết nối và vận dụng kiến thức?</td>
        <td>Kết nối trực tiếp quy tắc mô phỏng với kỹ năng dựng hình SGK</td>
        <td class="text-center badge-real">2 / 2</td>
      </tr>
      <tr style="background: #f3f4f6; font-weight: bold;">
        <td>Tổng Enhancement</td>
        <td>Mức độ Nâng cao hiệu quả bài học</td>
        <td>Đạt mức nâng cao tối đa</td>
        <td class="text-center badge-real">6 / 6</td>
      </tr>
      <tr>
        <td><b>Extension (E1)</b></td>
        <td>Cơ hội học tập ngoài giờ lên lớp?</td>
        <td>Web online chạy 24/7 trên máy tính, điện thoại qua GitHub Pages</td>
        <td class="text-center badge-real">2 / 2</td>
      </tr>
      <tr>
        <td><b>Extension (E2)</b></td>
        <td>Kết nối với hiện tượng thực tế đời sống?</td>
        <td>Giải thích nguyên lý kính lúp (d&lt;f), máy ảnh (d&gt;2f)</td>
        <td class="text-center badge-real">2 / 2</td>
      </tr>
      <tr>
        <td><b>Extension (E3)</b></td>
        <td>Phát triển kỹ năng mềm và kỹ năng số?</td>
        <td>Học sinh thực hành thao tác số, cần thêm hướng dẫn nhóm của GV</td>
        <td class="text-center" style="font-weight: bold;">1 / 2</td>
      </tr>
      <tr class="summary-row">
        <td>TỔNG ĐIỂM TRIPLE E</td>
        <td>XẾP LOẠI TOÀN DIỆN (Thang điểm 18)</td>
        <td>MỨC ĐỘ CAO NHẤT: EXCEPTIONAL CONNECTION TO LEARNING</td>
        <td class="text-center highlight-score">17 / 18</td>
      </tr>
    </tbody>
  </table>

  <h1>5. Đề xuất quy trình tổ chức hoạt động dạy học 4 bước chuẩn mực sư phạm</h1>
  <p>Nhằm khai thác tối đa tiềm năng của học liệu số và khắc phục triệt để 4 lỗi thường gặp trong đổi mới phương pháp dạy học, nhóm đề xuất tiến trình dạy học gồm 4 bước dựa trên chu trình POE kết hợp hoạt động nhóm:</p>
  <ul>
    <li><b>Bước 1: Dự đoán (Predict) - </b> Giáo viên nêu tình huống có vấn đề: <i>"Khi một tia sáng tới song song với trục chính chiếu qua thấu kính phân kì, tia ló sẽ đi như thế nào?"</i> Học sinh suy nghĩ độc lập và ghi dự đoán vào Phiếu học tập trước khi mở mô phỏng.</li>
    <li><b>Bước 2: Quan sát mô phỏng và thu thập số liệu (Observe) - </b> Học sinh truy cập mô phỏng trên thiết bị, tự tay kích hoạt từng tia sáng hoặc kéo thả vị trí vật sáng, đối chiếu hiện tượng diễn ra với dự đoán ban đầu, ghi nhận các số liệu và đặc điểm ảnh.</li>
    <li><b>Bước 3: Thảo luận và rút ra kết luận (Explain) - </b> Các nhóm học sinh thảo luận, so sánh hiện tượng giữa thấu kính hội tụ và phân kì, giải thích vì sao ảnh ảo lại cùng chiều và nhỏ hơn vật. Đại diện nhóm trình bày, giáo viên chuẩn hóa kiến thức.</li>
    <li><b>Bước 4: Vận dụng và đánh giá (Apply & Assess) - </b> Học sinh vận dụng quy tắc vừa học để vẽ ảnh của vật sáng AB trên giấy kẻ ô; làm bài tập liên hệ thực tế về kính lúp, máy ảnh hoặc hoàn thành Phiếu học tập điện tử.</li>
  </ul>

  <h1>6. Kết luận và khuyến nghị sư phạm</h1>
  <p>Học liệu số mô phỏng Bài 8: Thấu kính do Nhóm Natural phát triển là một công cụ hỗ trợ dạy học có giá trị cao, được thiết kế đồng bộ về cả nội dung khoa học, phương pháp sư phạm và kỹ thuật lập trình hiện đại. Kết quả đánh giá cho thấy học liệu đáp ứng xuất sắc mô hình TPACK, có khả năng nâng cấp hoạt động học lên cấp độ Modification và Redefinition trong thang SAMR, và đạt 17/18 điểm (Exceptional connection to learning) theo thang Triple E.</p>
  <p>Khuyến nghị đối với giáo viên: Không nên biến buổi học thành giờ trình chiếu thụ động. Giáo viên cần thiết kế phiếu học tập định hướng rõ ràng, luôn duy trì bước Dự đoán (P) trước khi cho học sinh thao tác trên mô phỏng, và kết hợp hài hòa giữa thực hành ảo với kỹ năng vẽ hình thực tế trên giấy để đạt hiệu quả giáo dục toàn diện nhất.</p>

  <h1>TÀI LIỆU THAM KHẢO</h1>
  <ul>
    <li>1. Bộ Giáo dục và Đào tạo. (2018). <i>Chương trình Giáo dục phổ thông 2018 - Môn Khoa học tự nhiên</i>. Hà Nội.</li>
    <li>2. Kolb, L. (2017). <i>Learning first, technology second: The educator's guide to the Triple E Framework</i>. International Society for Technology in Education (ISTE).</li>
    <li>3. Mishra, P., & Koehler, M. J. (2006). Technological pedagogical content knowledge: A framework for teacher knowledge. <i>Teachers College Record</i>, 108(6), 1017-1054.</li>
    <li>4. Nhóm Natural. (2026). Website mô phỏng thí nghiệm tương tác Bài 8: Thấu kính (KHTN 9). https://minhlfc.github.io/nhom5-natural-thau-kinh/</li>
    <li>5. Puentedura, R. R. (2006). Transformation, technology, and education. Presentation at the Maine Department of Education.</li>
    <li>6. University of Calgary, Taylor Institute for Teaching and Learning. (2022). SAMR and TPACK: Two models to help with integrating technology into courses.</li>
  </ul>

</body>
</html>
"""
    with open(HTML_OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"HTML created: {HTML_OUT}")

def convert_html_to_pdf():
    # Use Edge headless to print the HTML to high-resolution vector PDF
    try:
        cmd = [
            EDGE_PATH,
            "--headless=new",
            f"--print-to-pdf={PDF_OUT}",
            "--no-pdf-header-footer",
            HTML_OUT
        ]
        subprocess.run(cmd, check=True)
        print(f"PDF created via Edge: {PDF_OUT}")
    except Exception as e:
        alt_pdf = os.path.join(BASE_DIR, 'Huong-Dan-Mo-Phong-Thi-Nghiem-Thau-Kinh-Natural-MoiNhat.pdf')
        cmd = [
            EDGE_PATH,
            "--headless=new",
            f"--print-to-pdf={alt_pdf}",
            "--no-pdf-header-footer",
            HTML_OUT
        ]
        subprocess.run(cmd, check=True)
        print(f"PDF created via Edge: {alt_pdf}")

if __name__ == '__main__':
    build_docx()
    build_html_for_pdf()
    convert_html_to_pdf()
    print("ALL_DOCUMENTS_CREATED_SUCCESSFULLY")
