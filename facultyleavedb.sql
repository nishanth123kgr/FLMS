-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 23, 2023 at 07:57 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.0.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `facultyleavedb`
--

-- --------------------------------------------------------

--
-- Table structure for table `el`
--

CREATE TABLE `el` (
  `_eL_id` int(4) NOT NULL,
  `id` mediumint(6) NOT NULL,
  `dept` varchar(50) NOT NULL,
  `from` date NOT NULL,
  `to` date NOT NULL,
  `prefix` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`prefix`)),
  `suffix` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`suffix`)),
  `with_permission_on` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`with_permission_on`)),
  `date_of_rejoin` date DEFAULT NULL,
  `total` int(3) NOT NULL,
  `doc` mediumtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `el`
--

INSERT INTO `el` (`_eL_id`, `id`, `dept`, `from`, `to`, `prefix`, `suffix`, `with_permission_on`, `date_of_rejoin`, `total`, `doc`) VALUES
(1, 961018, 'CSE', '2019-12-12', '2019-09-14', NULL, NULL, NULL, NULL, 3, NULL),
(2, 961018, 'CSE', '2020-05-19', '2020-05-23', NULL, NULL, NULL, NULL, 5, NULL),
(3, 961018, 'CSE', '2020-09-28', '2020-09-30', NULL, NULL, '[\"2020-09-27\"]', '2020-10-01', 3, NULL),
(4, 961018, 'CSE', '2020-11-04', '2020-11-07', NULL, NULL, '[\"2020-11-08\"]', '2020-11-09', 4, NULL),
(5, 961018, 'CSE', '2020-11-27', '2020-11-28', NULL, NULL, '[\"2020-11-29\"]', '2020-11-30', 2, NULL),
(6, 961018, 'CSE', '2022-09-14', '2022-09-16', NULL, NULL, '[\"17.09.2022 & 18.09.2022\"]', '2022-09-19', 3, NULL),
(7, 961018, 'CSE', '2022-10-18', '2022-10-20', NULL, NULL, '[\"NIL\"]', '2022-10-21', 3, NULL),
(8, 961018, 'CSE', '2022-11-28', '2022-11-29', NULL, NULL, '[\"2022-11-27\"]', '2022-11-30', 2, NULL),
(9, 961018, 'CSE', '2023-02-09', '2023-02-18', NULL, NULL, '[\"2023-02-19\"]', '2023-02-20', 9, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `ml`
--

CREATE TABLE `ml` (
  `_ml_id` int(6) NOT NULL,
  `id` mediumint(6) NOT NULL,
  `dept` varchar(80) NOT NULL,
  `from` date NOT NULL,
  `to` date NOT NULL,
  `prefix` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`prefix`)),
  `suffix` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`suffix`)),
  `medical_fittness_on` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`medical_fittness_on`)),
  `with_permission_on` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`with_permission_on`)),
  `doj` date NOT NULL,
  `total` int(6) NOT NULL,
  `doc` varchar(300) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `staff`
--

CREATE TABLE `staff` (
  `id` mediumint(6) NOT NULL,
  `name` varchar(50) NOT NULL,
  `department` varchar(80) NOT NULL,
  `doj` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `staff`
--

INSERT INTO `staff` (`id`, `name`, `department`, `doj`) VALUES
(961018, 'Dr.C.Akila', 'CSE', '2009-08-31');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `el`
--
ALTER TABLE `el`
  ADD PRIMARY KEY (`_eL_id`),
  ADD KEY `id` (`id`);

--
-- Indexes for table `ml`
--
ALTER TABLE `ml`
  ADD PRIMARY KEY (`_ml_id`),
  ADD KEY `id` (`id`);

--
-- Indexes for table `staff`
--
ALTER TABLE `staff`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `el`
--
ALTER TABLE `el`
  MODIFY `_eL_id` int(4) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `ml`
--
ALTER TABLE `ml`
  MODIFY `_ml_id` int(6) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `el`
--
ALTER TABLE `el`
  ADD CONSTRAINT `el_ibfk_1` FOREIGN KEY (`id`) REFERENCES `staff` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Constraints for table `ml`
--
ALTER TABLE `ml`
  ADD CONSTRAINT `ml_ibfk_1` FOREIGN KEY (`id`) REFERENCES `staff` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
