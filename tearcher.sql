/*
 Navicat MySQL Data Transfer

 Source Server         : local
 Source Server Type    : MySQL
 Source Server Version : 50717
 Source Host           : localhost
 Source Database       : tearcher

 Target Server Type    : MySQL
 Target Server Version : 50717
 File Encoding         : utf-8

 Date: 11/04/2018 19:23:39 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `tearchers`
-- ----------------------------
DROP TABLE IF EXISTS `tearchers`;
CREATE TABLE `tearchers` (
  `id` int(8) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `university` varchar(32) NOT NULL COMMENT '大学',
  `college` varchar(32) NOT NULL COMMENT '学院',
  `faculty` varchar(32) DEFAULT NULL COMMENT '系',
  `job` varchar(128) DEFAULT NULL COMMENT '职称',
  `email` varchar(64) DEFAULT NULL,
  `phone` varchar(16) DEFAULT NULL,
  `website` varchar(128) DEFAULT NULL,
  `resume` longtext COMMENT '工作经历',
  `education_resume` text,
  `society_position` text COMMENT '社会任职',
  `research_direction` text COMMENT '研究方向',
  `research_areas` text COMMENT '研究领域',
  `thesis` text COMMENT '论文著作',
  `patent` text COMMENT '专利',
  `research_project` text COMMENT '科研项目',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

SET FOREIGN_KEY_CHECKS = 1;
