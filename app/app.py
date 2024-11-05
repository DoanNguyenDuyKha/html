from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import datetime
app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'
app.secret_key = "your_secret_key"  # Cần đặt secret_key để sử dụng session

# Khởi tạo cơ sở dữ liệu
db = sqlite3.connect('phim.db')
cursor = db.cursor()

# Tạo bảng phim nếu chưa tồn tại
cursor.execute('''
    CREATE TABLE IF NOT EXISTS phim (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ten_phim TEXT,
        the_loai TEXT,
        thoi_luong INTEGER,
        khoi_chieu DATE,
        poster TEXT,
        xep_hang TEXT,
        loai_phim TEXT
    )
''')
db.commit()

# Tạo bảng đặt vé nếu chưa tồn tại
cursor.execute('''
    CREATE TABLE IF NOT EXISTS dat_ve (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_khach_hang TEXT,
    so_dien_thoai TEXT,
    email TEXT,
    phim_id INTEGER,
    so_luong_ve INTEGER,
    ngay_dat_ve DATE,
    rap TEXT, 
    suatchieu TEXT, 
    ghe TEXT, 
    gia_ve INTEGER
)
''')
db.commit()

# Tạo bảng người dùng nếu chưa tồn tại
cursor.execute('''
    CREATE TABLE IF NOT EXISTS nguoi_dung (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ten_dang_nhap TEXT,
        mat_khau TEXT,
        ho_ten TEXT,
        email TEXT
    )
''')
db.commit()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS ghe (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ten_ghe TEXT,
        loai_ghe TEXT,
        gia_ghe INTEGER
    )
''')
with sqlite3.connect('phim.db') as db:
    cursor = db.cursor()
    cursor.execute("INSERT INTO ghe (ten_ghe, loai_ghe, gia_ghe) VALUES ('A1', 'Vip', 100000)")
    cursor.execute("INSERT INTO ghe (ten_ghe, loai_ghe, gia_ghe) VALUES ('A2', 'Vip', 100000)")
    cursor.execute("INSERT INTO ghe (ten_ghe, loai_ghe, gia_ghe) VALUES ('B1', 'Thuong', 80000)")
    cursor.execute("INSERT INTO ghe (ten_ghe, loai_ghe, gia_ghe) VALUES ('B2', 'Thuong', 80000)")
    # Thêm dữ liệu cho các ghế còn lại
    db.commit()
db.commit()
# Route cho trang chủ
@app.route("/")
def index():
    if 'logged_in' in session and session['logged_in']:
        with sqlite3.connect('phim.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM phim WHERE loai_phim = 'dang-chieu' LIMIT 3")
            phim_dang_chieu = cursor.fetchall()
        return render_template("index.html", phim_dang_chieu=phim_dang_chieu, username=session['username'])
    else:
        return render_template("index.html")


# Route cho trang danh sách phim
@app.route("/danhsach")
def danhsach():
    if 'logged_in' in session and session['logged_in']:
        with sqlite3.connect('phim.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM phim WHERE loai_phim = 'dang-chieu'")
            phim_dang_chieu = cursor.fetchall()

            cursor.execute("SELECT * FROM phim WHERE loai_phim = 'sap-chieu'")
            phim_sap_chieu = cursor.fetchall()

        return render_template("danhsach.html", phim_dang_chieu=phim_dang_chieu, phim_sap_chieu=phim_sap_chieu, username=session['username'])
    else:
        return render_template("danhsach.html")

# Route cho trang quản lý phim
@app.route("/quan-ly")
def quan_ly():
    if 'logged_in' in session and session['logged_in']:
        with sqlite3.connect('phim.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM phim")
            ds_phim = cursor.fetchall()
        return render_template("quan-ly.html", ds_phim=ds_phim, username=session['username'])
    else:
        return redirect(url_for('dn'))

# Route cho trang thêm phim
@app.route("/add-phim", methods=["POST"])
def add_phim():
    ten_phim = request.form['ten-phim']
    the_loai = request.form['the-loai']
    thoi_luong = request.form['thoi-luong']
    khoi_chieu = request.form['khoi-chieu']
    poster = request.files['poster']
    poster_path = os.path.join(app.config['STATIC_FOLDER'], 'images', poster.filename)
    poster.save(poster_path)
    xep_hang = request.form['xep-hang']
    loai_phim = request.form['loai-phim']

    with sqlite3.connect('phim.db') as db:
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO phim (ten_phim, the_loai, thoi_luong, khoi_chieu, poster, xep_hang, loai_phim) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ten_phim, the_loai, thoi_luong, khoi_chieu, poster.filename, xep_hang, loai_phim))
        db.commit()

    return redirect(url_for('quan_ly'))

# Route cho trang cập nhật phim
@app.route('/update-phim/<int:phim_id>', methods=['GET', 'POST'])
def update_phim(phim_id):
    if request.method == 'GET':
        with sqlite3.connect('phim.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM phim WHERE id = ?", (phim_id,))
            phim = cursor.fetchone()
        if phim:
            return render_template('update-phim.html', phim=phim)
        else:
            return "Phim không tồn tại", 404
    elif request.method == 'POST':
        ten_phim = request.form['ten-phim']
        the_loai = request.form['the-loai']
        thoi_luong = request.form['thoi-luong']
        khoi_chieu = request.form['khoi-chieu']
        xep_hang = request.form['xep-hang']
        loai_phim = request.form['loai-phim']
        poster = request.files['poster']

        poster_filename = poster.filename if poster else None
        if poster:
            poster_path = os.path.join(app.config['STATIC_FOLDER'], 'images', poster.filename)
            poster.save(poster_path)

        with sqlite3.connect('phim.db') as db:
            cursor = db.cursor()
            cursor.execute('''
                UPDATE phim
                SET ten_phim = ?, the_loai = ?, thoi_luong = ?, khoi_chieu = ?, 
                    poster = ?, xep_hang = ?, loai_phim = ?
                WHERE id = ?
            ''', (ten_phim, the_loai, thoi_luong, khoi_chieu, poster_filename, xep_hang, loai_phim, phim_id))
            db.commit()

        return redirect(url_for('quan_ly'))

# Route cho trang xóa phim
@app.route('/delete-phim/<int:phim_id>', methods=['POST'])
def delete_phim(phim_id):
    with sqlite3.connect('phim.db') as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM phim WHERE id = ?", (phim_id,))
        db.commit()

    return redirect(url_for('quan_ly'))

# Route cho trang chi tiết phim
@app.route("/chi-tiet/<int:phim_id>")
def chi_tiet(phim_id):
    with sqlite3.connect('phim.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM phim WHERE id = ?", (phim_id,))
        phim = cursor.fetchone()
    return render_template("chitietphim.html", phim=phim)

# Route cho trang quản lý đặt vé
@app.route("/quan-ly-dat-ve")
def quan_ly_dat_ve():
    if 'logged_in' in session and session['logged_in']:
        with sqlite3.connect('phim.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM dat_ve")
            ds_dat_ve = cursor.fetchall()
            cursor.execute("SELECT * FROM phim")
            ds_phim = cursor.fetchall()
        return render_template("quan-ly-dat-ve.html", ds_dat_ve=ds_dat_ve, ds_phim=ds_phim, username=session['username'])
    else:
        return redirect(url_for('dn'))


# Route cho trang quản lý người dùng
@app.route("/quan-ly-nguoi-dung")
def quan_ly_nguoi_dung():
    if 'logged_in' in session and session['logged_in']:
        with sqlite3.connect('phim.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM nguoi_dung")
            ds_nguoi_dung = cursor.fetchall()
        return render_template("quan-ly-nguoi-dung.html", ds_nguoi_dung=ds_nguoi_dung, username=session['username'])
    else:
        return redirect(url_for('dn'))

# Route cho trang xóa người dùng
@app.route('/delete-nguoi-dung/<int:nguoi_dung_id>', methods=['POST'])
def delete_nguoi_dung(nguoi_dung_id):
    with sqlite3.connect('phim.db') as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM nguoi_dung WHERE id = ?", (nguoi_dung_id,))
        db.commit()

    return redirect(url_for('quan_ly_nguoi_dung'))
# Route cho trang đăng nhập
@app.route('/dn', methods=['GET', 'POST'])
def dn():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('phim.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM nguoi_dung WHERE ten_dang_nhap = ? AND mat_khau = ?", (username, password))
            user = cursor.fetchone()

        if user:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('dn.html', error="Tên đăng nhập hoặc mật khẩu không chính xác")

    return render_template('dn.html')

# Route cho trang đăng ký
@app.route('/dk', methods=['GET', 'POST'])
def dk():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        email = request.form['email']

        with sqlite3.connect('phim.db') as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO nguoi_dung (ten_dang_nhap, mat_khau, ho_ten, email) VALUES (?, ?, ?, ?)", (username, password, fullname, email))
            db.commit()

        # Chuyển hướng về trang đăng nhập
        return redirect(url_for('dn')) 

    return render_template('dk.html')

# Route cho trang đăng xuất
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))

# ... (code app.py hiện tại) ...

@app.route("/dat-ve/<int:phim_id>", methods=['GET', 'POST'])
def dat_ve(phim_id):
    if request.method == 'GET':
        with sqlite3.connect('phim.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM phim")  # Truy vấn tất cả phim
            phim_list = cursor.fetchall()
            cursor.execute("SELECT * FROM phim WHERE id = ?", (phim_id,))
            phim = cursor.fetchone()
            cursor.execute("SELECT * FROM ghe")  # Truy vấn danh sách ghế
            ghe_list = cursor.fetchall()
        return render_template('datve.html', phim_id=phim_id, phim=phim, phim_list=phim_list, ghe_list=ghe_list)
    
    elif request.method == 'POST':
        ten_khach_hang = request.form['ten_khach_hang']
        so_dien_thoai = request.form['so_dien_thoai']
        email = request.form['email']
        ghe_id = request.form['ghe']
        so_luong_ve = int(request.form['so_luong_ve'])
        rap = request.form['rap']
        suatchieu = request.form['suatchieu']

        # Lấy thông tin phim
        with sqlite3.connect('phim.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM phim WHERE id = ?", (phim_id,))
            phim = cursor.fetchone()
            ten_phim = phim[1]

        with sqlite3.connect('phim.db') as db:
            cursor = db.cursor()
            cursor.execute("SELECT gia_ghe FROM ghe WHERE id = ?", (ghe_id,))
            gia_ve = cursor.fetchone()[0]  

        # Tính tổng tiền vé
        tong_tien = so_luong_ve * gia_ve

        ngay_dat_ve = datetime.datetime.now().strftime('%Y-%m-%d')

        # Lưu thông tin đặt vé vào database
        with sqlite3.connect('phim.db') as db:
            cursor = db.cursor()
            cursor.execute('''INSERT INTO dat_ve (ten_khach_hang, so_dien_thoai, email, phim_id, so_luong_ve, ngay_dat_ve, rap, suatchieu, ghe, gia_ve) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (ten_khach_hang, so_dien_thoai, email, phim_id, so_luong_ve, ngay_dat_ve, rap, suatchieu, ghe_id, tong_tien))
            db.commit()

        # Chuyển hướng đến trang đặt vé thành công
        return render_template('datve_thanhcong.html', ten_khach_hang=ten_khach_hang, so_dien_thoai=so_dien_thoai, email=email, ten_phim=ten_phim, rap=rap, suatchieu=suatchieu, ghe=ghe_id, so_luong_ve=so_luong_ve, tong_tien=tong_tien)


# ... (code app.py còn lại) ...
@app.route("/xoa-dat-ve/<int:dat_ve_id>", methods=['POST'])
def xoa_dat_ve(dat_ve_id):
    with sqlite3.connect('phim.db') as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM dat_ve WHERE id = ?", (dat_ve_id,))
        db.commit()
    return redirect(url_for('quan_ly_dat_ve'))
    
if __name__ == "__main__":
    app.run(debug=True)