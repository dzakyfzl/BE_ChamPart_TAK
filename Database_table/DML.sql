-- Active: 1763538571248@@127.0.0.1@3307@champart
-- ===========================
-- Lampiran
-- ===========================
INSERT INTO Lampiran (nama, jenis, ukuran, folder) VALUES
('foto_pengguna1.jpg', 'image/jpeg', 204800, '/uploads/pengguna/foto_pengguna1.jpg'),
('foto_pengguna2.jpg', 'image/jpeg', 156000, '/uploads/pengguna/foto_pengguna2.jpg'),
('foto_pengguna3.png', 'image/png', 189000, '/uploads/pengguna/foto_pengguna3.png'),
('foto_pengguna4.jpg', 'image/jpeg', 178000, '/uploads/pengguna/foto_pengguna4.jpg'),
('foto_pengguna5.png', 'image/png', 201000, '/uploads/pengguna/foto_pengguna5.png');

-- ===========================
-- Pengguna
-- ===========================
INSERT INTO Pengguna (username, email, no_telp, fakultas, prodi, salt, hashed_password, idLampiran) VALUES
('adam_maulana', 'adam.maulana@student.ac.id', '081234567890', 'Fakultas Teknik', 'Teknik Informatika', 'salt_adam_123', 'hashed_password_adam', 1),
('dina_amalia', 'dina.amalia@student.ac.id', '081234567891', 'Fakultas Teknik', 'Sistem Informasi', 'salt_dina_456', 'hashed_password_dina', 2),
('budi_santoso', 'budi.santoso@student.ac.id', '081234567892', 'Fakultas Teknik', 'Teknik Elektro', 'salt_budi_789', 'hashed_password_budi', 3),
('citra_dewi', 'citra.dewi@student.ac.id', '081234567893', 'Fakultas Ekonomi', 'Manajemen', 'salt_citra_abc', 'hashed_password_citra', 4),
('eko_prasetyo', 'eko.prasetyo@student.ac.id', '081234567894', 'Fakultas Ekonomi', 'Akuntansi', 'salt_eko_def', 'hashed_password_eko', 5);

-- ===========================
-- Minat
-- ===========================
INSERT INTO Minat (nama) VALUES
('Kepemimpinan'),
('Kewirausahaan'),
('Teknologi'),
('Kemanusiaan'),
('Lingkungan');

-- ===========================
-- Bakat
-- ===========================
INSERT INTO Bakat (nama) VALUES
('Public Speaking'),
('Manajemen Proyek'),
('Programming'),
('Desain Grafis'),
('Menulis');

-- ===========================
-- Instansi
-- ===========================
INSERT INTO Instansi (nama, jenis, alamat, idLampiran) VALUES
('Universitas Indonesia', 'Perguruan Tinggi', 'Jl. Margonda Raya, Depok', 1),
('PT Teknologi Nusantara', 'Perusahaan', 'Jl. Sudirman No. 123, Jakarta', 2),
('Yayasan Peduli Sesama', 'Organisasi Sosial', 'Jl. Gatot Subroto No. 45, Bandung', 3),
('Green Indonesia Foundation', 'LSM', 'Jl. Diponegoro No. 78, Surabaya', 4),
('Komunitas Startup Indonesia', 'Komunitas', 'Jl. Asia Afrika No. 90, Bandung', 5);

-- ===========================
-- AdminInstansi
-- ===========================
INSERT INTO AdminInstansi (username, email, jabatan, salt, hashed_password, idInstansi, idLampiran) VALUES
('rafi_pratama', 'rafi.pratama@ui.ac.id', 'Koordinator Kemahasiswaan', 'salt_rafi_111', 'hashed_password_rafi', 1, 1),
('siti_nurhaliza', 'siti.nurhaliza@teknologi.com', 'HR Manager', 'salt_siti_222', 'hashed_password_siti', 2, 2),
('andi_gunawan', 'andi.gunawan@peduli.org', 'Direktur Program', 'salt_andi_333', 'hashed_password_andi', 3, 3),
('maya_kusuma', 'maya.kusuma@green.org', 'Project Coordinator', 'salt_maya_444', 'hashed_password_maya', 4, 4),
('teguh_santoso', 'teguh.santoso@startup.id', 'Community Manager', 'salt_teguh_555', 'hashed_password_teguh', 5, 5);

-- ===========================
-- AdminPengawas
-- ===========================
INSERT INTO AdminPengawas (username, email, jabatan, salt, hashed_password, idLampiran) VALUES
('ahmad_fauzi', 'ahmad.fauzi@pengawas.ac.id', 'Pengawas Utama', 'salt_ahmad_aaa', 'hashed_password_ahmad', 1),
('rina_wijaya', 'rina.wijaya@pengawas.ac.id', 'Pengawas Senior', 'salt_rina_bbb', 'hashed_password_rina', 2),
('dedi_kurniawan', 'dedi.kurniawan@pengawas.ac.id', 'Pengawas Lapangan', 'salt_dedi_ccc', 'hashed_password_dedi', 3),
('yulia_rahayu', 'yulia.rahayu@pengawas.ac.id', 'Quality Assurance', 'salt_yulia_ddd', 'hashed_password_yulia', 4),
('bambang_setiawan', 'bambang.setiawan@pengawas.ac.id', 'Supervisor', 'salt_bambang_eee', 'hashed_password_bambang', 5);

-- ===========================
-- Kegiatan (dengan views column)
-- ===========================
INSERT INTO Kegiatan (nama, deskripsi, waktu, nominal_TAK, TAK_wajib, status_kegiatan, waktuDiupload, views, idAdminPengawas, idAdminInstansi, idInstansi, idLampiran) VALUES
('Workshop Machine Learning', 'Pelatihan dasar machine learning untuk mahasiswa', '2025-12-15 09:00:00', 10, 1, 'approved', '2025-10-29 10:00:00', 150, 1, 1, 1, 1),
('Seminar Kewirausahaan Digital', 'Diskusi tentang membangun startup di era digital', '2025-12-20 13:00:00', 8, 0, 'approved', '2025-10-29 11:00:00', 89, 2, 5, 5, 2),
('Bakti Sosial di Panti Asuhan', 'Kegiatan berbagi dengan anak-anak panti asuhan', '2025-12-25 08:00:00', 12, 1, 'pending', '2025-10-29 12:00:00', 45, 3, 3, 3, 3),
('Penanaman Pohon Mangrove', 'Aksi peduli lingkungan dengan menanam mangrove', '2026-01-01 07:00:00', 15, 1, 'approved', '2025-10-29 13:00:00', 200, 4, 4, 4, 4),
('Hackathon 2025', 'Kompetisi programming 48 jam non-stop', '2026-01-10 08:00:00', 20, 0, 'approved', '2025-10-29 14:00:00', 320, 5, 2, 2, 5),
('Webinar Data Science', 'Pengenalan data science dan career path di industri', '2025-12-05 10:00:00', 6, 0, 'approved', '2025-10-30 09:00:00', 180, 1, 1, 1, 1),
('Lomba Debat Bahasa Inggris', 'Kompetisi debat tingkat universitas', '2025-12-08 08:00:00', 15, 1, 'approved', '2025-10-30 10:00:00', 95, 2, 2, 2, 2),
('Workshop UI/UX Design', 'Pelatihan desain antarmuka aplikasi mobile', '2025-12-12 13:00:00', 10, 0, 'approved', '2025-10-30 11:00:00', 210, 3, 5, 5, 3),
('Donor Darah Bersama PMI', 'Kegiatan donor darah rutin bulanan', '2025-12-18 07:00:00', 8, 1, 'approved', '2025-10-30 12:00:00', 75, 4, 3, 3, 4),
('Seminar Investasi Saham', 'Belajar investasi saham untuk pemula', '2025-12-22 14:00:00', 6, 0, 'approved', '2025-10-30 13:00:00', 165, 5, 5, 5, 5),
('Workshop Fotografi', 'Teknik dasar fotografi dan editing', '2025-12-28 09:00:00', 8, 0, 'approved', '2025-10-31 08:00:00', 120, 1, 2, 2, 1),
('Pelatihan Public Speaking', 'Meningkatkan kemampuan berbicara di depan umum', '2026-01-05 10:00:00', 10, 1, 'approved', '2025-10-31 09:00:00', 230, 2, 1, 1, 2),
('Kompetisi Business Plan', 'Lomba membuat rencana bisnis startup', '2026-01-12 08:00:00', 18, 0, 'approved', '2025-10-31 10:00:00', 145, 3, 5, 5, 3),
('Bersih-bersih Pantai', 'Aksi bersih pantai dan edukasi lingkungan', '2026-01-15 06:00:00', 12, 1, 'approved', '2025-10-31 11:00:00', 88, 4, 4, 4, 4),
('Workshop Penulisan Ilmiah', 'Teknik menulis jurnal dan paper akademik', '2026-01-18 13:00:00', 8, 1, 'approved', '2025-10-31 12:00:00', 67, 5, 1, 1, 5),
('Seminar Cyber Security', 'Keamanan siber dan ethical hacking', '2026-01-22 09:00:00', 10, 0, 'approved', '2025-11-01 08:00:00', 280, 1, 2, 2, 1),
('Lomba Karya Tulis Ilmiah', 'Kompetisi LKTI tingkat nasional', '2026-01-25 08:00:00', 20, 1, 'approved', '2025-11-01 09:00:00', 110, 2, 1, 1, 2),
('Workshop Android Development', 'Membuat aplikasi Android dengan Kotlin', '2026-01-28 10:00:00', 12, 0, 'approved', '2025-11-01 10:00:00', 195, 3, 2, 2, 3),
('Mengajar di Desa Tertinggal', 'Pengabdian masyarakat mengajar anak-anak', '2026-02-01 07:00:00', 15, 1, 'approved', '2025-11-01 11:00:00', 55, 4, 3, 3, 4),
('Seminar Karir di Bidang IT', 'Tips dan trick memulai karir di teknologi', '2026-02-05 14:00:00', 6, 0, 'approved', '2025-11-01 12:00:00', 175, 5, 2, 2, 5),
('Workshop Digital Marketing', 'Strategi pemasaran digital untuk UMKM', '2026-02-08 09:00:00', 8, 0, 'approved', '2025-11-02 08:00:00', 140, 1, 5, 5, 1),
('Pelatihan Leadership Camp', 'Camp pelatihan kepemimpinan 3 hari', '2026-02-12 06:00:00', 25, 1, 'approved', '2025-11-02 09:00:00', 98, 2, 1, 1, 2),
('Lomba Poster Lingkungan', 'Kompetisi desain poster tema lingkungan', '2026-02-15 08:00:00', 10, 0, 'approved', '2025-11-02 10:00:00', 82, 3, 4, 4, 3),
('Workshop Cloud Computing', 'Pengenalan AWS dan Google Cloud', '2026-02-18 10:00:00', 12, 0, 'approved', '2025-11-02 11:00:00', 215, 4, 2, 2, 4),
('Kunjungan ke Pabrik Industri', 'Studi banding ke perusahaan manufaktur', '2026-02-22 08:00:00', 10, 1, 'approved', '2025-11-02 12:00:00', 65, 5, 2, 2, 5),
('Seminar Kesehatan Mental', 'Pentingnya menjaga kesehatan mental mahasiswa', '2026-02-25 13:00:00', 6, 0, 'approved', '2025-11-03 08:00:00', 190, 1, 3, 3, 1),
('Workshop Video Editing', 'Teknik editing video dengan Adobe Premiere', '2026-02-28 09:00:00', 8, 0, 'approved', '2025-11-03 09:00:00', 135, 2, 5, 5, 2),
('Lomba Cerdas Cermat', 'Kompetisi kecerdasan antar fakultas', '2026-03-02 08:00:00', 12, 1, 'approved', '2025-11-03 10:00:00', 78, 3, 1, 1, 3),
('Pelatihan First Aid', 'Pelatihan pertolongan pertama kecelakaan', '2026-03-05 09:00:00', 8, 1, 'approved', '2025-11-03 11:00:00', 102, 4, 3, 3, 4),
('Workshop Blockchain', 'Memahami teknologi blockchain dan crypto', '2026-03-08 10:00:00', 10, 0, 'approved', '2025-11-03 12:00:00', 245, 5, 2, 2, 5),
('Bakti Sosial Banjir', 'Bantuan korban banjir di daerah terdampak', '2026-03-10 06:00:00', 15, 1, 'pending', '2025-11-04 08:00:00', 42, 1, 3, 3, 1),
('Seminar Entrepreneurship', 'Kisah sukses pengusaha muda Indonesia', '2026-03-12 14:00:00', 6, 0, 'approved', '2025-11-04 09:00:00', 168, 2, 5, 5, 2),
('Workshop IoT Arduino', 'Membuat project IoT dengan Arduino', '2026-03-15 10:00:00', 12, 0, 'approved', '2025-11-04 10:00:00', 188, 3, 2, 2, 3),
('Lomba Fotografi Alam', 'Kompetisi foto tema keindahan alam', '2026-03-18 08:00:00', 10, 0, 'approved', '2025-11-04 11:00:00', 95, 4, 4, 4, 4),
('Pelatihan Microsoft Office', 'Penguasaan Excel, Word, dan PowerPoint', '2026-03-20 09:00:00', 6, 1, 'approved', '2025-11-04 12:00:00', 125, 5, 1, 1, 5);

-- ===========================
-- minatPengguna
-- ===========================
INSERT INTO minatPengguna (idMinat, idPengguna) VALUES
(3, 1),
(2, 2),
(1, 3),
(4, 4),
(5, 5);

-- ===========================
-- bakatPengguna
-- ===========================
INSERT INTO bakatPengguna (idBakat, idPengguna) VALUES
(2, 2),
(1, 3),
(5, 4),
(4, 5);

-- ===========================
-- bakatKegiatan
-- ===========================
INSERT INTO bakatKegiatan (idBakat, idKegiatan) VALUES
(3, 1),
(2, 2),
(1, 3),
(5, 4),
(3, 5),
(3, 6),
(1, 7),
(4, 8),
(1, 9),
(2, 10),
(4, 11),
(1, 12),
(2, 13),
(5, 14),
(5, 15),
(3, 16),
(5, 17),
(3, 18),
(1, 19),
(1, 20),
(2, 21),
(1, 22),
(4, 23),
(3, 24),
(2, 25),
(1, 26),
(4, 27),
(1, 28),
(1, 29),
(3, 30),
(1, 31),
(1, 32),
(3, 33),
(4, 34),
(2, 35);

-- ===========================
-- minatKegiatan
-- ===========================
INSERT INTO minatKegiatan (idMinat, idKegiatan) VALUES
(3, 1),
(2, 2),
(4, 3),
(5, 4),
(3, 5),
(3, 6),
(1, 7),
(3, 8),
(4, 9),
(2, 10),
(3, 11),
(1, 12),
(2, 13),
(5, 14),
(3, 15),
(3, 16),
(3, 17),
(3, 18),
(4, 19),
(3, 20),
(2, 21),
(1, 22),
(5, 23),
(3, 24),
(3, 25),
(4, 26),
(3, 27),
(1, 28),
(4, 29),
(3, 30),
(4, 31),
(2, 32),
(3, 33),
(5, 34),
(3, 35);

-- ===========================
-- Simpan
-- ===========================
INSERT INTO Simpan (idPengguna, idKegiatan, waktu) VALUES
(1, 1, '2025-10-29 15:00:00'),
(2, 2, '2025-10-29 15:30:00'),
(3, 3, '2025-10-29 16:00:00'),
(4, 4, '2025-10-29 16:30:00'),
(5, 5, '2025-10-29 17:00:00');