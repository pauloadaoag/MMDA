CREATE TABLE traffic_samples(
  `id` INTEGER UNSIGNED AUTO_INCREMENT,
  `segment_id` INTEGER,
  `direction` CHAR(2),
  `road_status` INTEGER,
  `update_time` INTEGER,
  `sample_time` INTEGER,
  `aa` VARCHAR(10),
  `alert_counts` INTEGER,
  `ac` VARCHAR(10),
  `alert_text` TEXT,
  PRIMARY KEY (`id`),
  INDEX  `segment_id_idx` (`segment_id`)
)engine=InnoDB;