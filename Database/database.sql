CREATE DATABASE IMPAL;

USE IMPAL;

CREATE TABLE Lampiran{
    idLampiran INT PRIMARY KEY AUTO_INCREMENT,
    nama VARCHAR(255) NOT NULL,
    jenis VARCHAR(50) NOT NULL,
    ukuran INT NOT NULL,
    folder VARCHAR(255) NOT NULL
};

CREATE TABLE Pengguna{
    idPengguna INT PRIMARY KEY AUTO_INCREMENT,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    no_telp VARCHAR(15) NOT NULL,
    prodi VARCHAR(100) NOT NULL,
    salt TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    idLampiran INT NOT NULL,
    FOREIGN KEY (idLampiran) REFERENCES Lampiran(idLampiran)
}

CREATE TABLE Minat{
    idMinat INT PRIMARY KEY AUTO_INCREMENT,
    nama VARCHAR(100) NOT NULL
}

CREATE TABLE Bakat{
    idBakat INT PRIMARY KEY AUTO_INCREMENT,
    nama VARCHAR(100) NOT NULL
}

CREATE TABLE instansi{
    idInstansi INT PRIMARY KEY AUTO_INCREMENT,
    nama VARCHAR(100) NOT NULL,
    jenis VARCHAR(50) NOT NULL,
    alamat VARCHAR(255) NOT NULL,
    idLampiran INT NOT NULL,
    FOREIGN KEY (idLampiran) REFERENCES Lampiran(idLampiran)
}

CREATE TABLE AdminInstansi{
    idAdminInstansi INT PRIMARY KEY AUTO_INCREMENT,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    jabatan VARCHAR(100) NOT NULL,
    salt TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    idInstansi INT NOT NULL,
    FOREIGN KEY (idInstansi) REFERENCES instansi(idInstansi),
    idLampiran INT NOT NULL,
    FOREIGN KEY (idLampiran) REFERENCES Lampiran(idLampiran)
}


CREATE TABLE AdminPengawas{
    idAdminPengawas INT PRIMARY KEY AUTO_INCREMENT,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    jabatan VARCHAR(100) NOT NULL,
    salt TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    idLampiran INT NOT NULL,
    FOREIGN KEY (idLampiran) REFERENCES Lampiran(idLampiran)
}

CREATE TABLE Kegiatan{
    idKegiatan INT PRIMARY KEY AUTO_INCREMENT,
    nama VARCHAR(100) NOT NULL,
    deskripsi TEXT NOT NULL,
    waktu DATETIME NOT NULL,
    nominal_TAK INT NOT NULL,
    TAK_wajib BOOLEAN NOT NULL,
    status_kegiatan VARCHAR(50) NOT NULL,
    waktuDiupload DATETIME NOT NULL,
    idAdminPengawas INT NOT NULL,
    FOREIGN KEY (idAdminPengawas) REFERENCES AdminPengawas(idAdminPengawas),
    idAdminInstansi INT NOT NULL,
    FOREIGN KEY (idAdminInstansi) REFERENCES AdminInstansi(idAdminInstansi),
    idInstansi INT NOT NULL,
    FOREIGN KEY (idInstansi) REFERENCES instansi(idInstansi),
    idLampiran INT NOT NULL,
    FOREIGN KEY (idLampiran) REFERENCES Lampiran(idLampiran)
}

CREATE TABLE minatPengguna{
    idMinat INT NOT NULL,
    FOREIGN KEY (idMinat) REFERENCES Minat(idMinat),
    idPengguna INT NOT NULL,
    FOREIGN KEY (idPengguna) REFERENCES Pengguna(idPengguna)
}

CREATE TABLE bakatPengguna{
    idBakat INT NOT NULL,
    FOREIGN KEY (idBakat) REFERENCES Bakat(idBakat),
    idPengguna INT NOT NULL,
    FOREIGN KEY (idPengguna) REFERENCES Pengguna(idPengguna)
}

CREATE TABLE bakatKegiatan{
    idBakat INT NOT NULL,
    FOREIGN KEY (idBakat) REFERENCES Bakat(idBakat),
    idKegiatan INT NOT NULL,
    FOREIGN KEY (idKegiatan) REFERENCES Kegiatan(idKegiatan)
}

CREATE TABLE minatKegiatan{
    idMinat INT NOT NULL,
    FOREIGN KEY (idMinat) REFERENCES Minat(idMinat),
    idKegiatan INT NOT NULL,
    FOREIGN KEY (idKegiatan) REFERENCES Kegiatan(idKegiatan)
}

CREATE TABLE Simpan{
    idPengguna INT NOT NULL,
    FOREIGN KEY (idPengguna) REFERENCES Pengguna(idPengguna),
    idKegiatan INT NOT NULL,
    FOREIGN KEY (idKegiatan) REFERENCES Kegiatan(idKegiatan),
    waktu DATETIME NOT NULL
}