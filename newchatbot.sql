-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jul 15, 2024 at 05:56 AM
-- Server version: 8.0.30
-- PHP Version: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `newchatbot`
--

-- --------------------------------------------------------

--
-- Table structure for table `sessions`
--

CREATE TABLE `sessions` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `role` varchar(50) NOT NULL DEFAULT 'user',
  `timestamp` timestamp NOT NULL,
  `audio_file` varchar(255) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `correction` text,
  `messages` json DEFAULT NULL,
  `conversation_id` varchar(36) DEFAULT NULL,
  `audio_files` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`) VALUES
(1, 'handi', 'scrypt:32768:8:1$wjioq7Hhz277wrmH$a9a34aea51d1a9683869745952c7990edcb0b2ee369a3eaf58388f730594cdc43b1249bde1d247a1842fd9df4393913de4162cdedaee5c04ae6e4760834cfe74'),
(2, 'roroayufasha16@gmail.com', 'scrypt:32768:8:1$tQ1HQHkVZOdPcQ9v$07e8c742ff8b85d15b278cf5639354d045f1992e247f4b847867717f6e75c21eec265f9c8e2c10ae2e7ae63ee8567205911ca6c6c7c6dff6449fdb3a717c2c66'),
(3, 'Velaansas', 'scrypt:32768:8:1$IGAhn3HSfv7tPhCx$d9a2572a76b52f9ffb3125568ae18aea25bcb51862ee911a8ab09212635e3af2ec7f6b716c9a3bda08a1f05630ec49b96be76daff974dc39a727f7f555f1b898');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `sessions`
--
ALTER TABLE `sessions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `idx_user_conversation` (`user_id`,`conversation_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `sessions`
--
ALTER TABLE `sessions`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=256;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `sessions`
--
ALTER TABLE `sessions`
  ADD CONSTRAINT `sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
