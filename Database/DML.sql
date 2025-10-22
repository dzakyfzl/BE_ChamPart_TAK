-- ===========================
-- Lampiran
-- ===========================
INSERT INTO Lampiran (nama, jenis, ukuran, folder) VALUES
('foto_pengguna1.jpg', 'jpg', 204800000, 'https://drive.google.com/file/d/Sfxzz221/view?usp=sharing'),
('foto_diri.jpeg', 'jpeg', 125000000, 'https://drive.google.com/file/d/ds117oouhansm/view?usp=sharing'),
('merry.png', 'png', 102400000, 'https://drive.google.com/file/d/rrrrrrrrr/view?usp=sharing'),
('bangjali.png', 'png', 256000000, 'https://coster-my.sharepoint.com/:w:/p/pz/tytrsg12 '),
('dsd.jpg', 'jpg', 18000000, 'https://fun-my.sharepoint.com/:w:/p/sdjhdhs/12kdsh9o122 ');

-- ===========================
-- Pengguna
-- ===========================
INSERT INTO Pengguna (nama, email, no_telp, fakultas, prodi, salt, hashed_password, idLampiran) VALUES
('Adam Atha', 'adam@example.com', '081234567890', 'Teknik', 'Informatika', 'xyz123', 'hashadam', 1),
('Dina Putri', 'dina@example.com', '081234567891', 'Ekonomi', 'Manajemen', 'abc456', 'hashdina', 1),
('Budi Santoso', 'budi@example.com', '081234567892', 'Teknik', 'Elektro', 'pqr789', 'hashbudi', 1),
('Citra Ayu', 'citra@example.com', '081234567893', 'Sastra', 'Inggris', 'def111', 'hashcitra', 1),
('Eko Saputra', 'eko@example.com', '081234567894', 'Kedokteran', 'Farmasi', 'ghi222', 'hasheko', 1);

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
-- MinatPengguna
-- ===========================
INSERT INTO MinatPengguna (idPengguna, idMinat) VALUES
(1, 3),
(2, 2),
(3, 1),
(4, 5),
(5, 4);

-- ===========================
-- Sektor
-- ===========================
INSERT INTO Sektor (nama) VALUES
('Sosial'),
('Pendidikan'),
('Bisnis'),
('Teknologi'),
('Lingkungan');

-- ===========================
-- SektorPengguna
-- ===========================
INSERT INTO SektorPengguna (idPengguna, idSektor) VALUES
(1, 4),
(2, 3),
(3, 2),
(4, 5),
(5, 1);

-- ===========================
-- Instansi
-- ===========================
INSERT INTO Instansi (nama, jenis, alamat, idLampiran) VALUES
('Universitas Manta', 'Kampus', 'Jl. Mawar No.10', 3),
('Komunitas Digital', 'Organisasi', 'Jl. Melati No.20', 3),
('PT Solusi Teknologi', 'Perusahaan', 'Jl. Anggrek No.15', 3),
('Badan Sosial Peduli', 'Lembaga', 'Jl. Kenanga No.5', 3),
('Lembaga Hijau', 'Lembaga', 'Jl. Pahlawan No.25', 3);

-- ===========================
-- Admin
-- ===========================
INSERT INTO AdminInstansi (idInstansi, nama, email, jabatan, salt, hashed_password, idLampiran) VALUES
(1, 'Rafi Pratama', 'rafi@unimanta.ac.id', 'Admin Utama', 'salt1', 'hash1', 4),
(2, 'Siti Lestari', 'siti@komunitas.id', 'Koordinator', 'salt2', 'hash2', 4),
(3, 'Andi Gunawan', 'andi@solusi.co.id', 'Supervisor', 'salt3', 'hash3', 4),
(4, 'Nurhaliza Putri', 'nur@bsp.org', 'Manager', 'salt4', 'hash4', 4),
(5, 'Teguh Wibowo', 'teguh@hijau.org', 'Koordinator', 'salt5', 'hash5', 4);

-- ===========================
-- AdminPengawas
-- ===========================
INSERT INTO AdminPengawas (nama, email, jabatan, salt, hashed_password, idLampiran) VALUES
('Ahmad Fauzi', 'fauzi@pengawas.id', 'Pengawas Pusat', 'saltA', 'hashA', 5),
('Rina Kusuma', 'rina@pengawas.id', 'Pengawas Bidang', 'saltB', 'hashB', 5),
('Dedi Saputra', 'dedi@pengawas.id', 'Koordinator', 'saltC', 'hashC', 5),
('Yulia Putri', 'yulia@pengawas.id', 'Admin QC', 'saltD', 'hashD', 5),
('Bambang Setiawan', 'bambang@pengawas.id', 'Supervisor', 'saltE', 'hashE', 5);

-- ===========================
-- Kegiatan
-- ===========================
INSERT INTO Kegiatan (idInstansi, nama, jenis, waktu, deskripsi, nominal_TAK, TAK_wajib, status_kegiatan, waktuDiupload, view, idAdminInstansi, idLampiran, idAdminPengawas) VALUES
(1, 'Workshop AI', 'Seminar', '2025-05-12 09:00:00', 'Pelatihan AI untuk mahasiswa', 10, TRUE, 'Aktif', NOW(), 50, 1, 2, 1),
(2, 'Startup Talk', 'Webinar', '2025-06-01 13:00:00', 'Diskusi seputar dunia startup', 8, FALSE, 'Aktif', NOW(), 120, 2, 2, 2),
(3, 'Coding Bootcamp', 'Pelatihan', '2025-07-10 08:00:00', 'Pelatihan intensif coding 3 hari', 12, TRUE, 'Aktif', NOW(), 90, 3, 2, 3),
(4, 'Donor Darah', 'Kegiatan Sosial', '2025-08-15 08:00:00', 'Aksi kemanusiaan donor darah', 5, FALSE, 'Aktif', NOW(), 60, 4, 2, 4),
(5, 'Green Day', 'Volunteer', '2025-09-05 07:00:00', 'Bersih lingkungan kampus', 7, TRUE, 'Aktif', NOW(), 70, 5, 2, 5);

-- ===========================
-- MinatKegiatan
-- ===========================
INSERT INTO MinatKegiatan (idKegiatan, idMinat) VALUES
(1, 3),
(2, 2),
(3, 3),
(4, 4),
(5, 5);

-- ===========================
-- SektorKegiatan
-- ===========================
INSERT INTO SektorKegiatan (idKegiatan, idSektor) VALUES
(1, 4),
(2, 3),
(3, 2),
(4, 1),
(5, 5);

-- ===========================
-- Simpan
-- ===========================
INSERT INTO Simpan (idPengguna, idKegiatan, waktu) VALUES
(1, 1, NOW()),
(2, 2, NOW()),
(3, 3, NOW()),
(4, 4, NOW()),
(5, 5, NOW());