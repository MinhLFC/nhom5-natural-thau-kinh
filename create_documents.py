import os
import subprocess
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, 'doc_images')
LOGO_PATH = os.path.join(BASE_DIR, 'assets', 'logo-hcmue.png')
DOCX_OUT = os.path.join(BASE_DIR, 'Huong-Dan-Mo-Phong-Thi-Nghiem-Thau-Kinh-Natural.docx')
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
    r_t1 = p_t1.add_run("MÔ PHỎNG THÍ NGHIỆM")
    r_t1.bold = True
    r_t1.font.size = Pt(16)
    r_t1.font.color.rgb = RGBColor(0x0d, 0x4a, 0x7a)

    p_t2 = doc.add_paragraph()
    p_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t2.paragraph_format.space_after = Pt(4)
    r_t2 = p_t2.add_run("BÀI 8: THẤU KÍNH")
    r_t2.bold = True
    r_t2.font.size = Pt(17)
    r_t2.font.color.rgb = RGBColor(0xd6, 0x3a, 0x3f)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("Môn Khoa học tự nhiên; Lớp: 9\nThời gian thực hiện: 2 tiết")
    r_sub.italic = True
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = RGBColor(0x33, 0x44, 0x55)

    # Helper function for adding headings and text
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

    # ==================== PHẦN 1 ====================
    add_h1("1. Thí nghiệm tìm hiểu đường truyền của các tia sáng đặc biệt qua thấu kính.")
    add_h2("1.1. Mục tiêu:")
    add_bullet("Trình bày và mô tả được đường truyền của 3 tia sáng đặc biệt (tia tới đi qua quang tâm O, tia tới song song với trục chính, tia tới đi qua tiêu điểm chính F hoặc có đường kéo dài đi qua F') khi qua thấu kính hội tụ và thấu kính phân kì thông qua quan sát mô phỏng.")
    add_bullet("Rút ra được quy luật hội tụ của chùm tia ló đối với thấu kính hội tụ và tính chất phân kì của chùm tia ló đối với thấu kính phân kì.")

    add_h2("1.2. Dụng cụ, thiết bị và các bước tiến hành.")
    add_h3("1.2.1. Dụng cụ, thiết bị.")
    add_bullet("Máy tính để bàn, máy tính xách tay hoặc điện thoại thông minh có kết nối Internet.")
    add_bullet("Trình duyệt web (Google Chrome, Microsoft Edge, Safari...) truy cập vào phần mềm mô phỏng Thấu kính của Nhóm Natural.")

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

    add_bullet("Tia tới song song với trục chính: Tích chọn ô \"Tia song song với trục chính\". Quan sát thấy tia ló bị loe rộng ra (phân kì), đường kéo dài của tia ló (nét đứt) đi qua tiêu điểm chính F ở phía trước thấu kính.", "2. ")
    add_pic("08_tn1_pk_ray_p.png", 5.4, "Hình 1.8: Tia tới song song trục chính cho tia ló có đường kéo dài đi qua tiêu điểm F")

    add_bullet("Tia tới có đường kéo dài hướng tới tiêu điểm chính F': Tích chọn ô \"Tia có đường kéo dài qua tiêu điểm F'\". Quan sát thấy tia ló sau khi qua thấu kính trở nên song song với trục chính.", "3. ")
    add_pic("09_tn1_pk_ray_f.png", 5.4, "Hình 1.9: Tia tới hướng tới tiêu điểm F' ở sau thấu kính cho tia ló song song trục chính")

    add_bullet("Chiếu đồng thời cả 3 tia sáng đặc biệt qua thấu kính phân kì: Quan sát thấy chùm tia ló loe rộng ra, các đường kéo dài của chúng cắt nhau tại điểm ảnh ảo S' ở phía trước thấu kính.", "4. ")
    add_pic("10_tn1_pk_all_rays.png", 5.4, "Hình 1.10: Chùm tia ló phân kì có các đường kéo dài cắt nhau tại ảnh ảo S'")

    # ==================== PHẦN 2 ====================
    add_h1("2. Thí nghiệm mô phỏng về sự tạo ảnh của vật qua thấu kính.")
    add_h2("2.1. Mục tiêu.")
    add_bullet("Thực hiện thí nghiệm mô phỏng quan sát quá trình dựng ảnh của một vật sáng AB (vuông góc với trục chính, A nằm trên trục chính) qua thấu kính hội tụ và thấu kính phân kì.")
    add_bullet("Khảo sát, xác định và ghi nhận được đặc điểm của ảnh A'B' (ảnh thật hay ảnh ảo, cùng chiều hay ngược chiều với vật, lớn hơn hay nhỏ hơn vật) ứng với các khoảng cách khác nhau từ vật đến thấu kính (d > 2f, d = 2f, f < d < 2f, d = f, d < f).")

    add_h2("2.2. Dụng cụ, thiết bị và các bước tiến hành.")
    add_h3("2.2.1. Dụng cụ, thiết bị.")
    add_bullet("Máy tính hoặc điện thoại có kết nối Internet.")
    add_bullet("Phần mềm mô phỏng Thấu kính trực tuyến (Nhóm Natural - KHTN 9).")

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
    r_tn = p_tbl_note.add_run("Bảng 2.1: Đối chiếu đặc điểm ảnh qua Thấu kính hội tụ và Thấu kính phân kì")
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

    doc.save(DOCX_OUT)
    print(f"DOCX created: {DOCX_OUT}")

def build_html_for_pdf():
    # Build a clean, styled HTML version that Edge can print directly to PDF
    # using exact same typography, images, and structure
    logo_rel = 'assets/logo-hcmue.png'
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Mô Phỏng Thí Nghiệm - Bài 8: Thấu Kính - Nhóm Natural</title>
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
      margin: 8px 0 12px 0;
      page-break-inside: avoid;
    }}
    table.data-table th, table.data-table td {{
      border: 1px solid #cbd5e1;
      padding: 6px 8px;
      font-size: 11pt;
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
    <div class="main-title">Mô Phỏng Thí Nghiệm</div>
    <div class="lesson-title">Bài 8: Thấu Kính</div>
    <div class="meta-title">Môn Khoa học tự nhiên; Lớp: 9 — Thời gian thực hiện: 2 tiết</div>
  </div>

  <!-- Phần 1 -->
  <h1>1. Thí nghiệm tìm hiểu đường truyền của các tia sáng đặc biệt qua thấu kính.</h1>
  
  <h2>1.1. Mục tiêu:</h2>
  <ul>
    <li>Trình bày và mô tả được đường truyền của 3 tia sáng đặc biệt (tia tới đi qua quang tâm O, tia tới song song với trục chính, tia tới đi qua tiêu điểm chính F hoặc có đường kéo dài đi qua F') khi qua thấu kính hội tụ và thấu kính phân kì thông qua quan sát mô phỏng.</li>
    <li>Rút ra được quy luật hội tụ của chùm tia ló đối với thấu kính hội tụ và tính chất phân kì của chùm tia ló đối với thấu kính phân kì khi chùm tia tới song song với trục chính.</li>
  </ul>

  <h2>1.2. Dụng cụ, thiết bị và các bước tiến hành.</h2>
  <h3>1.2.1. Dụng cụ, thiết bị.</h3>
  <ul>
    <li>Máy tính để bàn, máy tính xách tay hoặc điện thoại thông minh có kết nối Internet.</li>
    <li>Trình duyệt web hiện đại truy cập vào phần mềm mô phỏng Thấu kính của Nhóm Natural.</li>
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
    <li><b>2. Tia tới song song với trục chính:</b> Tích chọn ô <i>"Tia song song với trục chính"</i>. Quan sát thấy tia ló bị loe rộng ra (phân kì), đường kéo dài của tia ló (nét đứt) đi qua tiêu điểm chính F ở phía trước thấu kính.</li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/08_tn1_pk_ray_p.png" alt="Tia song song trục chính - TKPK">
    <div class="caption">Hình 1.8: Tia tới song song trục chính cho tia ló có đường kéo dài đi qua tiêu điểm F</div>
  </div>

  <ul>
    <li><b>3. Tia tới có đường kéo dài hướng tới tiêu điểm chính F':</b> Tích chọn ô <i>"Tia có đường kéo dài qua tiêu điểm F'"</i>. Tia ló sau khi qua thấu kính trở nên song song với trục chính.</li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/09_tn1_pk_ray_f.png" alt="Tia hướng tới tiêu điểm F' - TKPK">
    <div class="caption">Hình 1.9: Tia tới hướng tới tiêu điểm F' ở sau thấu kính cho tia ló song song trục chính</div>
  </div>

  <ul>
    <li><b>4. Chiếu đồng thời cả 3 tia sáng đặc biệt qua thấu kính phân kì:</b> Quan sát thấy chùm tia ló loe rộng ra, các đường kéo dài của chúng cắt nhau tại điểm ảnh ảo S' ở phía trước thấu kính.</li>
  </ul>
  <div class="img-wrap">
    <img src="doc_images/10_tn1_pk_all_rays.png" alt="Cả 3 tia sáng - TKPK">
    <div class="caption">Hình 1.10: Chùm tia ló phân kì có các đường kéo dài cắt nhau tại ảnh ảo S'</div>
  </div>

  <!-- Phần 2 -->
  <h1>2. Thí nghiệm mô phỏng về sự tạo ảnh của vật qua thấu kính.</h1>
  
  <h2>2.1. Mục tiêu.</h2>
  <ul>
    <li>Thực hiện thí nghiệm mô phỏng quan sát quá trình dựng ảnh của một vật sáng AB (đoạn thẳng vuông góc với trục chính, A nằm trên trục chính) qua thấu kính hội tụ và thấu kính phân kì.</li>
    <li>Khảo sát, xác định và ghi nhận được đặc điểm của ảnh A'B' (ảnh thật hay ảnh ảo, cùng chiều hay ngược chiều với vật, lớn hơn hay nhỏ hơn vật) ứng với các khoảng cách khác nhau từ vật đến thấu kính (d &gt; 2f, d = 2f, f &lt; d &lt; 2f, d = f, d &lt; f).</li>
  </ul>

  <h2>2.2. Dụng cụ, thiết bị và các bước tiến hành.</h2>
  <h3>2.2.1. Dụng cụ, thiết bị.</h3>
  <ul>
    <li>Máy tính để bàn, máy tính xách tay hoặc điện thoại có kết nối Internet.</li>
    <li>Phần mềm mô phỏng Thấu kính trực tuyến (Nhóm Natural - KHTN 9).</li>
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

</body>
</html>
"""
    with open(HTML_OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"HTML created: {HTML_OUT}")

def convert_html_to_pdf():
    # Use Edge headless to print the HTML to high-resolution vector PDF
    cmd = [
        EDGE_PATH,
        "--headless=new",
        f"--print-to-pdf={PDF_OUT}",
        "--no-pdf-header-footer",
        HTML_OUT
    ]
    subprocess.run(cmd, check=True)
    print(f"PDF created via Edge: {PDF_OUT}")

if __name__ == '__main__':
    build_docx()
    build_html_for_pdf()
    convert_html_to_pdf()
    print("ALL_DOCUMENTS_CREATED_SUCCESSFULLY")
