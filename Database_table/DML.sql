-- Active: 1761741670299@@127.0.0.1@3307@champart
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
INSERT INTO Pengguna (nama, email, no_telp, prodi, salt, hashed_password, idLampiran) VALUES
('Adam Maulana', 'adam.maulana@student.ac.id', '081234567890', 'Teknik Informatika', 'salt_adam_123', 'hashed_password_adam', 1),
('Dina Amalia', 'dina.amalia@student.ac.id', '081234567891', 'Sistem Informasi', 'salt_dina_456', 'hashed_password_dina', 2),
('Budi Santoso', 'budi.santoso@student.ac.id', '081234567892', 'Teknik Elektro', 'salt_budi_789', 'hashed_password_budi', 3),
('Citra Dewi', 'citra.dewi@student.ac.id', '081234567893', 'Manajemen', 'salt_citra_abc', 'hashed_password_citra', 4),
('Eko Prasetyo', 'eko.prasetyo@student.ac.id', '081234567894', 'Akuntansi', 'salt_eko_def', 'hashed_password_eko', 5);

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
INSERT INTO AdminInstansi (nama, email, jabatan, salt, hashed_password, idInstansi, idLampiran) VALUES
('Rafi Pratama', 'rafi.pratama@ui.ac.id', 'Koordinator Kemahasiswaan', 'salt_rafi_111', 'hashed_password_rafi', 1, 1),
('Siti Nurhaliza', 'siti.nurhaliza@teknologi.com', 'HR Manager', 'salt_siti_222', 'hashed_password_siti', 2, 2),
('Andi Gunawan', 'andi.gunawan@peduli.org', 'Direktur Program', 'salt_andi_333', 'hashed_password_andi', 3, 3),
('Maya Kusuma', 'maya.kusuma@green.org', 'Project Coordinator', 'salt_maya_444', 'hashed_password_maya', 4, 4),
('Teguh Santoso', 'teguh.santoso@startup.id', 'Community Manager', 'salt_teguh_555', 'hashed_password_teguh', 5, 5);

-- ===========================
-- AdminPengawas
-- ===========================
INSERT INTO AdminPengawas (nama, email, jabatan, salt, hashed_password, idLampiran) VALUES
('Dr. Ahmad Fauzi', 'ahmad.fauzi@pengawas.ac.id', 'Pengawas Utama', 'salt_ahmad_aaa', 'hashed_password_ahmad', 1),
('Prof. Rina Wijaya', 'rina.wijaya@pengawas.ac.id', 'Pengawas Senior', 'salt_rina_bbb', 'hashed_password_rina', 2),
('Dedi Kurniawan', 'dedi.kurniawan@pengawas.ac.id', 'Pengawas Lapangan', 'salt_dedi_ccc', 'hashed_password_dedi', 3),
('Yulia Rahayu', 'yulia.rahayu@pengawas.ac.id', 'Quality Assurance', 'salt_yulia_ddd', 'hashed_password_yulia', 4),
('Bambang Setiawan', 'bambang.setiawan@pengawas.ac.id', 'Supervisor', 'salt_bambang_eee', 'hashed_password_bambang', 5);

-- ===========================
-- Kegiatan
-- ===========================
INSERT INTO Kegiatan (nama, deskripsi, waktu, nominal_TAK, TAK_wajib, status_kegiatan, waktuDiupload, idAdminPengawas, idAdminInstansi, idInstansi, idLampiran) VALUES
('Workshop Machine Learning', 'Pelatihan dasar machine learning untuk mahasiswa', '2025-11-15 09:00:00', 10, 1, 'Approved', '2025-10-29 10:00:00', 1, 1, 1, 1),
('Seminar Kewirausahaan Digital', 'Diskusi tentang membangun startup di era digital', '2025-11-20 13:00:00', 8, 0, 'Approved', '2025-10-29 11:00:00', 2, 5, 5, 2),
('Bakti Sosial di Panti Asuhan', 'Kegiatan berbagi dengan anak-anak panti asuhan', '2025-11-25 08:00:00', 12, 1, 'Pending', '2025-10-29 12:00:00', 3, 3, 3, 3),
('Penanaman Pohon Mangrove', 'Aksi peduli lingkungan dengan menanam mangrove', '2025-12-01 07:00:00', 15, 1, 'Approved', '2025-10-29 13:00:00', 4, 4, 4, 4),
('Hackathon 2025', 'Kompetisi programming 48 jam non-stop', '2025-12-10 08:00:00', 20, 0, 'Approved', '2025-10-29 14:00:00', 5, 2, 2, 5);

-- ===========================
-- minatPengguna
-- ===========================
INSERT INTO MinatPengguna (idMinat, idPengguna) VALUES
(3, 1),
(2, 2),
(1, 3),
(4, 4),
(5, 5);

-- ===========================
-- bakatPengguna
-- ===========================
INSERT INTO BakatPengguna (idBakat, idPengguna) VALUES
(3, 1),
(2, 2),
(1, 3),
(5, 4),
(4, 5);

-- ===========================
-- bakatKegiatan
-- ===========================
INSERT INTO BakatKegiatan (idBakat, idKegiatan) VALUES
(3, 1),
(2, 2),
(1, 3),
(5, 4),
(3, 5);

-- ===========================
-- minatKegiatan
-- ===========================
INSERT INTO MinatKegiatan (idMinat, idKegiatan) VALUES
(3, 1),
(2, 2),
(4, 3),
(5, 4),
(3, 5);

-- ===========================
-- Simpan
-- ===========================
INSERT INTO Simpan (idPengguna, idKegiatan, waktu) VALUES
(1, 1, '2025-10-29 15:00:00'),
(2, 2, '2025-10-29 15:30:00'),
(3, 3, '2025-10-29 16:00:00'),
(4, 4, '2025-10-29 16:30:00'),
(5, 5, '2025-10-29 17:00:00');