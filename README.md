# Environment Variables<br/>
`host=your host`<br/>
`user=your user`<br/>
`password=your password`<br/>
`database=your database`<br/>
`apikey=your api key`<br/>

# Table
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